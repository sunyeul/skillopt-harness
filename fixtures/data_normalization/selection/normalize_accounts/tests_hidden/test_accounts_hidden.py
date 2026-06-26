from accounts import normalize_accounts


def test_empty_accounts():
    assert normalize_accounts([]) == []
