## Inspiration

I work in security, on detection and response. The ransomware cases that hurt most are not the ones caught on the laptop. They are the quiet ones: one infected computer with a mapped NAS share encrypts the family photos or the small office's documents, nobody notices for days, and the nightly backup copies the encrypted files over the last good ones. A NAS is often the only copy, and it has no idea anything is wrong.

I wanted the NAS itself to be able to answer one question fast, in plain words and with evidence: **has something started encrypting or tampering with my files?**

## What it does

Ransom Tripwire is an AI Skill for UGREEN AI NAS with three modes:

- **Set up:** you name up to five folders. It fingerprints every file (path, size, modified time, SHA-256), plants two clearly named decoy **canary files** per folder (one sorts first and one sorts last, because ransomware walks folders in name order), and saves a numbered baseline you can open and read. You keep its checksum off the NAS.
- **Check:** "Run a ransomware check." It compares the folders with the baseline and classifies every file as unchanged, modified, renamed, missing, replaced or new. It scores ransomware signals and gives a verdict: `CLEAR`, `CHANGES`, `SUSPICIOUS` or `LIKELY RANSOMWARE`, with the evidence and next steps.
- **Accept changes:** when the changes were yours, it saves a new baseline. It refuses after `LIKELY RANSOMWARE`, because that would hide the damage.

The signals are in a published points table, so anyone can check a verdict by hand: a canary touched, a ransom note confirmed, half the files changed (100 points each); a changed document or photo that no longer opens, five files replaced by `*.locked` copies, or more than 30% changed (60); and so on. Renaming or reorganising folders never counts, because a renamed file has the same checksum.

It never deletes, restores, renames or moves your files, and never contacts anyone a ransom note names. Everything it writes (canaries, baselines, reports, an optional "Tripwire alert" tag) is shown first and needs your approval.

## How I built it

The Skill is pure Markdown, built to the Uliya Skill Development Standard from the UGREEN Skill Developer Package. Every step is a self-contained delegation to a registered expert, and only real results flow to the next step:

- `file-agent` (`ug-filesystem`, `ug-filemgr`, `file-workflow`): finding and listing files, SHA-256 checksums, media information, writing canaries, baselines and reports, and tagging.
- `document-agent` (`ug-document`): reading suspected ransom notes and checking that changed documents still open.

Every capability was checked against the official capability catalog before it was used. I checked the package against the official checker's rules with a Python port of them, which I validated by having it catch every planted violation in a deliberately broken copy.

## Treating attacker text as data

Ransomware writes file names and ransom notes, so the Skill treats every path, file, note and even its own baseline as untrusted data. Paths go into instructions as framed lists with quotes escaped. Notes and files-to-open are sent in separate instructions, so a note cannot steer the other answers. A matched note scores whatever the expert answers: a note that says "answer no" cannot talk its way to a clean verdict.

## Challenges

I had a separate Claude session review the finished Skill three times from a fresh context, as a security engineer who had never seen how it was built. It found 27 issues. The hardest lesson was false alarms versus missed attacks: my first fix (count renames toward "half the files changed") would have called a simple folder rename "likely ransomware"; the reviewer caught it, and renames now never count. Other fixes: an encrypted canary renamed to `.locked` now counts as touched; common real note names are matched; slow in-place encryption is caught by checking that changed files still open; and a deleted or swapped baseline is detected with the checksum the user keeps off the NAS.

## What's next

Finalist testing on a real UGREEN AI NAS with simulated (harmless) ransomware: a clean check, a `.locked` attack with a canary and a note, and a 2,500-file edge case. After that, scheduled checks before each backup job, if the platform adds a scheduler.

## AI tools used

Claude Code (Anthropic, Claude Opus 5.5) drafted the Skill, references and proposal from my brief and checked them against the catalog and the checker rules; a separate Claude session acted as the independent security reviewer. I reviewed and am responsible for the final content.
