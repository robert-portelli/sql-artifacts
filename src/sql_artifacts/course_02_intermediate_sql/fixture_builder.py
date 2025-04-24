from sql_artifacts.db_client import PostgresCommandRunner
from sql_artifacts.prepare_csv import CsvHeaderRegistry


class FilmsFixtureBuilder(PostgresCommandRunner):
    """
    A table builder for initializing the `films` table for the Intermediate SQL course.

    Inherits from PostgresCommandRunner, allowing table creation via reusable command lambdas.
    """

    _target = "data/course_02_intermediate_sql/films.csv"

    def __init__(self, mode: str | None = None):
        super().__init__(mode=mode)

    def create_table_films(self):
        """
        Creates the 'films' table using the schema defined in CsvHeaderRegistry.
        """
        fields = CsvHeaderRegistry.for_file(self._target)
        column_definitions = ",\n    ".join(
            f'"{field.name}" {field.postgres_type.value}' for field in fields
        )
        ddl = f"""
        CREATE TABLE IF NOT EXISTS films (
            {column_definitions}
        );
        """
        self.db_cmd(lambda db: db.execute(ddl))

    def create_table_people(self):
        """
        Creates the 'people' table using the schema defined in CsvHeaderRegistry.
        """
        fields = CsvHeaderRegistry.for_file(self._target)
        column_definitions = ",\n    ".join(
            f'"{field.name}" {field.postgres_type.value}' for field in fields
        )
        ddl = f"""
        CREATE TABLE IF NOT EXISTS people (
            {column_definitions}
        );
        """
        self.db_cmd(lambda db: db.execute(ddl))

    def create_table_reviews(self):
        """
        Creates the 'reviews' table using the schema defined in CsvHeaderRegistry.
        """
        fields = CsvHeaderRegistry.for_file(self._target)
        column_definitions = ",\n    ".join(
            f'"{field.name}" {field.postgres_type.value}' for field in fields
        )
        ddl = f"""
        CREATE TABLE IF NOT EXISTS reviews (
            {column_definitions}
        );
        """
        self.db_cmd(lambda db: db.execute(ddl))

    def create_table_roles(self):
        """
        Creates the 'roles' table using the schema defined in CsvHeaderRegistry.
        """
        fields = CsvHeaderRegistry.for_file(self._target)
        column_definitions = ",\n    ".join(
            f'"{field.name}" {field.postgres_type.value}' for field in fields
        )
        ddl = f"""
        CREATE TABLE IF NOT EXISTS roles (
            {column_definitions}
        );
        """
        self.db_cmd(lambda db: db.execute(ddl))
