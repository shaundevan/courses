# Expense Refactor — Grading Rubric

Total: **100 points**

The rubric is observable: most of the points are tied to specific named
tests passing. The remainder come from how cleanly the refactor moved
logic into the four helper shapes.

---

## Part 1 — Parsing (25 pts)

| Criterion | Points |
|---|---|
| `test_parse_csv` passes | 8 |
| `test_parse_json` passes | 8 |
| Parsing logic for the two formats is **not duplicated** — the row-shaping work isn't pasted twice | 5 |
| `parse_csv` and `parse_json` skip malformed lines / handle the file types they're given without crashing | 4 |

**Common deductions:**
- −5 if there is an `if input.endswith(".json")` branch inside
  `build_report` or other report-building code.
- −3 if either parser opens a file internally (parsers receive *text*,
  not filenames — the contract is in their signatures).

---

## Part 2 — Configurable Categorizer (25 pts)

| Criterion | Points |
|---|---|
| `test_categorize` passes | 10 |
| Categories used in `main()` come from `data/categories.json`, not a hard-coded dict | 8 |
| `categorize` takes the categories dict as a parameter — it does not read it from a global, module-level cache, or file | 7 |

**Common deductions:**
- −5 if the categories are still a module-global dict that `categorize`
  reaches for instead of reading its parameter.
- −5 if there is no clear way to call `categorize` with a different
  config dict from a test (which is what `test_build_report_uses_passed_categories`
  checks indirectly).

---

## Part 3 — Pure Pipeline (35 pts)

| Criterion | Points |
|---|---|
| `test_build_report_does_no_io` passes (no `open`, no `print` inside `build_report`) | 15 |
| `test_build_report_uses_passed_categories` passes | 10 |
| `main()` is reduced to an I/O shell: read files, call `parse_csv`, call `build_report`, print | 5 |
| Running `python src/expense_report.py` still prints the same `TOTAL  $613.87` (behavior preserved) | 5 |

**Common deductions:**
- −10 if they tried to "fix" the no-I/O test by capturing or
  monkeypatching from the test side instead of refactoring.
- −5 if `build_report` returns nothing useful and printing happens
  inside it.
- −5 if the test passes but `python src/expense_report.py` no longer
  produces the same report (behavior must be preserved).

---

## Part 4 — Reflection (15 pts)

| Criterion | Points |
|---|---|
| Q1 (before/after) — concrete, points at specific things in the starter | 4 |
| Q2 (name what you did) — picks one named principle per part and points at lines/functions | 4 |
| Q3 (which hurt most) — names a real first-attempt mistake, not a generic one | 4 |
| Q4 (imagined future change) — believable estimate, walks through what they'd add | 3 |

**Common deductions:**
- −2 per question that is generic ("I learned a lot about coupling
  and decoupling") rather than specific.
- −5 if the reflection is less than half a page — this is the
  assessment that distinguishes "passed the tests" from "understood why."

---

## What "good" looks like

A submission scoring in the 90s typically has these properties:

- **Four real helper functions** filled in, no `NotImplementedError`
  remaining, each doing the one job named in its docstring.
- **A thin `main()`** — the inline parsing loop, the inline category
  dict, and the inline totaling are all gone. `main` just reads, calls,
  and prints. ~15-20 lines.
- **No globals.** `categorize` and `build_report` work entirely from
  what's passed in.
- **Tests pass on first run** after the helpers are filled — meaning the
  function shapes match the tests' expectations naturally, not
  "I tweaked the test output to satisfy the assertions."
- **A reflection that names principles by their lecture vocabulary** and
  points at specific functions or lines — not abstract restatement of
  what was in the README.

---

## What "barely passing" looks like

- Tests pass, but the refactor is shallow — e.g., `parse_csv` and
  `parse_json` exist as separate functions but `build_report` still
  branches on file type internally.
- Categories loaded from JSON but still cached in a module global,
  with `categorize` reaching for the global instead of using its
  argument.
- `main()` is still 30+ lines and `build_report` is a thin wrapper
  around what's still in `main`.

These submissions land in the 70-80 range. Use the reflection to
decide whether the student understood the principle or just satisfied
the test mechanically — that's the difference between 70 and 80.

---

## What "failing" looks like

- Several `NotImplementedError`s remaining and tests still failing.
- They tried to monkeypatch the I/O test rather than refactor the code.
- Reflection is missing or generic.

These submissions land below 60. The fix is conversation in office
hours, not a regrade — the lesson is the refactor, and they didn't do
it.
