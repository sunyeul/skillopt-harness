import importlib
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
parse_tokens = importlib.import_module("tokens").parse_tokens


def test_quoted_escapes_and_comments():
    assert parse_tokens(r'run "a \"quoted\" value" tag\ # ignored outside quotes') == [
        "run",
        'a "quoted" value',
        "tag ",
    ]


def test_hash_inside_quotes_is_not_a_comment():
    assert parse_tokens("'keep # hash', next # drop this") == ["keep # hash", "next"]


def test_rejects_unterminated_quote_and_dangling_quoted_escape():
    with pytest.raises(ValueError):
        parse_tokens('"unterminated')
    with pytest.raises(ValueError):
        parse_tokens(r"'dangling\'")


def test_backslash_escapes_separators_and_comment_marker_outside_quotes():
    assert parse_tokens(r"one\ two, three\,four, hash\#tag # real comment") == [
        "one two",
        "three,four",
        "hash#tag",
    ]
    with pytest.raises(ValueError):
        parse_tokens("trailing\\")
