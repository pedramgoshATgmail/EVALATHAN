# -*- coding: utf-8 -*-
"""Build Developer L&R five-pack MCQ banks from existing True/False packs.

Reads:  ui/v2/assets/prickly-dev-banks-variants.json
Writes: ui/v2/assets/prickly-dev-mcq-banks-variants.json
Also writes: ui/sandbox/reports/prickly_mcq_validation.json

Conversion:
  T/F true  -> stem asks for sound practice; correct = statement
  T/F false -> stem asks for unsound/trap;    correct = statement
Distractors come from opposite-polarity items in the same role (cross level/variant).

Usage:
  python scripts/generate_prickly_dev_mcq_banks.py
  python scripts/generate_prickly_dev_mcq_banks.py --validate-only
"""
from __future__ import annotations

import argparse
import hashlib
import json
import random
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TF_PATH = ROOT / "ui" / "v2" / "assets" / "prickly-dev-banks-variants.json"
MCQ_PATH = ROOT / "ui" / "v2" / "assets" / "prickly-dev-mcq-banks-variants.json"
SANDBOX_MCQ = ROOT / "ui" / "sandbox" / "assets" / "prickly-dev-mcq-banks-variants.json"
REPORT = ROOT / "ui" / "sandbox" / "reports" / "prickly_mcq_validation.json"

VARIANT_NAMES = ("V1", "V2", "V3", "V4", "V5")
LEVELS = ("1", "2", "3", "4", "5")
N_CHOICES = 5
N_DISTRACTORS = 4

STEM_SOUND = "Which of the following is sound practice?"
STEM_TRAP = "Which of the following is unsound or a trap to avoid?"

# Soft fillers only if the role pool still lacks opposite-polarity texts.
SOFT_SOUND = [
    "Ship a small change behind a check, then widen access only after it holds.",
    "Write down the decision and the rollback path before you enlarge the blast radius.",
    "Prefer a reversible step over a clever one-way cut when the stakes are high.",
    "Ask for a second pair of eyes when the change touches shared production paths.",
    "Measure the user-facing failure first, then tune the internal metric.",
]
SOFT_TRAP = [
    "Skip the check this once because the team is under time pressure.",
    "Push straight to main and fix issues only if someone complains later.",
    "Treat silent green dashboards as proof the user is fine.",
    "Keep the only copy of a critical secret in a personal chat history.",
    "Optimize a vanity metric while the real user path stays broken.",
]


def _seeded_rng(key: str) -> random.Random:
    digest = hashlib.sha256(key.encode("utf-8")).hexdigest()
    return random.Random(int(digest[:16], 16))


def _normalize(text: str) -> str:
    return " ".join((text or "").strip().lower().split())


def _collect_role_pools(tf: dict) -> dict[str, dict[str, list[str]]]:
    """role -> {sound: [texts], trap: [texts]} across all variants/levels."""
    pools: dict[str, dict[str, list[str]]] = defaultdict(lambda: {"sound": [], "trap": []})
    seen: dict[str, set[str]] = defaultdict(set)
    for vname in VARIANT_NAMES:
        roles = tf["variants"][vname]["roles"]
        for role_id, role in roles.items():
            for level in LEVELS:
                for item in role["levels"][level]["items"]:
                    text = (item.get("text") or "").strip()
                    if not text:
                        continue
                    key = _normalize(text)
                    if key in seen[role_id]:
                        continue
                    seen[role_id].add(key)
                    bucket = "sound" if item.get("answer") is True else "trap"
                    pools[role_id][bucket].append(text)
    return pools


def _pick_distractors(
    rng: random.Random,
    correct: str,
    opposite: list[str],
    soft: list[str],
) -> list[str]:
    correct_n = _normalize(correct)
    pool = [t for t in opposite if _normalize(t) != correct_n]
    rng.shuffle(pool)
    out: list[str] = []
    used = {correct_n}
    for t in pool:
        n = _normalize(t)
        if n in used:
            continue
        out.append(t)
        used.add(n)
        if len(out) >= N_DISTRACTORS:
            return out
    soft_shuffled = soft[:]
    rng.shuffle(soft_shuffled)
    for t in soft_shuffled:
        n = _normalize(t)
        if n in used:
            continue
        out.append(t)
        used.add(n)
        if len(out) >= N_DISTRACTORS:
            return out
    # Last resort: numbered placeholders (should never hit with soft lists).
    while len(out) < N_DISTRACTORS:
        filler = f"Placeholder distractor {len(out) + 1} for {correct[:24]}"
        n = _normalize(filler)
        if n in used:
            continue
        out.append(filler)
        used.add(n)
    return out


def _item_to_mcq(item: dict, role_id: str, pools: dict) -> dict:
    text = (item.get("text") or "").strip()
    is_true = item.get("answer") is True
    polarity = "sound" if is_true else "trap"
    stem = STEM_SOUND if is_true else STEM_TRAP
    opposite_key = "trap" if is_true else "sound"
    soft = SOFT_TRAP if is_true else SOFT_SOUND
    rng = _seeded_rng(item.get("id") or text)
    distractors = _pick_distractors(rng, text, pools[role_id][opposite_key], soft)
    choices = [text] + distractors
    rng.shuffle(choices)
    answer_index = choices.index(text)
    mcq_id = (item.get("id") or "ITEM").replace("-V", "-MCQ-V")
    if "-MCQ-" not in mcq_id:
        mcq_id = f"{item.get('id', 'ITEM')}-MCQ"
    return {
        "id": mcq_id,
        "stem": stem,
        "choices": choices,
        "answerIndex": answer_index,
        "theme": item.get("theme") or "",
        "slot": item.get("slot"),
        "source_id": item.get("id"),
        "polarity": polarity,
        "tf_answer": bool(is_true),
    }


def build_mcq(tf: dict) -> dict:
    pools = _collect_role_pools(tf)
    variants = {}
    total = 0
    for vname in VARIANT_NAMES:
        roles_out = {}
        for role_id, role in tf["variants"][vname]["roles"].items():
            levels_out = {}
            for level in LEVELS:
                src = role["levels"][level]
                items = [_item_to_mcq(it, role_id, pools) for it in src["items"]]
                total += len(items)
                levels_out[level] = {
                    "title": src.get("title"),
                    "blurb": src.get("blurb"),
                    "ladder": src.get("ladder"),
                    "items": items,
                }
            roles_out[role_id] = {
                "label": role.get("label") or role_id,
                "levels": levels_out,
            }
        variants[vname] = {
            "variant": vname,
            "variantIndex": VARIANT_NAMES.index(vname) + 1,
            "roles": roles_out,
        }
    return {
        "version": 1,
        "format": "multiple_choice",
        "maxLevel": 5,
        "variantCount": 5,
        "choicesPerItem": 5,
        "totalItems": total,
        "note": (
            "Derived from prickly-dev-banks-variants.json. "
            "Five MCQ packs (V1-V5), 15 roles x 5 levels x 10 items. "
            "Sound stem when source T/F is true; trap stem when source T/F is false. "
            "Practice feedback only - ship gate follows T/F HOLD policy."
        ),
        "levelMeta": tf.get("levelMeta"),
        "policy": tf.get("policy"),
        "source_tf": {
            "path": "ui/v2/assets/prickly-dev-banks-variants.json",
            "format": tf.get("format"),
            "totalItems": tf.get("totalItems"),
        },
        "variants": variants,
    }


def validate_mcq(mcq: dict, tf: dict | None = None) -> dict:
    errors: list[str] = []
    warnings: list[str] = []
    item_count = 0
    if mcq.get("format") != "multiple_choice":
        errors.append("format must be multiple_choice")
    if mcq.get("variantCount") != 5:
        errors.append("variantCount must be 5")
    if set(mcq.get("variants", {}).keys()) != set(VARIANT_NAMES):
        errors.append(f"variants keys must be {VARIANT_NAMES}")

    tf_ids: set[str] = set()
    if tf:
        for vname in VARIANT_NAMES:
            for role in tf["variants"][vname]["roles"].values():
                for level in LEVELS:
                    for it in role["levels"][level]["items"]:
                        tf_ids.add(it["id"])

    seen_mcq_ids: set[str] = set()
    role_ids_ref = None
    for vname in VARIANT_NAMES:
        v = mcq["variants"].get(vname) or {}
        roles = v.get("roles") or {}
        if role_ids_ref is None:
            role_ids_ref = set(roles.keys())
        elif set(roles.keys()) != role_ids_ref:
            errors.append(f"{vname}: role set mismatch")
        for role_id, role in roles.items():
            for level in LEVELS:
                pack = (role.get("levels") or {}).get(level)
                if not pack:
                    errors.append(f"{vname}/{role_id}/L{level}: missing pack")
                    continue
                items = pack.get("items") or []
                if len(items) != 10:
                    errors.append(
                        f"{vname}/{role_id}/L{level}: expected 10 items, got {len(items)}"
                    )
                for it in items:
                    item_count += 1
                    iid = it.get("id")
                    if not iid:
                        errors.append(f"{vname}/{role_id}/L{level}: item missing id")
                        continue
                    if iid in seen_mcq_ids:
                        errors.append(f"duplicate mcq id {iid}")
                    seen_mcq_ids.add(iid)
                    choices = it.get("choices") or []
                    if len(choices) != N_CHOICES:
                        errors.append(f"{iid}: need {N_CHOICES} choices, got {len(choices)}")
                    norms = [_normalize(c) for c in choices]
                    if any(not c.strip() for c in choices):
                        errors.append(f"{iid}: empty choice")
                    if len(set(norms)) != len(norms):
                        errors.append(f"{iid}: duplicate choice text")
                    ai = it.get("answerIndex")
                    if not isinstance(ai, int) or ai < 0 or ai >= len(choices):
                        errors.append(f"{iid}: bad answerIndex {ai}")
                        continue
                    src = it.get("source_id")
                    if tf and src and src not in tf_ids:
                        errors.append(f"{iid}: source_id {src} not in T/F bank")
                    # Correct choice must equal the source claim text polarity rules
                    correct = choices[ai]
                    if it.get("polarity") == "sound" and it.get("tf_answer") is not True:
                        errors.append(f"{iid}: polarity sound but tf_answer not true")
                    if it.get("polarity") == "trap" and it.get("tf_answer") is not False:
                        errors.append(f"{iid}: polarity trap but tf_answer not false")
                    if not (it.get("stem") or "").strip():
                        errors.append(f"{iid}: empty stem")
                    if it.get("polarity") == "sound" and it.get("stem") != STEM_SOUND:
                        warnings.append(f"{iid}: unexpected sound stem")
                    if it.get("polarity") == "trap" and it.get("stem") != STEM_TRAP:
                        warnings.append(f"{iid}: unexpected trap stem")
                    if correct and len(correct) < 8:
                        warnings.append(f"{iid}: very short correct choice")

    expected = 5 * 15 * 5 * 10  # variants * roles * levels * items
    if role_ids_ref is not None and len(role_ids_ref) != 15:
        errors.append(f"expected 15 roles, got {len(role_ids_ref)}")
    if item_count != expected and not errors:
        errors.append(f"expected {expected} items, counted {item_count}")
    elif item_count != mcq.get("totalItems"):
        warnings.append(
            f"totalItems field {mcq.get('totalItems')} != counted {item_count}"
        )

    return {
        "ok": len(errors) == 0,
        "item_count": item_count,
        "expected_items": expected,
        "role_count": len(role_ids_ref or []),
        "error_count": len(errors),
        "warning_count": len(warnings),
        "errors": errors[:200],
        "warnings": warnings[:100],
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--validate-only", action="store_true")
    args = ap.parse_args()

    tf = json.loads(TF_PATH.read_text(encoding="utf-8"))
    if args.validate_only:
        if not MCQ_PATH.exists():
            print(f"MISSING {MCQ_PATH}")
            return 1
        mcq = json.loads(MCQ_PATH.read_text(encoding="utf-8"))
        report = validate_mcq(mcq, tf)
    else:
        mcq = build_mcq(tf)
        report = validate_mcq(mcq, tf)
        text = json.dumps(mcq, ensure_ascii=False, indent=2) + "\n"
        MCQ_PATH.parent.mkdir(parents=True, exist_ok=True)
        MCQ_PATH.write_text(text, encoding="utf-8")
        SANDBOX_MCQ.parent.mkdir(parents=True, exist_ok=True)
        SANDBOX_MCQ.write_text(text, encoding="utf-8")

    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({k: report[k] for k in ("ok", "item_count", "expected_items", "error_count", "warning_count")}, indent=2))
    if report["errors"]:
        print("FIRST ERRORS:")
        for e in report["errors"][:20]:
            print(" -", e)
    return 0 if report["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
