from bounds import clamp


def test_value_below_low_is_capped():
    assert clamp(-4, 0, 10) == 0
