"""Insert Biasrex evaler cards into GLOSSARY.md + docs/glossary.html (Hydra fashion)."""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PIN = "5ef4b9372cd2a57342ce2f4fee87d51d546c2802"
W = 541
H = 404

CARDS = [
    ("filterly", "filterly-card.jpg", "Asks: too much noise, did you filter fairly?"),
    ("meaningly", "meaningly-card.jpg", "Asks: not enough facts, did you invent a neat story?"),
    ("hastely", "hastely-card.jpg", "Asks: need to move now, did you skip the brake?"),
    ("memoryly", "memoryly-card.jpg", "what stuck in memory, is it still true?"),
    ("confirmly", "confirmly-card.jpg", "did you only look for yes?"),
    ("automately", "automately-card.jpg", "Hmmm... Check before Trust?"),
]


def md_card(eid: str, file: str, alt: str) -> str:
    href = (
        "https://htmlpreview.github.io/?https://raw.githubusercontent.com/"
        f"pedramgoshATgmail/EVALATHAN/{PIN}/docs/glossary.html#xl-{eid}"
    )
    return (
        f'<p align="center"><a href="{href}">'
        f'<img src="assets/glossary/cards/{file}" alt="{alt}" width="{W}"></a></p>\n'
    )


def html_card(eid: str, file: str, alt: str) -> str:
    return (
        f'<p align="center"><a class="ludats-evaler-xl" href="#{eid}" '
        f'data-xl="../assets/glossary/cards/{file}">'
        f'<img src="../assets/glossary/cards/{file}" alt="{alt}" '
        f'width="{W}" height="{H}"></a></p>\n'
    )


def insert_after_score(text: str, eid: str, card_html: str, is_html: bool) -> str:
    marker = (
        f'<p><a id="{eid}" name="{eid}"></a></p>'
        if is_html
        else f'<a id="{eid}" name="{eid}"></a>'
    )
    i0 = text.find(marker)
    if i0 < 0:
        raise SystemExit(f"missing entry {eid}")
    ss = (
        '<h3><img src="../assets/glossary/simplespeak.png"'
        if is_html
        else '<h3><img src="assets/glossary/simplespeak.png"'
    )
    i_ss = text.find(ss, i0)
    if i_ss < 0:
        raise SystemExit(f"missing simplespeak for {eid}")
    if f"cards/{eid}-card" in text[i0:i_ss]:
        print("skip existing", eid)
        return text
    return text[:i_ss] + card_html + "\n" + text[i_ss:]


def main() -> None:
    md_path = ROOT / "GLOSSARY.md"
    html_path = ROOT / "docs" / "glossary.html"
    md = md_path.read_text(encoding="utf-8")
    html = html_path.read_text(encoding="utf-8")

    for eid, file, alt in CARDS:
        md = insert_after_score(md, eid, md_card(eid, file, alt), False)
        html = insert_after_score(html, eid, html_card(eid, file, alt), True)
        print("wired", eid)

    old = "Illustrations ship when the card art lands."
    new = "Evaler card art is Ed Slop (Educational Slop). Live conduct() for Biasrex is still held."
    # Only the Biasrex conductor line should change - it currently ends with that sentence.
    bias_old = (
        "The room is a curated subset of the Cognitive Bias Codex tradition (Buster Benson's four problems; "
        "John Manoogian III poster; <a href=\"https://en.wikipedia.org/wiki/Cognitive_bias\">Wikipedia: Cognitive bias</a>; "
        '<a href="https://bias.wiki/">bias.wiki</a>) - never one evaler per Codex leaf. Illustrations ship when the card art lands.'
    )
    bias_new = (
        "The room is a curated subset of the Cognitive Bias Codex tradition (Buster Benson's four problems; "
        "John Manoogian III poster; <a href=\"https://en.wikipedia.org/wiki/Cognitive_bias\">Wikipedia: Cognitive bias</a>; "
        '<a href="https://bias.wiki/">bias.wiki</a>) - never one evaler per Codex leaf. '
        + new
    )
    if bias_old in md:
        md = md.replace(bias_old, bias_new)
    if bias_old in html:
        html = html.replace(bias_old, bias_new)

    md_path.write_text(md, encoding="utf-8", newline="\n")
    html_path.write_text(html, encoding="utf-8", newline="\n")
    print("done")


if __name__ == "__main__":
    main()
