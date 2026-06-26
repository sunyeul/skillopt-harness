from bounds import clamp


def test_value_above_high_is_capped():
    assert clamp(12, 0, 10) == 10
