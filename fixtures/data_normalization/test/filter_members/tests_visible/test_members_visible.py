from members import active_member_ids


def test_active_member_ids():
    assert active_member_ids(
        [
            {"id": "m2", "status": "ACTIVE"},
            {"id": "m1", "status": "inactive"},
            {"id": "m3", "status": "active"},
        ]
    ) == ["m2", "m3"]
