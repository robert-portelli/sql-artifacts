"""
SBA Fixture Builder for PostgreSQL Database Schema

This module defines the `SbaFixtureBuilder` class, which creates tables used in
Small Business Association (SBA) loan application modeling. Tables include:

- `business_type`: Stores types of businesses (e.g., Corporation, Partnership)
- `applicant`: Stores applicant information with a foreign key to `business_type`

Designed for use in integration tests and fixture setup pipelines.
"""

from sql_artifacts.db_client import PostgresCommandRunner


class SbaFixtureBuilder(PostgresCommandRunner):
    """
    A table builder for initializing SBA-related database schema.

    Inherits from PostgresCommandRunner, allowing table creation via
    reusable command lambdas.
    """

    def create_table_business_type(self):
        """
        Creates the `business_type` table if it does not already exist.

        Fields:
        - id: Primary key
        - description: Text description of the business type
        """
        self.db_cmd(
            lambda db: db.execute("""
            CREATE TABLE IF NOT EXISTS business_type (
                id SERIAL PRIMARY KEY,
                description TEXT NOT NULL
            );
        """),
        )

    def create_table_applicant(self):
        """
        Creates the `applicant` table if it does not already exist.

        Fields:
        - id: Primary key
        - name: Full name of the applicant
        - zip_code: 5-character ZIP code
        - business_type_id: Foreign key to `business_type(id)`
        """
        self.db_cmd(
            lambda db: db.execute("""
            CREATE TABLE IF NOT EXISTS applicant (
                id SERIAL PRIMARY KEY,
                name TEXT NOT NULL,
                zip_code CHAR(5) NOT NULL,
                business_type_id INTEGER REFERENCES business_type(id)
            );
        """),
        )
