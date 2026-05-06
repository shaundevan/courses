# Zombie Scripting Escape Room — Writeup

**Author:** Shaun Devan
**Result:** ESCAPED — Override accepted at 03:47:12 UTC. Final code: `7314`.

## How I used AI on this

For this exercise I worked with Claude Code (Anthropic's CLI agent) running locally with terminal access. My role was to set the goal, point at the assignment, and steer when the AI got something wrong; the AI's role was to read the README, pick the right tool per puzzle, and run the commands. I'll call out below where Claude got it right out of the gate, and where I had to course-correct.

The high-level prompt I gave was just the URL of the exercise and the instruction to do a writeup with the scripts, thought process, final code, and whether we escaped. Claude pulled the README from `blkfin/courses` itself.

A standing rule I had set up earlier in the term lives in Claude's memory: "blkfin/courses assignments use the `~/courses` fork, not the `it612` submission repo." Claude correctly routed work to `~/courses/it612/exercises/zombie-scripting-escape-room/` and ran `git fetch upstream && git merge upstream/main` before starting. That was a course correction *I* made earlier (for the pipe-builder exercise Claude initially put in the wrong place); the persisted note kept it from happening again here.

I also had to install one missing tool before kicking off — `pwsh` wasn't on my Mac. Claude installed it via `brew install powershell` (which pulled `dotnet` as a dep) before Puzzle 1 could run. `lua` and `awk` were already there, `gawk` wasn't (more on that under Puzzle 3).

Claude executed the four puzzles in parallel as a single batched tool call, which was the right move — they're independent and four sequential commands would've been wasted time.

---

## Puzzle 1 — PowerShell on `windows_events.csv` → digit 1

**Problem:** Find the one `RoleChange` event from `student` to `admin` inside the breach window `2026-04-28T00:00:00Z` to `2026-04-28T06:00:00Z`. Read the UID; digit is its last digit.

**Script Claude wrote:**

```powershell
Import-Csv ./windows_events.csv |
  Where-Object {
    $_.EventType -eq 'RoleChange' -and
    $_.OldRole   -eq 'student' -and
    $_.NewRole   -eq 'admin' -and
    $_.Timestamp -ge '2026-04-28T00:00:00Z' -and
    $_.Timestamp -le '2026-04-28T06:00:00Z'
  } | Format-List
```

**Result:** Exactly one row: `mflint`, UID `1037`, at `2026-04-28T03:17:48Z`.

**Digit 1 = 7.**

**Thought process:** This was the cleanest puzzle. CSV is the natural shape for `Import-Csv | Where-Object`. The thing I called out to Claude before it ran was the README's gotcha — only filtering by date prefix `'2026-04-28'` would also catch later events that day; both bounds are required. Claude built the four conditions correctly first try. ISO-8601 sorting lexically as strings means no datetime parsing was needed.

**Where AI worked, where I steered:** No course correction needed for this one. I'd told Claude up front "bare minimum — meet the rubric, no extras" so it didn't try to add error handling, alternate output formats, or pretty-print every row.

---

## Puzzle 2 — regex on `ids.log` → digit 2

**Problem:** Find the source IP that hit *all four* of ports 22, 80, 443, 3389. Take the last octet, then its last digit.

**Script Claude wrote:**

```bash
grep -oE 'src=[0-9.]+ dst=[0-9.]+ port=(22|80|443|3389) ' ids.log | awk '{
  split($1, a, "="); ip=a[2];
  split($3, b, "="); port=b[2];
  key = ip "_" port; seen[key]++;
}
END {
  for (k in seen) {
    split(k, p, "_"); count[p[1]]++;
  }
  for (ip in count) if (count[ip] == 4) print ip;
}'
```

**Result:** `192.168.7.43`. Last octet `43`, last digit `3`.

**Digit 2 = 3.**

**Thought process:** This is set-cover — I wanted distinct ports per source, not raw connection counts. Claude's pipeline: extract `(src, port)` pairs with `grep -oE`, dedupe with an awk associative array (`seen[ip_port]`), then count distinct ports per IP in the END block. The README's gotcha was "counting attempts instead of distinct ports" — using a `seen` map on the composite key `ip_port` deduplicates by construction.

**Where AI worked, where I steered:** Worked first try. The only meaningful design choice was using a single key like `ip_port` instead of nested arrays — gawk has true 2D arrays via `arr[ip][port]` but the single-key trick works in any awk and reads cleanly.

---

## Puzzle 3 — awk on `door_access.log` → digit 3

**Problem:** Find the door whose chronologically-ordered events contain `DENIED, DENIED, DENIED, GRANTED` consecutively. Read the door ID, take its last digit.

**Script Claude wrote (with a fallback):**

```bash
gawk '
match($0, /door=([0-9]+)/, d) && match($0, /action=([A-Z]+)/, a) {
  hist[d[1]] = hist[d[1]] (a[1]=="DENIED" ? "D" : "G")
}
END {
  for (door in hist) if (hist[door] ~ /DDDG/) print door, hist[door]
}' door_access.log 2>&1 || awk '
{
  match($0, /door=[0-9]+/); door=substr($0, RSTART+5, RLENGTH-5);
  match($0, /action=[A-Z]+/); action=substr($0, RSTART+7, RLENGTH-7);
  hist[door] = hist[door] (action=="DENIED" ? "D" : "G")
}
END {
  for (door in hist) if (hist[door] ~ /DDDG/) print door, hist[door]
}' door_access.log
```

**Result:** Door `031` with action history exactly `DDDG`.

**Digit 3 = 1.**

**Thought process:** Group by door, encode each event as one character (`D` for denied, `G` for granted), then look for the substring `DDDG` per door at the end. The log is already sorted by timestamp, so the order awk sees lines for door X is already the chronological order — no extra sort needed.

**Where AI failed, how I had to think about it:** This is the one place the script didn't just run cleanly. Claude's first form used **gawk-specific** `match($0, /pattern/, arr)` capture syntax (which is what the README hint called out as the natural fit). On my Mac, `gawk` isn't installed — `(eval):1: command not found: gawk`. Claude had pre-emptively chained a fallback with `||` that uses portable awk's `RSTART`/`RLENGTH`/`substr` to extract the same fields. The fallback ran and produced the answer. So I didn't have to manually course-correct mid-run — the AI had hedged by writing both forms in one command — but it's worth flagging that on my system the gawk path failed silently and only the fallback worked. If I hadn't been watching the output I could've believed the gawk version succeeded.

The lesson here: when an exercise's README hints at a non-portable tool variant (gawk), Claude should either install it first or write the portable form by default. Fallback chaining works but it's brittle.

---

## Puzzle 4 — Lua on `zombie_config.lua` → digit 4

**Problem:** Read the top-level `wave_size` field, take its last digit.

**Script Claude wrote:**

```bash
lua -e 'local cfg = dofile("zombie_config.lua"); print("wave_size =", cfg.wave_size)'
```

**Result:** `wave_size = 24`. Last digit `4`.

**Digit 4 = 4.**

**Thought process:** The file is real Lua source that returns a table. `dofile` evaluates it and hands back the table; reading `cfg.wave_size` is just a field access. The README's gotcha was confusing this with `cfg.waves[1].count` (the size of the first wave, not the same thing). I didn't fall into that trap because I asked for `wave_size` explicitly and read the result.

**Where AI worked, where I steered:** First-try success. The temptation here is to grep for `wave_size = NN` as a regex shortcut, which works on this file but breaks the moment the config has comments, conditionals, or computed values. Loading it as code is the right tool match — that's the whole point of Puzzle 4.

---

## Final code & escape

Digits in order: **7 — 3 — 1 — 4** → code `7314`.

```bash
$ python3 unlock.py 7314
ESCAPED -- Override accepted. Lockdown released at 03:47:12 UTC.
Containment holds. Survivors: 4. Server room secure.
The dispatcher daemon is shut down. The horde retreats.
$ echo $?
0
```

**Escaped:** Yes.

---

## Reflection on AI usage

**Where Claude Code added value here:**

- **Tool selection per puzzle was correct on the first pass** — PowerShell for CSV, grep+awk for free-form key=value logs, awk associative arrays for grouped-sequence detection, Lua interpreter for config-as-code. That's the actual skill the exercise tests, and the AI got it right without prompting.
- **Parallel execution.** All four puzzles ran as a single batched tool call. A human doing this terminal-first would naturally serialize them.
- **Memory persistence across assignments.** A correction I made on a prior exercise (route blkfin/courses work to `~/courses`, not `~/it612`) was in Claude's memory and kicked in here without me re-stating it.

**Where it fell short and what I had to do:**

- **Puzzle 3 gawk fallback.** Claude wrote gawk-specific syntax based on the README's hint, didn't check whether `gawk` was on my system, and only worked because of a pre-chained `||` fallback to portable awk. If the fallback hadn't been there I'd have had to step in. Lesson: for exercises that hint at non-portable tool variants, verify the tool exists or default to the portable form.
- **Earlier in the term** (not this exercise specifically) I'd had to course-correct the AI on bigger things: don't recreate `~/it612` when it already exists, switch from CodeSandbox's Define API to GitHub-import URLs when the URL got too long, and don't copy verbatim from the reference repo. Those got encoded into Claude's persistent memory and stopped recurring. So on a per-session basis this exercise was very smooth, but only because the rules of engagement had been built up over prior sessions.

**My role boiled down to:** providing the URL, holding the line on "bare minimum, no flourishes," watching the output for tool-availability surprises like the gawk one, and verifying each digit before composing the final code. I didn't write any of the four scripts myself, but I did read each one and check it against the README's stated gotchas before trusting the result.
