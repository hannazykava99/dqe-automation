import pytest
import pandas as pd

pytestmark = [pytest.mark.table_patients, pytest.mark.db_tables]


@pytest.fixture(scope="module")
def df_patients(db_connection):
    """
    Load patients table once per module to reduce DB calls.
    """
    return db_connection.get_data_sql("SELECT * FROM patients")


# =========================================================
# BASIC DATA QUALITY CHECKS
# =========================================================

def test_patients_not_empty(df_patients, data_quality_library):
    """Table should not be empty."""
    data_quality_library.check_dataset_is_not_empty(df_patients)


def test_patients_columns_exist(df_patients, data_quality_library):
    """Validate required schema."""
    data_quality_library.check_column_exists(
        df_patients,
        ["id", "external_id", "first_name", "last_name", "address", "date_of_birth"]
    )


def test_patients_id_no_duplicates(df_patients, data_quality_library):
    """Primary key must be unique."""
    data_quality_library.check_duplicates(df_patients, ["id"])


def test_patients_not_null(df_patients, data_quality_library):
    """Critical fields must not contain NULLs."""
    data_quality_library.check_not_null_values(
        df_patients,
        ["id", "external_id", "first_name", "last_name", "date_of_birth"]
    )


# =========================================================
# BUSINESS LOGIC CHECKS
# =========================================================

def test_patients_valid_dob(df_patients):
    """date_of_birth must be in the past."""
    dob = pd.to_datetime(df_patients["date_of_birth"])
    assert (dob < pd.Timestamp.now()).all(), "Found future date_of_birth values"


def test_patients_reasonable_age(df_patients):
    """Age must be realistic (< 120 years)."""
    dob = pd.to_datetime(df_patients["date_of_birth"])
    age = (pd.Timestamp.now() - dob).dt.days / 365
    assert (age < 120).all(), "Unrealistic patient age detected"