import os
import psycopg


class DatabaseClient:
    def __init__(self, dsn=None):
        self.dsn = dsn or os.getenv(
            "DATABASE_URL",
            "postgres://dev:dev@localhost:5432/sql_artifacts",
        )
        self.conn = None

    def __enter__(self):
        self.conn = psycopg.connect(self.dsn)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.conn:
            self.conn.close()

    def execute(self, query, params=None):
        try:
            with self.conn.cursor() as cur:
                cur.execute(query, params or ())
                self.conn.commit()
        except Exception:
            self.conn.rollback()
            raise

    def fetchall(self, query, params=None):
        with self.conn.cursor() as cur:
            cur.execute(query, params or ())
            return cur.fetchall()

    def fetchone(self, query, params=None):
        with self.conn.cursor() as cur:
            cur.execute(query, params or ())
            return cur.fetchone()


class PostgresCommandRunner:
    def __init__(self, dsn=None):
        self.db_client = DatabaseClient(dsn)

    def db_cmd(self, cmd):
        with self.db_client as db:
            return cmd(db)

    def db_cmds(self, *cmds):
        with self.db_client as db:
            return [cmd(db) for cmd in cmds]
