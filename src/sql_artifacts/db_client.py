"""
Database client and command runner utilities for PostgreSQL using psycopg.

This module provides two main classes:
- `DatabaseClient`: A context-managed client for executing queries on a PostgreSQL database.
- `PostgresCommandRunner`: A lightweight utility for executing reusable query functions using `DatabaseClient`.

Typical usage involves subclassing or composition with `PostgresCommandRunner` to isolate database logic and simplify testability.
"""

import os
import psycopg


class DatabaseClient:
    """
    Context-managed PostgreSQL client using psycopg.

    Handles:
    - Connection lifecycle
    - Automatic transaction management
    - Common query interfaces: execute, fetchall, fetchone
    """

    def __init__(self, dsn=None):
        # Use provided DSN or fallback to DATABASE_URL env var
        self.dsn = dsn or os.getenv(
            "DATABASE_URL",
            "postgres://dev:dev@localhost:5432/sql_artifacts",
        )
        self.conn = None

    def __enter__(self):
        # Establish connection on context entry
        self.conn = psycopg.connect(self.dsn)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        # Ensure connection is closed on context exit
        if self.conn:
            self.conn.close()

    def execute(self, query, params=None):
        """
        Execute a query with optional parameters and commit the transaction.
        Rolls back on error.
        """
        try:
            with self.conn.cursor() as cur:
                cur.execute(query, params or ())
                self.conn.commit()
        except Exception:
            self.conn.rollback()
            raise

    def fetchall(self, query, params=None):
        """
        Execute a SELECT query and return all rows.
        """
        with self.conn.cursor() as cur:
            cur.execute(query, params or ())
            return cur.fetchall()

    def fetchone(self, query, params=None):
        """
        Execute a SELECT query and return the first row.
        """
        with self.conn.cursor() as cur:
            cur.execute(query, params or ())
            return cur.fetchone()


class PostgresCommandRunner:
    """
    Utility for running one or more query functions using a shared DatabaseClient.

    Designed for test fixtures and batch query operations.
    """

    def __init__(self, dsn=None):
        # Holds an instance of DatabaseClient for use in db_cmd(s)
        self.db_client = DatabaseClient(dsn)

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
