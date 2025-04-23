"""
Filename: prepare_csv.py

Purpose:
    Exploratory-phase tooling for inspecting and preparing CSV files
    prior to ingestion into a PostgreSQL database. Intended for
    developer/test use only — not runtime logic.

Typical REPL Usage:
    >>> from pathlib import Path
    >>> from sql_artifacts.prepare_csv import inspect_csv, inject_csv_header
    >>> inspect_csv(Path("data/course_02_intermediate_sql/films.csv"), sample=5)
    >>> inspect_csv(Path("data/course_02_intermediate_sql/films.csv"), report_lengths=True)
    >>> inject_csv_header(Path("data/course_02_intermediate_sql/films.csv"))
    >>> inject_csv_header(Path("custom.csv"), headers=["id", "name"], overwrite=False)

Future Enhancements:
1. 🧪 Add validation to ensure postgres_fill values are type-compatible with postgres_type.
"""

import csv
import tempfile
import shutil
from typing import Optional, Union
from pathlib import Path
from collections.abc import Iterable
from itertools import islice
from enum import Enum
from pprint import pformat
from pydantic import BaseModel, field_validator
from sql_artifacts.logger import get_logger

logger = get_logger(__name__)


class PGType(str, Enum):
    # Numeric
    SMALLINT = "SMALLINT"
    INTEGER = "INTEGER"
    BIGINT = "BIGINT"
    NUMERIC = "NUMERIC"
    REAL = "REAL"
    DOUBLE_PRECISION = "DOUBLE PRECISION"

    # Character
    TEXT = "TEXT"
    VARCHAR = "VARCHAR"

    # Boolean
    BOOLEAN = "BOOLEAN"

    # Date/Time
    DATE = "DATE"
    TIMESTAMP = "TIMESTAMP"
    TIMESTAMPTZ = "TIMESTAMPTZ"
    TIME = "TIME"

    # JSON / Others
    JSON = "JSON"
    JSONB = "JSONB"

    # UUID
    UUID = "UUID"


class CsvFieldSpec(BaseModel):
    """
    Represents a single field/column in a CSV file, along with metadata
    about its PostgreSQL type and default fill value for missing data.
    """

    name: str
    postgres_type: PGType
    postgres_fill: Optional[str | float | int | None] = None

    @field_validator("postgres_fill")
    @classmethod
    def validate_fill_value(cls, v, info):
        field_type = info.data.get("postgres_type")
        if v is None:
            return v
        try:
            match field_type:
                case PGType.INTEGER | PGType.SMALLINT | PGType.BIGINT:
                    return int(v)
                case PGType.NUMERIC | PGType.REAL | PGType.DOUBLE_PRECISION:
                    return float(v)
                case PGType.BOOLEAN:
                    if isinstance(v, bool):
                        return v
                    return str(v).lower() in ("true", "1", "t", "yes")
                case (
                    PGType.TEXT
                    | PGType.VARCHAR
                    | PGType.UUID
                    | PGType.JSON
                    | PGType.JSONB
                ):
                    return str(v)
                case _:
                    return v
        except Exception as e:
            raise ValueError(f"Invalid fill value '{v}' for type {field_type}: {e}")


class CsvHeaderRegistry:
    """
    Central mapping of CSV file paths to their structured headers.
    Each entry consists of a tuple of CsvFieldSpec describing the schema.
    """

    _registry = {
        "data/course_02_intermediate_sql/films.csv": (
            CsvFieldSpec(name="id", postgres_type=PGType.INTEGER, postgres_fill=None),
            CsvFieldSpec(name="title", postgres_type=PGType.TEXT, postgres_fill=""),
            CsvFieldSpec(
                name="release_year",
                postgres_type=PGType.INTEGER,
                postgres_fill=None,
            ),
            CsvFieldSpec(name="country", postgres_type=PGType.TEXT, postgres_fill=""),
            CsvFieldSpec(
                name="duration",
                postgres_type=PGType.INTEGER,
                postgres_fill=None,
            ),
            CsvFieldSpec(name="language", postgres_type=PGType.TEXT, postgres_fill=""),
            CsvFieldSpec(
                name="certification",
                postgres_type=PGType.TEXT,
                postgres_fill="",
            ),
            CsvFieldSpec(
                name="gross",
                postgres_type=PGType.NUMERIC,
                postgres_fill=None,
            ),
            CsvFieldSpec(
                name="budget",
                postgres_type=PGType.NUMERIC,
                postgres_fill=None,
            ),
        ),
        "data/course_02_intermediate_sql/people.csv": (
            CsvFieldSpec(name="id", postgres_type=PGType.INTEGER, postgres_fill=None),
            CsvFieldSpec(name="name", postgres_type=PGType.TEXT, postgres_fill=""),
            CsvFieldSpec(
                name="birthdate",
                postgres_type=PGType.DATE,
                postgres_fill="1970-01-01",
            ),
            CsvFieldSpec(
                name="deathdate",
                postgres_type=PGType.DATE,
                postgres_fill=None,
            ),
        ),
        "data/course_02_intermediate_sql/reviews.csv": (
            CsvFieldSpec(name="id", postgres_type=PGType.INTEGER, postgres_fill=None),
            CsvFieldSpec(
                name="duration",
                postgres_type=PGType.INTEGER,
                postgres_fill=None,
            ),
            CsvFieldSpec(
                name="budget",
                postgres_type=PGType.NUMERIC,
                postgres_fill=None,
            ),
            CsvFieldSpec(
                name="imdb_score",
                postgres_type=PGType.REAL,
                postgres_fill=None,
            ),
            CsvFieldSpec(
                name="imdb_votes",
                postgres_type=PGType.INTEGER,
                postgres_fill=0,
            ),
            CsvFieldSpec(
                name="facebook_likes",
                postgres_type=PGType.INTEGER,
                postgres_fill=0,
            ),
        ),
        "data/course_02_intermediate_sql/roles.csv": (
            CsvFieldSpec(name="id", postgres_type=PGType.INTEGER, postgres_fill=None),
            CsvFieldSpec(
                name="film_id",
                postgres_type=PGType.INTEGER,
                postgres_fill=None,
            ),
            CsvFieldSpec(
                name="person_id",
                postgres_type=PGType.INTEGER,
                postgres_fill=None,
            ),
            CsvFieldSpec(name="role", postgres_type=PGType.TEXT, postgres_fill=""),
        ),
    }

    @classmethod
    def for_file(cls, path: Union[str, Path]) -> tuple[CsvFieldSpec, ...]:
        normalized = str(Path(path).as_posix())
        return cls._registry[normalized]

    @classmethod
    def keys(cls) -> list[str]:
        return list(cls._registry.keys())


def inspect_csv(path: Path, sample: int = 10, report_lengths: bool = False) -> None:
    """
    Preview a CSV file by printing a sample of rows and optionally checking consistency.

    Args:
        path (Path): Path to the CSV file.
        sample (int): Number of rows to print. Defaults to 10.
        report_lengths (bool): If True, logs the set of unique row lengths.

    Example:
        >>> inspect_csv(Path("films.csv"), sample=3, report_lengths=True)
    """
    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.reader(f)
        for row in islice(reader, sample):
            logger.info(pformat(row))

    if report_lengths:
        with open(path, newline="", encoding="utf-8") as f:
            reader = csv.reader(f)
            lengths = {len(row) for row in reader}
            logger.info(f"📏 Unique row lengths: {lengths}")


def inject_csv_header(
    path: Path,
    headers: Optional[Iterable[str]] = None,
    overwrite: bool = True,
    use_registry: bool = True,
) -> None:
    """
    Add a header row to a CSV file.

    Args:
        path (Path): CSV file to operate on.
        headers (Optional[Iterable[str]]): Headers to use. If not provided and use_registry=True,
                                          fetches from CsvHeaderRegistry.
        overwrite (bool): Whether to overwrite the input file. If False, writes to *_with_header.csv.
        use_registry (bool): Whether to use registry as fallback when headers not passed explicitly.

    Raises:
        ValueError: If headers cannot be determined.
    """
    if headers is None and use_registry:
        try:
            headers = [field.name for field in CsvHeaderRegistry.for_file(path)]
        except KeyError:
            raise ValueError(
                f"No headers provided and no registry match found for: {path}\n"
                f"To fix: pass headers explicitly or add path to CsvHeaderRegistry.",
            )
    elif headers is None:
        raise ValueError("You must supply headers or set use_registry=True.")

    out_path = path if overwrite else path.with_name(path.stem + "_with_header.csv")

    if not overwrite:
        logger.info(f"✏️  Writing to new file: {out_path}")

    with tempfile.NamedTemporaryFile(
        mode="w",
        newline="",
        encoding="utf-8",
        delete=False,
    ) as tmp:
        writer = csv.writer(tmp)
        writer.writerow(headers)

        with open(path, newline="", encoding="utf-8") as f:
            reader = csv.reader(f)
            writer.writerows(reader)

    shutil.move(tmp.name, out_path)
    logger.info(f"✅ Header injected and saved to: {out_path}")
