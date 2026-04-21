import pytest
import pandas as pd

"""
Description: Data Quality checks for facility_type_avg_time_spent_per_visit_date parquet data
Requirement(s): TICKET-2
Author(s): Hanna Zykava
"""

pytestmark = [pytest.mark.facility_type_avg_time_spent_per_visit_date, pytest.mark.parquet_data]


@pytest.fixture(scope="module")
def df_parquet(parquet_reader):
    """
    Load parquet dataset once per test module.
    """
    return parquet_reader.read("facility_type_avg_time_spent_per_visit_date")


# =========================================================
# BASIC DATA QUALITY CHECKS
# =========================================================

def test_parquet_not_empty(df_parquet, data_quality_library):
    """Dataset should not be empty"""
    data_quality_library.check_dataset_is_not_empty(df_parquet)


def test_parquet_columns_exist(df_parquet, data_quality_library):
    """Required columns must exist"""
    data_quality_library.check_column_exists(
        df_parquet,
        ["facility_type", "visit_date", "avg_time_spent", "partition_date"]
    )

def test_parquet_not_null(df_parquet, data_quality_library):
    """Critical columns should not contain NULLs"""
    data_quality_library.check_not_null_values(
        df_parquet,
        ["facility_type", "visit_date", "avg_time_spent"]
    )

def test_parquet_no_duplicates(df_parquet, data_quality_library):
    """
    Combination of facility_type + visit_date should be unique
    (aggregation level)
    """
    data_quality_library.check_duplicates(
        df_parquet,
        ["facility_type", "visit_date"]
    )


# =========================================================
# DATA COMPLETENESS CHECK 
# =========================================================

def get_avg_visit_data(db_connection):
    return db_connection.get_data_sql("""
        SELECT
            f.facility_type,
            DATE(v.visit_timestamp) as visit_date,
            ROUND(AVG(v.duration_minutes), 2) AS avg_time_spent,
            TO_CHAR(DATE_TRUNC('month', v.visit_timestamp), 'YYYY-MM') AS partition_date
        FROM visits v
        JOIN facilities f ON v.facility_id = f.id
        GROUP BY 
            f.facility_type, 
            DATE(v.visit_timestamp), 
            TO_CHAR(DATE_TRUNC('month', v.visit_timestamp), 'YYYY-MM')
    """)


def test_parquet_vs_db_row_count(
    df_parquet,
    db_connection,
    data_quality_library
):
    """Row count in parquet and DB should match"""

    df_db = get_avg_visit_data(db_connection)
    data_quality_library.check_count(df_parquet, df_db)


def test_parquet_vs_db_data_match(
    df_parquet,
    db_connection,
    data_quality_library
):
    """Parquet data should fully match DB aggregation"""

    df_db = get_avg_visit_data(db_connection)

    data_quality_library.check_data_full_data_set(
        df_parquet,
        df_db,
        key_columns=["facility_type", "visit_date"],
        compare_columns=["avg_time_spent"]
    )

# =========================================================
# BUSINESS LOGIC CHECKS
# =========================================================

def test_avg_time_spent_positive(df_parquet):
    """
    avg_time_spent must be > 0
    """
    invalid = df_parquet[df_parquet["avg_time_spent"] <= 0]

    assert invalid.empty, (
        f"Found non-positive avg_time_spent values.\n"
        f"Sample:\n{invalid.head(10)}"
    )

def test_visit_date_valid(df_parquet):
    """
    visit_date should not be in the future
    """
    visit_date = pd.to_datetime(df_parquet["visit_date"], errors="coerce")

    invalid = df_parquet[visit_date > pd.Timestamp.now()]

    assert invalid.empty, (
        f"Found future visit_date values.\n"
        f"Sample:\n{invalid.head(10)}"
    )
