"""Rewrite Biasrex Simplespeak + Techspeak to Hydra depth from Codex/Wikipedia explainers."""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

# (id, simplespeak, techspeak) — plain text / HTML fragments used in both GLOSSARY.md and glossary.html
SPEAK: dict[str, tuple[str, str]] = {
    "filterly": (
        "Imagine a loud market where every stall shouts at once. You cannot hear them all, "
        "so your brain keeps the vivid, recent, and repeated bits and drops the rest. "
        "Filterly asks whether your eval design or agent pipeline did that filter on purpose - "
        "with a fair sampling note - or quietly cherry-picked the loud stalls that make the score look good. "
        "Asks: too much noise, did you filter fairly?",
        "Maps Buster Benson's Codex problem <b>Too much information</b> "
        '(<a href="https://buster.medium.com/cognitive-bias-cheat-sheet-55a472476b18">Cognitive bias cheat sheet</a>; '
        '<a href="https://commons.wikimedia.org/wiki/File:Cognitive_bias_codex_en.svg">Cognitive Bias Codex</a> SVG; '
        '<a href="https://bias.wiki/">bias.wiki</a>). '
        "When the world dumps more signal than working memory can hold, attention uses cheap tricks - "
        "availability, selective attention, mere exposure, frequency illusion - so some evidence is kept and most is discarded. "
        "Filterly grades whether a claimed score or agent run documents that filter (sampling plan, inclusion/exclusion, "
        "cherry-pick guard, or filter-bias test) instead of presenting a convenience slice as the whole field. "
        "Related leaf families include availability heuristic and attentional bias; Biasrex does not grade one Wikipedia leaf per name. "
        "Pass = mitigation artifact or explicit non-claim. Fail = leaderboard cherry-pick with no filter note. Blank = no pack. "
        "A blank is not a fail and not a zero.",
    ),
    "meaningly": (
        "After the filter, only scraps remain - and the mind hates a blank map. "
        "It connects dots, fills gaps with what it already believes, and invents a neat story so the scraps feel like a world. "
        "Meaningly asks whether your claims are still tied to inspectable evidence, or whether the story did the work the facts never did. "
        "Asks: not enough facts, did you invent a neat story?",
        "Maps Benson's Codex problem <b>Not enough meaning</b> "
        '(cheat sheet; <a href="https://commons.wikimedia.org/wiki/File:Cognitive_bias_codex_en.svg">Codex</a>; '
        '<a href="https://bias.wiki/">bias.wiki</a>). '
        "After information is reduced, people still need a usable model, so they fill gaps with prior beliefs - "
        "confabulation, clustering illusion, anecdotal fallacy, illusion of validity, neglect of probability, and related story-filling moves. "
        "Meaningly grades narrative or stereotype claims in eval writeups and agent rationales: do they cite artifacts a reader can open "
        "(logs, citations, Warrantly-adjacent evidence), or does the plot stand alone? "
        "Pass = claims cite inspectable evidence. Fail = stereotype or story without a source. Blank = no claim pack. "
        "Matching a psych pattern is not proof the product 'has' the bias. A blank is not a fail and not a zero.",
    ),
    "hastely": (
        "Sometimes waiting feels more dangerous than moving. Under time pressure the brain bets fast - "
        "overconfidence, sunk cost, illusion of control - and skips the brake that would have caught a bad path. "
        "Hastely asks whether your agent loop or decision pack still has a stop/review gate when urgency is loud. "
        "Asks: need to move now, did you skip the brake?",
        "Maps Benson's Codex problem <b>Need to act fast</b> "
        '(cheat sheet; <a href="https://commons.wikimedia.org/wiki/File:Cognitive_bias_codex_en.svg">Codex</a>; '
        '<a href="https://bias.wiki/">bias.wiki</a>). '
        "Limited time and incomplete information force action; without speed we stall, but speed without a brake "
        "licenses overconfidence effect, optimism bias, illusion of control, sunk-cost continuation, and always-act loops. "
        "Hastely grades whether trajectories, runbooks, or agent graphs show an explicit stop, escalate, or human-review gate "
        "before irreversible tools fire - not whether the operator felt sure. "
        "Pass = stop / review gates or haste tests exist. Fail = always-act loops with no brake. Blank = no trajectory pack. "
        "A blank is not a fail and not a zero.",
    ),
    "memoryly": (
        "Memory is not a perfect hard drive. It keeps generalizations and standout moments, then feeds those leftovers "
        "back into tomorrow's filters and stories - even after the world changed. "
        "Memoryly asks whether old scores, caches, and cites are still treated as live truth, or whether someone refreshed what stuck. "
        "Asks: what stuck in memory, is it still true?",
        "Maps Benson's Codex problem <b>What should we remember?</b> "
        '(cheat sheet; <a href="https://commons.wikimedia.org/wiki/File:Cognitive_bias_codex_en.svg">Codex</a>; '
        '<a href="https://bias.wiki/">bias.wiki</a>). '
        "Storage is selective: generalizations beat specifics; standout items survive; forgotten detail never corrects the next filter. "
        "Related families include false memory, source confusion / misattribution, suggestibility, and continued influence of retracted information. "
        "Memoryly grades whether eval products and agent stores refresh, version, or deprecate retained scores and cites "
        "instead of letting obsolete numbers keep steering decisions. "
        "Pairs with <a href=\"#benchrex\">Benchrex</a> deprecation evalers when the stale item is a benchmark claim. "
        "Pass = memory refresh / deprecation link exists. Fail = obsolete scores kept as live truth. Blank = no memory policy. "
        "A blank is not a fail and not a zero.",
    ),
    "confirmly": (
        "Once a hypothesis feels like 'yours,' search tends to hunt for yes. "
        "Disagreeing evidence gets skipped, ambiguous evidence gets bent, and memory rehearses the wins. "
        "Confirmly asks whether your protocol forced a look for no - a disconfirming check - or only collected agreeing samples. "
        "Asks: did you only look for yes?",
        "Named after <a href=\"https://en.wikipedia.org/wiki/Confirmation_bias\">confirmation bias</a>: "
        "the tendency to search for, interpret, favor, and recall information that supports prior beliefs, values, or decisions "
        "(selective exposure / positive-test strategy; biased interpretation; biased memory). "
        "Related: myside bias; one-sided hypothesis tests that never try to falsify. "
        "Confirmly is the Biasrex process-style gate for that pattern in eval packs and agent critique loops. "
        "It looks for adversarial prompts, red-team notes, holdout counterexamples, or other explicit disconfirming checks - "
        "interactive falsification preferred over keyword scans for the word 'bias'. "
        "Pass = disconfirming check exists. Fail = only confirming samples. Blank = no confirm protocol. "
        "Not fully wired in the default install yet. A blank is not a fail and not a zero.",
    ),
    "automately": (
        "Tools feel authoritative. When a model, checker, or autopilot speaks, people often accept the suggestion "
        "and stop watching the raw evidence - even when the tool is wrong or silent. "
        "Automately asks whether trust was earned with a verify/escalate step, or whether the tool got a free pass. "
        "Asks: check before trust?",
        "Named after <a href=\"https://en.wikipedia.org/wiki/Automation_bias\">automation bias</a>: "
        "the propensity to favor suggestions from automated decision systems and to ignore contradictory non-automated information, "
        "even when the latter is correct. Classic error split: "
        "<b>commission</b> (follow a bad automated directive) and <b>omission</b> (miss a problem the automation did not flag because monitoring stopped). "
        "Automately grades agent-tool and model-assist traces for an explicit human or second-system verify / escalate step "
        "before irreversible accept - Trajectly-adjacent evidence, not a seventeenth Hydra score. "
        "Pass = escalation / verify step exists. Fail = blind tool accept. Blank = no trust policy. "
        "Not fully wired in the default install yet. A blank is not a fail and not a zero.",
    ),
}


def replace_speak(text: str, eid: str, simple: str, tech: str, is_html: bool) -> str:
    marker = (
        f'<p><a id="{eid}" name="{eid}"></a></p>'
        if is_html
        else f'<a id="{eid}" name="{eid}"></a>'
    )
    i0 = text.find(marker)
    if i0 < 0:
        raise SystemExit(f"missing {eid}")
    # next term rule after this entry
    next_rule = text.find('<p><img src=', i0 + 10)
    # find simplespeak and techspeak headers inside this entry
    ss = (
        '<h3><img src="../assets/glossary/simplespeak.png"'
        if is_html
        else '<h3><img src="assets/glossary/simplespeak.png"'
    )
    ts = (
        '<h3><img src="../assets/glossary/techspeak.png"'
        if is_html
        else '<h3><img src="assets/glossary/techspeak.png"'
    )
    i_ss = text.find(ss, i0)
    i_ts = text.find(ts, i0)
    if i_ss < 0 or i_ts < 0 or (next_rule > 0 and (i_ss > next_rule or i_ts > next_rule)):
        raise SystemExit(f"speak headers missing for {eid}")

    # body after simplespeak header line through before techspeak header
    ss_line_end = text.find("\n", i_ss)
    # skip blank line after header
    body_ss_start = ss_line_end + 1
    while body_ss_start < len(text) and text[body_ss_start] == "\n":
        body_ss_start += 1
    # techspeak starts at i_ts; simplespeak body ends at last content before i_ts
    tech_line_end = text.find("\n", i_ts)
    body_ts_start = tech_line_end + 1
    while body_ts_start < len(text) and text[body_ts_start] == "\n":
        body_ts_start += 1
    # techspeak body ends at next blank+rule or next <p><img term-rule
    # Find term-rule after techspeak
    rule = text.find('<p><img src=', body_ts_start)
    if rule < 0:
        raise SystemExit(f"no term rule after {eid}")
    # walk back over blank lines before rule
    body_ts_end = rule
    while body_ts_end > body_ts_start and text[body_ts_end - 1] == "\n":
        body_ts_end -= 1

    if is_html:
        new_ss = f"<p>{simple}</p>\n\n"
        new_ts = f"<p>{tech}</p>\n\n\n"
    else:
        new_ss = f"{simple}\n\n"
        new_ts = f"{tech}\n\n\n"

    # Replace tech first (later indices), then simple
    text = text[:body_ts_start] + new_ts + text[rule:]
    # re-find simplespeak body after mutation
    i_ss = text.find(ss, i0)
    i_ts = text.find(ts, i0)
    ss_line_end = text.find("\n", i_ss)
    body_ss_start = ss_line_end + 1
    while body_ss_start < len(text) and text[body_ss_start] == "\n":
        body_ss_start += 1
    text = text[:body_ss_start] + new_ss + text[i_ts:]
    return text


def main() -> None:
    md_path = ROOT / "GLOSSARY.md"
    html_path = ROOT / "docs" / "glossary.html"
    md = md_path.read_text(encoding="utf-8")
    html = html_path.read_text(encoding="utf-8")
    for eid, (simple, tech) in SPEAK.items():
        md = replace_speak(md, eid, simple, tech, False)
        html = replace_speak(html, eid, simple, tech, True)
        print("rewrote", eid)
    md_path.write_text(md, encoding="utf-8", newline="\n")
    html_path.write_text(html, encoding="utf-8", newline="\n")
    print("ok")


if __name__ == "__main__":
    main()
