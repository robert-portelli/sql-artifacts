import pytest
from sql_artifacts.course_01_creating_postgresql_db.postgres_db_structure import (
    SbaFixtureBuilder,
    PGUser,
)
from sql_artifacts.db_client import DatabaseClient


@pytest.fixture
def db():
    """
    Provides a fresh DatabaseClient instance to use in assertions.
    Automatically connects and closes the database connection.
    """
    with DatabaseClient() as client:
        yield client


@pytest.fixture(scope="module")
def sba_fixture():
    """
    Creates schemas and tables according to the course flow.
    Schema creation is idempotent and safe for reuse across tests.
    """

    builder = SbaFixtureBuilder()

    # Create User Table
    builder.create_table_users()

    # Create user:
    builder.insert_user(
        PGUser(
            id=1,
            first_name="Robert",
            last_name="Portelli",
            email="rp@example.com",
            hashed_password="x" * 72,
        ),
    )

    # Create base tables
    builder.create_table_business_type()
    builder.create_table_applicant()

    # Create schemas
    builder.create_schema("loan_504")
    builder.create_schema("loan_7a")

    # Create bank and borrower tables in both schemas
    builder.create_table_bank("loan_504")
    builder.create_table_borrower("loan_504")
    builder.create_table_bank("loan_7a", with_express_provider=True)
    builder.create_table_borrower("loan_7a", with_individual_flag=True)

    return builder


pytestmark = pytest.mark.usefixtures("sba_fixture")


def test_applicant_business_type_fk_constraint(db):
    """
    Ensure applicant.business_type_id references business_type(id)
    """
    result = db.fetchone("""
        SELECT
            tc.constraint_type,
            kcu.column_name,
            ccu.table_name AS foreign_table,
            ccu.column_name AS foreign_column
        FROM information_schema.table_constraints AS tc
        JOIN information_schema.key_column_usage AS kcu
          ON tc.constraint_name = kcu.constraint_name
        JOIN information_schema.constraint_column_usage AS ccu
          ON ccu.constraint_name = tc.constraint_name
        WHERE tc.table_name = 'applicant'
          AND tc.constraint_type = 'FOREIGN KEY';
    """)

    assert result == ("FOREIGN KEY", "business_type_id", "business_type", "id")


def test_table_business_type_exists(db):
    result = db.fetchone("""
        SELECT EXISTS (
            SELECT FROM information_schema.tables
            WHERE table_name = 'business_type'
        );
    """)
    assert result == (True,)


def test_schema_loan_504_exists(db):
    result = db.fetchone("""
        SELECT schema_name FROM information_schema.schemata
        WHERE schema_name = 'loan_504';
    """)
    assert result == ("loan_504",)


def test_borrower_loan_504_columns(db):
    result = db.fetchall("""
        SELECT column_name, data_type
        FROM information_schema.columns
        WHERE table_schema = 'loan_504' AND table_name = 'borrower';
    """)
    expected = {("id", "integer"), ("full_name", "character varying")}
    assert set(result) == expected


def test_bank_loan_7a_columns(db):
    result = db.fetchall("""
        SELECT column_name, data_type
        FROM information_schema.columns
        WHERE table_schema = 'loan_7a' AND table_name = 'bank';
    """)
    expected = {
        ("id", "integer"),
        ("name", "character varying"),
        ("express_provider", "boolean"),
    }
    assert set(result) == expected


def test_user_exists(db):
    result = db.fetchone("""
        SELECT first_name, last_name, email
        FROM public.users
        WHERE id = 1;
    """)
    assert result == ("Robert", "Portelli", "rp@example.com")


def test_users_table_columns(db):
    """
    Assert that the 'users' table exists in the public schema and has the expected columns.
    """
    # Confirm the table exists
    result = db.fetchone("""
        SELECT EXISTS (
            SELECT FROM information_schema.tables
            WHERE table_schema = 'public' AND table_name = 'users'
        );
    """)
    assert result == (True,)

    # Confirm the expected columns and types
    columns = db.fetchall("""
        SELECT column_name, data_type, character_maximum_length
        FROM information_schema.columns
        WHERE table_schema = 'public' AND table_name = 'users';
    """)

    expected_columns = {
        ("id", "integer", None),
        ("first_name", "text", None),
        ("last_name", "text", None),
        ("email", "text", None),
        ("hashed_password", "character", 72),
    }

    assert set(columns) == expected_columns


def test_SbaFixtureBuilder_has_expected_methods():
    builder = SbaFixtureBuilder()
    assert hasattr(builder, "create_table_users")
    assert hasattr(builder, "insert_user")
    assert callable(builder.create_schema)
