"""
Description: Verify basic functionality and ensure the dataset is ready for further testing
Requirement(s): TICKET-1
Author(s): Hanna Zykava
"""

import pytest

# Mark all tests in this file as "smoke"
# Allows running only smoke tests via: pytest -m smoke
pytestmark = pytest.mark.smoke


# List of expected tables in the database (public schema)
EXPECTED_TABLES = [
    "facilities",
    "patients",
    "visits"
]


# List of expected parquet datasets (files or folders)
EXPECTED_PARQUET = [
    "facility_name_min_time_spent_per_visit_date",
    "facility_type_avg_time_spent_per_visit_date",
    "patient_sum_treatment_cost_per_facility_type"
]


# ------------------------
# DB CHECKS
# ------------------------

def test_db_connection(db_connection):
    """
    Verify that the database connection is working.

    Executes a simple query (SELECT 1) to ensure the DB is reachable
    and responding correctly.
    """
    result = db_connection.execute_scalar("SELECT 1")

    # Expect a valid response from DB
    assert result == 1


def test_tables_exist(db_connection):
    """
    Verify that all expected tables exist in the database.

    Queries information_schema to retrieve all tables
    from the 'public' schema and checks against the expected list.
    """
    df = db_connection.get_data_sql("""
        SELECT table_name
        FROM information_schema.tables
        WHERE table_schema = 'public'
    """)

    # Convert result to list for easy comparison
    db_tables = df["table_name"].tolist()

    # Check each expected table is present
    for table in EXPECTED_TABLES:
        assert table in db_tables, f"Missing table: {table}"


@pytest.mark.parametrize("table", EXPECTED_TABLES)
def test_tables_not_empty(db_connection, table):
    """
    Verify that each table contains at least one row.

    Uses COUNT(*) for efficiency instead of loading full data.
    """
    count = db_connection.execute_scalar(
        f"SELECT COUNT(*) FROM {table}"
    )

    # Table should not be empty
    assert count > 0, f"Table {table} is empty"


# ------------------------
# PARQUET CHECKS
# ------------------------

@pytest.mark.parametrize("dataset", EXPECTED_PARQUET)
def test_parquet_exists(parquet_reader, dataset):
    """
    Verify that parquet dataset exists and can be read.

    If the dataset does not exist, the reader will raise an error.
    """
    df = parquet_reader.read(dataset)

    # If read succeeds, df should not be None
    assert df is not None


@pytest.mark.parametrize("dataset", EXPECTED_PARQUET)
def test_parquet_not_empty(parquet_reader, dataset):
    """
    Verify that parquet dataset is not empty.

    Ensures that the dataset contains at least one row.
    """
    df = parquet_reader.read(dataset)

    # Dataset should contain data
    assert not df.empty, f"Parquet dataset {dataset} is empty"