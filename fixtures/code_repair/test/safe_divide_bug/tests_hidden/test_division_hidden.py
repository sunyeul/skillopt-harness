from division import safe_divide


def test_division_by_zero():
    assert safe_divide(1, 0) is None
