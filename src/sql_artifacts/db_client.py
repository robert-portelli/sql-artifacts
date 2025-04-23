"""
Database client and command runner utilities for PostgreSQL using psycopg.

This module provides two main classes:
- `DatabaseClient`: A context-managed client for executing queries on a PostgreSQL database.
- `PostgresCommandRunner`: A lightweight utility for executing reusable query functions using `DatabaseClient`.

Typical usage involves subclassing or composition with `PostgresCommandRunner` to isolate database logic and simplify testability.
"""

import logging
import psycopg

logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)


class DatabaseClient:
    """
    Context-managed PostgreSQL client using psycopg.

    Handles:
    - Connection lifecycle
    - Automatic transaction management
    - Common query interfaces: execute, fetchall, fetchone
    """

    def __init__(self, mode: str | None = None):
        """
        Initialize a database client with a connection string based on mode.

        Args:
            mode (str | None): One of "dev", "test", or None. Defaults to "test".
        """
        match mode:
            case "dev":
                self.dsn = "postgres://dev:dev@dev-db:5432/sql_artifacts"
                logger.info("DatabaseClient initialized in DEV mode.")
            case "test" | None:
                self.dsn = "postgres://test:test@test-db:5432/sql_artifacts_test_db"
                logger.info("DatabaseClient initialized in TEST mode (ephemeral).")
            case _:
                raise ValueError(f"Invalid mode: {mode!r}. Use 'dev' or 'test'.")

        self.conn: psycopg.Connection | None = None

    def __enter__(self):
        # Establish connection on context entry
        self.conn = psycopg.connect(self.dsn)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        # Ensure connection is closed on context exit
        if self.conn:
            self.conn.close()

    def quote_ident(self, ident):
        """Safely quote a SQL identifier (e.g., schema, table, column)."""
        return '"' + ident.replace('"', '""') + '"'

    def escape_literal(self, value):
        """Safely escape a string value as a SQL literal."""
        return "'" + str(value).replace("'", "''") + "'"

    def execute(self, query, params=None):
        """
        Execute a query with optional parameters and commit the transaction.
        Rolls back on error.
        """
        assert self.conn is not None  # mypy requires explicit non-None assertion

        try:
            with self.conn.cursor() as cur:
                cur.execute(query, params or ())
                self.conn.commit()
        except Exception:
            self.conn.rollback()
            raise

    def execute_insert(self, table: str, fields: list[str], values: list[tuple]):
        assert self.conn is not None

        """
        Safely generate and execute a parameterized INSERT statement.

        Args:
            table (str): Table name (unquoted).
            fields (list[str]): Column names (unquoted).
            values (list[tuple]): One or more row tuples.
        """
        quoted_table = self.quote_ident(table)
        quoted_fields = ", ".join(self.quote_ident(f) for f in fields)
        placeholders = ", ".join(["%s"] * len(fields))
        query = f"INSERT INTO {quoted_table} ({quoted_fields}) VALUES ({placeholders})"

        # Support single-row or multi-row insert
        with self.conn.cursor() as cur:
            if len(values) == 1:
                cur.execute(query, values[0])
            else:
                cur.executemany(query, values)

        self.conn.commit()

    def fetchall(self, query, params=None):
        """
        Execute a SELECT query and return all rows.
        """
        assert self.conn is not None

        with self.conn.cursor() as cur:
            cur.execute(query, params or ())
            return cur.fetchall()

    def fetchone(self, query, params=None):
        """
        Execute a SELECT query and return the first row.
        """
        assert self.conn is not None

        with self.conn.cursor() as cur:
            cur.execute(query, params or ())
            return cur.fetchone()


class PostgresCommandRunner:
    """
    Utility for running one or more query functions using a shared DatabaseClient.

    Designed for test fixtures and batch query operations.
    """

    def __init__(self, mode: str | None = None):
        # Holds an instance of DatabaseClient for use in db_cmd(s)
        self.db_client = DatabaseClient(mode)

    def db_cmd(self, cmd):
        """
        Execute a single command function with a DatabaseClient instance.
        `cmd` should be a lambda or function that accepts a db instance.
        """
        with self.db_client as db:
            return cmd(db)

    def db_cmds(self, *cmds):
        """
        Execute multiple command functions sequentially using a shared connection.
        Each cmd should be a callable accepting a db instance.
        """
        with self.db_client as db:
            return [cmd(db) for cmd in cmds]
