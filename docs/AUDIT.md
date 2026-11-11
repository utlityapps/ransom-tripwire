# Independent security review

Ransom Tripwire was drafted with Claude Code. To check that work, a separate Claude session reviewed the finished Skill from a fresh context, as a senior security engineer who had never seen how it was built. It worked to a written brief:

- **Scope:** the Skill package only, read-only, checked against the official UGREEN Skill Developer Package (capability catalog and checker rules) used as the specification.
- **Hunt for:** writes without approval or with too wide a scope, prompt injection from file names, file content, ransom notes or the baseline itself, ways a partial, failed or tampered check could come out "clean", claims the capability catalog does not support, unhandled failure states, and checker-rule violations.
- **Method:** list at least three breaking points per area, try to confirm each against the exact text, and classify each as confirmed, refuted or unproven, with the smallest fix.
- **Output:** a fixed JSON schema, with one worked example finding to match.

The review ran three times: the first pass, a recheck of the fixes, and a final recheck.

## What it found and what changed

| Finding | Severity | Change |
|---|---|---|
| An encrypted canary renamed to `*.locked` was scored as merely "missing" | High | A canary that is modified, replaced, or missing while anything else in its folder changed is "touched" (100 points). |
| Extension clusters needed more than 10% of a folder, so mid-attack encryption scored nothing | High | Five replaced files with the same added ending is enough. |
| A fully encrypted folder without a canary or a known note was only `SUSPICIOUS` | High | Half the files changed is `LIKELY RANSOMWARE` on its own; more than 30% scores 60. |
| Common real ransom-note names were not matched | High | The name list now covers the common families, and a matched note scores whatever the document expert answers. |
| Slow in-place encryption looked like normal edits and could be accepted into the baseline | High | Up to five changed documents and five changed media files are opened each check; a file that no longer opens scores 60 and blocks accepting changes. |
| A deleted, swapped or planted baseline could produce a clean result | High | Each check asks for the baseline checksum the user kept off the NAS; a missing, mismatched or unrecognised baseline is a signal; an unverified baseline is labelled. |
| Renaming or reorganising a folder would have scored `LIKELY RANSOMWARE` (introduced by the first fix round) | High | Renamed and moved files have identical checksums, so they never count toward a signal. |
| Attacker-controlled file names and note quotes were pasted into instructions without framing or quote escaping | Medium | Every inserted value is escaped and framed as untrusted data; notes and files-to-open are sent in separate instructions. |
| Instruction templates had no slot for the folder list | Medium | Every template has a marked slot and returns `failed` if it is empty. |
| File names needed a clock the catalog does not provide | Medium | Baselines and reports are numbered (`baseline-001.md`), never dated by the Skill. |
| Re-running set-up demoted existing canaries to ordinary files | Medium | Existing canaries are always recorded as canaries. |
| A new set-up after an alarm would record the damage as normal | Medium | Set-up runs a quick check first when a baseline exists. |
| The baseline row-count check could not pass on a valid baseline | Medium | Files and canary rows are counted separately against their totals. |
| Quick mode reported full coverage after hashing 25 files | Low | The verdict shows "(quick)" and "N hashed, M compared by size and time only". |
| README files, photo exports and RAW sidecars caused false alarms | Medium | Notes and new extensions score fully only in folders that also have changed files; system files are excluded; sidecars are not replacements. |
| A note telling the document expert to answer "no" could zero out a lone note; a file the expert could not read blocked accepting changes forever (third pass) | Medium | A lone note scores 30 and recommends a deep check; an unreadable format is "content not inspected" (30), and the user can confirm such files are theirs. |
| Row-count rules and test expectations did not follow from the rules (third pass) | Medium/Low | Definitions and the test plan were aligned with the scoring table. |

## Residual limits, accepted and labelled

- Slow in-place encryption of formats the experts cannot open (archives, CAD, databases) is listed as "content not inspected" but not scored.
- Without the checksum the user keeps off the NAS, a baseline overwritten in place cannot be told apart from the real one; the verdict says "baseline unverified".
- If an attacker deletes the whole Ransom Tripwire folder and the user then asks for a fresh set-up rather than a check, nothing warns them.
- The baseline is passed to the expert inline, about 1 MB at 10,000 files, and the comparison is done by the orchestrator; the file cap keeps this bounded.

## What it could not settle

Nothing has run on a UGREEN NAS: Round 1 entrants have no NAS access. Whether each expert follows its instruction exactly, how fast hashing is, and how approval prompts look are all finalist-testing items in [test-plan.md](../skill/ransom-tripwire/references/test-plan.md).
