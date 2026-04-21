import pytest

# Apply marks to all tests in this file
pytestmark = [pytest.mark.table_facilities, pytest.mark.db_tables]


@pytest.fixture(scope="module")
def df_facilities(db_connection):
    """
    Load facilities table once per module to reduce DB calls.
    """
    return db_connection.get_data_sql("SELECT * FROM facilities")


# =========================================================
# BASIC DATA QUALITY CHECKS
# =========================================================

def test_facilities_not_empty(df_facilities, data_quality_library):
    """Table should not be empty."""
    data_quality_library.check_dataset_is_not_empty(df_facilities)


def test_facilities_columns_exist(df_facilities, data_quality_library):
    """Validate required schema."""
    data_quality_library.check_column_exists(
        df_facilities,
        ["id", "external_id", "facility_name", "facility_type", "address", "city", "state"]
    )


def test_facilities_id_no_duplicates(df_facilities, data_quality_library):
    """Primary key must be unique."""
    data_quality_library.check_duplicates(df_facilities, ["id"])


def test_facilities_not_null(df_facilities, data_quality_library):
    """Critical fields must not contain NULLs."""
    data_quality_library.check_not_null_values(
        df_facilities,
        ["id", "facility_name", "facility_type"]
    )