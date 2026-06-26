import importlib
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
top_k_frequent = importlib.import_module("frequency").top_k_frequent


def test_normalizes_strings_skips_blanks_and_preserves_input():
    values = [" Alpha ", "beta", "ALPHA", "", " beta ", 2, 2]

    assert top_k_frequent(values, 3) == ["alpha", "beta", 2]
    assert values == [" Alpha ", "beta", "ALPHA", "", " beta ", 2, 2]
