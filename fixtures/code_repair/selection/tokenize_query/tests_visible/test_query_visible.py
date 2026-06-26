import importlib
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
parse_query = importlib.import_module("query").parse_query


def test_optional_question_mark_decoding_repeated_keys_and_blank_keys():
    assert parse_query("?q=agent+skill&q=code%20repair&flag&=skip&empty=") == {
        "q": ["agent skill", "code repair"],
        "flag": "",
        "empty": "",
    }
