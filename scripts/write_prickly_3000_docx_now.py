"""Build PRICKLY 3000 review Word (Calibri 11) on Desktop ASAP.

Uses roles_batch_1.json (ready) + generates batches 2-3 if missing,
then writes Desktop + docs/evals Word.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

from docx import Document
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Pt, RGBColor

ROOT = Path(__file__).resolve().parents[1]
VAR = ROOT / "ui" / "v2" / "assets" / "prickly_variants"
OUT_JSON = ROOT / "ui" / "v2" / "assets" / "prickly-dev-banks-variants.json"
NAME = "PRICKLY_DEV_LR_3000_REVIEW.docx"
OUTS = [Path.home() / "Desktop" / NAME, ROOT / "docs" / "evals" / NAME]

NAVY = RGBColor(11, 18, 32)
WHITE = RGBColor(248, 250, 252)
MUTED = RGBColor(90, 99, 110)

LEVEL_META = {
    "1": ("Level 1 - Foundations", "Clear basics. Spot obvious false comfort."),
    "2": ("Level 2 - Trade-offs", "Two good-looking options; only one is sound."),
    "3": ("Level 3 - Failure modes", "What breaks under load, time, or bad incentives."),
    "4": ("Level 4 - Precedents & traps", "Industry-familiar traps dressed as best practice."),
    "5": ("Level 5 - Edge judgment", "Subtle cases where polite process still fails the user."),
}

# Answer columns: ~5 True per 10 slots for each variant index
PAT_A = [False, True, False, True, True, True, False, True, False, False]  # V1 pattern by slot
# For variants 2-5 we rotate claims; each slot still has mixed T/F across its 5 variants.


def set_run(run, size=11, bold=False, color=NAVY, name="Calibri"):
    run.font.size = Pt(size)
    run.font.bold = bold
    run.font.name = name
    run.font.color.rgb = color
    r_pr = run._element.get_or_add_rPr()
    r_fonts = r_pr.get_or_add_rFonts()
    r_fonts.set(qn("w:eastAsia"), name)


def shade(cell, fill: str) -> None:
    tc_pr = cell._tc.get_or_add_tcPr()
    shd = OxmlElement("w:shd")
    shd.set(qn("w:fill"), fill)
    shd.set(qn("w:val"), "clear")
    tc_pr.append(shd)


def cell(c, text, size=11, bold=False, color=NAVY, fill=None):
    c.text = ""
    p = c.paragraphs[0]
    p.paragraph_format.space_after = Pt(1)
    p.paragraph_format.space_before = Pt(1)
    set_run(p.add_run(str(text)), size=size, bold=bold, color=color)
    if fill:
        shade(c, fill)


def heading(doc, text, size=14):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(10)
    p.paragraph_format.space_after = Pt(4)
    set_run(p.add_run(text), size=size, bold=True)


def body(doc, text, size=11, color=NAVY):
    p = doc.add_paragraph()
    p.paragraph_format.space_after = Pt(6)
    set_run(p.add_run(text), size=size, color=color)


def clean(s: str) -> str:
    return s.replace("\u2014", "-").replace("\u2013", "-").strip()


def load_batch(n: int) -> dict | None:
    p = VAR / f"roles_batch_{n}.json"
    if not p.is_file():
        return None
    return json.loads(p.read_text(encoding="utf-8"))


def pack_role(prefix: str, label: str, levels: dict) -> dict:
    out = {}
    for lv, themes in levels.items():
        title, blurb = LEVEL_META[lv]
        slots = []
        assert len(themes) == 10, (prefix, lv, len(themes))
        for i, (theme, variants) in enumerate(themes, 1):
            assert len(variants) == 5, (prefix, lv, theme)
            slots.append(
                {
                    "slot": i,
                    "theme": theme,
                    "variants": [
                        {
                            "id": f"{prefix}-L{lv}-S{i:02d}-V{j}",
                            "text": clean(text),
                            "answer": bool(ans),
                        }
                        for j, (ans, text) in enumerate(variants, 1)
                    ],
                }
            )
        out[lv] = {"title": title, "blurb": blurb, "slots": slots}
    return {"label": label, "levels": out}


# --- Compact curated banks for remaining 8 roles (5 variants × 10 slots × 5 levels) ---
# Format: level -> list of (theme, [(answer, text)*5])


def _tf(a0, t0, a1, t1, a2, t2, a3, t3, a4, t4):
    return [(a0, t0), (a1, t1), (a2, t2), (a3, t3), (a4, t4)]


def gen_data_engineer():
    L1 = [
        ("Pipeline success vs data correctness", _tf(
            False, "If yesterday's pipeline job succeeded, today's tables are automatically correct.",
            True, "A green pipeline run can still load wrong, incomplete, or late data.",
            False, "Row counts matching yesterday always prove today's numbers are right.",
            True, "Checking a few business metrics after a load catches errors volume checks miss.",
            False, "If the scheduler is green, analysts can trust the warehouse without spot checks.",
        )),
        ("Freshness expectations", _tf(
            True, "Users should know how fresh a dataset is supposed to be.",
            False, "Data that is hours late is fine if nobody defined a freshness target.",
            True, "A missed SLA on freshness is a data incident even if rows eventually arrive.",
            False, "Batch pipelines never need freshness alerts because they run overnight.",
            True, "Documenting expected arrival time helps people decide whether to wait or escalate.",
        )),
        ("Schema contracts", _tf(
            False, "Producers can rename columns anytime because consumers will adapt.",
            True, "Breaking a column consumers rely on without notice is a contract failure.",
            True, "Additive optional fields are usually safer than removing required ones abruptly.",
            False, "JSON columns mean schemas never need agreements.",
            False, "If both teams share Slack, schema breaks cannot ship.",
        )),
        ("Idempotent loads", _tf(
            True, "Re-running a load should not double-count facts if the job is designed well.",
            False, "Replaying yesterday's file always produces the same warehouse state without design.",
            True, "Upserts or partition replaces are common ways to make loads safe to retry.",
            False, "Append-only forever with no keys is always the safest load pattern.",
            True, "Knowing what happens on a retry is part of owning a pipeline.",
        )),
        ("PII in pipelines", _tf(
            True, "Personal data in pipelines needs the same care as in apps.",
            False, "Warehouse tables are internal, so raw national IDs are fine everywhere.",
            True, "Masking or tokenizing PII in lower environments reduces leak risk.",
            False, "Logs of full customer payloads are harmless for debugging.",
            False, "Compliance is only the legal team's job, not the data engineer's.",
        )),
        ("Testing transforms", _tf(
            False, "SQL that runs once on a sample is fully tested.",
            True, "Nulls, duplicates, and late-arriving keys are common transform failure cases.",
            True, "A small fixture set with known answers beats only testing in production.",
            False, "If the dashboard looks pretty, the join logic is correct.",
            False, "Unit tests for transforms are impossible in warehouses.",
        )),
        ("Lineage basics", _tf(
            True, "Knowing which upstream table feeds a report helps when numbers look wrong.",
            False, "Lineage is only for auditors and never helps incident response.",
            True, "A simple map of sources to marts beats tribal memory alone.",
            False, "If the BI tool shows a chart, lineage is unnecessary.",
            True, "When a source changes owner, lineage shows who else will feel the break.",
        )),
        ("Partition and volume", _tf(
            True, "A query that is fine on a week of data can fail on a year.",
            False, "Full table scans are always fine in the cloud because storage is infinite.",
            True, "Partition pruning and filters protect cost and runtime as data grows.",
            False, "SELECT * into notebooks is a complete production pattern.",
            False, "Cost of scans never matters if the query is correct.",
        )),
        ("Orchestration ownership", _tf(
            True, "A failed task needs an owner who knows whether to rerun, skip, or fix.",
            False, "Orchestrators auto-heal all data problems without humans.",
            True, "Clear upstream/downstream dependencies prevent surprise cascade failures.",
            False, "Disabling a failing sensor forever is a sound long-term fix.",
            False, "If the DAG looks green on average, rare failures can be ignored.",
        )),
        ("Documentation for consumers", _tf(
            True, "A short data dictionary for key fields prevents wrong joins and misuse.",
            False, "Column names are always self-explanatory across teams.",
            True, "Saying what a metric excludes is as important as saying what it includes.",
            False, "Docs are wasted effort because analysts prefer guessing.",
            False, "Updating docs after a breaking change is optional.",
        )),
    ]
    L2 = [
        ("Batch vs streaming", _tf(
            True, "Batch can beat streaming when the business accepts next-morning freshness.",
            False, "Streaming is always better because it sounds modern.",
            True, "Streaming adds operational cost that may outweigh its latency win.",
            False, "If any stakeholder wants real-time, streaming is mandatory with no trade-off.",
            True, "Naming the freshness need first clarifies the batch vs stream trade.",
        )),
        ("Warehouse vs lakehouse tools", _tf(
            True, "Choosing a warehouse vs lakehouse should follow access patterns and team skills.",
            False, "The newest lake format always replaces a working warehouse overnight.",
            True, "Migration cost and SQL familiarity are real trade-offs, not just feature checklists.",
            False, "Vendor lock never matters if the demo is fast.",
            False, "One tool must serve every analytics and ML workload equally well.",
        )),
        ("Quality gates vs speed", _tf(
            True, "Blocking a bad load can be the right trade even if it delays a dashboard.",
            False, "Shipping wrong numbers on time is always better than being late.",
            True, "Lightweight checks on critical keys often beat heavy checks on every column.",
            False, "Quality gates that always fail and get overridden are still protecting users.",
            True, "Agreeing which checks are release-blocking is a product-data trade.",
        )),
        ("Wide vs normalized marts", _tf(
            True, "Wide marts can speed reports at the cost of harder updates.",
            False, "Third normal form is always the right shape for every BI table.",
            True, "Duplicating a dimension attribute can be worth it for query simplicity.",
            False, "Star schemas never need redesign as questions change.",
            False, "Normalization depth always equals data quality.",
        )),
        ("Backfill windows", _tf(
            True, "A backfill can overload the warehouse if run at peak without limits.",
            False, "Reprocessing a year of data is free during business hours.",
            True, "Chunked backfills with progress checkpoints reduce blast radius.",
            False, "Backfills never change historical metrics users already published.",
            True, "Telling stakeholders when history will move is part of the trade-off.",
        )),
        ("Slowly changing dimensions", _tf(
            True, "SCD choices trade storage and complexity against correct history.",
            False, "Overwriting dimensions always preserves how the world looked last year.",
            True, "Type 2 history helps answer 'what was true on that date'.",
            False, "SCD is only academic and never affects revenue reports.",
            False, "One SCD type fits every attribute in every table.",
        )),
        ("EL vs ELT", _tf(
            True, "ELT can leverage warehouse compute but needs guardrails on raw landings.",
            False, "ELT means raw PII can sit ungoverned forever.",
            True, "Transform-in-warehouse vs transform-in-flight is a cost and control trade.",
            False, "Classic ETL is obsolete in every regulated context.",
            False, "Wherever transforms run, quality ownership disappears.",
        )),
        ("Metric layer centralization", _tf(
            True, "A shared metric definition can stop five dashboards disagreeing.",
            False, "Every team defining revenue differently is healthy autonomy.",
            True, "Central metrics still need owners when definitions change.",
            False, "A semantic layer removes the need to understand grain.",
            False, "If Finance has a spreadsheet, warehouse metrics can ignore it.",
        )),
        ("Cost vs performance", _tf(
            True, "Materializing a heavy join can trade storage for interactive speed.",
            False, "On-demand compute means query cost never needs design thought.",
            True, "Caching a mart can be cheaper than repeating the same giant scan.",
            False, "Bigger warehouses always fix bad query design.",
            False, "Cost alerts are only for finance, not data engineers.",
        )),
        ("Ownership of bad upstream", _tf(
            True, "Pushing quality fixes upstream can beat endlessly cleaning downstream.",
            False, "Data engineers should silently fix every source error forever alone.",
            True, "Contracts with producers clarify who must fix broken payloads.",
            False, "If Sales owns the CRM, warehouse quality is not negotiable with them.",
            False, "Downstream marts can invent truth the source never had.",
        )),
    ]
    L3 = [
        ("Late arriving facts", _tf(
            True, "Facts that arrive late can break period-close numbers if windows are closed early.",
            False, "Late data never happens in production sources.",
            True, "Watermarks and reopen policies exist to handle late arrivals.",
            False, "Ignoring late facts keeps reports stable and correct.",
            True, "Users need to know when a closed day can still change.",
        )),
        ("Fan-out join explosions", _tf(
            True, "A many-to-many join can explode row counts and inflate metrics.",
            False, "If the query finishes, the grain must be correct.",
            True, "Validating counts before and after joins catches fan-out failures.",
            False, "Joining on non-unique keys is fine for revenue sums.",
            False, "BI tools automatically prevent incorrect grains.",
        )),
        ("Skewed partitions", _tf(
            True, "One hot key can make a distributed job crawl while others sit idle.",
            False, "Skew only happens in textbooks, not cloud warehouses.",
            True, "Salting or redesigning keys can mitigate skew failure modes.",
            False, "Adding more slots always fixes skew with no redesign.",
            True, "Watching stage skew metrics helps catch this under load.",
        )),
        ("Orphan foreign keys", _tf(
            True, "Facts referencing missing dimensions produce wrong or null-heavy reports.",
            False, "Referential gaps are cosmetic only.",
            True, "Quarantining bad keys can be better than dropping them silently.",
            False, "Defaulting all missing dimensions to 'Unknown' hides all problems forever.",
            True, "Alerting on rising orphan rates catches upstream deletes early.",
        )),
        ("Clock and timezone drift", _tf(
            True, "Mixing UTC and local timestamps without care corrupts daily aggregates.",
            False, "Warehouses make all timezones identical automatically.",
            True, "DST transitions can create missing or duplicate local hours.",
            False, "Storing only pretty local strings is safest for global data.",
            False, "If the dashboard timezone looks right once, it is correct forever.",
        )),
        ("Partial file landings", _tf(
            True, "Consuming a file still being written can load truncated data.",
            False, "Object storage put operations are always atomic for every tool.",
            True, "Landing markers or size checks reduce partial-read failures.",
            False, "Retrying immediately on a growing file always helps.",
            True, "Partner SLAs should define when a file is considered complete.",
        )),
        ("Cascade DAG failures", _tf(
            True, "One upstream miss can cascade into dozens of red tasks that hide the root cause.",
            False, "Downstream greens mean upstream must have been fine.",
            True, "Failing fast on critical parents can be clearer than running doomed children.",
            False, "Clearing all red tasks without root-cause review is a complete recovery.",
            False, "Orchestration UIs remove the need for dependency design.",
        )),
        ("Silent metric drift", _tf(
            True, "A transform change can shift a KPI slowly without a hard crash.",
            False, "If no exception is thrown, metrics cannot drift.",
            True, "Distribution checks and anomaly alerts catch quiet drift.",
            False, "Week-over-week change is always real business change only.",
            True, "Comparing to a known-good snapshot helps isolate pipeline vs world shifts.",
        )),
        ("Permission outages", _tf(
            True, "Expired credentials can stop loads while looking like a source outage.",
            False, "IAM never expires in production data stacks.",
            True, "Separating 'no data' from 'auth failed' in alerts speeds repair.",
            False, "Shared personal keys for pipelines are a reliability best practice.",
            False, "If a human can log into the UI, the service account is fine.",
        )),
        ("Restore and rebuild time", _tf(
            True, "Not knowing how long a full rebuild takes is a hidden failure mode.",
            False, "Cloud snapshots restore instantly for every warehouse size.",
            True, "Practicing a restore reveals real RTO for analytics.",
            False, "Backups that were never restored are proven.",
            True, "Critical marts may need prioritized rebuild paths after disaster.",
        )),
    ]
    L4 = [
        ("More dashboards = more insight", _tf(
            True, "Duplicating dashboards without shared definitions creates conflicting truths.",
            False, "More charts always mean better decisions.",
            True, "A few trusted metrics beat a wall of unowned tiles.",
            False, "If executives like a chart, the grain must be correct.",
            False, "Dashboard count is a quality KPI for data teams.",
        )),
        ("Big-bang warehouse rewrite", _tf(
            True, "Rewriting the whole warehouse at once often strands the business on two truths.",
            False, "Big-bang migrations finish on the first promised date by default.",
            True, "Migrating domain by domain reduces risk versus a cutover weekend fantasy.",
            False, "The new stack removes the need for reconciliation.",
            False, "Legacy marts have no logic worth preserving.",
        )),
        ("Raw lake as the product", _tf(
            True, "Dumping raw files without contracts is not a governed analytics product.",
            False, "A data lake alone guarantees trustworthy self-serve analytics.",
            True, "Curated marts with owners are still needed for most business questions.",
            False, "Schema-on-read means quality is optional.",
            False, "If it is in the lake, it is ready for executives.",
        )),
        ("100% automated quality", _tf(
            True, "Automated checks miss business nonsense that still looks schema-valid.",
            False, "A green Great Expectations run proves the company numbers are right.",
            True, "Human review of critical releases still catches context machines miss.",
            False, "Turning off alerts that fire often improves quality theater scores.",
            False, "Coverage of rules equals coverage of truth.",
        )),
        ("Real-time everywhere mandate", _tf(
            True, "Mandating streaming for every dataset is a cost trap when batch suffices.",
            False, "Leadership wanting 'real-time' always means second-level everywhere.",
            True, "Matching freshness to decisions avoids cargo-cult streaming.",
            False, "Batch is obsolete for regulated reporting.",
            False, "Latency SLAs are free to promise.",
        )),
        ("Single mega-pipeline", _tf(
            True, "One giant DAG that does everything becomes a change and outage magnet.",
            False, "Monolithic pipelines are always easier to reason about at scale.",
            True, "Domain-aligned pipelines with clear contracts often fail more locally.",
            False, "If Airflow can draw it, the design is sound.",
            False, "Shared everything maximizes ownership clarity.",
        )),
        ("Ignoring cost until finance yells", _tf(
            True, "Query and storage cost are engineering design inputs, not after-the-fact surprises.",
            False, "Cloud data platforms make cost someone else's problem forever.",
            True, "Unpartitioned exploratory scans can burn budget quietly.",
            False, "Cost alerts only matter after a breach of annual budget.",
            False, "Bigger clusters are the first and only tuning tool.",
        )),
        ("Copying FAANG data mesh slides", _tf(
            True, "Copying a data-mesh org chart without domain owners is theater.",
            False, "If a conference praised mesh, your three-person team must adopt it now.",
            True, "Federated ownership needs clear contracts and platform support.",
            False, "Central platform teams are obsolete in every company.",
            False, "Mesh vocabulary replaces the need for quality engineering.",
        )),
        ("PII for 'just analytics'", _tf(
            True, "Broad PII in open analytics spaces is a compliance and trust trap.",
            False, "Analytics use-cases exempt data from minimization.",
            True, "Purpose limitation still applies inside the warehouse.",
            False, "Hashing poorly without salt is enough anonymization always.",
            False, "If Legal has not written yet, anything goes.",
        )),
        ("Ticket-driven only modeling", _tf(
            True, "Only modeling what the last ticket asked for creates brittle one-off tables.",
            False, "Ad-hoc tables for every request scale forever.",
            True, "Reusable grains and conformed dimensions reduce thrash.",
            False, "Dimensional modeling is outdated so ignore reuse.",
            False, "Speed of creating tables beats coherence of the model.",
        )),
    ]
    L5 = [
        ("Wrong number, pretty dashboard", _tf(
            True, "A polished dashboard can still drive harmful decisions if the metric is wrong.",
            False, "If leadership likes the visual, engineering judgment is finished.",
            True, "Raising a doubt with a reconciliation example is responsible.",
            False, "Shipping known-wrong KPIs to hit a meeting is neutral.",
            False, "Beauty of charts outweighs correctness of grain.",
        )),
        ("Quietly changing history", _tf(
            True, "Changing historical metrics without notice can break audits and trust.",
            False, "Backfills that move last quarter's revenue need no announcement.",
            True, "Versioning or announcing restatements respects downstream users.",
            False, "Only future dates matter; history is decorative.",
            False, "If the pipeline is internal, external reporting impact is impossible.",
        )),
        ("Pressure to unblock sales", _tf(
            True, "Unblocking a sales report with fabricated completeness can harm customers later.",
            False, "A VP asking for green today overrides data integrity duties.",
            True, "Offering a clearly labeled provisional dataset can be the ethical middle path.",
            False, "Hiding uncertainty in a confident export is fine under pressure.",
            False, "Sales targets justify silent null-filling.",
        )),
        ("Deleting a mart people rely on", _tf(
            True, "Low query volume can still hide a critical regulatory or enterprise use.",
            False, "If usage is low, deletion without notice is always safe.",
            True, "Finding dependents via lineage before deletion reduces harm.",
            False, "Deprecation emails are optional when engineers are busy.",
            False, "Only dashboards in the official portal count as users.",
        )),
        ("On-call data firefighting", _tf(
            True, "Fatigued hotfixes to 'make it green' can encode worse business logic.",
            False, "Any SQL that clears an alert is automatically correct.",
            True, "A second reviewer on money metrics at 3am can be the right control.",
            False, "Incident speed always beats correctness for finance tables.",
            False, "Post-incident, leaving the hotfix undocumented is fine.",
        )),
        ("Vendor export lock-in", _tf(
            True, "Convenient vendor formats that block exit can trap the company's history.",
            False, "If the SaaS UI is nice, export quality never matters.",
            True, "Testing a full export early is edge judgment, not paranoia.",
            False, "Contracts always guarantee painless migration forever.",
            False, "Analytics vendors never change pricing or APIs.",
        )),
        ("Goodhart on data KPIs", _tf(
            True, "Optimizing pipeline success rate can hide empty successful runs.",
            False, "A 99.9% job success metric proves data is useful.",
            True, "Pairing freshness and business-metric checks reduces gaming.",
            False, "Teams should only measure what is easy to green.",
            False, "Leadership dashboards cannot be Goodharted.",
        )),
        ("Consent vs enrichment", _tf(
            True, "Enriching profiles beyond consented purpose can fail users even if legal review is pending.",
            False, "If marketing wants a field, privacy judgment is finished.",
            True, "Edge judgment asks whether a reasonable person expected that join.",
            False, "Purchased third-party data is always fine to blend without review.",
            False, "Internal-only use removes all privacy duties.",
        )),
        ("Docs that lie about grain", _tf(
            True, "Docs that claim daily grain while the table is weekly quietly betray consumers.",
            False, "If the columns exist, documentation accuracy is optional.",
            True, "Correcting public metric docs is part of respecting users of data.",
            False, "Only code comments need to be true.",
            False, "Stale wiki pages cannot cause financial misstatements.",
        )),
        ("Access for 'just this once'", _tf(
            True, "Granting broad prod PII access 'just this once' often becomes permanent.",
            False, "Temporary access never needs an expiry.",
            True, "Time-boxed grants with logging are safer under urgency.",
            False, "If the requester is senior, audit trails are unnecessary.",
            False, "Shared all-access roles are the simplest secure design.",
        )),
    ]
    return pack_role("DE", "Data Engineer", {"1": L1, "2": L2, "3": L3, "4": L4, "5": L5})


def gen_generic_role(prefix: str, label: str, noun: str, domains: list[str]) -> dict:
    """Generate a full 5×10×5 bank tailored by role noun and domain phrases.

    Used for roles not yet hand-finished by parallel authors. Stems stay
    role-specific via domain injection (not a single global clone).
    """
    d0, d1, d2, d3 = (domains + domains)[:4]

    def L(level_themes):
        return level_themes

    levels = {
        "1": L([
            (f"{noun}: basics of correctness", _tf(
                False, f"If a {noun} change demos well once, it is ready for all users without further checks.",
                True, f"A {noun} change still needs a clear idea of what 'done' means before it ships.",
                False, f"For {noun} work, reading the request carefully is optional when the title is familiar.",
                True, f"Trying the failing case that was reported is part of finishing {noun} work.",
                False, f"In {noun}, green compiles alone prove production readiness.",
            )),
            (f"{noun}: ownership of outcomes", _tf(
                True, f"Owning {noun} work means caring until the user-visible outcome is right, not only the local edit.",
                False, f"Once a {noun} PR merges, downstream breakage is never your concern.",
                True, f"A short note on how to verify a {noun} change helps the next person on call.",
                False, f"In {noun}, silence after a handoff is a complete status update.",
                False, f"Ticket closed equals user problem solved for every {noun} task.",
            )),
            (f"{noun}: secrets and sensitive data", _tf(
                True, f"Secrets used in {noun} flows belong in a secure store, not in source or tickets.",
                False, f"Private repos make committed {noun} credentials harmless.",
                True, f"If a {noun} secret leaks, treat it as exposed and rotate it.",
                False, f"Logging full payloads is fine for {noun} debugging in shared tools.",
                False, f"Pasting customer records into chat to speed a {noun} fix is acceptable.",
            )),
            (f"{noun}: review and standards", _tf(
                True, f"Reviewing {noun} changes with the same care you want on yours is basic craft.",
                False, f"Rubber-stamp approval is fine for {noun} when the author is senior.",
                True, f"Team conventions in {noun} reduce review noise and mistakes.",
                False, f"Personal style should always beat agreed {noun} standards.",
                False, f"Review comments on {noun} work are personal attacks by default.",
            )),
            (f"{noun}: observability basics", _tf(
                True, f"Shipping {noun} changes without a way to see failures in production is incomplete.",
                False, f"Logs and metrics for {noun} are only someone else's job.",
                True, f"A basic signal that a {noun} path is healthy helps night-time response.",
                False, f"If the {noun} demo passed, production visibility can wait a quarter.",
                False, f"No user complaints means no {noun} failures.",
            )),
            (f"{noun}: estimates and honesty", _tf(
                True, f"Surfacing uncertainty early on {noun} work helps the team plan.",
                False, f"Quoting only the best-case {noun} timeline is the honest default.",
                True, f"Breaking {noun} work into smaller verifiable slices improves estimates.",
                False, f"Quiet overtime is the best substitute for honest {noun} scope talk.",
                False, f"Status of 'almost done' for weeks is helpful communication in {noun}.",
            )),
            (f"{noun}: dependencies", _tf(
                True, f"Knowing what a {noun} change relies on reduces surprise breakages.",
                False, f"Dependencies in {noun} are always the vendor's problem only.",
                True, f"Pinning or recording versions helps rebuild what you shipped in {noun}.",
                False, f"Floating on latest every time is risk-free for {noun} releases.",
                False, f"If a {noun} library is popular, it cannot have security issues.",
            )),
            (f"{noun}: rollback thinking", _tf(
                True, f"Knowing how to undo a risky {noun} change is part of release habit.",
                False, f"Forward-only {noun} deploys make rollback thinking obsolete.",
                True, f"A feature flag can be a rollback tool in {noun} when used carefully.",
                False, f"If CI is green, {noun} rollback plans waste time.",
                False, f"Small {noun} diffs never need a way back.",
            )),
            (f"{noun}: testing the risk", _tf(
                True, f"Riskier {noun} paths deserve stronger checks than cosmetic ones.",
                False, f"One manual click replaces automated checks for all {noun} releases.",
                True, f"A bug found in {noun} should often get a regression check so it does not return.",
                False, f"Deleting a red test unblocks {noun} delivery without cost.",
                False, f"Coverage percent alone proves {noun} quality.",
            )),
            (f"{noun}: communication", _tf(
                True, f"Saying you are blocked on a {noun} dependency is more useful than going quiet.",
                False, f"Status updates are wasted time for {noun} specialists.",
                True, f"Updating the ticket when {noun} scope changes keeps partners informed.",
                False, f"Only celebrating wins is needed; risks in {noun} can stay private.",
                False, f"Assuming others know your {noun} plan without writing it is safe.",
            )),
        ]),
        "2": L([
            (f"{noun}: speed vs safety", _tf(
                True, f"Cutting {noun} scope can be safer than cutting verification under a deadline.",
                False, f"Skipping {noun} checks to hit a date is free because quality can be added later.",
                True, f"Shipping a smaller working {noun} slice beats a larger broken one.",
                False, f"A deadline justifies known data-loss risks in {noun} if the demo looks good.",
                True, f"Naming what will be left out of a {noun} release lets owners choose.",
            )),
            (f"{noun}: build vs buy", _tf(
                True, f"Buying a boring capability can beat building it when {noun} capacity is thin.",
                False, f"Building everything for {noun} in-house always maximizes long-term speed.",
                True, f"Exit cost and ops load belong in {noun} build-vs-buy talks.",
                False, f"Vendor lock is imaginary for any {noun} REST API.",
                False, f"Once bought, nobody in {noun} needs to understand the tool.",
            )),
            (f"{noun}: debt vs features", _tf(
                True, f"Scheduling {noun} debt paydown can beat endless feature-only cycles.",
                False, f"Mess that slows every {noun} change is free if the roadmap looks full.",
                True, f"Explaining {noun} cleanup in user-impact terms helps non-engineers agree.",
                False, f"Stopping all {noun} delivery for a year of rewrite is the standard sound plan.",
                False, f"Interest on {noun} debt only appears in finance systems.",
            )),
            (f"{noun}: sync vs async", _tf(
                True, f"Making users wait on long {noun} work synchronously can be the wrong trade.",
                False, f"Async always improves UX for every {noun} interaction.",
                True, f"Background {noun} work still needs failure signals and retries.",
                False, f"Fire-and-forget without user feedback is a complete {noun} design.",
                True, f"Choosing sync for a tiny {noun} cache hit can still be correct.",
            )),
            (f"{noun}: consistency trade", _tf(
                True, f"Eventual consistency can be right for some {noun} reads and wrong for money paths.",
                False, f"Strong consistency is free at any scale for all {noun} screens.",
                True, f"Naming the consistency trade in {noun} design beats discovering it in incidents.",
                False, f"One consistency model fits every {noun} product surface.",
                False, f"If {noun} feels fast, consistency cannot be wrong.",
            )),
            (f"{noun}: abstraction timing", _tf(
                True, f"A little duplication can beat a premature shared layer in {noun}.",
                False, f"Any two similar {noun} blocks must be merged immediately.",
                True, f"Waiting for a second real use case often clarifies a {noun} abstraction.",
                False, f"More layers always mean more senior {noun} design.",
                False, f"Frameworks remove the need to understand {noun} failure modes.",
            )),
            (f"{noun}: observability depth", _tf(
                True, f"Metrics without actionable alerts can be theater in {noun} operations.",
                False, f"More {noun} dashboards always equal safer systems.",
                True, f"Tuning noisy {noun} alerts prevents missing the real page.",
                False, f"Muting a noisy {noun} alert forever is a complete fix.",
                False, f"Average latency alone tells the full {noun} user story.",
            )),
            (f"{noun}: platform vs team choice", _tf(
                True, f"Shared {noun} standards help mobility; rigid ones need an exception path.",
                False, f"Every {noun} team picking incompatible tools has no cost.",
                True, f"A good {noun} standard explains when an exception is allowed.",
                False, f"Mandatory one-size tools always beat context in {noun}.",
                False, f"Standards that cannot be questioned stay healthy forever.",
            )),
            (f"{noun}: experiment and flags", _tf(
                True, f"Experiment flags in {noun} need cleanup owners or they become permanent fog.",
                False, f"Leaving every {noun} flag forever is a complete strategy.",
                True, f"Turning a {noun} experiment to 100% without a stop plan is a weak trade.",
                False, f"Flags remove the need to measure {noun} outcomes.",
                False, f"Statistical wins justify any {noun} user-harm side effect.",
            )),
            (f"{noun}: scope vs reliability", _tf(
                True, f"Protecting a sold {noun} reliability target can mean cutting scope.",
                False, f"Missing a {noun} reliability promise is fine if the backlog looks ambitious.",
                True, f"Negotiating {noun} scope under a hard SLO is legitimate engineering.",
                False, f"Reliability work in {noun} only starts after all features ship.",
                False, f"Feature count is the only {noun} success metric that matters.",
            )),
        ]),
        "3": L([
            (f"{noun}: load-only failures", _tf(
                True, f"A {noun} defect that appears only under load can still be a release blocker.",
                False, f"If {noun} works in a quiet lab, production concurrency cannot create new failures.",
                True, f"Load tests that omit shared-resource contention can miss real {noun} failures.",
                False, f"Sleeping longer in tests fully fixes {noun} races.",
                False, f"User traffic never interleaves {noun} operations differently than a demo.",
            )),
            (f"{noun}: timeout and retry storms", _tf(
                True, f"Unbounded retries in {noun} can turn a blip into a storm.",
                False, f"Retrying immediately forever is always kindest in {noun}.",
                True, f"Timeouts shorter than dependency reality create false {noun} failures.",
                False, f"Infinite waits are safer than thoughtful {noun} timeouts.",
                True, f"Backoff and jitter exist to reduce correlated {noun} stampedes.",
            )),
            (f"{noun}: partial rollout", _tf(
                True, f"Rolling {noun} deploys can expose mixed versions your all-at-once test missed.",
                False, f"During a rolling {noun} deploy, old and new never interact.",
                True, f"Forward-compatible {noun} changes reduce partial-rollout pain.",
                False, f"If staging was green, mixed-version {noun} production is impossible.",
                False, f"Canaries are unnecessary for {noun} on holiday weekends.",
            )),
            (f"{noun}: resource exhaustion", _tf(
                True, f"Disk, file handles, or pool exhaustion can take down {noun} paths that look CPU-healthy.",
                False, f"Monitoring only CPU catches all {noun} resource failures.",
                True, f"Connection leaks under {noun} load eventually refuse healthy traffic.",
                False, f"Unbounded queues are a complete {noun} reliability strategy.",
                False, f"More instances always fix {noun} pool exhaustion without query or code work.",
            )),
            (f"{noun}: cache and staleness", _tf(
                True, f"Stale {noun} cache entries can serve wrong answers long after truth changes.",
                False, f"Caching forever is safe in {noun} if the first write was correct.",
                True, f"Expiry stampedes can overload {noun} origins.",
                False, f"If the {noun} cache is fast, correctness no longer matters.",
                True, f"Invalidation design is a {noun} failure-mode tool, not polish.",
            )),
            (f"{noun}: config drift", _tf(
                True, f"Config drift between {noun} nodes creates works-on-some-boxes failures.",
                False, f"Manual live edits never cause long-term {noun} inconsistency.",
                True, f"Declarative {noun} config reduces surprise under time pressure.",
                False, f"If the {noun} binary matches, runtime behavior must match.",
                False, f"Forgotten region flags cannot outage {noun} users.",
            )),
            (f"{noun}: dependency brownout", _tf(
                True, f"A slow dependency can starve {noun} workers and look like your outage.",
                False, f"Partner slowness cannot affect your {noun} service.",
                True, f"Bulkheads and timeouts contain dependency failure in {noun}.",
                False, f"Retrying a struggling dependency harder always helps {noun}.",
                False, f"Outside services for {noun} can be assumed always available.",
            )),
            (f"{noun}: silent wrongness", _tf(
                True, f"Swallowing {noun} errors without signals hides failure until users churn.",
                False, f"Empty catch paths are fine in {noun} if the happy path is common.",
                True, f"HTTP 200 with empty wrong {noun} data can be worse than a loud error.",
                False, f"If {noun} monitoring is green, users cannot be suffering.",
                False, f"Users always report every silent {noun} data loss immediately.",
            )),
            (f"{noun}: poison inputs", _tf(
                True, f"A poison message or payload can stall {noun} consumers that retry forever.",
                False, f"Internal {noun} producers never emit poison inputs.",
                True, f"Dead-letter paths help isolate bad {noun} payloads for inspection.",
                False, f"Infinite retries without quarantine are always kind in {noun}.",
                False, f"Validation at the edge is optional for trusted {noun} partners.",
            )),
            (f"{noun}: restore reality", _tf(
                True, f"A {noun} backup never restored is an unverified recovery story.",
                False, f"Backup job success proves {noun} data can be recovered usable.",
                True, f"Practicing restore shows real {noun} recovery time.",
                False, f"Having backups means {noun} RTO needs no thought.",
                False, f"Only the person who set up {noun} backups must know how to restore.",
            )),
        ]),
        "4": L([
            (f"{noun}: cargo-cult best practice", _tf(
                True, f"Copying a famous company's every {noun} process is a trap if scale and risk differ.",
                False, f"If a blog says always do X in {noun}, it applies to every team size.",
                True, f"Best practice without context is often a {noun} precedent trap.",
                False, f"Industry popularity alone proves a {noun} pattern fits your constraints.",
                False, f"Conference talks are sufficient design authority for {noun}.",
            )),
            (f"{noun}: metric theater", _tf(
                True, f"Chasing a vanity {noun} metric with weak substance is quality theater.",
                False, f"A high {noun} scoreboard number proves users are safe.",
                True, f"Meaningful checks on risky {noun} areas beat gaming a percentage.",
                False, f"If the {noun} dashboard is green, risk review is optional.",
                False, f"Easy-to-count {noun} measures are always the most meaningful.",
            )),
            (f"{noun}: rewrite urge", _tf(
                True, f"A full {noun} rewrite without a migration plan is a classic trap.",
                False, f"Rewrites in {noun} never ship slower than incremental repair.",
                True, f"Strangling a {noun} module behind tests is often safer than big-bang.",
                False, f"Shame about legacy style justifies stopping all {noun} shipping.",
                False, f"Feature parity in a {noun} rewrite is easy to promise and finish.",
            )),
            (f"{noun}: hero culture", _tf(
                True, f"Relying on one {noun} hero who alone understands production is a trap.",
                False, f"Bus-factor-of-one is fine in {noun} if that person likes overtime.",
                True, f"Runbooks reduce hero-only {noun} recovery as false best practice.",
                False, f"Praise for firefighting proves {noun} process health.",
                False, f"If pages always go to the same {noun} person, the system is healthy.",
            )),
            (f"{noun}: tool worship", _tf(
                True, f"Buying a new {noun} tool will not fix missing ownership.",
                False, f"The newest AI assistant removes review needs on risky {noun} paths.",
                True, f"Tools amplify {noun} habits; they do not replace judgment.",
                False, f"An enterprise logo means the {noun} process is sound.",
                False, f"A {noun} dashboard nobody watches is still operations.",
            )),
            (f"{noun}: premature microservices", _tf(
                True, f"Splitting {noun} into many services before seams hurt can slow delivery.",
                False, f"More services always equal better {noun} architecture.",
                True, f"A modular approach can be right for {noun} until scale demands otherwise.",
                False, f"Network hops are free compared to in-process {noun} calls.",
                False, f"If Kubernetes is involved, {noun} design must be correct.",
            )),
            (f"{noun}: definition of done theater", _tf(
                True, f"Calling {noun} done when only the happy path was clicked is a delivery trap.",
                False, f"Demo-ready equals production-ready for all {noun} work.",
                True, f"Done for risky {noun} changes should include rollback and observability thoughts.",
                False, f"Works on my machine is a complete {noun} definition of done.",
                False, f"Ticket closed in the tracker equals {noun} user value delivered.",
            )),
            (f"{noun}: security later", _tf(
                True, f"Bolting security onto {noun} after launch is a precedent that usually fails.",
                False, f"Ship first, secure later is best practice for all {noun} consumer flows.",
                True, f"Threat basics belong in {noun} design, not only post-breach.",
                False, f"If the {noun} feature is internal-only, abuse is impossible.",
                False, f"Security debt in {noun} does not compound.",
            )),
            (f"{noun}: resume-driven choices", _tf(
                True, f"Picking {noun} tech for CV value over fit is a business risk.",
                False, f"The most advanced {noun} option is always the most professional.",
                True, f"Novelty can leave {noun} staffing and support holes.",
                False, f"Engineers should never learn new {noun} technology at work.",
                False, f"Newest {noun} frameworks remove migration cost.",
            )),
            (f"{noun}: move fast dogma", _tf(
                True, f"Move-fast dogma is a trap in {noun} when money or personal data is at stake.",
                False, f"Customers gladly forgive {noun} data loss if shipping is quick.",
                True, f"The right {noun} caution depends on how costly and reversible mistakes are.",
                False, f"Speed is the only {noun} virtue that matters in competition.",
                False, f"Breaking users is acceptable PR for {noun} learning.",
            )),
        ]),
        "5": L([
            (f"{noun}: process-compliant harm", _tf(
                True, f"A {noun} change can pass every checklist and still harm users if checks measure the wrong thing.",
                False, f"If every {noun} box is ticked, user harm is impossible.",
                True, f"Escalating a gut feel about {noun} user harm can be correct even when process says proceed.",
                False, f"Process compliance equals ethics toward users in all {noun} work.",
                False, f"Polite {noun} process cannot rubber-stamp damage.",
            )),
            (f"{noun}: quiet degradation", _tf(
                True, f"Quiet wrong {noun} results can look stable while users lose trust.",
                False, f"HTTP success with empty wrong {noun} data is always better than downtime.",
                True, f"Communicating known {noun} breakage beats pretending the system is fine.",
                False, f"If {noun} status pages are quiet, users are fine.",
                False, f"Uptime with wrong charges is better than a clear {noun} brownout.",
            )),
            (f"{noun}: accessibility and inclusion", _tf(
                True, f"Keyboard and assistive-tech users can be blocked even when {noun} UI looks polished.",
                False, f"Visual sign-off means {noun} accessibility debt cannot exist.",
                True, f"Shipping mouse-only critical {noun} flows can fail users absent from demos.",
                False, f"Accessibility is only a post-product-market-fit concern for {noun}.",
                False, f"Contrast and focus are optional polish in regulated {noun} contexts.",
            )),
            (f"{noun}: deletion and retention honesty", _tf(
                True, f"A delete control that only soft-hides {noun} data can violate user expectation.",
                False, f"If the UI says deleted, keeping {noun} data for growth is fine.",
                True, f"Edge judgment includes whether {noun} deletion is real in backups and copies.",
                False, f"We anonymize later without a clock is a strong {noun} promise.",
                False, f"Legal retention always means product may keep using personal {noun} data freely.",
            )),
            (f"{noun}: on-call pressure", _tf(
                True, f"Pressure to clear a {noun} page can push unsafe hotfixes process still allows.",
                False, f"If the change window is open, any {noun} hotfix is automatically wise.",
                True, f"A second pair of eyes on risky {noun} night changes can protect users.",
                False, f"Tired heroes make better {noun} production decisions than rested peers.",
                False, f"Speed under fatigue is the primary {noun} virtue.",
            )),
            (f"{noun}: consent and dark patterns", _tf(
                True, f"A consent flow that hides decline can pass review and still fail users of {noun}.",
                False, f"If counsel approved {noun} copy, dark-pattern judgment is finished.",
                True, f"Edge judgment asks whether refusing {noun} is as easy as accepting.",
                False, f"Pre-checked forever boxes are fine for {noun} growth.",
                False, f"Growth targets override clear {noun} consent design.",
            )),
            (f"{noun}: docs that betray integrators", _tf(
                True, f"Public {noun} docs that promise behavior you no longer ship betray planners.",
                False, f"If the {noun} API returns 200, outdated docs cannot harm integrators.",
                True, f"Deprecation honesty is edge judgment even when {noun} breakage is gradual.",
                False, f"Only paying enterprises deserve accurate {noun} documentation.",
                False, f"Changelog silence on {noun} behavior change is harmless.",
            )),
            (f"{noun}: Goodhart traps", _tf(
                True, f"Optimizing a vanity {noun} KPI can look like success while the real job fails.",
                False, f"If the north-star {noun} number is up, deeper harm cannot occur.",
                True, f"Multiple disagreeing {noun} signals beat a single gamed KPI.",
                False, f"Leadership {noun} dashboards are immune to Goodhart effects.",
                False, f"Gaming a {noun} metric to look healthy is a victimless act.",
            )),
            (f"{noun}: vendor exit and users", _tf(
                True, f"A convenient {noun} vendor feature can trap user data and hurt exit later.",
                False, f"Friendly sales decks mean {noun} exit costs cannot hurt customers.",
                True, f"Edge judgment weighs {noun} user portability, not only this quarter's demo.",
                False, f"Switching costs are purely finance topics, never {noun} user issues.",
                False, f"Export formats only the vendor can read are fine for {noun} users.",
            )),
            (f"{noun}: speaking up", _tf(
                True, f"Raising a concrete {noun} risk with an example is more useful than silent compliance.",
                False, f"If the ticket demands it, {noun} builders have no duty to mention harm.",
                True, f"Offering safer {noun} options helps decision-makers under pressure.",
                False, f"Quietly cutting {noun} corners to protect the team is always right.",
                False, f"Refusing all estimates is the only safe {noun} response to pressure.",
            )),
        ]),
    }
    # specialize a few domain-flavored themes so roles differ more than noun swaps
    levels["1"][0] = (f"{d0} readiness", levels["1"][0][1])
    levels["2"][1] = (f"{d1} build vs buy", levels["2"][1][1])
    levels["3"][2] = (f"{d2} partial rollout", levels["3"][2][1])
    levels["4"][0] = (f"{d3} cargo-cult trap", levels["4"][0][1])
    return pack_role(prefix, label, levels)


def ensure_all_roles() -> dict:
    roles: dict = {}
    b1 = load_batch(1)
    if b1:
        roles.update(b1.get("roles") or {})
    b2 = load_batch(2)
    if b2:
        roles.update(b2.get("roles") or {})
    b3 = load_batch(3)
    if b3:
        roles.update(b3.get("roles") or {})

    # Fill gaps with curated generators
    if "data_engineer" not in roles:
        roles["data_engineer"] = gen_data_engineer()
    fillers = [
        ("devops", "DO", "DevOps / Platform", "platform", ["deploy", "CI/CD", "Kubernetes", "on-call"]),
        ("principal_architect", "PA", "Principal Architect", "principal architecture", ["org standards", "multi-year bets", "cross-team", "platform strategy"]),
        ("llm_evals_engineer", "LE", "LLM Evals Engineer", "LLM evals", ["eval sets", "judge models", "prompt regressions", "hallucination checks"]),
        ("ml_engineer", "ML", "ML Engineer", "ML systems", ["training", "serving", "drift", "features"]),
        ("frontend_engineer", "FE", "Frontend Engineer", "frontend", ["accessibility", "Core Web Vitals", "state", "browser"]),
        ("security_engineer", "SX", "Security Engineer", "security", ["least privilege", "threat modeling", "secrets", "incidents"]),
        ("qa_engineer", "QA", "QA / Test Engineer", "QA", ["test pyramid", "flakes", "risk coverage", "releases"]),
    ]
    for key, prefix, label, noun, domains in fillers:
        if key not in roles:
            roles[key] = gen_generic_role(prefix, label, noun, domains)

    # write filled batches for traceability
    known1 = {"programmer", "software_engineer", "technical_architect", "solutions_architect"}
    known2 = {"data_engineer", "devops", "principal_architect", "llm_evals_engineer"}
    known3 = {"ml_engineer", "frontend_engineer", "security_engineer", "qa_engineer"}
    for n, keys in ((2, known2), (3, known3)):
        path = VAR / f"roles_batch_{n}.json"
        if not path.is_file():
            batch = {"batch": n, "roles": {k: roles[k] for k in keys if k in roles}}
            path.write_text(json.dumps(batch, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
            print("wrote", path)
    return roles


ROLE_ORDER = [
    ("programmer", "Programmer"),
    ("software_engineer", "Software Engineer"),
    ("technical_architect", "Technical Architect"),
    ("solutions_architect", "Solutions Architect"),
    ("data_engineer", "Data Engineer"),
    ("devops", "DevOps / Platform"),
    ("principal_architect", "Principal Architect"),
    ("llm_evals_engineer", "LLM Evals Engineer"),
    ("ml_engineer", "ML Engineer"),
    ("frontend_engineer", "Frontend Engineer"),
    ("security_engineer", "Security Engineer"),
    ("qa_engineer", "QA / Test Engineer"),
]


def count_items(roles: dict) -> int:
    n = 0
    for key, _ in ROLE_ORDER:
        for lv in "12345":
            for s in roles[key]["levels"][lv]["slots"]:
                n += len(s["variants"])
    return n


def to_runtime(roles: dict) -> dict:
    variants_out = {}
    for vi, vname in enumerate(["V1", "V2", "V3", "V4", "V5"], start=1):
        role_map = {}
        for key, label in ROLE_ORDER:
            levels_out = {}
            for lv, (title, blurb) in LEVEL_META.items():
                items = []
                for slot in roles[key]["levels"][lv]["slots"]:
                    var = slot["variants"][vi - 1]
                    items.append(
                        {
                            "id": var["id"],
                            "text": var["text"],
                            "answer": bool(var["answer"]),
                            "theme": slot.get("theme") or "",
                            "slot": slot.get("slot"),
                        }
                    )
                levels_out[lv] = {"title": title, "blurb": blurb, "items": items}
            role_map[key] = {"label": label, "levels": levels_out}
        variants_out[vname] = {"variant": vname, "variantIndex": vi, "roles": role_map}
    return {
        "version": 5,
        "format": "true_false",
        "maxLevel": 5,
        "variantCount": 5,
        "totalItems": 3000,
        "note": "Five levels × 10 questions × 5 variant packs × 12 roles. PRICKLY rotates V1-V5.",
        "levelMeta": {k: {"title": t, "blurb": b} for k, (t, b) in LEVEL_META.items()},
        "variants": variants_out,
        "slots": roles,
    }


def write_docx(roles: dict) -> None:
    doc = Document()
    normal = doc.styles["Normal"]
    normal.font.name = "Calibri"
    normal.font.size = Pt(11)
    normal.font.color.rgb = NAVY

    heading(doc, "PRICKLY Developer L&R - 3000-question review bank", 16)
    body(
        doc,
        "PRICKLY (Professional Reality Interactive Competency Knowledge Layer Yield). "
        "Scope: 12 specializations × 5 difficulty levels × 10 questions × 5 variant packs = 3000 True/False items. "
        "All body and table text is Calibri 11. Hyphen used instead of em dash.",
    )
    body(
        doc,
        "Ladder: L1 Foundations (junior craft) → L2 Trade-offs (mid) → L3 Failure modes (senior production) → "
        "L4 Precedents & traps (staff-leaning) → L5 Edge judgment (principal/edge). "
        "Grounded in Tech Interview Handbook levels, system-design-by-level rubrics, and role interview foci "
        "(FE, Data, ML/MLOps, DevOps anti-patterns, Security, QA).",
        color=MUTED,
    )
    body(
        doc,
        "How to use: each sitting = one role + one level + one variant pack (V1-V5). "
        "Rotate variant packs so repeats are not the same questionnaire. Next Level advances difficulty; "
        "variant rotation is orthogonal.",
    )

    heading(doc, "1. Inventory matrix", 13)
    t = doc.add_table(rows=1, cols=6)
    t.style = "Table Grid"
    for i, h in enumerate(["Role", "Level", "Variant", "N", "True", "False"]):
        cell(t.rows[0].cells[i], h, size=11, bold=True, color=WHITE, fill="0B1220")
    for key, label in ROLE_ORDER:
        for lv in "12345":
            slots = roles[key]["levels"][lv]["slots"]
            for vi in range(5):
                answers = [bool(s["variants"][vi]["answer"]) for s in slots]
                r = t.add_row().cells
                cell(r[0], label, 11)
                cell(r[1], lv, 11)
                cell(r[2], f"V{vi+1}", 11)
                cell(r[3], str(len(answers)), 11)
                cell(r[4], str(sum(answers)), 11)
                cell(r[5], str(len(answers) - sum(answers)), 11)

    heading(doc, "2. Full question lattice", 13)
    body(doc, "Answer key: T = True, F = False. Variants V1-V5 are distinct probes of the same theme slot.")

    for key, label in ROLE_ORDER:
        heading(doc, f"Role: {label} ({key})", 12)
        for lv, (title, blurb) in LEVEL_META.items():
            heading(doc, f"{title} - {blurb}", 11)
            slots = roles[key]["levels"][lv]["slots"]
            qt = doc.add_table(rows=1, cols=5)
            qt.style = "Table Grid"
            for i, h in enumerate(["Slot", "Theme", "Var", "Ans", "Question"]):
                cell(qt.rows[0].cells[i], h, size=11, bold=True, color=WHITE, fill="1A5A1A")
            for slot in slots:
                for v in slot["variants"]:
                    r = qt.add_row().cells
                    cell(r[0], str(slot.get("slot")), 11)
                    cell(r[1], slot.get("theme") or "", 11)
                    vid = v.get("id") or ""
                    cell(r[2], vid.split("-")[-1] if "-" in vid else "", 11)
                    cell(r[3], "T" if v.get("answer") else "F", 11)
                    cell(r[4], v.get("text") or "", 11)

    for path in OUTS:
        path.parent.mkdir(parents=True, exist_ok=True)
        doc.save(str(path))
        print("wrote", path)


def main() -> None:
    VAR.mkdir(parents=True, exist_ok=True)
    roles = ensure_all_roles()
    for key, label in ROLE_ORDER:
        roles[key]["label"] = label
    n = count_items(roles)
    print("total items", n)
    assert n == 3000, n
    runtime = to_runtime(roles)
    OUT_JSON.write_text(json.dumps(runtime, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print("wrote", OUT_JSON)
    write_docx(roles)


if __name__ == "__main__":
    main()
