"""
Filename: data_loader.py

Purpose:
    Load CSV files into PostgreSQL tables using the structured DatabaseClient.
    Also provides utilities to inspect CSV files and look up expected headers.

Modules:
    - inspect_csv(): Preview CSV row data in the terminal.
    - load_csv_to_table(): Load a CSV file into a table with optional header overrides.
    - CsvHeaderRegistry: Central mapping of known CSVs to their column definitions.

Typical REPL Usage:
    >>> from pathlib import Path
    >>> from sql_artifacts.data_loader import inspect_csv, load_csv_to_table
    >>> from sql_artifacts.db_client import DatabaseClient

    >>> inspect_csv(Path("data/course_02_intermediate_sql/films.csv"), sample=5)

    >>> with DatabaseClient("dev") as db:
    ...     load_csv_to_table(db, "data/course_02_intermediate_sql/films.csv", "films", verbose=True)

Future enhancements:
    - A CLI command to batch-load all registry entries.
    - Schema validation to catch column count mismatches.
    - A dry-run flag to preview loads without insertion.
"""

import csv
from typing import Union, Optional
from collections.abc import Iterable
from pathlib import Path
from sql_artifacts.db_client import DatabaseClient
from sql_artifacts.prepare_csv import CsvHeaderRegistry
from sql_artifacts.logger import get_logger

logger = get_logger(__name__)


def load_csv_to_table(
    db: DatabaseClient,
    csv_path: Union[str, Path],
    table_name: str,
    delimiter: str = ",",
    has_header: bool = True,
    commit: bool = True,
    verbose: bool = False,
    override_headers: Optional[Iterable[str]] = None,
) -> None:
    """
    Load a CSV file into a PostgreSQL table using DatabaseClient.execute_insert().

    The header row is determined by:
        1. `override_headers`, if provided.
        2. The first row of the CSV file (if `has_header=True`).
        3. A lookup from CsvHeaderRegistry (if `has_header=False` and no override).

    Args:
        db (DatabaseClient): Connected database client.
        csv_path (str | Path): Path to the CSV file.
        table_name (str): Target table name in the database.
        delimiter (str): CSV delimiter. Default ",".
        has_header (bool): Whether the CSV file has a header row. Default True.
        commit (bool): Whether to commit the transaction. Default True.
        verbose (bool): Whether to log row and header data to the terminal.
        override_headers (Iterable[str], optional): Override header detection with explicit headers.

    Raises:
        FileNotFoundError: If the CSV file doesn't exist.
        ValueError: If headers could not be determined or if they are missing.

    Example:
        >>> with DatabaseClient("test") as db:
        ...     load_csv_to_table(
        ...         db,
        ...         "data/course_02_intermediate_sql/people.csv",
        ...         "people",
        ...         verbose=True
        ...     )
    """
    csv_path = Path(csv_path)

    if not csv_path.exists():
        raise FileNotFoundError(f"CSV file not found: {csv_path}")

    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.reader(f, delimiter=delimiter)

        headers: Optional[list[str]]

        # 1. Try using override
        if override_headers:
            headers = list(override_headers)

        # 2. Try reading from file
        elif has_header:
            raw_header = next(reader, None)
            headers = raw_header if raw_header else None

        # 3. Fallback to registry
        else:
            headers = [field.name for field in CsvHeaderRegistry.for_file(csv_path)]

        if headers is None:
            raise ValueError("Headers must be present to insert into a table.")

        rows = [tuple(row) for row in reader]

    if verbose:
        logger.info(
            f"Loading {len(rows)} rows into table '{table_name}' from {csv_path.name}",
        )
        logger.debug(f"CSV headers: {headers}")
        logger.debug(f"Sample row: {rows[0] if rows else 'EMPTY'}")

    db.execute_insert(table=table_name, fields=headers, values=rows)

    if verbose:
        logger.info(f"Insert completed for table '{table_name}'")
