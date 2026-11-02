"""Glossary patches: paper assessment link, cell->evaler, Codex Commons link."""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PAPER = "https://arxiv.org/abs/2507.06434"
CODEX = "https://commons.wikimedia.org/wiki/File:Cognitive_bias_codex_en.svg"


def rewrite(text: str) -> str:
    text = text.replace("table cell", "<<TABLE_CELL>>")

    old_assess = "Maps the paper's <b>assessment</b> phase."
    new_assess = (
        f'Maps the <a href="{PAPER}">paper\'s <b>assessment</b></a> phase.'
    )
    if old_assess not in text:
        raise SystemExit("assessment phrase missing")
    text = text.replace(old_assess, new_assess)

    old_c = "Definition-only. The Cognitive Bias Codex rearranges"
    new_c = (
        f'Definition-only. The <a href="{CODEX}">Cognitive Bias Codex</a> rearranges'
    )
    if old_c not in text:
        raise SystemExit("codex body missing")
    text = text.replace(old_c, new_c, 1)

    old_ref = (
        'Primary references: <a href="https://en.wikipedia.org/wiki/Cognitive_bias">'
        "Wikipedia Cognitive bias</a>;"
    )
    new_ref = (
        f'Primary references: <a href="{CODEX}">Cognitive Bias Codex</a> '
        "(Wikimedia Commons SVG); "
        '<a href="https://en.wikipedia.org/wiki/Cognitive_bias">'
        "Wikipedia Cognitive bias</a>;"
    )
    if old_ref not in text:
        raise SystemExit("codex refs missing")
    text = text.replace(old_ref, new_ref, 1)

    text = re.sub(r"\bcells\b", "evalers", text)
    text = re.sub(r"\bcell\b", "evaler", text)
    text = text.replace("<<TABLE_CELL>>", "table cell")
    return text


def main() -> None:
    for rel in ("GLOSSARY.md", "docs/glossary.html"):
        path = ROOT / rel
        before = path.read_text(encoding="utf-8")
        after = rewrite(before)
        if "bold table cell" not in after:
            raise SystemExit(f"table cell lost in {rel}")
        if "paper's <b>assessment</b></a>" not in after:
            raise SystemExit(f"assessment link missing in {rel}")
        if CODEX not in after:
            raise SystemExit(f"codex link missing in {rel}")
        left_cell = len(re.findall(r"\bcell\b", after))
        left_cells = len(re.findall(r"\bcells\b", after))
        print(rel, "remaining cell", left_cell, "cells", left_cells)
        path.write_text(after, encoding="utf-8", newline="\n")
    print("ok")


if __name__ == "__main__":
    main()
