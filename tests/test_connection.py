import psycopg
import os


def test_can_connect_to_postgres():
    dsn = os.getenv("DATABASE_URL", "postgres://dev:dev@db:5432/sql_artifacts")
    with psycopg.connect(dsn) as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT 1;")
            result = cur.fetchone()
            assert result[0] == 1
