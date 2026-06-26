from division import safe_divide


def test_regular_division():
    assert safe_divide(6, 3) == 2
