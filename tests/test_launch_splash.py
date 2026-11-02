"""Launch-splash stop/pid helpers (no GUI)."""

from __future__ import annotations

from pathlib import Path

from evalathan import launch_splash as splash


def test_request_close_writes_stop_file(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setenv("EVALATHAN_STATE_DIR", str(tmp_path))
    assert not splash.stop_path().is_file()
    splash.request_close()
    assert splash.stop_path().is_file()
    assert splash.stop_path().read_text(encoding="utf-8").strip() == "1"


def test_already_running_false_without_pid(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setenv("EVALATHAN_STATE_DIR", str(tmp_path))
    assert splash.already_running() is False


def test_clear_stop_removes_stop_only(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setenv("EVALATHAN_STATE_DIR", str(tmp_path))
    splash.stop_path().write_text("1", encoding="utf-8")
    splash.pid_path().write_text("1", encoding="utf-8")
    splash.clear_stop()
    assert not splash.stop_path().is_file()
    assert splash.pid_path().is_file()


def test_splash_script_points_at_ui_file() -> None:
    path = splash.splash_script()
    assert path.name == "launch_splash.py"
    assert path.parent.name == "v2"
    assert (path.parent / "assets" / "fuss.png").is_file()
    assert (path.parent / "assets" / "fuss-splash.png").is_file()
