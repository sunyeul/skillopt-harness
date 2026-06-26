import importlib
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
clamp = importlib.import_module("bounds").clamp


def test_clamp_coerces_numeric_strings_and_normalizes_reversed_bounds():
    assert clamp("12", "10", "0") == 10
