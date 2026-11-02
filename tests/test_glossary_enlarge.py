import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_search_opens_enlarge_from_xl_hash() -> None:
    html = (ROOT / "docs" / "glossary.html").read_text(encoding="utf-8")
    assert "function landingId" in html
    assert "function openFromLanding" in html
    assert 'indexOf("xl-") === 0' in html
    assert "ludats-xl-close" in html
    assert "function xlSrc(a)" in html


def test_github_cards_point_at_search_enlarge() -> None:
    glossary = (ROOT / "GLOSSARY.md").read_text(encoding="utf-8")
    pin = re.search(
        r"htmlpreview\.github\.io/\?https://raw\.githubusercontent\.com/pedramgoshATgmail/EVALATHAN/([0-9a-f]{40})/docs/glossary\.html",
        glossary,
    )
    assert pin, "Search pin missing"
    sha = pin.group(1)
    cards = re.findall(
        r'<p align="center"><a href="([^"]+)"><img src="assets/glossary/cards/',
        glossary,
    )
    assert len(cards) == 28
    for href in cards:
        assert sha in href, href
        assert "htmlpreview.github.io/?" in href
        assert "#xl-" in href
        assert "docs/glossary.html#xl-" in href
    assert 'href="assets/glossary/cards/' not in glossary
