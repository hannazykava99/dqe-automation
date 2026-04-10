import pytest
import re


def test_file_not_empty(csv_data):
    assert len(csv_data) > 0, "CSV file is empty"


@pytest.mark.validate_csv
def test_validate_schema(validate_schema):
    assert validate_schema, "CSV schema validation failed"


@pytest.mark.validate_csv
@pytest.mark.skip(reason="Skipping age validation as required")
def test_age_column_valid(csv_data):
    for row in csv_data:
        age = int(row["age"])
        assert 0 <= age <= 100, f"Invalid age: {age}"


@pytest.mark.validate_csv
def test_email_column_valid(csv_data):
    pattern = r"^[\w\.]+@[\w\.]+\.\w+$"
    for row in csv_data:
        assert re.match(pattern, row["email"]), f"Invalid email: {row['email']}"


@pytest.mark.validate_csv
@pytest.mark.xfail(reason="There are expected duplicates in dataset")
def test_duplicates(csv_data):
    unique = set()
    for row in csv_data:
        row_tuple = tuple(row.items())
        assert row_tuple not in unique, f"Duplicate row found: {row}"
        unique.add(row_tuple)


@pytest.mark.parametrize(
    "player_id, is_active",
    [
        ("1", "FALSE"),
        ("2", "TRUE"),
    ],
)
def test_active_players(csv_data, player_id, is_active):
    player = next((row for row in csv_data if row["id"] == player_id), None)

    assert player is not None, f"Player with id={player_id} not found"
    assert player["is_active"] == is_active, (
        f"Incorrect is_active for id={player_id}: "
        f"expected {is_active}, got {player['is_active']}"
    )


def test_active_player(csv_data):
    player = next((row for row in csv_data if row["id"] == "2"), None)

    assert player is not None, "Player with id=2 not found"
    assert player["is_active"] == "TRUE", (
        f"Incorrect is_active for id=2: got {player['is_active']}"
    )
