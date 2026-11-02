"""Insert Benchrex evaler cards into GLOSSARY.md + docs/glossary.html (Hydra fashion)."""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PIN = "e8227dcda599d84d7dc0f582708367f253af9ccf"  # replaced by pin commit after content ships
W = 541
H = 404  # 1024x764 scaled to width 541

CARDS = [
    (
        "saturly",
        "saturly-card.jpg",
        "Hmm... are these all the same difficulty? Can this harder one still tell them apart?",
    ),
    ("contamly", "contamly-card.jpg", "did the model see the test?"),
    ("skewly", "skewly-card.jpg", "is the score riding an uneven label stack?"),
    ("annotly", "annotly-card.jpg", "are the labels clean enough to trust the grade?"),
    ("obsoletely", "obsoletely-card.png", "is this still the right exam for what you claim?"),
    ("assumly", "assumly-card.jpg", "Asks: did the ground rules change under the score?"),
    ("driftly", "driftly-card.jpg", "do the words on the bench still mean what they meant?"),
    ("assessly", "assessly-card.jpg", "Asks: did anyone actually assess whether to deprecate?"),
    (
        "reportly",
        "reportly-card.jpg",
        "was the deprecation decision written down where others can find it?",
    ),
    (
        "notifyly",
        "notifyly-card.jpg",
        "did the people still citing this bench get notified?",
    ),
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
    if is_html:
        # Find <a id="eid"> then Score Constitution section ends at next <h3> Simplespeak
        marker = f'<p><a id="{eid}" name="{eid}"></a></p>'
    else:
        marker = f'<a id="{eid}" name="{eid}"></a>'
    i0 = text.find(marker)
    if i0 < 0:
        raise SystemExit(f"missing entry {eid}")
    # Prefer insert before Simplespeak heading inside this entry
    ss = '<h3><img src="../assets/glossary/simplespeak.png"' if is_html else '<h3><img src="assets/glossary/simplespeak.png"'
    i_ss = text.find(ss, i0)
    if i_ss < 0:
        raise SystemExit(f"missing simplespeak for {eid}")
    # Avoid double-insert
    if f"glossary/cards/{eid}-card" in text[i0:i_ss] or f"cards/{eid}-card" in text[i0:i_ss]:
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

    # Conductor copy: illustrations are no longer pending for Benchrex evalers
    md = md.replace(
        "Illustrations for Benchrex and his evalers ship when the card art lands; the desk names are live now.",
        "Evaler card art is Ed Slop (Educational Slop). The desk names are live; live conduct() for Benchrex is still held.",
    )
    html = html.replace(
        "Illustrations for Benchrex and his evalers ship when the card art lands; the desk names are live now.",
        "Evaler card art is Ed Slop (Educational Slop). The desk names are live; live conduct() for Benchrex is still held.",
    )

    md_path.write_text(md, encoding="utf-8", newline="\n")
    html_path.write_text(html, encoding="utf-8", newline="\n")
    print("done")


if __name__ == "__main__":
    main()
