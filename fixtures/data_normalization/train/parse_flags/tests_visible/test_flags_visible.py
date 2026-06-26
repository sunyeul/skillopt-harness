from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from flags import normalize_flags


def test_normalizes_key_aliases_tokens_and_later_overrides():
    assert normalize_flags(
        [
            {"key": " Enabled ", "value": "yes"},
            {"name": "Archived", "value": "0"},
            {"key": "enabled", "value": "OFF"},
            {"name": "Preview", "value": True},
            {"key": " ", "value": "yes"},
        ]
    ) == {"enabled": False, "archived": False, "preview": True}
