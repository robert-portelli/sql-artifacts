"""
SBA Fixture Builder for PostgreSQL Database Schema

This module defines the `SbaFixtureBuilder` class, which creates tables used in
Small Business Association (SBA) loan application modeling. Tables include:

- `business_type`: Stores types of businesses (e.g., Corporation, Partnership)
- `applicant`: Stores applicant information with a foreign key to `business_type`

Designed for use in integration tests and fixture setup pipelines.
"""

from typing import Annotated
from sql_artifacts.db_client import PostgresCommandRunner
from pydantic import BaseModel, EmailStr, StringConstraints


class PGUser(BaseModel):
    """
    Represents an application-level user to be inserted into a PostgreSQL `users` table.

    This model validates input fields using Pydantic and can generate a SQL `INSERT` statement
    targeting a specified schema. The default schema is `public`.

    Attributes:
        id (int): Unique identifier for the user (usually a surrogate key).
        first_name (str): User's first name (required).
        last_name (str): User's last name (required).
        email (EmailStr): Validated email address.
        hashed_password (constr): Hashed password with fixed CHAR(72) length.
        schema (str): Name of the schema where the users table resides (default is "public").
    """

    id: int
    first_name: str
    last_name: str
    email: EmailStr
    hashed_password: Annotated[str, StringConstraints(min_length=72, max_length=72)]
    schema: str = "public"  # Default schema for user table

    def to_insert_sql(self) -> str:
        """
        Generates a SQL INSERT statement for the current user instance.

        Returns:
            str: SQL string to insert the user into the specified schema's users table.
        """
        return (
            f"INSERT INTO {self.schema}.users "
            f"(id, first_name, last_name, email, hashed_password) "
            f"VALUES ({self.id}, '{self.first_name}', '{self.last_name}', "
            f"'{self.email}', '{self.hashed_password}');"
        )


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
