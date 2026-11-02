"""Unit tests for desk launch update check (no live GitHub fetch)."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

from evalathan.desk_update import UpdateStatus, check_for_update, ensure_published_main


def test_check_for_update_not_a_repo(tmp_path: Path) -> None:
    status = check_for_update(tmp_path, fetch=False)
    assert status.behind is False
    assert status.error


def test_check_for_update_behind(tmp_path: Path) -> None:
    (tmp_path / ".git").mkdir()
    (tmp_path / "ui" / "v2").mkdir(parents=True)
    (tmp_path / "ui" / "v2" / "index.html").write_text("ok", encoding="utf-8")

    def fake_git(repo: Path, *args: str, timeout: int = 45):
        class R:
            returncode = 0
            stdout = ""
            stderr = ""

        r = R()
        if args[:1] == ("fetch",):
            return r
        if args == ("rev-parse", "HEAD"):
            r.stdout = "aaaaaaa1\n"
            return r
        if args == ("rev-parse", "origin/main"):
            r.stdout = "bbbbbbb2\n"
            return r
        return r

    with patch("evalathan.desk_update._git", side_effect=fake_git):
        with patch("evalathan.desk_update.shutil.which", return_value="git"):
            status = check_for_update(tmp_path, fetch=True)
    assert status.behind is True
    assert status.local.startswith("aaaa")
    assert status.remote.startswith("bbbb")


def test_ensure_skips_when_env_set(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setenv("EVALATHAN_SKIP_UPDATE", "1")
    with patch("evalathan.desk_update.check_for_update") as check:
        ensure_published_main(interactive=False)
        check.assert_not_called()


def test_ensure_applies_when_behind_noninteractive(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.delenv("EVALATHAN_SKIP_UPDATE", raising=False)
    monkeypatch.delenv("EVALATHAN_RELAUNCHED", raising=False)
    status = UpdateStatus(tmp_path, "aaa", "bbb", True)
    with patch("evalathan.desk_update.check_for_update", return_value=status):
        with patch(
            "evalathan.desk_update.apply_published_main", return_value=(True, "bbbbbbb")
        ) as apply:
            with patch("evalathan.desk_update._spawn_fuss_splash") as splash:
                with patch(
                    "evalathan.desk_update._reexec_desk", side_effect=SystemExit(42)
                ) as reexec:
                    try:
                        ensure_published_main(interactive=False)
                    except SystemExit as exc:
                        assert exc.code == 42
                    splash.assert_called_once()
                    apply.assert_called_once_with(tmp_path)
                    reexec.assert_called_once()
