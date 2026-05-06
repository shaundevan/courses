"""Tests for the expense-refactor lab.

Six tests, all wired up. Initially `test_starter_runs` will pass and
the other five will fail because the four helper functions raise
NotImplementedError. Make them pass as you work through Parts 1-3.

Do not modify any of the assertions in this file.

Run from the lab root:

    pytest -v
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

# Make `src` importable from anywhere pytest is invoked.
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from src.expense_report import (  # noqa: E402
    build_report,
    categorize,
    parse_csv,
    parse_json,
)


def _categories() -> dict:
    return json.loads((ROOT / "data" / "categories.json").read_text())


# -----------------------------------------------------------------------------
# Part 0 — sanity
# -----------------------------------------------------------------------------

def test_starter_runs():
    """`python src/expense_report.py` runs end-to-end and prints a report.

    This test must keep passing through every part — the change requests
    should not change observable behavior on the starting CSV.
    """
    result = subprocess.run(
        [sys.executable, "src/expense_report.py"],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, f"script crashed:\n{result.stderr}"
    assert "Expense Report" in result.stdout
    assert "TOTAL" in result.stdout
    assert "613.87" in result.stdout, "starter total changed; behavior must be preserved"


# -----------------------------------------------------------------------------
# Part 1 — parsing
# -----------------------------------------------------------------------------

def test_parse_csv():
    text = (
        "date,vendor,amount,note\n"
        "2026-04-01,Starbucks,4.85,coffee\n"
        "2026-04-02,Shell,52.30,gas\n"
        "bad,line\n"  # malformed — should be skipped
    )
    rows = parse_csv(text)
    assert len(rows) == 2
    assert rows[0]["vendor"] == "Starbucks"
    assert rows[0]["date"] == "2026-04-01"
    assert float(rows[0]["amount"]) == 4.85
    assert float(rows[1]["amount"]) == 52.30


def test_parse_json():
    text = json.dumps([
        {"date": "2026-04-01", "vendor": "Starbucks", "amount": 4.85, "note": "coffee"},
        {"date": "2026-04-02", "vendor": "Shell",     "amount": 52.30, "note": "gas"},
    ])
    rows = parse_json(text)
    assert len(rows) == 2
    assert rows[1]["vendor"] == "Shell"
    assert float(rows[1]["amount"]) == 52.30


# -----------------------------------------------------------------------------
# Part 2 — categorization
# -----------------------------------------------------------------------------

def test_categorize():
    cats = _categories()
    assert categorize("Starbucks #4421", cats) == "food"
    assert categorize("SHELL Gas Station", cats) == "gas"
    assert categorize("Random Cafe", cats) == "other"


# -----------------------------------------------------------------------------
# Part 3 — pure pipeline
# -----------------------------------------------------------------------------

def test_build_report_does_no_io(monkeypatch, capsys):
    """build_report must not open files or print."""
    def boom(*a, **k):
        raise AssertionError("build_report opened a file")
    monkeypatch.setattr("builtins.open", boom)

    rows = [
        {"date": "2026-04-01", "vendor": "Starbucks", "amount": "4.85", "note": ""},
        {"date": "2026-04-01", "vendor": "Shell",     "amount": "52.30", "note": ""},
    ]
    totals = build_report(rows, _categories())

    captured = capsys.readouterr()
    assert captured.out == "", "build_report must not print"
    assert totals["food"] == pytest.approx(4.85)
    assert totals["gas"] == pytest.approx(52.30)


def test_build_report_uses_passed_categories():
    """build_report respects the categories you pass in — no globals."""
    rows = [
        {"date": "2026-04-01", "vendor": "Starbucks", "amount": "4.85", "note": ""},
    ]
    custom = {"coffee_only": ["STARBUCKS"]}
    totals = build_report(rows, custom)
    assert totals["coffee_only"] == pytest.approx(4.85)
    assert "food" not in totals
