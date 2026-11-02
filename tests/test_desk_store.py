"""Saved Hydra runs must survive desk restart via the on-disk store."""

from __future__ import annotations

import io
import json

from evalathan.desk_store import load_run_sets, runs_path, save_run_sets, state_dir
from evalathan.webdesk import DeskHandler


def test_save_and_load_run_sets(tmp_path, monkeypatch):
    monkeypatch.setenv("EVALATHAN_STATE_DIR", str(tmp_path / "state"))
    sample = [
        {
            "targetKey": "https://github.com/example/memanto",
            "titleCaps": "MEMANTO",
            "shortTitle": "memanto",
            "target": "https://github.com/example/memanto",
            "latest": {"id": "run_1", "title": "memanto"},
            "saved": [{"id": "run_1", "title": "memanto", "engine": "HYDRA"}],
        }
    ]
    path = save_run_sets(sample)
    assert path == runs_path()
    assert path.is_file()
    assert state_dir() == tmp_path / "state"
    loaded = load_run_sets()
    assert len(loaded) == 1
    assert loaded[0]["saved"][0]["id"] == "run_1"
    # Second process / restart reads the same file
    again = json.loads(path.read_text(encoding="utf-8"))
    assert again[0]["titleCaps"] == "MEMANTO"


def test_api_runs_get_post_via_handler(tmp_path, monkeypatch):
    monkeypatch.setenv("EVALATHAN_STATE_DIR", str(tmp_path / "http-state"))
    handler = DeskHandler.__new__(DeskHandler)
    payloads: list[tuple[int, dict]] = []

    def _send_json(code, payload):
        payloads.append((code, payload))

    handler._send_json = _send_json  # type: ignore[method-assign]
    handler.path = "/api/runs"
    handler.headers = {"Content-Length": "0"}
    handler.rfile = io.BytesIO(b"")
    DeskHandler.do_GET(handler)
    assert payloads[-1][0] == 200
    assert payloads[-1][1]["ok"] is True
    assert payloads[-1][1]["runSets"] == []

    sample = {
        "runSets": [
            {
                "targetKey": "demo",
                "saved": [{"id": "r2", "engine": "HYDRA"}],
                "latest": None,
            }
        ]
    }
    raw = json.dumps(sample).encode("utf-8")
    handler.headers = {"Content-Length": str(len(raw))}
    handler.rfile = io.BytesIO(raw)
    DeskHandler._save_runs(handler)
    assert payloads[-1][0] == 200
    assert payloads[-1][1]["ok"] is True
    assert runs_path().is_file()
    assert load_run_sets()[0]["saved"][0]["id"] == "r2"
    # Restart simulation: load from disk again
    assert load_run_sets()[0]["saved"][0]["id"] == "r2"
