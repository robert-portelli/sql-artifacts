"""
Integration tests for SBA schema operations using live PostgreSQL database.

Covers insertions, constraints, and multi-row queries across business_type and applicant.
"""

import pytest
from sql_artifacts.course_01_creating_postgresql_db.main import SbaFixtureBuilder
from sql_artifacts.db_client import DatabaseClient
import psycopg


@pytest.fixture(scope="module")
def db():
    """Provides a single database connection for integration tests."""
    with DatabaseClient() as client:
        yield client


@pytest.fixture(scope="module", autouse=True)
def setup_tables():
    """Ensures required tables exist before tests begin."""
    builder = SbaFixtureBuilder()
    builder.create_table_business_type()
    builder.create_table_applicant()


@pytest.fixture
def business_type_id(db):
    """Creates and returns a business_type.id for use in foreign key constraints."""
    description = "Test Type"
    db.execute("INSERT INTO business_type (description) VALUES (%s)", (description,))
    result = db.fetchone(
        "SELECT id FROM business_type WHERE description = %s",
        (description,),
    )
    return result[0]


@pytest.mark.usefixtures("setup_tables")
class TestApplicant:
    def test_insert_valid_applicant(self, db, business_type_id):
        """Test inserting a valid applicant with foreign key to business_type."""
        name = "Jane Doe"
        zip_code = "12345"

        db.execute(
            """
            INSERT INTO applicant (name, zip_code, business_type_id)
            VALUES (%s, %s, %s)
        """,
            (name, zip_code, business_type_id),
        )

        result = db.fetchone(
            """
            SELECT name, zip_code, business_type_id FROM applicant
            WHERE name = %s
        """,
            (name,),
        )

        assert result == (name, zip_code, business_type_id)

    def test_insert_invalid_foreign_key(self, db):
        """Assert insert fails when referencing nonexistent business_type_id."""
        with pytest.raises(psycopg.errors.ForeignKeyViolation):
            db.execute(
                """
                INSERT INTO applicant (name, zip_code, business_type_id)
                VALUES (%s, %s, %s)
            """,
                ("Invalid", "00000", 999999),
            )


def test_fetchall_multiple_rows(db, business_type_id):
    """Verify fetchall returns all matching business_type records."""
    descriptions = ["B1", "B2", "B3"]
    for desc in descriptions:
        db.execute("INSERT INTO business_type (description) VALUES (%s)", (desc,))

    results = db.fetchall(
        """
        SELECT description FROM business_type
        WHERE description = ANY(%s)
    """,
        (descriptions,),
    )

    returned = {row[0] for row in results}
    assert returned == set(descriptions)
