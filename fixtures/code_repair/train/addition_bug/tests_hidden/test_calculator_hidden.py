from calculator import add_numbers


def test_negative_numbers():
    assert add_numbers(-2, 5) == 3
