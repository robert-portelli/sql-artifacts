"""
Unit tests for schema creation using SbaFixtureBuilder.

Tests individual fixture methods for idempotent schema creation.
"""

import pytest
from sql_artifacts.course_01_creating_postgresql_db.postgres_db_structure import (
    SbaFixtureBuilder,
)
from sql_artifacts.db_client import DatabaseClient


@pytest.fixture
def db():
    """Provides a fresh database connection for schema introspection."""
    with DatabaseClient() as client:
        yield client


def test_create_table_business_type(db):
    """Ensure business_type table can be created without error."""
    builder = SbaFixtureBuilder()
    builder.create_table_business_type()

    exists = db.fetchone("""
        SELECT EXISTS (
            SELECT FROM information_schema.tables
            WHERE table_name = 'business_type'
        );
    """)
    assert exists == (True,)

    columns = db.fetchall("""
        SELECT column_name, data_type
        FROM information_schema.columns
        WHERE table_name = 'business_type';
    """)
    expected_columns = [("id", "integer"), ("description", "text")]
    # enforce content regardless of order
    assert set(columns) == set(expected_columns)
    # enforce content exact order
    # assert columns == expected_columns


def test_create_table_applicant(db):
    """Ensure applicant table can be created without error."""
    builder = SbaFixtureBuilder()
    builder.create_table_applicant()

    exists = db.fetchone("""
        SELECT EXISTS (
            SELECT FROM information_schema.tables
            WHERE table_name = 'applicant'
        );
    """)
    assert exists == (True,)

    columns = db.fetchall("""
        SELECT column_name, data_type
        FROM information_schema.columns
        WHERE table_name = 'applicant';
    """)
    expected_columns = [
        ("id", "integer"),
        ("name", "text"),
        ("zip_code", "character"),
        ("business_type_id", "integer"),
    ]
    # enforce content regardless of order
    assert set(columns) == set(expected_columns)
    # enforce content exact order
    # assert columns == expected_columns

    # Query all columns in the 'applicant' table that are of type CHAR(n)
    # and return their names and defined character lengths
    char_lengths = db.fetchall("""
        SELECT column_name, character_maximum_length
        FROM information_schema.columns
        WHERE table_name = 'applicant' AND data_type = 'character';
    """)

    # Assert that the 'zip_code' column exists and is defined as CHAR(5)
    # This ensures the column has a fixed length of exactly 5 characters
    assert ("zip_code", 5) in char_lengths
