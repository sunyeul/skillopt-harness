from query import parse_query


def test_keys_without_equals_and_blank_parts():
    assert parse_query("flag&name=Ada%20Lovelace&&flag=again") == {
        "flag": ["", "again"],
        "name": "Ada Lovelace",
    }
