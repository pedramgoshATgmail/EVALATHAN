"""Generate Benchrex + Biasrex glossary blocks (GLOSSARY.md + docs/glossary.html)."""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GLOSS_MD = ROOT / "GLOSSARY.md"
GLOSS_HTML = ROOT / "docs" / "glossary.html"

RULE_MD = '<p><img src="assets/term-rule.png" alt="" width="100%" height="18"></p>'
RULE_HTML = '<p><img src="../assets/term-rule.png" alt="" width="100%" height="18"></p>'

SC_MD = '<h3><img src="assets/glossary/score-constitution.png" alt="Score Constitution" height="17"></h3>'
SS_MD = '<h3><img src="assets/glossary/simplespeak.png" alt="Simplespeak" height="21"></h3>'
TS_MD = '<h3><img src="assets/glossary/techspeak.png" alt="Techspeak" height="21"></h3>'

SC_HTML = '<h3><img src="../assets/glossary/score-constitution.png" alt="Score Constitution" height="17" width="176"></h3>'
SS_HTML = '<h3><img src="../assets/glossary/simplespeak.png" alt="Simplespeak" height="21" width="113"></h3>'
TS_HTML = '<h3><img src="../assets/glossary/techspeak.png" alt="Techspeak" height="21" width="95"></h3>'


def md_entry(eid: str, title: str, score: str, simple: str, tech: str) -> str:
    return "\n".join(
        [
            f'<a id="{eid}" name="{eid}"></a>',
            f"<h2>{title}</h2>",
            "",
            SC_MD,
            "",
            score,
            "",
            SS_MD,
            "",
            simple,
            "",
            TS_MD,
            "",
            tech,
            "",
            "",
            RULE_MD,
            "",
        ]
    )


def html_entry(eid: str, title: str, score: str, simple: str, tech: str) -> str:
    def p(text: str) -> str:
        # light markdown-ish links already as HTML in callers
        return f"<p>{text}</p>"

    return "\n".join(
        [
            f'<p><a id="{eid}" name="{eid}"></a></p>',
            f"<h2>{title}</h2>",
            "",
            SC_HTML,
            "",
            p(score),
            SS_HTML,
            "",
            p(simple),
            TS_HTML,
            "",
            p(tech),
            RULE_HTML,
            "",
        ]
    )


BENCHREX = {
    "id": "benchrex",
    "title": "Benchrex",
    "score": (
        "Benchrex (Benchmark + rex) is the routing conductor for deprecation / cite-fitness cells. "
        "He calls ten evalers and writes each report beside the others. He counts how many ran, "
        "how many passed their own gate, and how many are deferred. He does not turn a blank into "
        "a zero, and he does not fold the ten into one number. He is not a seventeenth Hydra score "
        "and not a ninth Dehydrus score. The criterion set follows "
        '<a href="https://arxiv.org/abs/2507.06434">Deprecating Benchmarks: Criteria and Framework</a> '
        "(Ayrton San Joaquin, Rokas Gipiškis, Leon Staufer, Ariel Gil; TAIG @ ICML 2025; arXiv:2507.06434; "
        'also <a href="https://aistandardslab.org/deprecating-benchmarks-criteria-and-framework/">AI Standards Lab</a>). '
        "Illustrations for Benchrex and his evalers ship when the card art lands; the desk names are live now."
    ),
    "simple": (
        "The bench-deprecation conductor. Hydra grades software. Dehydrus grades locked physical worlds. "
        "Benchrex asks whether a claimed benchmark is still fit to cite. A missing Deprecard-style pack "
        "stays blank - not a fail and not a zero."
    ),
    "tech": (
        "Desk route id <code>benchrex</code>. Ten cells, in this order: "
        '<a href="#saturly">Saturly</a>, <a href="#contamly">Contamly</a>, <a href="#skewly">Skewly</a>, '
        '<a href="#annotly">Annotly</a>, <a href="#obsoletely">Obsoletely</a>, <a href="#assumly">Assumly</a>, '
        '<a href="#driftly">Driftly</a>, <a href="#assessly">Assessly</a>, <a href="#reportly">Reportly</a>, '
        '<a href="#notifyly">Notifyly</a>. The first seven map 1:1 to the paper&apos;s soft criteria '
        "(saturation, contamination, statistical bias, high annotation error, task obsolescence, "
        "invalidated assumptions, semantic drift). The last three map the paper&apos;s assessment → "
        "reporting → notification process. Soft heuristics, not hard cutoffs. Rooms stay unmerged."
    ),
}

BIASREX = {
    "id": "biasrex",
    "title": "Biasrex",
    "score": (
        "Biasrex (Bias + rex) is the routing conductor for decision-quality / cognitive-bias gate cells. "
        "He calls six evalers and writes each report beside the others. He counts how many ran, how many "
        "passed their own gate, and how many are deferred. He does not turn a blank into a zero, and he "
        "does not fold the six into one number. He is not a seventeenth Hydra score, not a ninth Dehydrus "
        "score, and not an eleventh Benchrex score. The room is a curated subset of the Cognitive Bias "
        "Codex tradition (Buster Benson&apos;s four problems; John Manoogian III poster; "
        '<a href="https://en.wikipedia.org/wiki/Cognitive_bias">Wikipedia: Cognitive bias</a>; '
        '<a href="https://bias.wiki/">bias.wiki</a>) - never one evaler per Codex leaf. '
        "Illustrations ship when the card art lands."
    ),
    "simple": (
        "The bias-gate conductor. He does not grade ~180 named biases. He grades six runnable gates "
        "built from the Codex&apos;s four problems (filter / meaning / haste / memory) plus confirmation "
        "and automation trust. A missing mitigation artifact stays blank."
    ),
    "tech": (
        "Desk route id <code>biasrex</code>. Six cells, in this order: "
        '<a href="#filterly">Filterly</a>, <a href="#meaningly">Meaningly</a>, <a href="#hastely">Hastely</a>, '
        '<a href="#memoryly">Memoryly</a>, <a href="#confirmly">Confirmly</a>, <a href="#automately">Automately</a>. '
        "See also <a href=\"#cognitive-bias-codex\">Cognitive Bias Codex</a>. Matching a psych pattern is not "
        "proof the product &apos;has&apos; the bias (PsyAgentBench warning). No composite bias score."
    ),
}

CODEX = {
    "id": "cognitive-bias-codex",
    "title": "Cognitive Bias Codex",
    "score": (
        "Definition-only. The Cognitive Bias Codex rearranges Wikipedia&apos;s long cognitive-bias inventory "
        "into four evolutionary problems (Buster Benson), drawn as a radial poster (John Manoogian III). "
        "bias.wiki is an interactive explorer of that map. Evalathan does not import ~175–188 leaves as "
        "evalers. <a href=\"#biasrex\">Biasrex</a> keeps six curated cells."
    ),
    "simple": (
        "A teaching map of many named biases, not a ready-made test harness. Too much information → filter. "
        "Not enough meaning → fill stories. Need to act fast → jump. What to remember → compress. Those four "
        "problems become Filterly, Meaningly, Hastely, and Memoryly."
    ),
    "tech": (
        "Primary references: "
        '<a href="https://en.wikipedia.org/wiki/Cognitive_bias">Wikipedia Cognitive bias</a>; '
        '<a href="https://en.wikipedia.org/wiki/List_of_cognitive_biases">List of cognitive biases</a>; '
        "Benson four-problem cheat sheet; UNC SOG Codex poster; "
        '<a href="https://bias.wiki/">bias.wiki</a>. Dimara et al. 2020 (~154 biases / 7 tasks) is the '
        "better test-design taxonomy. Malberg et al. ACL 2025 curates ~30 LLM bias tests - evidence that "
        "serious work does not ship 180 cells. Confirmly and Automately add confirmation bias and "
        "automation bias gates with interactive falsification in mind."
    ),
}

BENCH_EVALS = [
    (
        "saturly",
        "Saturly",
        "Checks whether a cited benchmark is saturated - scores near a ceiling so further gains lose discrimination. Looks for flat curves, near-perfect leaderboards, or explicit saturation notes. Pass = saturation evidence is documented or ruled out with a method note. Fail = cite claims SOTA without addressing saturation. Blank = no benchmark claim pack.",
        "Asks: is this bench still hard enough to tell models apart?",
        "Maps paper criterion <b>Saturation</b>. Soft heuristic. A blank is not a fail and not a zero.",
    ),
    (
        "contamly",
        "Contamly",
        "Checks contamination / leakage risk on a claimed score - train-test overlap, memorization signals, or missing holdout honesty. Pass = contamination stance is stated with evidence or a holdout method. Fail = public score presented as generalization with no leakage discussion. Blank = no score pack.",
        "Asks: did the model see the test?",
        "Maps paper criterion <b>Contamination</b>. Method-agnostic on public vs private holdouts (paper footnote 3).",
    ),
    (
        "skewly",
        "Skewly",
        "Checks statistical bias / class or label imbalance that a model could exploit without the claimed capability. Pass = balance or stratified metrics are shown. Fail = overall accuracy hides a broken minority class. Blank = no distribution note.",
        "Asks: is the score riding an uneven label stack?",
        "Maps paper criterion <b>Statistical bias</b>.",
    ),
    (
        "annotly",
        "Annotly",
        "Checks high annotation / label error evidence behind the number (human or auto labelers). Pass = error audit or quarantine note exists. Fail = cite ignores known label-error reports. Blank = no annotation quality record.",
        "Asks: are the labels clean enough to trust the grade?",
        "Maps paper criterion <b>High annotation error rate</b>.",
    ),
    (
        "obsoletely",
        "Obsoletely",
        "Checks task obsolescence - whether the benchmark task still matches the capability being claimed. Pass = relevance argument is on disk. Fail = obsolete task sold as current skill. Blank = no task-relevance note.",
        "Asks: is this still the right exam for what you claim?",
        "Maps paper criterion <b>Task obsolescence</b>.",
    ),
    (
        "assumly",
        "Assumly",
        "Checks invalidated design assumptions (for example a no-tool exam used to grade a tool-using agent). Pass = assumptions vs current use are stated. Fail = old assumptions silently reused. Blank = no assumption note.",
        "Asks: did the ground rules change under the score?",
        "Maps paper criterion <b>Invalidated assumptions</b>.",
    ),
    (
        "driftly",
        "Driftly",
        "Checks semantic / cultural / language drift since the claimed result - labels or meanings that aged. Pass = drift review or refresh date exists. Fail = stale meanings treated as fixed. Blank = no drift pack.",
        "Asks: do the words on the bench still mean what they meant?",
        "Maps paper criterion <b>Semantic drift</b>.",
    ),
    (
        "assessly",
        "Assessly",
        "Process cell. Checks whether a project or governance actor ran a deprecation assessment against the soft criteria (Deprecard-shaped evidence pack). Pass = assessment artifact exists. Fail = deprecation claimed with no assessment. Blank = process not started. Not wired as a live simulator in the default install yet.",
        "Asks: did anyone actually assess whether to deprecate?",
        "Maps the paper&apos;s <b>assessment</b> phase. Soft gate.",
    ),
    (
        "reportly",
        "Reportly",
        "Process cell. Checks whether assessment findings were reported in a durable, citable form (Deprecard / changelog / advisory). Pass = report artifact exists. Fail = silent deprecation talk. Blank = no report. Not wired as a live simulator in the default install yet.",
        "Asks: was the deprecation decision written down where others can find it?",
        "Maps the paper&apos;s <b>reporting</b> phase.",
    ),
    (
        "notifyly",
        "Notifyly",
        "Process cell. Checks whether users and dependents were notified (partial update vs full retire; third-party path when creators will not act). Pass = notification channel or advisory exists. Fail = users left on a dead cite. Blank = no notify pack. Not wired as a live simulator in the default install yet.",
        "Asks: did the people still citing this bench get told?",
        "Maps the paper&apos;s <b>notification</b> phase, including governance-list paths.",
    ),
]

BIAS_EVALS = [
    (
        "filterly",
        "Filterly",
        "Grades attention / selection / availability hygiene in eval design and agent pipelines (Benson problem: too much information). Looks for cherry-pick guards, sampling notes, or filter-bias tests. Pass = mitigation artifact or explicit non-claim. Fail = leaderboard cherry-pick with no filter note. Blank = no pack.",
        "Too much noise - did you filter fairly?",
        "Codex quadrant <b>Too much information</b>. Related biases include availability and selective attention families - not one leaf per name.",
    ),
    (
        "meaningly",
        "Meaningly",
        "Grades story-filling vs evidence (Benson problem: not enough meaning). Looks for narrative claims backed by artifacts (Warrantly-adjacent). Pass = claims cite inspectable evidence. Fail = stereotype or story without a source. Blank = no claim pack.",
        "Not enough facts - did you invent a neat story?",
        "Codex quadrant <b>Not enough meaning</b>. Framing / stereotype / illusory-correlation families.",
    ),
    (
        "hastely",
        "Hastely",
        "Grades overconfidence, sunk-cost, and irreversible-action gates in agent loops (Benson problem: need to act fast). Pass = stop / review gates or haste tests exist. Fail = always-act loops with no brake. Blank = no trajectory pack.",
        "Need to move now - did you skip the brake?",
        "Codex quadrant <b>Need to act fast</b>. Overconfidence / sunk-cost families.",
    ),
    (
        "memoryly",
        "Memoryly",
        "Grades continued influence of old scores, stale memory, and deprecated cites (Benson problem: what should we remember?). Pass = memory refresh / deprecation link exists. Fail = obsolete scores kept as live truth. Blank = no memory policy.",
        "What stuck in memory - is it still true?",
        "Codex quadrant <b>What should we remember?</b>. Continued-influence / stale-belief families. Pairs with Benchrex deprecation cells.",
    ),
    (
        "confirmly",
        "Confirmly",
        "Grades confirmation-bias gates - seeking only agreeing evidence. Looks for adversarial / falsification prompts or red-team notes. Pass = disconfirming check exists. Fail = only confirming samples. Blank = no confirm protocol. Interactive falsification preferred over keyword scans. Not fully wired in the default install yet.",
        "Did you only look for yes?",
        "Named after <a href=\"https://en.wikipedia.org/wiki/Confirmation_bias\">confirmation bias</a>. Optional Biasrex process-style cell with a hard protocol bar.",
    ),
    (
        "automately",
        "Automately",
        "Grades automation bias / tool-trust - over-trusting model or tool output without a human or second check. Pass = escalation / verify step exists. Fail = blind tool accept. Blank = no trust policy. Not fully wired in the default install yet.",
        "Did the tool get a free pass?",
        "Named after <a href=\"https://en.wikipedia.org/wiki/Automation_bias\">automation bias</a>. Pairs with agent-tool traces (Trajectly-adjacent), not a Hydra seventeenth score.",
    ),
]


def build_md() -> str:
    parts: list[str] = []
    # conductors
    for block in (BENCHREX, BIASREX, CODEX):
        parts.append(
            md_entry(
                block["id"],
                block["title"],
                block["score"].replace("<code>", "`").replace("</code>", "`")
                if False
                else block["score"]
                .replace("<b>", "**")
                .replace("</b>", "**")
                .replace("<code>", "`")
                .replace("</code>", "`")
                .replace("&apos;", "'"),
                block["simple"].replace("&apos;", "'"),
                block["tech"]
                .replace("<b>", "**")
                .replace("</b>", "**")
                .replace("<code>", "`")
                .replace("</code>", "`")
                .replace("&apos;", "'"),
            )
        )
    # For MD, prefer GitHub-friendly links without raw HTML where possible - but glossary already uses HTML heavily.
    # Rebuild conductors with HTML style matching existing GLOSSARY.md
    parts = []
    for block in (BENCHREX, BIASREX):
        parts.append(
            "\n".join(
                [
                    f'<a id="{block["id"]}" name="{block["id"]}"></a>',
                    f"<h2>{block['title']}</h2>",
                    "",
                    SC_MD,
                    "",
                    block["score"],
                    "",
                    SS_MD,
                    "",
                    block["simple"],
                    "",
                    TS_MD,
                    "",
                    block["tech"],
                    "",
                    "",
                    RULE_MD,
                    "",
                ]
            )
        )
    # codex - definition-only still uses SC in our structure for consistency with Evalathan style for major terms
    parts.append(
        "\n".join(
            [
                f'<a id="{CODEX["id"]}" name="{CODEX["id"]}"></a>',
                f"<h2>{CODEX['title']}</h2>",
                "",
                SC_MD,
                "",
                CODEX["score"],
                "",
                SS_MD,
                "",
                CODEX["simple"],
                "",
                TS_MD,
                "",
                CODEX["tech"],
                "",
                "",
                RULE_MD,
                "",
            ]
        )
    )
    for eid, title, score, simple, tech in BENCH_EVALS + BIAS_EVALS:
        parts.append(
            "\n".join(
                [
                    f'<a id="{eid}" name="{eid}"></a>',
                    f"<h2>{title}</h2>",
                    "",
                    SC_MD,
                    "",
                    score,
                    "",
                    SS_MD,
                    "",
                    simple,
                    "",
                    TS_MD,
                    "",
                    tech,
                    "",
                    "",
                    RULE_MD,
                    "",
                ]
            )
        )
    return "".join(parts)


def build_html() -> str:
    parts: list[str] = []
    for block in (BENCHREX, BIASREX, CODEX):
        parts.append(html_entry(block["id"], block["title"], block["score"], block["simple"], block["tech"]))
    for eid, title, score, simple, tech in BENCH_EVALS + BIAS_EVALS:
        parts.append(html_entry(eid, title, score, simple, tech))
    return "".join(parts)


def replace_between(text: str, start_marker: str, end_marker: str, new_middle: str) -> str:
    i0 = text.find(start_marker)
    if i0 < 0:
        raise SystemExit(f"start marker not found: {start_marker}")
    i1 = text.find(end_marker, i0)
    if i1 < 0:
        raise SystemExit(f"end marker not found: {end_marker}")
    return text[:i0] + new_middle + text[i1:]


def patch_index(html: str) -> str:
    needle = '    {"id":"biasrex","label":"Biasrex","kind":"term","aliases":["biasrex","bias rex"]},'
    extra = [
        needle,
        '    {"id":"cognitive-bias-codex","label":"Cognitive Bias Codex","kind":"term","aliases":["codex","benson","manoogian"]},',
        '    {"id":"saturly","label":"Saturly","kind":"evaler","aliases":["saturation"]},',
        '    {"id":"contamly","label":"Contamly","kind":"evaler","aliases":["contamination"]},',
        '    {"id":"skewly","label":"Skewly","kind":"evaler","aliases":["statistical bias"]},',
        '    {"id":"annotly","label":"Annotly","kind":"evaler","aliases":["annotation error"]},',
        '    {"id":"obsoletely","label":"Obsoletely","kind":"evaler","aliases":["task obsolescence"]},',
        '    {"id":"assumly","label":"Assumly","kind":"evaler","aliases":["invalidated assumptions"]},',
        '    {"id":"driftly","label":"Driftly","kind":"evaler","aliases":["semantic drift"]},',
        '    {"id":"assessly","label":"Assessly","kind":"evaler","aliases":["assessment phase"]},',
        '    {"id":"reportly","label":"Reportly","kind":"evaler","aliases":["reporting phase"]},',
        '    {"id":"notifyly","label":"Notifyly","kind":"evaler","aliases":["notification phase"]},',
        '    {"id":"filterly","label":"Filterly","kind":"evaler","aliases":["filter bias"]},',
        '    {"id":"meaningly","label":"Meaningly","kind":"evaler","aliases":["meaning bias"]},',
        '    {"id":"hastely","label":"Hastely","kind":"evaler","aliases":["haste bias"]},',
        '    {"id":"memoryly","label":"Memoryly","kind":"evaler","aliases":["memory bias"]},',
        '    {"id":"confirmly","label":"Confirmly","kind":"evaler","aliases":["confirmation bias"]},',
        '    {"id":"automately","label":"Automately","kind":"evaler","aliases":["automation bias"]},',
    ]
    if '"id":"saturly"' in html:
        return html
    return html.replace(needle, "\n".join(extra))


def main() -> None:
    md = GLOSS_MD.read_text(encoding="utf-8")
    html = GLOSS_HTML.read_text(encoding="utf-8")
    md_block = build_md()
    html_block = build_html()
    md2 = replace_between(
        md,
        '<a id="benchrex" name="benchrex"></a>',
        '<a id="archly" name="archly"></a>',
        md_block,
    )
    # Expand Evalathan intro to name four rooms lightly
    old_intro = (
        "[Dehydrus](#dehydrus) writes eight [LuDaTs](#ludats) (Limited-universe Data Test sets) cells under "
        "[PRETRUWs](#pretruws), in this order: [Copernly](#copernly), [Keplerly](#keplerly), [Galileoly](#galileoly), "
        "[Darwinly](#darwinly), [Mendly](#mendly), [Einsteinly](#einsteinly), [CurCuriely](#curcuriely), [Newtonly](#newtonly). "
        "The two rooms stay apart. A blank is not a fail and not a zero. Evalathan does not fold the twenty-four cells "
        "into one number, and it does not award a state-of-the-art stamp."
    )
    new_intro = (
        "[Dehydrus](#dehydrus) writes eight [LuDaTs](#ludats) (Limited-universe Data Test sets) cells under "
        "[PRETRUWs](#pretruws), in this order: [Copernly](#copernly), [Keplerly](#keplerly), [Galileoly](#galileoly), "
        "[Darwinly](#darwinly), [Mendly](#mendly), [Einsteinly](#einsteinly), [CurCuriely](#curcuriely), [Newtonly](#newtonly). "
        "[Benchrex](#benchrex) writes ten deprecation cells. [Biasrex](#biasrex) writes six bias-gate cells. "
        "The rooms stay apart. A blank is not a fail and not a zero. Evalathan does not fold the rooms into one number, "
        "and it does not award a state-of-the-art stamp."
    )
    if old_intro in md2:
        md2 = md2.replace(old_intro, new_intro)
    html2 = replace_between(
        html,
        '<p><a id="benchrex" name="benchrex"></a></p>',
        '<p><a id="archly" name="archly"></a></p>',
        html_block,
    )
    html2 = patch_index(html2)
    GLOSS_MD.write_text(md2, encoding="utf-8", newline="\n")
    GLOSS_HTML.write_text(html2, encoding="utf-8", newline="\n")
    print("patched", GLOSS_MD)
    print("patched", GLOSS_HTML)
    print("bench_evals", len(BENCH_EVALS), "bias_evals", len(BIAS_EVALS))


if __name__ == "__main__":
    main()
