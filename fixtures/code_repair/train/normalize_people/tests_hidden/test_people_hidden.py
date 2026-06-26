import importlib
import sys
from copy import deepcopy
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
normalize_people = importlib.import_module("people").normalize_people


def test_active_token_map_sorting_and_no_mutation():
    people = [
        {"id": "3", "name": "  mary jackson  ", "active": "inactive"},
        {"profile": {"id": "1", "name": "dorothy vaughan"}, "active": "Y"},
        {"person_id": 2, "full_name": "katherine johnson", "active": "0"},
    ]
    original = deepcopy(people)

    assert normalize_people(people) == [
        {"id": 1, "name": "Dorothy Vaughan", "active": True},
        {"id": 2, "name": "Katherine Johnson", "active": False},
        {"id": 3, "name": "Mary Jackson", "active": False},
    ]
    assert people == original


def test_duplicate_ids_keep_last_normalized_record():
    assert normalize_people(
        [
            {"id": 1, "name": "ada lovelace", "active": True},
            {"person_id": "1", "full_name": "grace hopper", "active": "no"},
        ]
    ) == [
        {"id": 1, "name": "Grace Hopper", "active": False},
    ]


def test_invalid_records_raise_value_error():
    with pytest.raises(ValueError):
        normalize_people([{"name": "missing id"}])

    with pytest.raises(ValueError):
        normalize_people([{"id": 1}])

    with pytest.raises(ValueError):
        normalize_people([{"id": "abc", "name": "bad id"}])

    with pytest.raises(ValueError):
        normalize_people([{"id": 1, "name": "bad active", "active": "maybe"}])


def test_empty_input_returns_empty_list():
    assert normalize_people([]) == []
