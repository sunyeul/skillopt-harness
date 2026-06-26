from members import active_member_ids


def test_blank_ids_and_missing_status_are_skipped():
    assert active_member_ids(
        [{"id": " "}, {"id": "m1"}, {"id": "m0", "status": "Active"}]
    ) == ["m0"]
