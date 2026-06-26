import importlib
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
evaluate_expression = importlib.import_module("calculator").evaluate_expression


def test_precedence_parentheses_unary_and_variables():
    assert evaluate_expression("2 + x * (3 + -1)", {"x": 4}) == 10


def test_integer_division_left_associative():
    assert evaluate_expression("20 // 3 // 2") == 3
