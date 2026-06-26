import importlib
import sys
from copy import deepcopy
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
normalize_records = importlib.import_module("records").normalize_records


def test_aliases_nested_duplicate_schema_and_no_mutation():
    records = [
        {"record_id": "2", "full_name": " grace hopper ", "active": "yes"},
        {"profile": {"id": "1", "name": "ada lovelace"}},
        {"id": 2, "name": "katherine johnson", "active": False, "extra": "drop"},
    ]
    original = deepcopy(records)

    result = normalize_records(records)

    assert result == [
        {"id": 1, "name": "Ada Lovelace", "active": False},
        {"id": 2, "name": "Katherine Johnson", "active": False},
    ]
    assert [set(record) for record in result] == [{"id", "name", "active"}] * 2
    assert records == original
