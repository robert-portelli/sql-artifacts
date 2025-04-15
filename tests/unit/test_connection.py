import psycopg
import os


def test_can_connect_to_postgres():
    dsn = os.getenv(
        "DATABASE_URL",
        "postgres://test:test@test-db:55432/sql_artifacts_test_db",
    )
    with psycopg.connect(dsn) as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT 1;")
            result = cur.fetchone()
            assert result[0] == 1
