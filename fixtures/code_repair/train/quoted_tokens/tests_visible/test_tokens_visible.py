import importlib
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
parse_tokens = importlib.import_module("tokens").parse_tokens


def test_commas_whitespace_and_quoted_groups():
    assert parse_tokens('alpha, "two words", beta  \'three,four\'') == [
        "alpha",
        "two words",
        "beta",
        "three,four",
    ]


def test_empty_quoted_tokens_are_preserved():
    assert parse_tokens("start '' \"\" end") == ["start", "", "", "end"]
