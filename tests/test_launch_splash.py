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


def _load_ui_splash_module():
    import importlib.util

    ui_script = splash.splash_script()
    spec = importlib.util.spec_from_file_location("launch_splash_ui", ui_script)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod, ui_script


def test_keyed_splash_png_uses_transparent_key(tmp_path: Path, monkeypatch) -> None:
    """RGBA transparency must bake to the window key, not black."""
    from PIL import Image

    mod, ui_script = _load_ui_splash_module()
    monkeypatch.setenv("EVALATHAN_STATE_DIR", str(tmp_path))

    src = ui_script.parent / "assets" / "fuss-splash.png"
    keyed = mod._keyed_splash_png(src, 220, (1, 2, 3))
    assert keyed.is_file()
    im = Image.open(keyed)
    assert im.mode == "RGB"
    assert im.getpixel((0, 0)) == (1, 2, 3)
    # Interior stays warm orange, not black.
    center = im.getpixel((110, 110))
    assert center[0] > 150 and center[1] > 80


def test_build_base_rgba_has_transparent_corners() -> None:
    """Layered splash matte must be clear outside the circle (no black fringe)."""
    mod, ui_script = _load_ui_splash_module()
    src = ui_script.parent / "assets" / "fuss-splash.png"
    im = mod._build_base_rgba(src, 220)
    assert im.mode == "RGBA"
    assert im.getpixel((0, 0))[3] == 0
    assert im.getpixel((110, 110))[3] > 200
    assert im.getpixel((110, 110))[0] > 150
