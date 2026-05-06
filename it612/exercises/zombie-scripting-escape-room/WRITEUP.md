# Zombie Scripting Escape Room Writeup

**Author:** Shaun Devan
**Result:** Escaped. Final code was `7314`. Override accepted at 03:47:12 UTC.

## How I worked through this

I used Claude Code (Anthropic's CLI agent) for this one. Same way I've been using it for most of the assignments this term: I tell it what I'm trying to do, it runs commands in my terminal, I watch the output and push back when something looks off. For this exercise I basically gave it the URL of the assignment and asked it to solve the four puzzles and write up the result.

A note I'd saved earlier in the term told it that anything coming from `blkfin/courses` should land in my `~/courses` fork rather than my `it612` submission repo. That kicked in automatically here, so it pulled latest with `git fetch upstream && git merge upstream/main` and worked in the right folder without me having to remind it. That's a course-correction from a previous exercise that stuck.

One bit of setup before anything could run: my Mac didn't have PowerShell installed. I had it install pwsh via Homebrew before Puzzle 1. Lua and awk were already there. `gawk` wasn't, which mattered later in Puzzle 3.

It ran the four puzzles in parallel as a single batched call, which was the right move since they don't depend on each other.

Below is each puzzle with the script, the answer, what I was thinking, and where things went well or didn't.

## Puzzle 1, PowerShell on `windows_events.csv`, digit 1

The puzzle was to find the one role change from `student` to `admin` that happened inside the breach window from `2026-04-28T00:00:00Z` to `2026-04-28T06:00:00Z`. Take the UID of that row and grab its last digit.

Script:

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

Result: one row, account `mflint`, UID `1037`, timestamp `2026-04-28T03:17:48Z`.

**Digit 1 was 7.**

This was the cleanest puzzle. CSV is exactly what `Import-Csv | Where-Object` is for. The README warned that filtering by date prefix `'2026-04-28'` alone would catch other promotions later that day, so I made sure both bounds were in the filter. Worked first try, no course correction needed. ISO-8601 timestamps sort lexically as strings, so I didn't need to parse them as dates.

## Puzzle 2, regex on `ids.log`, digit 2

Find the source IP that touched all four target ports (22, 80, 443, 3389). Take the last octet of that IP, then its last digit.

Script:

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

Result: `192.168.7.43`. Last octet is `43`, last digit is `3`.

**Digit 2 was 3.**

This is the set-cover thing the README flagged. The trap is counting attempts instead of distinct ports. One IP could hit port 22 fifty times and that's still one port. I solved this by using a composite key `ip_port` in the `seen` map, which dedupes by construction. Then the END block counts how many distinct ports each IP touched. Only one IP came back with a count of 4. Worked first try.

## Puzzle 3, awk on `door_access.log`, digit 3

Find the door whose chronologically-ordered events contain `DENIED, DENIED, DENIED, GRANTED` consecutively. Read the door ID and take its last digit.

Script (with a fallback chained on):

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

Result: door `031` with action history exactly `DDDG`.

**Digit 3 was 1.**

The idea: group by door, encode each event as one character (D or G), then look for the substring `DDDG` per door at the end. Since the log is already sorted by timestamp, the order awk sees lines for door X is the chronological order for door X, so I didn't need to sort first.

This is the puzzle that didn't go cleanly. The README suggested gawk's `match($0, /pattern/, arr)` capture syntax, so Claude wrote that version first. My Mac doesn't have `gawk` installed though, just regular `awk`. The first form failed with `command not found: gawk`. There was a fallback chained on with `||` that used portable `awk` syntax (`RSTART`, `RLENGTH`, `substr`), and that one ran and gave the answer.

So I didn't have to step in mid-run, but if that fallback hadn't been pre-written I'd have had to either install gawk or rewrite the script myself. The honest takeaway is that when an exercise hints at a non-portable tool, the AI should either check if it's installed first or default to the portable version. Chaining a fallback works, but if I hadn't been watching the output I might have believed the gawk version succeeded.

## Puzzle 4, Lua on `zombie_config.lua`, digit 4

Read the top-level `wave_size` field from the Lua config and take its last digit.

Script:

```bash
lua -e 'local cfg = dofile("zombie_config.lua"); print("wave_size =", cfg.wave_size)'
```

Result: `wave_size = 24`. Last digit is `4`.

**Digit 4 was 4.**

The file is real Lua source that returns a table. `dofile` evaluates it and gives back that table, then it's just a field access. The trap the README pointed at was reading `cfg.waves[1].count` (the size of the first wave, 20) instead of the top-level `cfg.wave_size`. Two different fields with similar names. I made sure to ask for `wave_size` specifically and didn't fall into that. Worked first try.

The other temptation was to just grep for `wave_size = NN` in the file. It would have worked here, but the whole point of Puzzle 4 is that the right tool for code-as-config is the language's own interpreter, not regex. If the config grew comments or computed values, the grep approach would silently break.

## Final code and escape

Digits in order: **7, 3, 1, 4**. Code: `7314`.

```bash
$ python3 unlock.py 7314
ESCAPED -- Override accepted. Lockdown released at 03:47:12 UTC.
Containment holds. Survivors: 4. Server room secure.
The dispatcher daemon is shut down. The horde retreats.
$ echo $?
0
```

**Escaped: yes.**

## What worked and what didn't with AI

What worked:

- Tool choice was right on the first pass for all four puzzles. PowerShell for the CSV, grep plus awk for the free-form key=value log, awk associative arrays for the grouped sequence pattern, Lua interpreter for the config. That's the actual skill the exercise is testing, and Claude got it without me having to nudge.
- Running all four puzzles in parallel saved time. If I'd been doing this in a terminal myself I'd have done them one at a time.
- A correction I'd made in an earlier exercise (route blkfin/courses work to my `~/courses` fork) was already remembered, so it didn't drift back to the wrong location.

What didn't:

- The gawk-versus-awk thing in Puzzle 3. Claude wrote gawk-specific syntax because the README mentioned it, but didn't check if gawk was on my system. The `||` fallback rescued it, but it's the kind of thing that could have stalled me out if it hadn't been there.
- Earlier in the term I'd had to push back on bigger things, like not recreating folders that already existed and not copying solutions verbatim from the course's reference repo. Those got saved as standing instructions in Claude's memory and haven't recurred since. So this specific exercise went smoothly partly because the rules had been worked out over earlier sessions.

What I actually did myself was: pick the assignment, hold the line on "bare minimum, just meet the rubric," watch the output to catch tool-availability surprises like the gawk one, and verify each digit against the README's described gotchas before composing the final code. I didn't write any of the four scripts but I read each one and checked it against the puzzle description before trusting the result.
