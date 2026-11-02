"""Assemble PRICKLY Developer L&R 5-variant banks + font-11 review Word.

Expects batch JSON files under ui/v2/assets/prickly_variants/roles_batch_{1,2,3}.json
each with roles -> levels -> slots[10] -> variants[5].

Outputs:
  ui/v2/assets/prickly-dev-banks-variants.json  (runtime + review source)
  docs/evals/PRICKLY_DEV_LR_3000_REVIEW.docx
  Desktop/PRICKLY_DEV_LR_3000_REVIEW.docx
  ui/v2/assets/prickly_variants/inventory.json
"""
from __future__ import annotations

import json
import re
from collections import Counter
from pathlib import Path

from docx import Document
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Pt, RGBColor

ROOT = Path(__file__).resolve().parents[1]
BATCH_DIR = ROOT / "ui" / "v2" / "assets" / "prickly_variants"
OUT_JSON = ROOT / "ui" / "v2" / "assets" / "prickly-dev-banks-variants.json"
INVENTORY = BATCH_DIR / "inventory.json"
NAME = "PRICKLY_DEV_LR_3000_REVIEW.docx"
OUT_DOCXS = [
    ROOT / "docs" / "evals" / NAME,
    Path.home() / "Desktop" / NAME,
]

NAVY = RGBColor(11, 18, 32)
WHITE = RGBColor(248, 250, 252)
MUTED = RGBColor(90, 99, 110)

LEVEL_META = {
    "1": {
        "title": "Level 1 - Foundations",
        "blurb": "Clear basics. Spot obvious false comfort.",
        "ladder": "Junior scope: clear right/wrong craft basics (Tech Interview Handbook junior band).",
    },
    "2": {
        "title": "Level 2 - Trade-offs",
        "blurb": "Two good-looking options; only one is sound.",
        "ladder": "Mid scope: own a path; defend local choices under constraints.",
    },
    "3": {
        "title": "Level 3 - Failure modes",
        "blurb": "What breaks under load, time, or bad incentives.",
        "ladder": "Senior scope: production failure, load, time, and incentive failure.",
    },
    "4": {
        "title": "Level 4 - Precedents & traps",
        "blurb": "Industry-familiar traps dressed as best practice.",
        "ladder": "Staff-leaning: org precedents and fake best-practice traps.",
    },
    "5": {
        "title": "Level 5 - Edge judgment",
        "blurb": "Subtle cases where polite process still fails the user.",
        "ladder": "Principal/edge: multi-team, multi-quarter, user-harm despite process.",
    },
}

ROLE_ORDER = [
    ("programmer", "Programmer"),
    ("software_engineer", "Software Engineer"),
    ("technical_architect", "Technical Architect"),
    ("solutions_architect", "Solutions Architect"),
    ("data_engineer", "Data Engineer"),
    ("devops", "DevOps / Platform"),
    ("principal_architect", "Principal Architect"),
    ("llm_evals_engineer", "LLM Evals Engineer"),
    ("ml_engineer", "ML Engineer"),
    ("frontend_engineer", "Frontend Engineer"),
    ("security_engineer", "Security Engineer"),
    ("qa_engineer", "QA / Test Engineer"),
]

EM_DASH = "\u2014"


def set_run(run, size=11, bold=False, color=NAVY, name="Calibri"):
    run.font.size = Pt(size)
    run.font.bold = bold
    run.font.name = name
    run.font.color.rgb = color
    r_pr = run._element.get_or_add_rPr()
    r_fonts = r_pr.get_or_add_rFonts()
    r_fonts.set(qn("w:eastAsia"), name)


def shade(cell, fill: str) -> None:
    tc_pr = cell._tc.get_or_add_tcPr()
    shd = OxmlElement("w:shd")
    shd.set(qn("w:fill"), fill)
    shd.set(qn("w:val"), "clear")
    tc_pr.append(shd)


def cell(c, text, size=11, bold=False, color=NAVY, fill=None):
    c.text = ""
    p = c.paragraphs[0]
    p.paragraph_format.space_after = Pt(1)
    p.paragraph_format.space_before = Pt(1)
    set_run(p.add_run(str(text)), size=size, bold=bold, color=color)
    if fill:
        shade(c, fill)


def heading(doc, text, size=14):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(12)
    p.paragraph_format.space_after = Pt(4)
    set_run(p.add_run(text), size=size, bold=True)


def body(doc, text, size=11, color=NAVY):
    p = doc.add_paragraph()
    p.paragraph_format.space_after = Pt(6)
    p.paragraph_format.line_spacing = 1.1
    set_run(p.add_run(text), size=size, color=color)


def load_batches() -> dict:
    roles: dict = {}
    missing = []
    for i in (1, 2, 3):
        path = BATCH_DIR / f"roles_batch_{i}.json"
        if not path.is_file():
            missing.append(str(path))
            continue
        data = json.loads(path.read_text(encoding="utf-8"))
        roles.update(data.get("roles") or {})
    if missing:
        raise FileNotFoundError("Missing batch files:\n" + "\n".join(missing))
    return roles


def validate(roles: dict) -> list[str]:
    issues: list[str] = []
    texts_global: set[str] = set()
    dupes = 0
    em = 0
    total = 0
    for key, label in ROLE_ORDER:
        role = roles.get(key)
        if not role:
            issues.append(f"missing role {key}")
            continue
        levels = role.get("levels") or {}
        for lv in ("1", "2", "3", "4", "5"):
            pack = levels.get(lv)
            if not pack:
                issues.append(f"{key} missing level {lv}")
                continue
            slots = pack.get("slots") or []
            if len(slots) != 10:
                issues.append(f"{key} L{lv} has {len(slots)} slots (need 10)")
            for slot in slots:
                variants = slot.get("variants") or []
                if len(variants) != 5:
                    issues.append(
                        f"{key} L{lv} slot {slot.get('slot')} has {len(variants)} variants"
                    )
                answers = []
                for v in variants:
                    total += 1
                    text = (v.get("text") or "").strip()
                    if not text:
                        issues.append(f"empty text {v.get('id')}")
                    if EM_DASH in text:
                        em += 1
                        issues.append(f"em dash in {v.get('id')}")
                    norm = re.sub(r"\s+", " ", text.lower())
                    if norm in texts_global:
                        dupes += 1
                    texts_global.add(norm)
                    answers.append(bool(v.get("answer")))
                # soft check per-slot variety of answers allowed
                _ = answers
            # balance across V1 of each slot
            v1_answers = []
            for slot in slots:
                vs = slot.get("variants") or []
                if vs:
                    v1_answers.append(bool(vs[0].get("answer")))
            if v1_answers:
                t = sum(1 for a in v1_answers if a)
                f = len(v1_answers) - t
                if t < 3 or f < 3:
                    issues.append(f"{key} L{lv} V1 balance True={t} False={f}")
    if dupes:
        issues.append(f"duplicate stems (normalized): {dupes}")
    if total != 3000 and not any("missing" in i for i in issues):
        issues.append(f"total items {total} (expected 3000)")
    return issues


def to_runtime(roles: dict) -> dict:
    """Pack variants as V1..V5 banks the PRICKLY agent can switch between."""
    variants_out = {}
    for vi, vname in enumerate(["V1", "V2", "V3", "V4", "V5"], start=1):
        role_map = {}
        for key, label in ROLE_ORDER:
            src = roles[key]
            levels_out = {}
            for lv, meta in LEVEL_META.items():
                slots = src["levels"][lv]["slots"]
                items = []
                for slot in slots:
                    var = slot["variants"][vi - 1]
                    items.append(
                        {
                            "id": var["id"],
                            "text": var["text"],
                            "answer": bool(var["answer"]),
                            "theme": slot.get("theme") or "",
                            "slot": slot.get("slot"),
                        }
                    )
                levels_out[lv] = {
                    "title": meta["title"],
                    "blurb": meta["blurb"],
                    "items": items,
                }
            role_map[key] = {"label": label, "levels": levels_out}
        variants_out[vname] = {
            "variant": vname,
            "variantIndex": vi,
            "roles": role_map,
        }
    return {
        "version": 5,
        "format": "true_false",
        "maxLevel": 5,
        "variantCount": 5,
        "itemsPerSitting": 10,
        "rolesCount": 12,
        "totalItems": 3000,
        "note": (
            "Five progressive levels per developer kind. Five parallel variant packs "
            "(V1-V5) so PRICKLY can rotate sittings and avoid repeat sets. "
            "Each sitting uses one variant pack: 10 questions at the selected level."
        ),
        "levelMeta": {k: {"title": v["title"], "blurb": v["blurb"], "ladder": v["ladder"]} for k, v in LEVEL_META.items()},
        "sources": [
            "Tech Interview Handbook engineering levels (junior→principal)",
            "System-design-by-level rubrics (mid/senior/staff trade-offs)",
            "Role interview foci: FE/Data/ML/DevOps/Security/QA/MLOps drift-rollback",
            "DevOps anti-patterns (tools-over-culture, siloed DevOps team)",
        ],
        "variants": variants_out,
        "slots": roles,  # full slot×variant lattice for review
    }


def inventory(roles: dict) -> dict:
    rows = []
    for key, label in ROLE_ORDER:
        for lv in ("1", "2", "3", "4", "5"):
            slots = roles[key]["levels"][lv]["slots"]
            for vi in range(5):
                answers = [bool(s["variants"][vi]["answer"]) for s in slots]
                rows.append(
                    {
                        "role": key,
                        "label": label,
                        "level": int(lv),
                        "variant": f"V{vi+1}",
                        "n": len(answers),
                        "true": sum(answers),
                        "false": len(answers) - sum(answers),
                    }
                )
    return {
        "totalItems": 3000,
        "roles": 12,
        "levels": 5,
        "variants": 5,
        "questionsPerSitting": 10,
        "sittingsPerRole": 25,
        "rows": rows,
    }


def write_docx(roles: dict, inv: dict, issues: list[str]) -> None:
    doc = Document()
    normal = doc.styles["Normal"]
    normal.font.name = "Calibri"
    normal.font.size = Pt(11)
    normal.font.color.rgb = NAVY

    heading(doc, "PRICKLY Developer L&R - 3000-question review bank", 16)
    body(
        doc,
        "Scope: 12 specializations × 5 difficulty levels × 10 questions × 5 variant packs = 3000 True/False items. "
        "PRICKLY (Professional Reality Interactive Competency Knowledge Layer Yield) can rotate variant packs V1-V5 "
        "so a repeat sitting is not the same questionnaire. All body and table text is Calibri 11.",
    )
    body(
        doc,
        "Difficulty ladder (mapped to published engineering levels): L1 Foundations (junior craft) → L2 Trade-offs (mid) → "
        "L3 Failure modes (senior production) → L4 Precedents & traps (staff-leaning) → L5 Edge judgment (principal/edge). "
        "Sources grounded via Tech Interview Handbook levels, system-design-by-level rubrics, and role interview foci "
        "(FE, Data, ML/MLOps, DevOps anti-patterns, Security, QA).",
        color=MUTED,
    )
    if issues:
        body(doc, "Validation flags for reviewer: " + "; ".join(issues[:40]), color=MUTED)

    heading(doc, "1. Inventory matrix", 13)
    t = doc.add_table(rows=1, cols=6)
    t.style = "Table Grid"
    for i, h in enumerate(["Role", "Level", "Variant", "N", "True", "False"]):
        cell(t.rows[0].cells[i], h, size=11, bold=True, color=WHITE, fill="0B1220")
    for row in inv["rows"]:
        r = t.add_row().cells
        cell(r[0], row["label"], 11)
        cell(r[1], str(row["level"]), 11)
        cell(r[2], row["variant"], 11)
        cell(r[3], str(row["n"]), 11)
        cell(r[4], str(row["true"]), 11)
        cell(r[5], str(row["false"]), 11)

    heading(doc, "2. Full question lattice (by role → level → slot → variant)", 13)
    body(
        doc,
        "Each slot is one theme. Variants V1-V5 are distinct probes of that theme for rotation. "
        "Answer key: T = True, F = False.",
    )

    for key, label in ROLE_ORDER:
        heading(doc, f"Role: {label} ({key})", 12)
        for lv, meta in LEVEL_META.items():
            heading(doc, f"{meta['title']} - {meta['blurb']}", 11)
            body(doc, meta["ladder"], size=11, color=MUTED)
            slots = roles[key]["levels"][lv]["slots"]
            qt = doc.add_table(rows=1, cols=5)
            qt.style = "Table Grid"
            for i, h in enumerate(["Slot", "Theme", "Var", "Ans", "Question"]):
                cell(qt.rows[0].cells[i], h, size=11, bold=True, color=WHITE, fill="1A5A1A")
            for slot in slots:
                theme = slot.get("theme") or ""
                for v in slot["variants"]:
                    r = qt.add_row().cells
                    cell(r[0], str(slot.get("slot")), 11)
                    cell(r[1], theme, 11)
                    vid = v.get("id") or ""
                    var = vid.split("-")[-1] if "-" in vid else ""
                    cell(r[2], var, 11)
                    cell(r[3], "T" if v.get("answer") else "F", 11)
                    cell(r[4], v.get("text") or "", 11)
            body(doc, "")

    heading(doc, "3. How PRICKLY should use this", 13)
    body(
        doc,
        "On Start / Next Level: pick role + level, then choose a variant pack V1-V5 that the examinee has not "
        "used recently (localStorage rotation). Serve exactly the 10 items for that pack. Never reshuffle a "
        "completed level's same variant as 'Next Level'. Next Level advances level index; variant rotation is orthogonal.",
    )

    for path in OUT_DOCXS:
        path.parent.mkdir(parents=True, exist_ok=True)
        doc.save(path)
        print("wrote", path)


def main() -> None:
    roles = load_batches()
    # ensure labels
    for key, label in ROLE_ORDER:
        if key in roles:
            roles[key]["label"] = label
    issues = validate(roles)
    runtime = to_runtime(roles)
    inv = inventory(roles)
    OUT_JSON.write_text(json.dumps(runtime, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    INVENTORY.write_text(json.dumps(inv, indent=2), encoding="utf-8")
    print("wrote", OUT_JSON)
    print("wrote", INVENTORY)
    print("issues", len(issues))
    for i in issues[:30]:
        print(" -", i)
    write_docx(roles, inv, issues)


if __name__ == "__main__":
    main()
