# Expense Refactor — Make It Easy to Change

You will be given a working Python script — `src/expense_report.py` —
that reads a CSV of transactions, categorizes them, and prints a report.
The code **works**. It is also crammed into one big `main()` function with
hard-coded filenames, a hard-coded categories dictionary, and `print()`
statements interleaved with the calculations.

Below `main()` you'll find four helper functions that currently raise
`NotImplementedError`:

```python
parse_csv(text)              # Part 1
parse_json(text)             # Part 1
categorize(vendor, categories)   # Part 2
build_report(rows, categories)   # Part 3
```

Your job: refactor the script **in place** by moving the right logic into
those four shapes, in response to three change requests. Then write a
short reflection naming what you did.

You will not write a lot of *new* code. You will move existing logic into
better shapes so future changes don't fight you.

This lab puts into practice ideas from this semester's design lectures.
You'll name the principles yourself in the reflection.

---

## Setup

```bash
pip install -r requirements.txt
python src/expense_report.py     # see the report
pytest -v tests/                 # see what's currently passing/failing
```

You should see `TOTAL  $613.87` printed. `pytest -v` should show
**1 passing** (`test_starter_runs`) and **5 failing** — those failures are
your roadmap.

---

## Part 0 — Run the starter (5 min)

Run the script and the test suite. Confirm the report prints and
`test_starter_runs` is green.

Then read `src/expense_report.py` carefully. **Before doing anything else,
write down — in your reflection (Part 4) — three things in this script
that would be hard to change.** You'll check that list against what you
discover below.

---

## Part 1 — Add JSON support (25%)

> "Some transactions arrive as JSON now, not CSV. We need to support both
> formats from the same code path."

`data/transactions.json` is the same data in JSON shape:

```json
[
  {"date": "2026-04-01", "vendor": "Starbucks #4421", "amount": 4.85, "note": "morning coffee"},
  ...
]
```

**What you should notice in the starter:**
The CSV-reading loop is woven directly into `main()` (roughly lines 80-87
of `expense_report.py`). There is no place to plug in a different format
without touching that loop.

**Questions to sit with:**
- If JSON support has to live next to CSV support, where does it go?
- What changes for each format? What stays the same?
- Once both formats parse cleanly, what does the rest of `main()` need
  to know about which format the data came from? (You should be able to
  arrange for the answer to be: nothing.)

**Done when:**
- `parse_csv(text)` and `parse_json(text)` both return a list of row
  dicts in the same shape: `{"date", "vendor", "amount", "note"}`.
- `tests/test_parse_csv` and `tests/test_parse_json` pass.
- `python src/expense_report.py` still prints `TOTAL  $613.87`.

**Out of scope for this part:**
- Choosing which format to read at runtime (CLI flags, file detection).
  Keep `main()` reading the CSV. The point of this part is the *shape*
  of the parsing functions, not user-facing format selection.

---

## Part 2 — Configurable categories (25%)

> "Different users want different category schemes. Categories should be
> loaded from a config file, not hard-coded."

`data/categories.json` is the new config format. Each category maps to a
list of vendor keywords. A vendor matches a category if any of its
keywords appears in the vendor name (case-insensitive).

```json
{
  "food":     ["STARBUCKS", "DUNKIN", "WHOLEFOODS", "WHOLE FOODS"],
  "gas":      ["SHELL", "EXXON"],
  ...
}
```

**What you should notice in the starter:**
The category dictionary lives at lines ~92-104 of `main()` — hard-coded
as a flat `{KEYWORD: category}` dict, the *opposite* shape from the JSON
config. To change categories, you have to edit the script.

**Questions to sit with:**
- The new config has the structure `{category: [keywords]}`. How does
  `categorize` need to walk that structure to find a match?
- Why is "load the config from disk" a different concern from
  "given a vendor and a config, decide its category"? Which of those
  belongs in `main()`, and which belongs somewhere else?
- If a test wants to pass in a custom set of categories
  (say, `{"coffee_only": ["STARBUCKS"]}`) to verify behavior, where does
  that custom dict get accepted?

**Done when:**
- `categorize(vendor, categories)` returns the right category given any
  config dict in `{category: [keywords]}` shape, or `"other"` when
  nothing matches.
- `tests/test_categorize` passes.
- The categories used by `main()` come from `data/categories.json`,
  not a hard-coded dict in the script.

**Out of scope:**
- Validating the config file (assume it's well-formed JSON in the
  expected shape).
- Caching or preprocessing the config dict for performance.

---

## Part 3 — A pure pipeline (35%)

> "Write a unit test that runs the full pipeline without touching the
> filesystem or stdout. We want to be able to test the totaling logic in
> isolation."

This is the change request that exposes everything else.

**What you should notice in the starter:**
`main()` mixes three jobs: reading files, computing totals, and printing.
There is no point in the code where you can call "the calculation"
without also doing I/O.

**Questions to sit with:**
- Which lines of `main()` are reading or printing, and which are
  *deciding* what the answer is?
- If `build_report` had to give back its result without printing,
  what shape would it return?
- Where does file reading move to? Where does printing move to?
- After this part, what is `main()`'s job in one sentence?

**Done when:**
- `build_report(rows, categories)` returns a `dict[str, float]` of
  category totals.
- `build_report` does NOT call `open`, read stdin, or print.
  (`tests/test_build_report_does_no_io` monkeypatches `open` to crash
  if it gets called from inside `build_report`.)
- `tests/test_build_report_uses_passed_categories` passes — `build_report`
  uses the categories you pass in, not a globally-loaded dict.
- `main()` is now a thin shell: read the file(s), call `parse_csv`,
  call `build_report`, print the result.
- `python src/expense_report.py` still prints `TOTAL  $613.87`.

**Out of scope:**
- Streaming / large-file handling.
- Logging frameworks. `print` from `main()` is fine.

---

## Part 4 — Reflection (15%)

Create `REFLECTION.md` in the lab root. ~1 page. **Specific beats long.**

1. **Before / after.** What three things in the starter did you write
   down in Part 0 as "hard to change"? Were you right? What surprised
   you?

2. **Name what you did.** For each of Parts 1, 2, 3: which design idea
   from class shows up in your refactor? You learned several this
   semester — *single responsibility*, *dependency injection*,
   *separation of I/O from logic*, *strategy / pluggable parts*. Pick
   the one that fits each part. Point at the lines or function names
   in your code.

3. **The change request that hurt the most.** Which of the three was
   hardest, and why? What was your *first* attempt before you realized
   it wouldn't work?

4. **One imagined future change.** If next week the requirement is
   *"now pull transactions from a remote API,"* walk through what you'd
   add or change in your refactored code. (You don't have to actually
   implement it. About a paragraph is enough.)

---

## Submission

Push your fork to GitHub and submit the URL on Canvas. Your fork should
contain:

- `src/expense_report.py` — refactored. **Keep everything in this one
  file.** This lab is graded on what you do *inside* the file, not on
  splitting it up.
- `tests/test_pipeline.py` — unchanged. All 6 tests passing.
- `REFLECTION.md` — Part 4.
- `data/` — untouched.

`pytest -v` from the lab root should show **all 6 tests passing**.

---

## Grading

| Section | Points |
|---|---|
| Part 0 — starter runs | 0 (sanity) |
| Part 1 — parse_csv + parse_json | 25 |
| Part 2 — categorize from config | 25 |
| Part 3 — pure build_report | 35 |
| Part 4 — reflection | 15 |
| **Total** | **100** |

See `rubric.md` for the per-section breakdown of what we're looking for.

---

## Allowed and not allowed

- **Allowed:** Python standard library only. Type hints encouraged.
  Adding more small helper functions inside `expense_report.py` is fine
  if it makes your code clearer.
- **Not allowed:** External libraries beyond `pytest`. Modifying the
  `data/` files. Modifying any assertion in `tests/test_pipeline.py`.
  Catching the monkeypatched `open` to sneak past Part 3. Splitting
  the code into multiple `.py` files.

---

## When to ask for help

The point of this lab is to *feel* the pain of mixed responsibilities
and the relief of separating them. If you're stuck for more than 30
minutes on the same change request, ask in office hours or on the
discussion board — we'd rather you finish than grind.
