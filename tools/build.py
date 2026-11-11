#!/usr/bin/env python3
"""Build the two Round 1 deliverables into dist/.

- dist/ransom-tripwire.zip : the Skill package (a ransom-tripwire/ folder with SKILL.md and references/)
- dist/proposal.pdf        : the project proposal rendered from proposal/proposal.md

Usage: python3 tools/build.py
"""

from __future__ import annotations

import re
import sys
import zipfile
from pathlib import Path

from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import LETTER
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer

ROOT = Path(__file__).resolve().parent.parent
SKILL = ROOT / "skill" / "ransom-tripwire"
DIST = ROOT / "dist"
WORD_LIMIT = 500
ZIP_MAX = 10 * 1024 * 1024
PDF_MAX = 1024 * 1024


def build_zip() -> Path:
    out = DIST / "ransom-tripwire.zip"
    files = sorted(p for p in SKILL.rglob("*") if p.is_file())
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
        for p in files:
            z.write(p, Path("ransom-tripwire") / p.relative_to(SKILL))
    if out.stat().st_size > ZIP_MAX or len(files) > 100:
        sys.exit(f"ZIP over limits: {out.stat().st_size} bytes, {len(files)} files")
    print(f"{out.relative_to(ROOT)}: {len(files)} files, {out.stat().st_size} bytes")
    return out


def inline(text: str) -> str:
    text = text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    text = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", text)
    return re.sub(r"`(.+?)`", r"<font face='Courier'>\1</font>", text)


def answer_words(markdown: str) -> int:
    body = markdown.split("## 1.", 1)[1]
    answers = "\n".join(line for line in body.splitlines() if not line.startswith("#"))
    return len(re.findall(r"\S+", answers))


def build_pdf() -> Path:
    source = (ROOT / "proposal" / "proposal.md").read_text(encoding="utf-8")
    words = answer_words(source)
    if words > WORD_LIMIT:
        sys.exit(f"proposal answers are {words} words, over the {WORD_LIMIT}-word limit")
    styles = getSampleStyleSheet()
    title = ParagraphStyle("t", parent=styles["Title"], fontSize=17, spaceAfter=4, alignment=TA_LEFT)
    h2 = ParagraphStyle("h", parent=styles["Heading2"], fontSize=11.5, spaceBefore=7, spaceAfter=2)
    body = ParagraphStyle("b", parent=styles["BodyText"], fontSize=10, leading=13.2)
    story = []
    for block in re.split(r"\n\s*\n", source.strip()):
        block = block.strip()
        if block.startswith("# "):
            story.append(Paragraph(inline(block[2:]), title))
        elif block.startswith("## "):
            story.append(Paragraph(inline(block[3:]), h2))
        else:
            story.append(Paragraph(inline(" ".join(block.splitlines())), body))
    story.append(Spacer(1, 6))
    story.append(Paragraph(f"<i>Answers: {words} words.</i>", body))
    out = DIST / "proposal.pdf"
    doc = SimpleDocTemplate(
        str(out), pagesize=LETTER, leftMargin=0.8 * inch, rightMargin=0.8 * inch,
        topMargin=0.7 * inch, bottomMargin=0.7 * inch,
        title="Ransom Tripwire: Round 1 Project Proposal", author="Aanu Ajayi",
    )
    doc.build(story)
    if out.stat().st_size > PDF_MAX:
        sys.exit(f"PDF over 1 MB: {out.stat().st_size} bytes")
    print(f"{out.relative_to(ROOT)}: {words} words in answers, {out.stat().st_size} bytes")
    return out


if __name__ == "__main__":
    DIST.mkdir(exist_ok=True)
    build_zip()
    build_pdf()
