# Ransom Tripwire

A ransomware early-warning Skill for UGREEN AI NAS, built for the [UGREEN Hackathon 2026 on AI NAS](https://ugreenhackathon.devpost.com/) (Round 1, Automate Your Workflow track).

Ransomware on one infected laptop can quietly encrypt the NAS shares it has mapped, and the damage is often found days later, after a nightly backup has copied the encrypted files over the good ones. Ransom Tripwire answers one question fast, in plain words and with evidence: **has something started encrypting or tampering with my files?**

## How it works

| Mode | What happens | Writes (each needs approval) |
|---|---|---|
| Set up | Fingerprints up to five folders (path, size, modified time, SHA-256) and plants two decoy canary files per folder, one that sorts first and one that sorts last. | Canaries, a versioned baseline file |
| Check | Compares the folders with the newest baseline, classifies every file (unchanged, modified, renamed, missing, new), scores ransomware signals and returns `CLEAR`, `CHANGES`, `SUSPICIOUS` or `LIKELY RANSOMWARE` with the evidence and next steps. | Optional report, optional "Tripwire alert" file tag |
| Accept changes | Saves a new baseline after the user confirms the changes were theirs. Refused for `LIKELY RANSOMWARE`. | A new baseline version |

The Skill never deletes, restores, renames or moves the user's files, and never contacts anyone a ransom note names. Ransom-note text is treated as untrusted data: the document expert only answers two yes/no questions about it.

The signals and their points (canary touched, confirmed ransom note, appended-extension cluster, changed content with preserved timestamps, share of files changed) are in [detection-rules.md](skill/ransom-tripwire/references/detection-rules.md), so anyone can check a verdict by hand.

## Repository layout

| Path | What it is |
|---|---|
| `skill/ransom-tripwire/` | The Skill package: `SKILL.md` and `references/` (Markdown only). This is what is zipped and submitted. |
| `proposal/proposal.md` | The Round 1 proposal (10 answers, under 500 words). |
| `tools/build.py` | Builds `dist/ransom-tripwire.zip` and `dist/proposal.pdf`, and enforces the size and word limits. |
| `tools/check_skill.py` | A Python port of the official static checker's rules, used as a cross-check. |
| `docs/AUDIT.md` | The independent security review and what changed because of it. |

## Build and check

```bash
python3 -m pip install reportlab
python3 tools/build.py                          # dist/ransom-tripwire.zip and dist/proposal.pdf
python3 tools/check_skill.py skill/ransom-tripwire
```

With the official [UGREEN Skill Developer Package](https://ai.ugreen.com/pages/hackathon-starter-kit) unzipped next to this repository:

```bash
node uliya-skill-kit/scripts/check-skill.mjs skill/ransom-tripwire
```

## Status

- The Skill package is complete and passes the Python port of the static checker with 0 errors and 0 warnings. The port was validated by catching every planted violation in a broken copy and agreeing with the official checker on another entrant's passing package. Run the official checker (command above) before uploading.
- An independent fresh-context security review found 27 issues across three passes; all are fixed except residual limits that are labelled in every verdict. See [docs/AUDIT.md](docs/AUDIT.md).
- **Nothing has run on a UGREEN NAS yet.** Round 1 entrants have no NAS access. The finalist tests are in [test-plan.md](skill/ransom-tripwire/references/test-plan.md).

## License

MIT. See [LICENSE](LICENSE).
