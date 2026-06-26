import importlib
import sys
from copy import deepcopy
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
normalize_people = importlib.import_module("people").normalize_people


def test_normalize_people_aliases_deduplicates_schema_and_preserves_input():
    people = [
        {"person_id": "2", "full_name": " grace hopper ", "active": "yes"},
        {"profile": {"id": "1", "name": "ada lovelace"}},
        {"id": 2, "name": "katherine johnson", "active": False},
    ]
    original = deepcopy(people)

    result = normalize_people(people)

    assert result == [
        {"id": 1, "name": "Ada Lovelace", "active": False},
        {"id": 2, "name": "Katherine Johnson", "active": False},
    ]
    assert [set(person) for person in result] == [{"id", "name", "active"}] * 2
    assert people == original
