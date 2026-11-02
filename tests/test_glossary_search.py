import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_search_index_matches_glossary_anchors() -> None:
    glossary = (ROOT / "GLOSSARY.md").read_text(encoding="utf-8")
    html = (ROOT / "docs" / "glossary.html").read_text(encoding="utf-8")
    anchors = set(re.findall(r'<a id="([^"]+)"', glossary))
    raw = html.split('<script type="application/json" id="glossary-index">', 1)[1]
    raw = raw.split("</script>", 1)[0]
    indexed = {item["id"] for item in json.loads(raw)}
    assert indexed == anchors
    assert "desk.py" not in html
    assert "launch.bat" not in html
    assert "(glossary.html)" not in glossary
    assert "htmlpreview.github.io/?" in glossary
    assert "raw.githubusercontent.com/pedramgoshATgmail/EVALATHAN/" in glossary
    assert "docs/glossary.html" in glossary
    assert 'id="archly"' in html
    assert "assets/glossary/archly.png" in html
    assert "Rubric stem" in html
    assert "GLOSSARY.md#user-content-" not in html
    assert "scrollIntoView" in html
    assert "new URL(window.location.href)" in html
    assert 'replaceState(null, "", "#"' not in html
    assert "evalathanOpenGlossary" in html
    assert "scrollTo" in html
    assert "__evalathanGlossarySearch" in html
    assert 'createElement("a")' in html
    assert "touchstart" in html
    assert "hrefFor" in html
    assert "curcuriely" in indexed
    assert "ludats-mode-pair" in indexed
    hydra = (
        "archly",
        "chorely",
        "codely",
        "devly",
        "domly",
        "levi",
        "menschly",
        "mixly",
        "pressly",
        "refactorly",
        "runly",
        "stackly",
        "tokely",
        "trajectly",
        "triadly",
        "warrantly",
    )
    ludats = (
        "copernly",
        "keplerly",
        "galileoly",
        "newtonly",
        "darwinly",
        "mendly",
        "curcuriely",
        "einsteinly",
    )
    for brand in hydra + ludats:
        assert any(
            "ludats-evaler-xl" in m.group(0)
            for m in re.finditer(
                r"<a[^>]+href=\"[^\"]*" + re.escape(brand) + r"[^\"]*\"[^>]*>",
                html,
            )
        ), brand
    card_links = re.findall(
        r"<a([^>]*data-xl=\"[^\"]*glossary/cards/[^\"]+\"[^>]*)>",
        html,
    )
    assert card_links
    for attrs in card_links:
        assert "ludats-evaler-xl" in attrs
        assert 'href="#' in attrs
    assert 'href="assets/glossary/cards/' not in glossary
    assert "function xlSrc(a)" in html
    assert "openXl(xlSrc(a), a);" in html
    assert 'id="ludats-xl-close"' in html
    assert "__evalathanCloseLudatsXl" in html
    assert "evalathanXlHome" in html
    assert "addEventListener(\"click\"" in html
    assert ", true);" in html
