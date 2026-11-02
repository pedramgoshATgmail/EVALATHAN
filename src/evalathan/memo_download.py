"""Direct memo download to the user's Downloads folder (no print dialog)."""

from __future__ import annotations

import html as html_lib
import os
import re
import shutil
import subprocess
import sys
import tempfile
from html.parser import HTMLParser
from pathlib import Path


def downloads_dir() -> Path:
    home = Path.home()
    for name in ("Downloads", "Download"):
        candidate = home / name
        if candidate.is_dir():
            return candidate
    out = home / "Downloads"
    out.mkdir(parents=True, exist_ok=True)
    return out


def safe_stem(name: str, limit: int = 72) -> str:
    raw = re.sub(r"[^\w\-]+", "-", str(name or "").strip(), flags=re.UNICODE)
    raw = re.sub(r"-{2,}", "-", raw).strip("-._")
    if not raw:
        raw = "Evalathan-memo"
    return raw[:limit].rstrip("-._")


def unique_path(folder: Path, stem: str, suffix: str) -> Path:
    folder.mkdir(parents=True, exist_ok=True)
    candidate = folder / f"{stem}{suffix}"
    if not candidate.exists():
        return candidate
    for i in range(2, 200):
        alt = folder / f"{stem}-{i}{suffix}"
        if not alt.exists():
            return alt
    return folder / f"{stem}-{os.getpid()}{suffix}"


def _browser_candidates() -> list[list[str]]:
    """Return argv prefixes for headless Chromium-family print-to-pdf."""
    found: list[list[str]] = []
    if sys.platform == "darwin":
        mac_apps = (
            "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
            "/Applications/Chromium.app/Contents/MacOS/Chromium",
            "/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge",
            "/Applications/Brave Browser.app/Contents/MacOS/Brave Browser",
            "/Applications/Arc.app/Contents/MacOS/Arc",
        )
        for path in mac_apps:
            if Path(path).is_file():
                found.append([path])
    elif sys.platform == "win32":
        local = os.environ.get("LOCALAPPDATA", "")
        pf = os.environ.get("PROGRAMFILES", r"C:\Program Files")
        pf86 = os.environ.get("PROGRAMFILES(X86)", r"C:\Program Files (x86)")
        win_paths = (
            shutil.which("msedge"),
            shutil.which("chrome"),
            shutil.which("chromium"),
            str(Path(local) / "Google" / "Chrome" / "Application" / "chrome.exe") if local else "",
            str(Path(pf) / "Google" / "Chrome" / "Application" / "chrome.exe"),
            str(Path(pf86) / "Google" / "Chrome" / "Application" / "chrome.exe"),
            str(Path(pf) / "Microsoft" / "Edge" / "Application" / "msedge.exe"),
            str(Path(pf86) / "Microsoft" / "Edge" / "Application" / "msedge.exe"),
        )
        for path in win_paths:
            if path and Path(path).is_file():
                found.append([path])
    else:
        for name in ("google-chrome", "chromium", "chromium-browser", "microsoft-edge"):
            path = shutil.which(name)
            if path:
                found.append([path])
    # de-dupe while preserving order
    seen: set[str] = set()
    out: list[list[str]] = []
    for argv in found:
        key = argv[0].lower()
        if key in seen:
            continue
        seen.add(key)
        out.append(argv)
    return out


def html_to_pdf_via_browser(html: str, pdf_path: Path) -> bool:
    """Best-looking path: Chromium/Edge headless print-to-pdf (no UI print sheet)."""
    browsers = _browser_candidates()
    if not browsers:
        return False
    pdf_path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="evalathan-memo-") as tmp:
        html_path = Path(tmp) / "memo.html"
        html_path.write_text(html, encoding="utf-8")
        uri = html_path.resolve().as_uri()
        for argv in browsers:
            try:
                if pdf_path.exists():
                    pdf_path.unlink()
                cmd = argv + [
                    "--headless",
                    "--disable-gpu",
                    "--no-pdf-header-footer",
                    f"--print-to-pdf={pdf_path}",
                    uri,
                ]
                proc = subprocess.run(
                    cmd,
                    capture_output=True,
                    timeout=90,
                    check=False,
                )
                if proc.returncode == 0 and pdf_path.is_file() and pdf_path.stat().st_size > 64:
                    return True
            except (OSError, subprocess.SubprocessError, subprocess.TimeoutExpired):
                continue
    return False


class _TextExtractor(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.parts: list[str] = []
        self._skip = False

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag in {"script", "style"}:
            self._skip = True
            return
        if tag in {"p", "div", "h1", "h2", "h3", "h4", "li", "tr", "br", "hr"}:
            self.parts.append("\n")
        if tag == "li":
            self.parts.append("• ")

    def handle_endtag(self, tag: str) -> None:
        if tag in {"script", "style"}:
            self._skip = False
            return
        if tag in {"p", "div", "h1", "h2", "h3", "h4", "li", "tr"}:
            self.parts.append("\n")

    def handle_data(self, data: str) -> None:
        if self._skip:
            return
        text = data.replace("\xa0", " ")
        if text.strip():
            self.parts.append(text)


def html_to_plain(html: str) -> str:
    parser = _TextExtractor()
    try:
        parser.feed(html or "")
        parser.close()
    except Exception:  # noqa: BLE001
        return html_lib.unescape(re.sub(r"<[^>]+>", " ", html or ""))
    text = "".join(parser.parts)
    text = html_lib.unescape(text)
    text = re.sub(r"[ \t]+\n", "\n", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def _core_font_pdf(plain: str, pdf_path: Path, title: str) -> bool:
    """Always-available PDF via fpdf2 when installed; latin-1 safe fallback otherwise."""
    try:
        from fpdf import FPDF
    except ImportError:
        return _minimal_latin_pdf(plain, pdf_path, title)

    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=16)
    pdf.add_page()
    # Prefer a Unicode TTF when present so · and glossary names stay intact.
    font_loaded = False
    for path in (
        Path(r"C:\Windows\Fonts\arial.ttf"),
        Path("/System/Library/Fonts/Supplemental/Arial.ttf"),
        Path("/Library/Fonts/Arial.ttf"),
        Path("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"),
    ):
        if path.is_file():
            try:
                pdf.add_font("MemoBody", fname=str(path))
                pdf.set_font("MemoBody", size=11)
                font_loaded = True
                break
            except Exception:  # noqa: BLE001
                continue
    if not font_loaded:
        pdf.set_font("Helvetica", size=11)
        plain = plain.encode("latin-1", "replace").decode("latin-1")

    if title:
        if font_loaded:
            pdf.set_font("MemoBody", size=16)
        else:
            pdf.set_font("Helvetica", size=16)
        pdf.multi_cell(0, 8, title)
        pdf.ln(4)
        if font_loaded:
            pdf.set_font("MemoBody", size=11)
        else:
            pdf.set_font("Helvetica", size=11)
    for block in plain.split("\n"):
        pdf.multi_cell(0, 6, block or " ")
    pdf.output(str(pdf_path))
    return pdf_path.is_file() and pdf_path.stat().st_size > 64


def _minimal_latin_pdf(plain: str, pdf_path: Path, title: str) -> bool:
    """Tiny PDF writer (Helvetica) when fpdf2 is not installed."""
    body = (title + "\n\n" + plain) if title else plain
    body = body.encode("latin-1", "replace").decode("latin-1")
    lines = []
    for paragraph in body.splitlines() or [""]:
        while len(paragraph) > 90:
            lines.append(paragraph[:90])
            paragraph = paragraph[90:]
        lines.append(paragraph)
    if not lines:
        lines = [""]

    def esc(s: str) -> str:
        return s.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")

    content_parts = ["BT", "/F1 11 Tf", "50 780 Td", "14 TL"]
    first = True
    y_lines = 0
    page_streams: list[str] = []
    for line in lines:
        if y_lines >= 52:
            content_parts.append("ET")
            page_streams.append("\n".join(content_parts))
            content_parts = ["BT", "/F1 11 Tf", "50 780 Td", "14 TL"]
            first = True
            y_lines = 0
        if first:
            content_parts.append(f"({esc(line)}) Tj")
            first = False
        else:
            content_parts.append("T*")
            content_parts.append(f"({esc(line)}) Tj")
        y_lines += 1
    content_parts.append("ET")
    page_streams.append("\n".join(content_parts))

    objects: list[bytes] = []
    objects.append(b"<< /Type /Catalog /Pages 2 0 R >>")
    kids = " ".join(f"{3 + i * 2} 0 R" for i in range(len(page_streams)))
    objects.append(
        f"<< /Type /Pages /Kids [{kids}] /Count {len(page_streams)} >>".encode("ascii")
    )
    for i, stream in enumerate(page_streams):
        stream_b = stream.encode("latin-1", "replace")
        page_obj_num = 3 + i * 2
        content_obj_num = page_obj_num + 1
        objects.append(
            (
                f"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] "
                f"/Contents {content_obj_num} 0 R "
                f"/Resources << /Font << /F1 << /Type /Font /Subtype /Type1 "
                f"/BaseFont /Helvetica >> >> >> >>"
            ).encode("ascii")
        )
        objects.append(
            f"<< /Length {len(stream_b)} >>\nstream\n".encode("ascii")
            + stream_b
            + b"\nendstream"
        )

    out = bytearray(b"%PDF-1.4\n")
    offsets = [0]
    for i, obj in enumerate(objects, start=1):
        offsets.append(len(out))
        out.extend(f"{i} 0 obj\n".encode("ascii"))
        out.extend(obj)
        out.extend(b"\nendobj\n")
    xref_pos = len(out)
    out.extend(f"xref\n0 {len(objects) + 1}\n".encode("ascii"))
    out.extend(b"0000000000 65535 f \n")
    for off in offsets[1:]:
        out.extend(f"{off:010d} 00000 n \n".encode("ascii"))
    out.extend(
        (
            f"trailer\n<< /Size {len(objects) + 1} /Root 1 0 R >>\n"
            f"startxref\n{xref_pos}\n%%EOF\n"
        ).encode("ascii")
    )
    pdf_path.write_bytes(bytes(out))
    return pdf_path.is_file() and pdf_path.stat().st_size > 64


def reveal_in_folder(path: Path) -> None:
    try:
        if sys.platform == "darwin":
            subprocess.Popen(["open", "-R", str(path)])  # noqa: S603
        elif sys.platform == "win32":
            subprocess.Popen(["explorer", "/select,", str(path)])  # noqa: S603
        else:
            subprocess.Popen(["xdg-open", str(path.parent)])  # noqa: S603
    except OSError:
        pass


def save_memo_download(html: str, suggested_name: str = "Evalathan-memo") -> dict:
    """Write a PDF into Downloads without opening a print dialog.

    Prefer Chromium/Edge headless layout. Fall back to a text PDF so Download
    still produces a real .pdf on machines with no browser binary.
    """
    if not (html or "").strip():
        return {"ok": False, "error": "Memo HTML is empty."}

    stem = safe_stem(suggested_name)
    dest_dir = downloads_dir()
    pdf_path = unique_path(dest_dir, stem, ".pdf")

    if html_to_pdf_via_browser(html, pdf_path):
        reveal_in_folder(pdf_path)
        return {
            "ok": True,
            "path": str(pdf_path),
            "kind": "pdf",
            "engine": "browser",
        }

    plain = html_to_plain(html)
    title = "Evalathan memo"
    if _core_font_pdf(plain, pdf_path, title):
        reveal_in_folder(pdf_path)
        return {
            "ok": True,
            "path": str(pdf_path),
            "kind": "pdf",
            "engine": "text",
            "note": "Saved a text PDF (no Chrome/Edge headless on this machine).",
        }

    # Last resort: HTML in Downloads (still a direct file, no print sheet).
    html_path = unique_path(dest_dir, stem, ".html")
    html_path.write_text(html, encoding="utf-8")
    reveal_in_folder(html_path)
    return {
        "ok": True,
        "path": str(html_path),
        "kind": "html",
        "engine": "html",
        "note": "Could not build a PDF; saved HTML to Downloads instead.",
    }
