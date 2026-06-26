import importlib
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
parse_query = importlib.import_module("query").parse_query


def test_keys_without_equals_blank_parts_and_repeated_lists():
    assert parse_query("&&flag&name=Ada%20Lovelace&&flag=again&encoded%20key=value%2Fone") == {
        "flag": ["", "again"],
        "name": "Ada Lovelace",
        "encoded key": "value/one",
    }


def test_percent_decoded_keys_and_plus_as_space():
    assert parse_query("?first%20name=Ada+Lovelace&first%20name=Grace%20Hopper") == {
        "first name": ["Ada Lovelace", "Grace Hopper"],
    }
