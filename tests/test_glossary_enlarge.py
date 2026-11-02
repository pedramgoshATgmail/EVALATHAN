from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_search_opens_enlarge_from_xl_hash() -> None:
    html = (ROOT / "docs" / "glossary.html").read_text(encoding="utf-8")
    assert "function landingId" in html
    assert "function openFromLanding" in html
    assert 'indexOf("xl-") === 0' in html
    assert "ludats-xl-close" in html
    assert "function xlSrc(a)" in html
