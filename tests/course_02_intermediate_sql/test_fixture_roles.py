from sql_artifacts.db_client import DatabaseClient
from sql_artifacts.course_02_intermediate_sql.fixture_builder import FilmsFixtureBuilder
from sql_artifacts.prepare_csv import CsvHeaderRegistry


def test_roles_table_structure():
    builder = FilmsFixtureBuilder(mode="test")
    builder.create_table_roles()

    expected_columns = [
        field.name for field in CsvHeaderRegistry.for_file(builder._target)
    ]

    with DatabaseClient(mode="test") as db:
        result = db.fetchall("""
            SELECT column_name
            FROM information_schema.columns
            WHERE table_schema = 'public'
              AND table_name = 'roles'
            ORDER BY ordinal_position;
        """)
        actual_columns = [row[0] for row in result]

    assert actual_columns == expected_columns, (
        f"Column mismatch: {actual_columns} != {expected_columns}"
    )
