"""Direct Downloads-folder memo save (no print dialog)."""

from __future__ import annotations

from pathlib import Path

from evalathan.memo_download import (
    html_to_plain,
    safe_stem,
    save_memo_download,
    unique_path,
)


def test_safe_stem_strips_junk():
    assert safe_stem("Evalathan memo / Foo!") == "Evalathan-memo-Foo"
    assert safe_stem("") == "Evalathan-memo"


def test_unique_path_increments(tmp_path: Path):
    first = unique_path(tmp_path, "memo", ".pdf")
    first.write_text("a", encoding="utf-8")
    second = unique_path(tmp_path, "memo", ".pdf")
    assert second != first
    assert second.name.startswith("memo-")


def test_html_to_plain_keeps_prose():
    plain = html_to_plain("<h1>Hello</h1><p>Devly ran.</p><ul><li>Note</li></ul>")
    assert "Hello" in plain
    assert "Devly ran." in plain
    assert "Note" in plain


def test_save_memo_download_writes_pdf(tmp_path, monkeypatch):
    monkeypatch.setattr(
        "evalathan.memo_download.downloads_dir", lambda: tmp_path / "Downloads"
    )
    monkeypatch.setattr(
        "evalathan.memo_download.html_to_pdf_via_browser", lambda html, path: False
    )
    monkeypatch.setattr("evalathan.memo_download.reveal_in_folder", lambda path: None)

    html = """<!DOCTYPE html><html><body>
    <h1>Evalathan memo</h1>
    <p>Hydra conducted sixteen evalers. Devly measured commits.</p>
    </body></html>"""
    result = save_memo_download(html, "Evalathan-memo-demo")
    assert result["ok"] is True
    assert result["kind"] == "pdf"
    path = Path(result["path"])
    assert path.is_file()
    assert path.suffix == ".pdf"
    assert path.stat().st_size > 64
    assert path.parent == tmp_path / "Downloads"
