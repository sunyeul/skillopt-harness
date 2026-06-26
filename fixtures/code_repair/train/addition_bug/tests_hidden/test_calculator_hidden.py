import importlib
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
evaluate_expression = importlib.import_module("calculator").evaluate_expression


def test_nested_unary_and_python_floor_division_semantics():
    assert evaluate_expression("-(a + 5) // 2", {"a": 2}) == -4


def test_rejects_missing_variables_bools_and_bad_syntax():
    with pytest.raises(ValueError):
        evaluate_expression("missing + 1", {})
    with pytest.raises(ValueError):
        evaluate_expression("flag + 1", {"flag": True})
    with pytest.raises(ValueError):
        evaluate_expression("1 + * 2")


def test_rejects_division_by_zero_and_trailing_tokens():
    with pytest.raises(ValueError):
        evaluate_expression("4 // (2 - 2)")
    with pytest.raises(ValueError):
        evaluate_expression("1 2")
