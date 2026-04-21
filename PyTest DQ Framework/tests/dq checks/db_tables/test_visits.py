import pytest
import pandas as pd

pytestmark = [pytest.mark.table_visits, pytest.mark.db_tables]


@pytest.fixture(scope="module")
def df_visits(db_connection):
    """
    Load visits table once per module to reduce DB calls.
    """
    return db_connection.get_data_sql("SELECT * FROM visits")


# =========================================================
# BASIC DATA QUALITY CHECKS
# =========================================================

def test_visits_not_empty(df_visits, data_quality_library):
    """Table should not be empty."""
    data_quality_library.check_dataset_is_not_empty(df_visits)


def test_visits_columns_exist(df_visits, data_quality_library):
    """Validate required schema."""
    data_quality_library.check_column_exists(
        df_visits,
        ["id", "patient_id", "facility_id", "visit_timestamp", "treatment_cost", "duration_minutes"]
    )


def test_visits_id_no_duplicates(df_visits, data_quality_library):
    """Primary key must be unique."""
    data_quality_library.check_duplicates(df_visits, ["id"])


def test_visits_not_null(df_visits, data_quality_library):
    """Critical fields must not contain NULLs."""
    data_quality_library.check_not_null_values(
        df_visits,
        ["id", "patient_id", "facility_id", "visit_timestamp"]
    )

# =========================================================
# BUSINESS LOGIC CHECKS
# =========================================================

def test_visits_cost_positive(df_visits, data_quality_library):
    """Treatment cost must be >= 0."""
    data_quality_library.check_values_in_range(
        df_visits,
        column="treatment_cost",
        min_value=0
    )


def test_visits_time_positive(df_visits, data_quality_library):
    """Visit duration must be > 0."""
    data_quality_library.check_values_in_range(
        df_visits,
        column="duration_minutes",
        min_value=0
    )


def test_visits_valid_date(df_visits):
    """Visit_date must not be in the future"""
    visit_date = pd.to_datetime(df_visits["visit_timestamp"])
    assert (visit_date <= pd.Timestamp.now()).all(), "Future visit_date detected"
    