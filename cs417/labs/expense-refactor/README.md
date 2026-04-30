# Expense Refactor — Make It Easy to Change

## Overview

You will be given a working Python script — `src/expense_report.py` — that
reads a CSV of transactions, categorizes them, and prints a report. The code
**works**. It is also one big `main()` function with hard-coded filenames, a
hard-coded categories dictionary, and `print()` statements scattered through
the logic.

Your job is to refactor that script in response to **three change requests**.
Each change request will hurt to implement in the starter code. Each one
becomes easy after the right refactor. Naming the refactor — *"this is
dependency injection,"* *"this is single responsibility,"* — is the lesson.

You will not be writing a lot of new logic. You will be **moving existing
logic into the right shapes** so future changes don't fight you.

This lab puts into practice the refactoring and design ideas from this
semester's lectures on:

- Single Responsibility (SRP)
- Dependency Injection (DI)
- Strategy / polymorphism
- Separating I/O from logic
- Optimize for change

---

## Setup

```bash
pip install -r requirements.txt
python src/expense_report.py        # see the report
pytest -v tests/                    # only test_starter_runs should pass
```

You should see an expense report printed. The other tests are commented out
in `tests/test_pipeline.py` — you will uncomment and adjust them as you go.

---

## Part 0 — Run the starter (5 min)

Confirm `python src/expense_report.py` produces a report. Confirm
`pytest -v` shows `test_starter_runs PASSED` and zero other tests collected
(yet).

Now read `src/expense_report.py` carefully. Before doing anything else,
**write down** (in your reflection — see Part 4) three things that would be
hard to change about this script. You will check that list against what you
discover in Parts 1–3.

---

## Part 1 — Add JSON support (25%)

> "Some transactions arrive as JSON now, not CSV. We need to support both."

`data/transactions.json` is the same data as `data/transactions.csv` in JSON
shape:

```json
[
  {"date": "2026-04-01", "vendor": "Starbucks #4421", "amount": 4.85, "note": "morning coffee"},
  ...
]
```

**Your task:** make the program handle both CSV and JSON input. *How* the
caller picks (CLI flag, file extension, argument to a function — your call)
is not graded. What is graded: the parsing logic should be a separate
component the pipeline takes as an argument, not a conditional inside the
report-building code.

**The trap:** if you copy the parsing block and paste it into an
`if filename.endswith(".json")` branch, you will pass this part. You will
also make Part 2 and Part 3 harder. Read the change request and ask: *what
should this code actually look like so the next parser format is trivial?*

**Hint (only if stuck):** what if there were a `Parser` interface with a
`.parse(source)` method, and `CSVParser` and `JSONParser` both implemented it?
The pipeline takes a parser as an argument. (This is **dependency injection**
+ **strategy pattern**.)

After Part 1, uncomment `test_csv_parsing_no_io` and `test_json_parsing_no_io`
in `tests/test_pipeline.py` and adjust the imports to point at whatever you
named your modules. Run `pytest -v` until they pass.

---

## Part 2 — User-configurable categories (25%)

> "Different users have different category schemes. Categories should be
> loaded from a config file at startup, not hard-coded."

`data/categories.json` is the new config format. Each category maps to a list
of vendor keywords. A vendor matches a category if any of its keywords appears
in the vendor name (case-insensitive).

**Your task:** stop hard-coding the categories dict. Load it from the config
file. Make it easy to **swap categorizers** — for example, in a test, pass in
a tiny in-memory dict instead of reading the file.

**The trap:** if you turn `categories` into a global module variable read at
import time, your tests will start fighting you. Reading the file is one
concern; categorizing a vendor is another. Keep them separate.

**Hint:** consider a `Categorizer` class whose constructor takes the dict.
Loading the dict from disk is somebody else's job (a separate function or
module). Your pipeline takes a `Categorizer` as an argument, not a filename.

After Part 2, uncomment `test_swap_categorizer` and make it pass.

---

## Part 3 — The killer test (35%)

> "Write a unit test that runs the full pipeline without touching the
> filesystem, the network, or stdout."

This is the change request that exposes everything. If your pipeline still
opens files internally, or prints partway through, you cannot pass this test
without refactoring further.

**Your task:** refactor your pipeline so the *core logic* — parsing
in-memory data, categorizing, computing totals — does **no I/O at all**.
Reading the file becomes the caller's job. Printing becomes the caller's
job. Your `build_report(parser, categorizer, source)` (or whatever you call
it) returns a dict and that's it.

The CLI entry point — the `main()` that the user runs — is where I/O
happens. The library functions stay pure.

**The trap:** "I'll just monkeypatch `open()` and `print()` in the test."
Don't. The test deliberately monkeypatches `open` to crash if your code
calls it. Refactor the code, don't trick the test.

After Part 3, uncomment `test_pipeline_does_no_io` and make it pass. All
four real tests + `test_starter_runs` should now pass.

---

## Part 4 — Reflection (15%)

Create `REFLECTION.md` in the lab root. Answer all four questions. **Aim for
~1 page total.** Specific beats long.

1. **Before/after.** What were the three things you wrote down in Part 0
   that would be hard to change? Were you right? Did anything else turn out
   harder than you expected, or easier?

2. **Name the patterns.** For each of Parts 1, 2, 3: which design principle
   or pattern from class shows up in your refactor? (DI, SRP, strategy,
   separation of I/O, etc.) Point at the specific lines/functions where it
   shows up.

3. **The change request that hurt the most.** Which of the three was
   hardest, and why? What was your *first* attempt before you realized it
   wouldn't work?

4. **One imagined future change.** If next week the requirement is *"now
   pull transactions from a remote API,"* how long does it take you to
   implement, given your current code? Walk through what you'd add or
   change. (You don't have to actually implement it.)

---

## Submission

Push your fork to GitHub and submit the URL on Canvas. Your fork should
contain:

- `src/` — your refactored code (multiple files is normal here)
- `tests/test_pipeline.py` — with the originally-commented tests now
  uncommented and passing
- `REFLECTION.md` — Part 4
- The original `data/` folder, untouched

`pytest -v` from the lab root should show **5 passing tests** when graded.

---

## Grading

| Section | Points |
|---|---|
| Part 0 — starter runs | 0 (sanity) |
| Part 1 — CSV + JSON parsing | 25 |
| Part 2 — configurable categorizer | 25 |
| Part 3 — pure pipeline / no I/O | 35 |
| Part 4 — reflection | 15 |
| **Total** | **100** |

See `rubric.md` for the per-section breakdown of what we're looking for.

---

## Allowed and not-allowed

- **Allowed:** refactor anything in `src/`. Add new files in `src/`. Rename
  things. Change function signatures. Use anything from the Python standard
  library.
- **Not allowed:** add external libraries beyond `pytest`. Modify the
  `data/` files. Modify the assertions in the provided tests. Catch the
  monkeypatched `open` failure to sneak past Part 3.
- **Encouraged:** type hints, docstrings, dataclasses where they fit.

---

## When to ask for help

The point of this lab is to *feel* the pain of bad coupling and the relief
of fixing it. If you're stuck for more than 30 minutes on the same change
request, ask in office hours or on the discussion board — we'd rather you
finish than grind.
