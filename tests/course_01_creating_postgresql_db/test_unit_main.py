"""
Unit tests for schema creation using SbaFixtureBuilder.

Tests individual fixture methods for idempotent schema creation.
"""

import pytest
from sql_artifacts.course_01_creating_postgresql_db.main import SbaFixtureBuilder
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
