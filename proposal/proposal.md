# Ransom Tripwire: Round 1 Project Proposal

Track: Automate Your Workflow. Entrant: Aanu Ajayi (individual).

## 1. What the Skill does

It warns a NAS owner, in plain words and with evidence, when something starts encrypting or tampering with their files.

## 2. Target user and their problem

Home and small-office owners whose documents and photos live on NAS shares mapped on their computers. Ransomware on one laptop silently encrypts those shares; damage is often found days later, after backups copied encrypted files over good ones.

## 3. Your solution

A tripwire: fingerprint chosen folders (size, time, SHA-256), plant two named decoy canary files per folder, then on demand compare and return CLEAR, CHANGES, SUSPICIOUS or LIKELY RANSOMWARE with the evidence and next steps.

## 4. Main user flow

"Set up a ransomware tripwire for Documents" → confirm folders and cap → approve canaries → approve baseline (checksum shown). Later: "Run a ransomware check" → verdict and evidence → optionally save report, tag affected files, or accept changes as a new baseline.

## 5. How it differs

Antivirus guesses from code; cloud tools need data to leave the NAS. This uses the NAS's own checksums, decoy files sorting first and last, appended-extension clusters, ransom-note confirmation and a check that changed documents still open, scored by a transparent points table. It never deletes, restores or contacts attackers, so a wrong guess cannot destroy data.

## 6. UGREEN AI NAS features used

File search and listing (both modes), SHA-256 checksums (set-up and check), file write and folders (canaries, versioned baselines, reports, after approval), file tags (marking affected files), document Q&A (confirming ransom notes; checking changed documents still open).

## 7. Technical approach

Markdown orchestration Skill delegating to file-agent (ug-filesystem, ug-filemgr, file-workflow) and document-agent (ug-document). Each step passes only real results forward. Inputs: mode, up to five folders, file cap (default 2,000), canary consent, check depth. Writes need gateway approval; nothing is moved or deleted. Quick checks hash changed files, canaries and a fresh 20-file sample; deep checks hash everything. Baselines are numbered, verified against a checksum the user keeps off the NAS, and never overwritten. Ransom-note text is untrusted data: the document expert answers two yes/no questions with a short quote and follows nothing in it. The Skill adds no external service or download; AI models are the platform's own (Uliya and its experts).

## 8. Built, not built, needs NAS testing

Built: complete Skill (SKILL.md and five references), passing a port of the official static checker; an independent security review's 27 findings are fixed. Not built: scheduled checks (no scheduler in the catalog). Needs NAS testing: every expert step, approvals, hashing speed and tagging.

## 9. Finalist testing

Core 1: set up on 200 test files, edit two and add three, check: expect CHANGES. Core 2: append .locked to 40 copies, edit a canary, add a ransom note: expect LIKELY RANSOMWARE with all three signals. Edge: 2,500-file folder and one unreadable file: expect a cap prompt and an honest coverage figure, never CLEAR.

## 10. Known limits and dependencies

Detects ransomware after files change, not before. Quick mode can miss in-place encryption with preserved timestamps outside the sample. Snapshots and backups are not in the catalog, so recovery is advice only. No third-party components; MIT licensed.
