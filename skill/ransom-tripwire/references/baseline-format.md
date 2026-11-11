# Baseline and report format

Ransom Tripwire writes plain Markdown into a folder named `Ransom Tripwire` in the user's home directory, so a person can open and read every file it writes. Files are never overwritten: each version is a new numbered file. The NAS supplies the modified time of each file; the Skill never invents a date.

## Baseline file

Name: `baseline-001.md`, `baseline-002.md` and so on, using the next unused number.

An example, with most rows left out for space:

```markdown
# Ransom Tripwire baseline

- Skill version: 1.0
- Mode: set up
- Canaries: yes
- Canary rows: 4
- File cap per folder: 2000

## Folders

| Folder | Files fingerprinted | Checksum failures |
|---|---:|---:|
| Documents | 1840 | 0 |
| Photos/2026 | 612 | 2 |

## Canaries

| Path | Size | Modified | SHA-256 |
|---|---:|---|---|
| Documents/000-ransom-tripwire-canary-do-not-edit.txt | 131 | 2026-11-14 21:04 | 9f1c... (64 hex characters) |

## Files

| Path | Size | Modified | SHA-256 |
|---|---:|---|---|
| Documents/Taxes/2025-return.pdf | 482113 | 2026-04-02 10:11 | 3b7a... (64 hex characters) |
```

Paths are shown as the expert returned them. A row with an empty checksum carries the reason in place of the checksum, for example `(unreadable: permission denied)`.

## Check report

Name: `report-001.md`, `report-002.md` and so on.

```markdown
# Ransom Tripwire check

- Baseline: baseline-001.md (checksum matches the one the user kept: yes / not given)
- Depth: quick
- Coverage: 25 hashed, 2427 compared by size and time only, 0 unreadable
- Random sample: 20 files, chosen anew for this check

## Verdict: SUSPICIOUS (quick, score 45)

| Signal | Points |
|---|---:|
| New extension cluster .tmpx on 31 files | 30 |
| 14% of baseline files modified | 15 |

## Changes

| Class | Count |
|---|---:|
| Unchanged | 2101 |
| Modified | 318 |
| Renamed or moved | 2 |
| Missing | 0 |
| New | 31 |

## Canaries

| Path | Result |
|---|---|
| Documents/000-ransom-tripwire-canary-do-not-edit.txt | unchanged |

## Suspected ransom notes

None.

## Files

| Class | Path | Detail |
|---|---|---|
| Modified | Documents/Budget.xlsx | size 20311 to 20410; opens: yes |
| Modified | Documents/notes.txt | size 812 to 845; content not inspected |

## Next steps

(the steps for this verdict from the detection rules)
```

The file list in a report is capped at 500 rows, most suspicious first (canaries, then notes, then documents that no longer open, then appended extensions and replaced files, then modified files with preserved timestamps, then the rest). The counts above it are always complete.

"Files fingerprinted" is the number of rows written to the Files table for that folder, including rows whose checksum failed and excluding canaries. The baseline is verified when it is read back: the number of Files table rows must equal the sum of the Folders table's "Files fingerprinted" column, and the number of Canaries table rows must equal the "Canary rows" line. If either does not match, the check stops and reports the baseline as unreadable. Canaries appear only in the Canaries table.
