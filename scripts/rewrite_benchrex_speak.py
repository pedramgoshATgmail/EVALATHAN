"""Rewrite Benchrex Simplespeak + Techspeak from Deprecating Benchmarks (arXiv:2507.06434)."""

from __future__ import annotations

from pathlib import Path

from rewrite_biasrex_speak import replace_speak

ROOT = Path(__file__).resolve().parents[1]
PAPER = "https://arxiv.org/abs/2507.06434"
LAB = "https://aistandardslab.org/deprecating-benchmarks-criteria-and-framework/"
CITE = (
    f'<a href="{PAPER}">Deprecating Benchmarks: Criteria and Framework</a> '
    "(San Joaquin, Gipiškis, Staufer, Gil; TAIG @ ICML 2025; arXiv:2507.06434; "
    f'also <a href="{LAB}">AI Standards Lab</a>)'
)
SOFT = (
    "The paper treats criteria as soft, case-law-like heuristics - not rigid binary cutoffs "
    "with numeric thresholds (Section 3). A blank is not a fail and not a zero."
)

SPEAK: dict[str, tuple[str, str]] = {
    "saturly": (
        "A test that everyone aces stops separating the strong from the stronger. "
        "When scores hug the ceiling, another point of 'progress' barely tells you anything new about real capability. "
        "Saturly asks whether the cited bench still has headroom to discriminate - or whether you are citing a flattened exam as if it still ranks models. "
        "Asks: is this bench still hard enough to tell models apart?",
        f"Maps paper criterion <b>Saturation</b> in {CITE}. "
        "Saturation means the benchmark has reached or approached its evaluation ceiling so further gains give limited information about true capabilities; "
        "nuanced improvements may go undetected (paper cites MMLU (Massive Multitask Language Understanding), "
        "GSM8K (Grade School Math 8K), and HumanEval as observed cases). "
        "Saturly grades whether a cite or leaderboard pack documents flat curves, near-ceiling scores, or an explicit saturation stance - "
        "instead of selling SOTA (state-of-the-art) on a saturated exam as fresh discrimination. "
        "Partial deprecation may still apply when components retain utility; full retire when the ceiling kills the measure. "
        f"{SOFT}",
    ),
    "contamly": (
        "If the model already saw the answer key - through leakage, memorization, or train-test overlap - a high score is not generalization. "
        "It is rehearsal. Contamly asks whether anyone stated a contamination stance with evidence or a holdout method, "
        "or whether a public number is presented as if the test stayed unseen. "
        "Asks: did the model see the test?",
        f"Maps paper criterion <b>Contamination</b> in {CITE}. "
        "When models memorize benchmark data through leakage or contamination, performance no longer reflects true generalization on the claimed capability. "
        "The paper notes multiple observed leakage cases and stays method-agnostic on fully public benches vs private holdouts (footnote 3 - out of scope). "
        "Contamly grades whether the claim pack states a contamination / leakage stance with evidence, audit, or holdout honesty - "
        "not whether Evalathan itself can prove membership. "
        "Paper: contamination often suits <b>partial</b> deprecation (remove leaked items, resample) rather than automatic full retire. "
        f"{SOFT}",
    ),
    "skewly": (
        "An uneven stack of labels can fake competence. Nail the common class, ignore the rare one, and the headline accuracy still looks fine. "
        "Skewly asks whether the score rides class or label imbalance - or whether balance and stratified metrics are on the record. "
        "Asks: is the score riding an uneven label stack?",
        f"Maps paper criterion <b>Statistical bias</b> in {CITE}. "
        "Poorly balanced classes or label distributions skew results so models exploit imbalance instead of showing the intended capability "
        "(paper example: anomaly detection won by majority-benign accuracy while missing minority anomalies). "
        "Skewly grades whether distribution notes, stratified metrics, or rebalance evidence exist for the cited score. "
        "Paper: statistical bias often suits <b>partial</b> deprecation via corrective resampling or rebalancing. "
        f"{SOFT}",
    ),
    "annotly": (
        "A grade is only as clean as the answer key. Human or auto labelers can plant errors that make every model look wrong - or look right for the wrong reason. "
        "Annotly asks whether anyone audited annotation quality, or whether known label-error reports were ignored while the cite kept traveling. "
        "Asks: are the labels clean enough to trust the grade?",
        f"Maps paper criterion <b>High annotation error rate</b> in {CITE}. "
        "Errors from creators or labelers (human or automated) compromise benchmark quality and make model evaluations unreliable "
        "(paper example: Gema et al. 2024 - 57% errors in analysed MMLU Virology items; 6.49% of all MMLU questions erred). "
        "Annotly grades whether an error audit, quarantine, or correction note exists for the cited bench. "
        "Paper: minor correctable labeling may warrant <b>partial</b> deprecation with documented fixes; large flawed slices may need full or subset retire. "
        f"{SOFT}",
    ),
    "obsoletely": (
        "Some exams stay on the board out of habit long after the task stopped mattering - or after the field already solved it. "
        "Familiarity is not relevance. Obsoletely asks whether the underlying task still matches the capability you claim, "
        "or whether inertia is keeping a dead exam alive as a progress signal. "
        "Asks: is this still the right exam for what you claim?",
        f"Maps paper criterion <b>Task obsolescence</b> in {CITE}. "
        "A benchmark may become obsolete when the underlying task is no longer relevant or has effectively been solved; "
        "continued use from familiarity or research inertia yields misleading progress and wasted resources. "
        "Related to saturation, but focused on evolving <b>task relevance</b>, not score ceilings "
        "(paper example: BIG weighing bag-of-letters word generation equally with causal reasoning - the former may be obsolete for reasoning models). "
        "Obsoletely grades whether a relevance argument is on disk for the claimed use. "
        "Paper: task obsolescence typically pushes toward <b>full</b> deprecation when the task no longer fits the use context. "
        f"{SOFT}",
    ),
    "assumly": (
        "Every bench rests on simplifying ground rules. When the field moves - tools, RAG (retrieval-augmented generation) multi-hop, agent loops - those rules can go stale without anyone rewriting the exam. "
        "Assumly asks whether the original assumptions still hold for how the score is being used today. "
        "Asks: did the ground rules change under the score?",
        f"Maps paper criterion <b>Invalidated assumptions</b> in {CITE}. "
        "Benchmarks rely on simplifying assumptions that can become inappropriate as the field evolves; "
        "when they fail, the bench no longer reflects real-world complexity or task diversity "
        "(paper example: Needle-in-a-Haystack single-fact retrieval vs real RAG (retrieval-augmented generation) "
        "that retrieves and reasons over multiple pieces; long-context LLM (large language model) retrieval tests). "
        "Assumly grades whether assumptions vs current use are stated for the cite. "
        "Paper: invalidated assumptions typically require <b>full</b> deprecation when fundamental misalignment exists. "
        f"{SOFT}",
    ),
    "driftly": (
        "Datasets freeze at creation. Words, labels, and cultural associations keep moving. "
        "A tag that meant one thing in the collection year can mean another now - and the score still pretends the dictionary never changed. "
        "Driftly asks whether anyone refreshed meanings, or whether stale labels are treated as fixed truth. "
        "Asks: do the words on the bench still mean what they meant?",
        f"Maps paper criterion <b>Semantic drift</b> in {CITE}. "
        "Over time the meaning or interpretation of a task or its labels can shift, as word meanings and cultural associations do "
        "(paper cites Kutuzov et al. 2018; Luccioni et al. 2022 on datasets as static / frozen at creation). "
        "As language, context, or social conventions evolve, benches can become outdated or unrepresentative. "
        "Driftly grades whether a drift review, refresh date, or label-semantics note exists for the cited pack. "
        f"{SOFT}",
    ),
    "assessly": (
        "Deprecation is not a vibe. Someone has to actually check the soft criteria - saturation curves, literature critique, community feedback - "
        "and decide partial upgrade vs full retire, with room for appeal. "
        "Assessly asks whether that assessment pack exists, or whether 'deprecate it' was said with no evidence trail. "
        "Asks: did anyone actually assess whether to deprecate?",
        f"Maps the <a href=\"{PAPER}\">paper's <b>assessment</b></a> phase in {CITE} (Section 4.1). "
        "Assessment decides whether deprecation is necessary by weighing impacts and which components remain valid against the Section 3 criteria. "
        "It should run regularly: track saturation curves, read emerging critique, solicit feedback from users and curators. "
        "Deprecation level (partial vs full) depends on issue nature - e.g. bias/contamination often correctable; "
        "task obsolescence / invalidated assumptions often full. "
        "Governance actors should offer a formalized appeals path (contact, timeline, partial-deprecation proposals, independent review). "
        "Assessly grades whether a Deprecard-shaped assessment artifact exists. "
        "Pass = assessment artifact exists. Fail = deprecation claimed with no assessment. Blank = process not started. "
        "Not wired as a live simulator in the default install yet. A blank is not a fail and not a zero.",
    ),
    "reportly": (
        "A silent deprecate leaves everyone citing ghosts. The paper wants a durable deprecation report: rationale, risks, full vs partial scope, "
        "what remains valid, how to read old scores, timelines, alternatives, and who to contact. "
        "Reportly asks whether that writeup exists where others can find it. "
        "Asks: was the deprecation decision written down where others can find it?",
        f"Maps the paper's <b>reporting</b> phase in {CITE} (Section 4.2). "
        "The deprecation report must state clear rationale and underlying risks, backed by assessment evidence; "
        "give explicit future-use instructions (full vs partial / which tasks or subcomponents); "
        "for upgrades, say what remains valid and how past usage should be reinterpreted; "
        "include timelines, harm-mitigation, alternatives if any, authorized archival/research use, "
        "actor identity and contacts (contextual transparency), and - when a governance actor writes it - an appeals path. "
        "Paper appendices show sample Deprecard-style reports (e.g. SWE-bench (Software Engineering Bench) illustrations). "
        "Reportly grades whether a durable, citable report artifact exists (Deprecard / changelog / advisory). "
        "Pass = report artifact exists. Fail = silent deprecation talk. Blank = no report. "
        "Not wired as a live simulator in the default install yet. A blank is not a fail and not a zero.",
    ),
    "notifyly": (
        "Assessment and a report still fail if dependents never hear. Notices should hit the same channels as the original publish, "
        "mark catalogs like a retraction, and - when creators will not act - let governance actors carry third-party deprecation lists. "
        "Notifyly asks whether the people still citing this bench were told. "
        "Asks: did the people still citing this bench get notified?",
        f"Maps the paper's <b>notification</b> phase in {CITE} (Section 4.3), including governance-list paths. "
        "Notification prevents continued use and reduces ecosystem disruption: prefer the same channels as the original publication; "
        "use clear visual / metadata markers in catalogs (retraction-like); notify key users whose evals may be invalidated; "
        "version-control upgrades so original vs modified stay distinct. "
        "When creators are unavailable or refuse, third-party governance actors may deprecate via curated <b>deprecation lists</b> "
        "with extra transparency (Sections 4 and 6). "
        "Notifyly grades whether a notification channel, advisory, or list inclusion exists. "
        "Pass = notification channel or advisory exists. Fail = users left on a dead cite. Blank = no notify pack. "
        "Not wired as a live simulator in the default install yet. A blank is not a fail and not a zero.",
    ),
}


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
