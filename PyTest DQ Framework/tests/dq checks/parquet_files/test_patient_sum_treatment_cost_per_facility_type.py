import pytest
import pandas as pd

"""
Description: Data Quality checks for patient_sum_treatment_cost_per_facility_type rarquet data
Requirement(s): TICKET-3
Author(s): Hanna Zykava
"""

pytestmark = [pytest.mark.patient_sum_treatment_cost_per_facility_type, pytest.mark.parquet_data]


@pytest.fixture(scope="module")
def df_parquet(parquet_reader):
    """
    Load parquet dataset once per test module.
    """
    return parquet_reader.read("patient_sum_treatment_cost_per_facility_type")


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
        ["facility_type", "full_name", "sum_treatment_cost", "facility_type_partition"]
    )

def test_parquet_not_null(df_parquet, data_quality_library):
    """Critical columns should not contain NULLs"""
    data_quality_library.check_not_null_values(
        df_parquet,
        ["facility_type", "full_name", "sum_treatment_cost"]
    )

def test_parquet_no_duplicates(df_parquet, data_quality_library):
    """
    Combination of facility_name + visit_date should be unique
    (aggregation level)
    """
    data_quality_library.check_duplicates(
        df_parquet,
        ["facility_type", "full_name"]
    )


# =========================================================
# DATA COMPLETENESS CHECK 
# =========================================================

def get_treatment_cost_data(db_connection):
    return db_connection.get_data_sql("""
        SELECT
            f.facility_type,
            p.first_name || ' ' || p.last_name AS full_name,
            ROUND(SUM(v.treatment_cost), 2) AS sum_treatment_cost,
            f.facility_type as facility_type_partition
        FROM visits v
        JOIN facilities f ON v.facility_id = f.id
        JOIN patients p ON v.patient_id = p.id
        GROUP BY 
            f.facility_type, 
            p.first_name || ' ' || p.last_name
    """)


def test_parquet_vs_db_row_count(
    df_parquet,
    db_connection,
    data_quality_library
):
    """Row count in parquet and DB should match"""

    df_db = get_treatment_cost_data(db_connection)
    data_quality_library.check_count(df_parquet, df_db)


def test_parquet_vs_db_data_match(
    df_parquet,
    db_connection,
    data_quality_library
):
    """Parquet data should fully match DB aggregation"""

    df_db = get_treatment_cost_data(db_connection)

    data_quality_library.check_data_full_data_set(
        df_parquet,
        df_db,
        key_columns=["facility_type", "full_name"],
        compare_columns=["sum_treatment_cost"]
    )

# =========================================================
# BUSINESS LOGIC CHECKS
# =========================================================

def test_sum_treatment_cost_positive(df_parquet):
    """
    min_time_spent must be > 0
    """
    invalid = df_parquet[df_parquet["sum_treatment_cost"] <= 0]

    assert invalid.empty, (
        f"Found non-positive sum_treatment_cost values.\n"
        f"Sample:\n{invalid.head(10)}"
    )

