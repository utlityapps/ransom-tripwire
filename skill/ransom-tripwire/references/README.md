# Ransom Tripwire: user guide

## Who it is for

Anyone who keeps the only good copy of their documents, photos or work files on a UGREEN AI NAS and maps those shares on their computers. Ransomware on one infected laptop can quietly encrypt a mapped NAS share, and the damage is often found days later, after a nightly backup or sync has already copied the encrypted files over the good ones.

Ransom Tripwire gives you a quick, readable answer to "has something started encrypting my files?" before that happens.

## What it does, in one minute

1. **Set up:** you name up to five folders. The Skill records a fingerprint (size, modified time and SHA-256) of every file, plants two clearly named decoy files in each folder, and saves the result as a baseline file you can open and read.
2. **Check:** whenever you like (for example before a backup job), ask "run a ransomware check". The Skill compares the folders with the baseline and tells you, in plain words, what changed and whether it looks like ransomware.
3. **Accept changes:** when the changes were yours, ask it to save a new baseline.

It never deletes, restores, renames or moves your files. Everything it writes (canaries, baselines, reports, an optional file tag) is shown to you first and needs your approval.

## Install

1. Download the Skill package (a ZIP containing `SKILL.md` and the `references` folder).
2. Open UGREEN Skills Hub on your NAS and add the Skill from the ZIP, following the Skills Hub instructions for your UGOS version.
3. Ask Uliya: "What can Ransom Tripwire do?" to confirm it is available.

## Set up

Say, for example: "Set up a ransomware tripwire for my Documents and Photos folders."

- Confirm the folders. If a folder is large, the Skill tells you before it starts; pick a subfolder or raise the file cap (default 2,000 files per folder).
- Say yes to canary files (recommended). You will see their names: `000-ransom-tripwire-canary-do-not-edit.txt` and `zzz-ransom-tripwire-canary-do-not-edit.txt`. Leave them where they are.
- Approve saving the baseline. Keep the baseline checksum the Skill shows you somewhere off the NAS, such as a note on your phone. Each check asks for it, to prove the baseline was not altered.

## Everyday use

- "Run a ransomware check." (quick: hashes only what looks changed, plus the canaries and a fresh random sample; also opens up to five changed documents to make sure they still open)
- "Run a deep ransomware check." (re-hashes every file; slower)
- "My files look strange since Tuesday. Check Documents for ransomware."
- "Those changes were mine. Save a new baseline."

Reading the verdict:

| Verdict | What to do |
|---|---|
| `CLEAR` | Nothing. |
| `CHANGES` | Glance at the list; accept the changes if they were yours. |
| `SUSPICIOUS` | Look at the listed files before your next backup job runs. |
| `LIKELY RANSOMWARE` | Disconnect the computers that use these shares, pause backup and sync jobs, do not pay, and follow the steps in the report. |

## Remove

1. Remove the Skill in Skills Hub.
2. Delete the two canary files from each protected folder, and the `Ransom Tripwire` folder in your home directory, with the Files app. The Skill does not delete them for you.
3. If you used tagging, delete the "Tripwire alert" tag in the Files app.

## Test it safely

Do not test with real ransomware. In a test folder:

1. Set up a tripwire with canaries.
2. Copy five files and rename the copies with `.locked` appended, edit one canary, and add a text file named `README_DECRYPT.txt` containing "Your files are encrypted. Pay to recover."
3. Run a check. Expected verdict: `LIKELY RANSOMWARE`, with the canary, the note and the `.locked` cluster listed as evidence.
4. Undo your changes, run a check, and accept changes to return to a clean baseline.

The full finalist test plan is in [Test plan](test-plan.md).

## Limits

- It detects ransomware after files start changing, not before. It is a fast, honest alarm, not a prevention or recovery tool.
- Quick checks can miss an encrypted file whose size and modified time were both preserved, unless it falls in the random sample. The verdict says "(quick)" and how many files were actually hashed. Deep checks do not have this gap.
- The baseline lives on the NAS, where ransomware on a mapped share might reach it. Keeping its checksum off the NAS is what lets a check detect a swapped or deleted baseline.
- It compares only the folders and files in the baseline, and only up to the file cap.
- Snapshots and backups are not in the public NAS capability catalog, so it tells you to check them but cannot manage them.
