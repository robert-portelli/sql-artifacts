"""
Unit tests for DatabaseClient and PostgresCommandRunner.

These tests verify:
- Basic SQL execution with commit/rollback behavior.
- Data retrieval via fetchone and fetchall.
- Use of db_cmd and db_cmds to execute database operations in a reusable pattern.
"""

import pytest
from sql_artifacts.db_client import DatabaseClient, PostgresCommandRunner


@pytest.fixture
def db():
    """
    Yields a fresh DatabaseClient instance for each test.

    Cleans up any temporary test tables before the test runs.
    """
    with DatabaseClient() as client:
        client.execute("DROP TABLE IF EXISTS _test_table_one CASCADE;")
        client.execute("DROP TABLE IF EXISTS _test_table_two CASCADE;")
        yield client


def test_execute_and_fetchone(db):
    """
    Tests inserting and retrieving a single row using execute and fetchone.
    """
    db.execute("""
        CREATE TABLE _test_table_one (
            id SERIAL PRIMARY KEY,
            name TEXT
        )
    """)
    db.execute("INSERT INTO _test_table_one (name) VALUES (%s)", ("Alpha",))
    result = db.fetchone("SELECT name FROM _test_table_one WHERE name = %s", ("Alpha",))
    assert result == ("Alpha",)


def test_fetchall_returns_all_rows(db):
    """
    Tests inserting multiple rows and retrieving them all with fetchall.
    """
    db.execute("""
        CREATE TABLE _test_table_two (
            id SERIAL PRIMARY KEY,
            code TEXT
        )
    """)
    values = [("A1",), ("B2",), ("C3",)]
    for val in values:
        db.execute("INSERT INTO _test_table_two (code) VALUES (%s)", val)

    result = db.fetchall("SELECT code FROM _test_table_two ORDER BY id")
    result_values = [row[0] for row in result]
    assert result_values == ["A1", "B2", "C3"]


def test_db_cmd_runs_function():
    """
    Tests PostgresCommandRunner.db_cmd for executing a single function.
    """
    runner = PostgresCommandRunner()

    def create_simple_table(db):
        db.execute("CREATE TABLE IF NOT EXISTS _cmd_table (id SERIAL PRIMARY KEY)")
        return "created"

    result = runner.db_cmd(create_simple_table)
    assert result == "created"

    # Verify the table was created
    with runner.db_client as db:
        exists = db.fetchone("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables
                WHERE table_name = '_cmd_table'
            )
        """)
        assert exists == (True,)


def test_db_cmds_runs_multiple_commands():
    """
    Tests PostgresCommandRunner.db_cmds for running multiple functions in one connection.
    """
    runner = PostgresCommandRunner()

    def create_one(db):
        db.execute("CREATE TABLE IF NOT EXISTS _cmds_one (id SERIAL PRIMARY KEY)")
        return "one"

    def create_two(db):
        db.execute("CREATE TABLE IF NOT EXISTS _cmds_two (id SERIAL PRIMARY KEY)")
        return "two"

    results = runner.db_cmds(create_one, create_two)
    assert results == ["one", "two"]

    # Verify both tables were created
    with runner.db_client as db:
        tables = db.fetchall("""
            SELECT table_name FROM information_schema.tables
            WHERE table_name IN ('_cmds_one', '_cmds_two')
        """)
        found = {row[0] for row in tables}
        assert found == {"_cmds_one", "_cmds_two"}
