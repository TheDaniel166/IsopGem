import importlib.util
import math
from pathlib import Path

import pytest


def load_safe_math_eval():
    repo_root = Path(__file__).resolve().parents[1]
    module_path = repo_root / "src" / "pillars" / "geometry" / "ui" / "advanced_scientific_calculator_window.py"
    spec = importlib.util.spec_from_file_location("advanced_scientific_calculator_window", module_path)
    if spec is None or spec.loader is None:
        raise RuntimeError("Unable to load calculator module for tests")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


_calc_module = load_safe_math_eval()
_safe_math_eval = _calc_module._safe_math_eval


def smart_backspace(text: str) -> str:
    return _calc_module._smart_backspace(text)


ALLOWED_FUNCS = {
    "sin": math.sin,
    "cos": math.cos,
    "tan": math.tan,
    "asin": math.asin,
    "acos": math.acos,
    "atan": math.atan,
    "sqrt": math.sqrt,
    "log": math.log,
    "log10": math.log10,
    "pow": math.pow,
    "factorial": math.factorial,
    "abs": abs,
    "round": round,
    "deg": math.degrees,
    "rad": math.radians,
    "exp": math.exp,
    "floor": math.floor,
    "ceil": math.ceil,
    "gcd": math.gcd,
    "lcm": math.lcm,
    "min": min,
    "max": max,
}

ALLOWED_CONSTS = {
    "pi": math.pi,
    "e": math.e,
    "tau": math.tau,
    "ans": 0.0,
    "mem": 0.0,
}


def safe_eval(expr: str):
    return _safe_math_eval(expr, allowed_funcs=ALLOWED_FUNCS, allowed_consts=ALLOWED_CONSTS)


@pytest.mark.parametrize(
    "expr, expected",
    [
        ("1+2*3", 7),
        ("(1+2)*3", 9),
        ("2^3", 8),
        ("2**3**2", 512),
        ("-5 + 2", -3),
        ("abs(-3)", 3),
        ("round(1.2345, 2)", 1.23),
        ("sqrt(9)", 3),
        ("factorial(5)", 120),
    ],
)
def test_basic_math(expr, expected):
    assert safe_eval(expr) == expected


def test_trig_and_constants():
    assert pytest.approx(safe_eval("sin(pi/2)"), rel=1e-12, abs=1e-12) == 1.0


def test_unit_suffixes_deg_rad():
    assert safe_eval("sin(90deg)") == pytest.approx(1.0)
    assert safe_eval("cos(180deg)") == pytest.approx(-1.0)
    assert safe_eval("sin(1.5707963267948966rad)") == pytest.approx(1.0)
    assert safe_eval("2 + 30deg") == pytest.approx(2 + math.radians(30))


def test_deg_rad_helpers():
    assert safe_eval("deg(pi)") == pytest.approx(180.0)
    assert safe_eval("rad(180)") == pytest.approx(math.pi)


def test_ans_constant_usage():
    assert safe_eval("ans + 2") == 2


@pytest.mark.parametrize(
    "expr, expected",
    [
        ("2pi", 2 * math.pi),
        ("2(pi)", 2 * math.pi),
        ("2(3+4)", 14),
        ("(1+2)(3+4)", 21),
        ("2sin(pi/2)", 2.0),
        ("(1+1)sqrt(9)", 6.0),
    ],
)
def test_implicit_multiplication(expr, expected):
    assert safe_eval(expr) == pytest.approx(expected)


@pytest.mark.parametrize(
    "expr, expected",
    [
        ("5!", 120),
        ("(3+2)!", 120),
        ("3!!", math.factorial(math.factorial(3))),
        ("2 pi", 2 * math.pi),
        ("2 sin(pi/2)", 2.0),
    ],
)
def test_postfix_factorial_and_whitespace(expr, expected):
    assert safe_eval(expr) == pytest.approx(expected)


def test_factorial_ui_style_postfix():
    assert safe_eval("5!") == 120


def test_more_functions_allowlist():
    assert safe_eval("exp(1)") == pytest.approx(math.e)
    assert safe_eval("floor(1.9)") == 1
    assert safe_eval("ceil(1.1)") == 2
    assert safe_eval("gcd(12, 18)") == 6
    assert safe_eval("lcm(6, 8)") == 24
    assert safe_eval("min(3, 1, 2)") == 1
    assert safe_eval("max(3, 1, 2)") == 3


@pytest.mark.parametrize(
    "before, after",
    [
        ("sin(", ""),
        ("log10(", ""),
        ("factorial(", ""),
        ("2**", "2"),
        ("5!", "5"),
        ("ans", ""),
        ("mem", ""),
        ("12 ", "1"),
    ],
)
def test_smart_backspace(before, after):
    assert smart_backspace(before) == after


@pytest.mark.parametrize(
    "expr",
    [
        "__import__('os').system('echo hi')",
        "(lambda: 1)()",
        "[x for x in (1,2,3)]",
        "(1,2,3)",
        "{'a': 1}",
        "(1<2)",
        "a + 1",
        "sin.__class__",
        "(1).__class__",
        "globals()",
    ],
)
def test_rejects_unsafe_constructs(expr):
    with pytest.raises(ValueError):
        safe_eval(expr)


def test_domain_errors_become_valueerror():
    with pytest.raises(ValueError):
        safe_eval("sqrt(-1)")
