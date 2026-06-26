from query import parse_query


def test_decodes_values_and_repeated_keys():
    assert parse_query("q=agent+skill&q=code%20repair&empty=") == {
        "q": ["agent skill", "code repair"],
        "empty": "",
    }
