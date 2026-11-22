"""
Hi0 - lossless compact serialization for LLM prompts (Evalathan transplant).

Utility only (not an agent). Mirrors AZ Signal Engine / SEISMO hi0_serialize
without binding to SEISMO tokex_session. Callers record TOKEX separately.
"""
from __future__ import annotations

import json
import re
from typing import Any

_SCALAR_KEYS_SKIP_NEST = frozenset({"pluto", "permit_scope", "record", "event_tier_meta"})


def estimate_tokens(text: str) -> int:
    """Rough tokenizer proxy (~4 chars/token) for before/after comparison."""
    if not text:
        return 0
    return max(1, len(text) // 4)


def _escape_csv(val: str) -> str:
    s = str(val or "").replace("\n", " ").strip()
    if "," in s or '"' in s:
        return '"' + s.replace('"', '""') + '"'
    return s


def _toon_table(rows: list[dict], fields: list[str]) -> str:
    if not rows:
        return ""
    lines = [f"[{len(rows)}]{{{','.join(fields)}}}:" ]
    for row in rows:
        lines.append(",".join(_escape_csv(row.get(f, "")) for f in fields))
    return "\n".join(lines)


def _serialize_scalar(key: str, val: Any, lines: list[str], indent: int = 0) -> None:
    pad = "  " * indent
    if val is None:
        lines.append(f"{pad}{key}: null")
    elif isinstance(val, bool):
        lines.append(f"{pad}{key}: {'true' if val else 'false'}")
    elif isinstance(val, (int, float)):
        lines.append(f"{pad}{key}: {val}")
    else:
        text = str(val).strip()
        if "\n" in text:
            lines.append(f"{pad}{key}: |")
            for ln in text.splitlines():
                lines.append(f"{pad}  {ln}")
        else:
            lines.append(f"{pad}{key}: {text}")


def _serialize_dict(d: dict, lines: list[str], indent: int = 0) -> None:
    for key in sorted(d.keys()):
        val = d[key]
        pad = "  " * indent
        if key in _SCALAR_KEYS_SKIP_NEST and isinstance(val, dict):
            lines.append(f"{pad}{key}:")
            _serialize_pluto_or_dict(val, lines, indent + 1)
        elif isinstance(val, dict):
            lines.append(f"{pad}{key}:")
            _serialize_dict(val, lines, indent + 1)
        elif isinstance(val, list):
            block = _serialize_list(key, val)
            if block:
                lines.append(f"{pad}{block}")
        else:
            _serialize_scalar(key, val, lines, indent)


def _serialize_pluto_or_dict(d: dict, lines: list[str], indent: int) -> None:
    if not d:
        lines.append("  " * indent + "(empty)")
        return
    fields = sorted(d.keys())
    if all(not isinstance(v, (dict, list)) for v in d.values()):
        lines.append("  " * indent + _toon_table([{k: d[k] for k in fields}], fields))
        return
    _serialize_dict(d, lines, indent)


def _serialize_list(key: str, val: list) -> str:
    if not val:
        return f"{key}: []"
    if all(isinstance(x, str) for x in val):
        fields = ["text"]
        rows = [{"text": x} for x in val]
        return f"{key}\n{_toon_table(rows, fields)}"
    if all(isinstance(x, dict) for x in val):
        fields = sorted({k for row in val for k in row})
        if fields and all(set(row.keys()) <= set(fields) for row in val):
            return f"{key}\n{_toon_table(val, fields)}"
    return f"{key}: {json.dumps(val, separators=(',', ':'), default=str)}"


def serialize_payload(payload: Any) -> str:
    """Lossless compact text for LLM prompts."""
    lines = ["# Hi0 v1"]
    if isinstance(payload, list):
        if len(payload) == 1 and isinstance(payload[0], dict):
            _serialize_dict(payload[0], lines, 0)
        elif payload and all(isinstance(x, dict) for x in payload):
            fields = sorted({k for row in payload for k in row})
            lines.append("leads")
            lines.append(_toon_table(payload, fields))
        else:
            lines.append(json.dumps(payload, separators=(",", ":"), default=str))
    elif isinstance(payload, dict):
        _serialize_dict(payload, lines, 0)
    else:
        lines.append(str(payload))
    return "\n".join(lines) + "\n"


def _json_baseline(payload: Any) -> str:
    if isinstance(payload, (list, dict)):
        return json.dumps(payload, indent=2, default=str)
    return str(payload)


def lossless_check(payload: Any, hi0_text: str) -> bool:
    """Every top-level payload key must appear in Hi0 output."""
    if isinstance(payload, dict):
        for key in payload:
            if not re.search(rf"(^|\n){re.escape(str(key))}([:\[]|\n)", hi0_text):
                return False
        return True
    if isinstance(payload, list) and len(payload) == 1 and isinstance(payload[0], dict):
        return lossless_check(payload[0], hi0_text)
    return True


def serialize_for_llm(payload: Any, *, max_chars: int = 100_000) -> tuple[str, int]:
    """
    Return (compact Hi0 text, estimated tokens saved vs pretty JSON).
    Falls back to minified JSON if lossless check fails.
    """
    baseline = _json_baseline(payload)
    hi0 = serialize_payload(payload)
    if not lossless_check(payload, hi0):
        hi0 = json.dumps(payload, separators=(",", ":"), sort_keys=True, default=str)
    saved = max(0, estimate_tokens(baseline) - estimate_tokens(hi0))
    return hi0[:max_chars], saved
