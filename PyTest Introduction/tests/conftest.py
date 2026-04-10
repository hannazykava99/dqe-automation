from pathlib import Path
import pytest
import csv


@pytest.fixture(scope="session")
def path_to_file():
    return Path(__file__).parent.parent / "src" / "data" / "data.csv"


@pytest.fixture(scope="session")
def csv_data(path_to_file):
    with open(path_to_file, newline="") as f:
        reader = csv.DictReader(f)
        return list(reader)


@pytest.fixture(scope="session")
def validate_schema(csv_data):
    expected_schema = {"id", "name", "age", "email", "is_active"}

    for row in csv_data:
        actual_schema = set(row.keys())
        if actual_schema != expected_schema:
            pytest.fail(f"Schema mismatch: {actual_schema} != {expected_schema}")

    return True


# Pytest hook to mark unmarked tests with a custom mark
def pytest_collection_modifyitems(config, items):
    for item in items:
        if not list(item.iter_markers()):
            item.add_marker(pytest.mark.unmarked)