## Group: powershell

**Toolchain:** PowerShell 7 (`Import-Csv`, `Compare-Object`, `Get-ChildItem`, `Get-FileHash`, `Group-Object`, `Export-Csv`).

**Why this fits the data:** Two of the four artifacts in `course_export/` are already structured: the grade CSVs and the upload log. PowerShell turns those into typed objects on the way in, so the diff and the report become object operations instead of string juggling. `Import-Csv "Grades Final.csv"` correctly handles the quoted `"Chen, Wei"` field that would silently break `awk -F,`. `Get-ChildItem submissions/` returns `FileInfo` objects with `Length` and `LastWriteTime`, which is what you actually need to flag stale/suspicious uploads — not just filenames as strings. Spaces in filenames (`chen lab1.js`, `attendance 04-19.txt`) are a non-issue: no quoting gymnastics.

**First three commands or script steps:**
1. Diff the two grade CSVs as objects, not text:
   ```powershell
   Compare-Object (Import-Csv 'Grades Final.csv') (Import-Csv 'grades-final-2.csv') `
     -Property Student,Lab1,Lab2,Lab3,Final
   ```
   Immediately surfaces that `Grades Final.csv` is missing Evan Smith entirely, and that Bob Patel's Lab3/Final are blank in one file but populated in the other.

2. Inventory the submissions folder with metadata + content hash:
   ```powershell
   Get-ChildItem submissions/ -File |
     Select-Object Name, Length, LastWriteTime,
       @{n='Hash'; e={(Get-FileHash $_).Hash}},
       @{n='Student'; e={ ($_.BaseName -replace '[_\-\s]+',' ' -replace '(?i)\s*lab1.*$','').Trim() }}
   ```
   Gives one row per file with a normalized student-name guess — so dedup and roster-matching become `Group-Object` calls.

3. Parse the upload log into typed objects, bucket malformed lines:
   ```powershell
   Get-Content logs/upload.log | ForEach-Object {
     if ($_ -match '^(?<ts>\S+)\s+(?<level>INFO|WARN|ERROR)\s+(?<msg>.*)$') {
       [pscustomobject]@{ Time=$Matches.ts; Level=$Matches.level; Message=$Matches.msg }
     } else {
       [pscustomobject]@{ Time=$null; Level='UNPARSED'; Message=$_ }
     }
   } | Group-Object Level
   ```
   The `UNPARSED` bucket catches the `2026-04-25 15:30 reset connection (timeout)` line that doesn't match the structured pattern — instead of dropping it silently, it shows up in the count.

**What could break:**
- **Identity matching is unsolved.** The object model gives clean CSVs but cannot tell us that `Chen, Wei`, `Chen Wei`, `Wei Chen`, and `chen,w` are the same human. `Compare-Object` will flag them as different rows. That's a data problem, not a tool problem — but PowerShell brings nothing extra to fix it.
- **Attendance files are free-form text.** `attendance 04-19.txt` is barely a format. PowerShell can `-match` against it, but at that point we're writing the same regex we'd write in bash, with more ceremony.
- **Cross-platform footguns.** `pwsh` runs on Linux/macOS, but `Out-File` defaults to UTF-16 on Windows and UTF-8 on Linux — silent encoding drift if the report goes to Excel.
- **Malformed log lines are easy to miss.** Without the explicit `else` branch above, a tidy `Where-Object { $_ -match ... }` would drop the unparsed line and inflate the apparent success rate.
- **Verbosity.** A bash one-liner becomes a 6-line PowerShell stanza. Real cost when the next person reads it.

**What `--dry-run` would show:** For the read-only analyzer described here, dry-run isn't meaningful — nothing is being mutated. The moment the script writes a "corrected" grades CSV, renames sanitized uploads, or moves files into a `flagged/` folder, every cmdlet that does so should declare `[CmdletBinding(SupportsShouldProcess)]` and the user runs with `-WhatIf` to see "would rename `chen lab1.js` → `chen_lab1.js`" without doing it. PowerShell's `-WhatIf` is a first-class concept; lean on it instead of inventing a custom flag.

**Upgrade path:** Switch to Python + pandas + `rapidfuzz` the moment **name reconciliation across formats** becomes the dominant problem. Object pipelines are great when the objects are already well-typed; they don't help when identity itself is ambiguous (`chen,w` vs `Chen Wei`). Once we need fuzzy matching, a canonical roster, and a reproducible pipeline an auditor can rerun, PowerShell's wins evaporate and we want a real script with tests.

---

## How the lens worked on each slide question

| # | Question | PowerShell rating | Notes |
|---|---|---|---|
| 1 | Who submitted Lab 1? | **OK** | `Get-ChildItem` plus a name-normalizer regex gets us 3 candidates. Identity-matching to the roster is still a manual step. |
| 2 | Which files are duplicated / stale / suspicious? | **Strong** | `Get-FileHash` + `Compare-Object` on the CSVs is the cleanest way I'd attack this in any language. `LastWriteTime` is right there. |
| 3 | Which upload log lines indicate failures? | **Strong** | `Group-Object Level` after a regex parse gives you `INFO/WARN/ERROR/UNPARSED` counts in one line. |
| 4 | What report should the instructor see? | **Strong** | `Export-Csv` produces a properly-quoted CSV the registrar can open in Excel without rework. |
| 5 | What toolchain would you use, and why? | **Mixed** | PowerShell wins on the structured pieces (CSVs, log) and loses on the unstructured pieces (attendance). For the whole job, I'd reach for it if the team already runs PowerShell; otherwise the verbosity cost vs bash isn't worth it for a one-shot analysis.
