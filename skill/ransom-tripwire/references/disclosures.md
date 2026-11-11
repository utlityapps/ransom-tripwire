# Disclosures

## Third-party components and open-source libraries

None. The Skill is plain Markdown. It contains no scripts, executables, binaries, libraries, manifests, credentials or downloads. All NAS work is performed by UGREEN's registered experts (`file-agent` and `document-agent`) through the public capabilities listed in `SKILL.md`.

The UGREEN Skill Developer Package (uliya-skill-kit 0.7.3-en, capability catalog 2.0.0) was used during development to confirm every capability and as the specification for the static checks. It is not included in this Skill.

## Principal functionality developed for this Hackathon

All of it was developed during the Hackathon submission period:

- The three-mode workflow (set up, check, accept changes) and its expert delegations.
- The canary-file design (one name sorting first, one last).
- The file classification, the signal scores and the four verdicts in [Detection rules](detection-rules.md).
- The baseline and report formats in [Baseline and report format](baseline-format.md).
- The user guide and the finalist test plan.

## AI tools used and their principal uses

- **Claude Code (Anthropic), Claude Opus 5.5:** drafted the Skill, references and proposal from the author's brief; checked every capability against the official catalog; checked the package against the official checker's rules with a Python port of them.
- **A separate Claude session acting as an independent security reviewer:** reviewed the finished Skill three times for unsafe behaviour (unapproved writes, prompt injection from file names and ransom notes, false clean results, false alarms); its findings were fixed before submission.

The author reviewed and is responsible for the final content.

## License

MIT License. Copyright (c) 2026 Aanu Ajayi.
