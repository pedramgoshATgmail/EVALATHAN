#!/usr/bin/env python3
"""Rebuild PRICKLY Dev L&R banks to challenge grade (v6).

Fixes catastrophic packs where always-True scored ~90-100% because many
role×level×variant packs were 9-10/10 True (failure-mode lists with no myths).

Also hardens soft virtue stems and strips costume leaks.
Writes batches + runtime JSON version 6. Does not bump package version.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BATCH_DIR = ROOT / "ui" / "v2" / "assets" / "prickly_variants"
RUNTIME = ROOT / "ui" / "v2" / "assets" / "prickly-dev-banks-variants.json"
PRICKLY_JS = ROOT / "ui" / "v2" / "prickly.js"

LEVEL_META = {
    "1": ("Level 1 - Foundations", "Clear basics. Spot obvious false comfort."),
    "2": ("Level 2 - Trade-offs", "Two good-looking options; only one is sound."),
    "3": ("Level 3 - Failure modes", "What breaks under load, time, or bad incentives."),
    "4": ("Level 4 - Precedents & traps", "Industry-familiar traps dressed as best practice."),
    "5": ("Level 5 - Edge judgment", "Subtle cases where polite process still fails the user."),
}

ROLE_ORDER = [
    ("programmer", "Programmer", "PG"),
    ("software_engineer", "Software Engineer", "SE"),
    ("technical_architect", "Technical Architect", "TA"),
    ("solutions_architect", "Solutions Architect", "SA"),
    ("data_engineer", "Data Engineer", "DE"),
    ("devops", "DevOps / Platform", "DO"),
    ("principal_architect", "Principal Architect", "PA"),
    ("llm_evals_engineer", "LLM Evals Engineer", "LE"),
    ("ml_engineer", "ML Engineer", "ML"),
    ("frontend_engineer", "Frontend Engineer", "FE"),
    ("security_engineer", "Security Engineer", "SEC"),
    ("qa_engineer", "QA / Test Engineer", "QA"),
]

# Per variant index: desired True/False pattern across 10 slots (1=True, 0=False).
# Each sums to 5 so always-True scores 50% max by key balance alone; stems must still challenge.
PATTERNS = [
    [1, 0, 1, 0, 1, 0, 1, 0, 1, 0],  # V1
    [0, 1, 0, 1, 0, 1, 0, 1, 0, 1],  # V2
    [1, 1, 0, 0, 1, 0, 0, 1, 1, 0],  # V3
    [0, 0, 1, 1, 0, 1, 1, 0, 0, 1],  # V4
    [1, 0, 0, 1, 0, 1, 1, 0, 1, 0],  # V5
]

COSTUME = re.compile(
    r"\b(as a |the )?(programmer|software engineer|technical architect|"
    r"solutions architect|data engineer|devops|devops engineer|"
    r"principal architect|llm evals engineer|ml engineer|frontend engineer|"
    r"security engineer|qa engineer|qa / test engineer)s?\b[,:]?\s*",
    re.I,
)


def clean(text: str) -> str:
    t = text.replace("\u2014", "-").replace("\u2013", "-")
    t = COSTUME.sub("", t)
    # Drop stuffed role adjective prefixes like "security deploys" -> keep technical noun
    t = re.sub(
        r"\b(security|qa|ml|frontend|devops|data|llm)\s+(defect|deploys|cache|nodes|"
        r"workers|errors|consumers|backup|paths|pipeline|model|tests)\b",
        lambda m: m.group(2),
        t,
        flags=re.I,
    )
    return re.sub(r"\s+", " ", t).strip()


# Role -> level -> list of 10 themes, each theme is list of 5 (true_stem, false_stem)
# Variants pick true or false stem according to PATTERNS[vi][slot].
BANKS: dict[str, dict[str, list[tuple[str, list[tuple[str, str]]]]]] = {}


def T(true_s: str, false_s: str) -> tuple[str, str]:
    return (clean(true_s), clean(false_s))


def themes(*pairs: tuple[str, list[tuple[str, str]]]):
    assert len(pairs) == 10
    for name, vars_ in pairs:
        assert len(vars_) == 5, name
    return list(pairs)


def build_banks() -> None:
    """Populate BANKS with challenge-grade true/false stem pairs."""

    # -------- programmer --------
    BANKS["programmer"] = {
        "1": themes(
            ("readiness", [T(
                "A feature flag still needs a smoke check on the flagged path before broad enablement.",
                "If unit tests are green, a feature that only runs on the author laptop is ready for every customer.",
            ), T(
                "Matching production locale and dependency versions can change behavior even when a local demo passes.",
                "Customer machines can be treated as identical to the developer workstation for release decisions.",
            ), T(
                "An intermittent crash that appears once a week still needs a tracked repro before calling the release clean.",
                "Flaky failures that vanish on retry can be ignored forever if the dashboard stays green.",
            ), T(
                "Understanding a borrowed snippet that touches secrets is required even when the build is green.",
                "If a snippet worked for someone online, it automatically fits your threat model.",
            ), T(
                "A missing environment variable that exists only on one laptop is a release risk.",
                "Skipping a smoke check is acceptable when the diff is under ten lines and touches login.",
            )]),
            ("tests", [T(
                "A failing test that used to pass is a signal to investigate, not a reason to delete the assertion.",
                "Deleting a red test to unblock a release is fine if the feature demo looked good.",
            ), T(
                "Changing an assertion to match a bug is not the same as fixing the bug.",
                "If a test fails only on CI, the green laptop run is the source of truth.",
            ), T(
                "Quarantining a flake without a fix ticket is how flakes become permanent.",
                "Green coverage percent proves every important branch outcome was checked.",
            ), T(
                "Trying the exact reported broken case is part of finishing a fix.",
                "If the code compiles with no errors, it has been tested.",
            ), T(
                "Logging enough context to reproduce an intermittent bug is part of fixing it.",
                "Rare production crashes are acceptable if they never happened in a demo.",
            )]),
            ("naming_review", [T(
                "A public name that states intent reduces the chance of a wrong edit later.",
                "Short cryptic names are fine in hot paths because reviewers never read them.",
            ), T(
                "Tiny diffs that touch auth or money still deserve careful review.",
                "Line count alone is a reliable measure of review risk.",
            ), T(
                "Self-merging a one-line secret-handling change on a quiet Friday is still a risk.",
                "If a change is small, reviewing it is optional even when it touches passwords.",
            ), T(
                "Comments that only restate a bad name are not a substitute for fixing the name.",
                "Renaming a confusing public function is wasted work if the code already runs.",
            ), T(
                "Dead paths that still compile can confuse the next fix and hide real bugs.",
                "Keeping commented-out blocks for years is a valid substitute for version control history.",
            )]),
            ("api_time", [T(
                "Two writers saving the same record without concurrency control can overwrite each other.",
                "Storing local wall time with no time zone is fine for a service used across countries.",
            ), T(
                "An empty catch block can hide a production fault for months.",
                "If it runs on a laptop, it will run the same way in production.",
            ), T(
                "Loading every row into memory at once can crash when the table grows.",
                "Updating every library the moment a new version appears is always risk free.",
            ), T(
                "When code is copied, a bug fixed in one copy may remain in the others.",
                "A TODO from three years ago still guarantees the work will happen.",
            ), T(
                "Accepting empty, huge, or accented input in a name field is part of basic robustness.",
                "An error message can usually be ignored if the process keeps running.",
            )]),
            ("flags_secrets", [T(
                "Flags need an owner, default, and removal plan or they become permanent branches.",
                "A flag that is never cleaned up is free and has no operational cost.",
            ), T(
                "Putting a password directly in source that might ship is a defect, not a shortcut.",
                "Logging customer passwords to an internal log is safe because only engineers can open it.",
            ), T(
                "Shipping behind a flag does not remove the need to test the flagged path.",
                "Turning a flag on for all users without a rollout plan equals a careful canary.",
            ), T(
                "Redacting secrets in logs is part of a sound debug trade-off.",
                "More verbose logs always beat privacy during an outage.",
            ), T(
                "Using flags to limit blast radius still requires a readiness check before full enablement.",
                "Personal style beats team style because strong programmers know best.",
            )]),
            ("hotfix", [T(
                "A hotfix that stops the bleeding still needs a follow-up check on the neighboring path.",
                "If a hotfix works in production, skipping regression on related paths is justified forever.",
            ), T(
                "Prefer a narrow hotfix plus a tracked follow-up over an untested broad rewrite under fire.",
                "Once users stop complaining, residual risk from the hotfix can be forgotten.",
            ), T(
                "Urgency does not permanently remove the need to verify billing paths.",
                "Praise for the fastest fix always encourages careful work.",
            ), T(
                "Checking a sibling call site after a related fix is often cheap insurance.",
                "Ticket scope always forbids looking one call site away.",
            ), T(
                "A shared helper bug can surface as two different user reports.",
                "When two bugs look related, fixing only the ticketed one is always enough.",
            )]),
            ("ci_debt", [T(
                "A failing CI check you do not understand should block merge until explained or fixed.",
                "Skipping a red lint job is fine if stakeholders liked the demo.",
            ), T(
                "Untracked shortcuts that grow every sprint are a trade you already lost.",
                "All shortcuts are free because tomorrow's team will enjoy cleaning them.",
            ), T(
                "Pinning and reading release notes is part of a responsible dependency upgrade.",
                "Newest always means safest.",
            ), T(
                "Measure before twisting readable code into a micro-optimized shape.",
                "Every function should be micro-optimized on first write.",
            ), T(
                "A known-ugly path with an owner and date beats silent rot.",
                "Never shipping beats shipping with a named follow-up ticket.",
            )]),
            ("compat", [T(
                "Changing a public response field without a version plan can break silent clients.",
                "If you control both ends today, compatibility forever is guaranteed without discipline.",
            ), T(
                "Additive optional fields are usually safer than renaming required ones in place.",
                "Internal-only callers mean you can rename fields freely with no notice.",
            ), T(
                "Documenting a breaking change after clients fail is later than ideal.",
                "Green locally always overrides red CI.",
            ), T(
                "Rubber-stamping flaky without evidence trains the team to ignore real failures.",
                "Major upgrades with no changelog read are fine if CI is green once.",
            ), T(
                "Security patches can justify an upgrade that a cosmetic API change cannot.",
                "Obscure language features always signal senior craft.",
            )]),
            ("edge_l1", [T(
                "Before changing code nobody understands, capturing current behavior with tests reduces risk.",
                "If all tests pass, the user's original complaint is definitely solved.",
            ), T(
                "A test that fails randomly should be fixed or removed with a note, not rerun until green.",
                "A tight deadline is a good reason to skip a required security review.",
            ), T(
                "Writing customers' passwords or card numbers into logs is dangerous even for internal logs.",
                "A known bug can be left out of release notes if it seems minor.",
            ), T(
                "Disagreeing with a senior with a specific reason is fine; the decision still needs a clear owner.",
                "A quick approval from a trusted reviewer means the author needs to check nothing more.",
            ), T(
                "If the ticket says to do it, mentioning a likely user harm is still part of the job.",
                "An estimate is a promise carved in stone rather than a guess with uncertainty.",
            )]),
            ("clear_vs_clever", [T(
                "A boring readable fix usually beats a clever one-liner only one author understands.",
                "Clever bit-twiddling that only one author understands is fine if it is shorter.",
            ), T(
                "If a trick saves three lines but costs an hour of review confusion, it is usually a bad trade.",
                "Performance work never needs a baseline.",
            ), T(
                "A slow rare admin page can wait while a hot checkout path is profiled first.",
                "Every cold path should be optimized before measuring.",
            ), T(
                "Structured logs without secrets usually beat dumping entire requests.",
                "PII in logs is fine if only engineers can open the log tool.",
            ), T(
                "Ownership of a failing path includes knowing whether to rerun, skip, or fix.",
                "Acceptance notes in a ticket are optional suggestions rather than part of the request.",
            )]),
        ),
    }

    # Copy ascending difficulty skeletons for PG L2-L5 from denser technical pairs
    BANKS["programmer"]["2"] = _level_tradeoffs("PG")
    BANKS["programmer"]["3"] = _level_failures("PG")
    BANKS["programmer"]["4"] = _level_traps("PG")
    BANKS["programmer"]["5"] = _level_edge("PG")

    BANKS["software_engineer"] = {
        "1": _se_l1(),
        "2": _level_tradeoffs("SE"),
        "3": _level_failures("SE"),
        "4": _level_traps("SE"),
        "5": _level_edge("SE"),
    }
    BANKS["technical_architect"] = {str(i): _arch_level("TA", i) for i in range(1, 6)}
    BANKS["solutions_architect"] = {str(i): _arch_level("SA", i) for i in range(1, 6)}
    BANKS["data_engineer"] = {str(i): _de_level(i) for i in range(1, 6)}
    BANKS["devops"] = {str(i): _do_level(i) for i in range(1, 6)}
    BANKS["principal_architect"] = {str(i): _pa_level(i) for i in range(1, 6)}
    BANKS["llm_evals_engineer"] = {str(i): _le_level(i) for i in range(1, 6)}
    BANKS["ml_engineer"] = {str(i): _ml_level(i) for i in range(1, 6)}
    BANKS["frontend_engineer"] = {str(i): _fe_level(i) for i in range(1, 6)}
    BANKS["security_engineer"] = {str(i): _sec_level(i) for i in range(1, 6)}
    BANKS["qa_engineer"] = {str(i): _qa_level(i) for i in range(1, 6)}


def _five(pairs: list[tuple[str, str]]) -> list[tuple[str, str]]:
    assert len(pairs) == 5
    return [T(a, b) for a, b in pairs]


def _ten(theme_pairs: list[tuple[str, list[tuple[str, str]]]]):
    return themes(*[(n, _five(v)) for n, v in theme_pairs])


def _level_tradeoffs(tag: str):
    return _ten([
        ("scope_vs_test", [
            ("Cutting scope under a deadline is usually safer than cutting the regression that protects billing.",
             "Cutting automated checks is usually safer than cutting scope when the deadline is tight."),
            ("A reversible flag rollout beats an irreversible schema rewrite under the same calendar pressure.",
             "An irreversible schema rewrite is preferable to a flagged partial launch when time is short."),
            ("Prefer measuring the hot path before micro-optimizing a cold admin screen.",
             "Prefer micro-optimizing every path before measuring which one is hot."),
            ("Readable boring code that passes review beats a clever shortcut that only one person can debug.",
             "A clever shortcut that only one person can debug beats readable boring code."),
            ("Shipping a narrow fix with a dated follow-up ticket beats a silent broad rewrite during an incident.",
             "A silent broad rewrite during an incident beats a narrow fix with a follow-up ticket."),
        ]),
        ("consistency", [
            ("Raising a database isolation level to SERIALIZABLE can increase application deadlock risk.",
             "Raising isolation to SERIALIZABLE always reduces application-level deadlock risk."),
            ("Idempotent retry keys are often required when clients may double-submit under timeouts.",
             "Client timeouts never create duplicate submits if the server is healthy."),
            ("Eventual consistency can make a read-after-write UI lie unless the read path is designed for it.",
             "Eventual consistency never affects what a user sees right after a write."),
            ("A cache without a clear invalidation rule can serve stale authorization decisions.",
             "Caches never affect authorization if the origin database is correct."),
            ("At-least-once delivery without idempotent consumers can double-apply money movements.",
             "At-least-once delivery never double-applies if the broker is durable."),
        ]),
        ("api_compat", [
            ("Renaming a required JSON field in place can break silent clients you do not control.",
             "Renaming a required JSON field in place is safe if your team owns the producer today."),
            ("Additive optional fields are usually safer than removing fields without a deprecation window.",
             "Removing fields without a deprecation window is usually safer than adding optional fields."),
            ("Contract tests between producer and consumer catch many breakages unit tests miss.",
             "Unit tests on the producer alone prove consumers will not break."),
            ("Versioning a public API is part of owning a breaking change, not optional ceremony.",
             "Versioning a public API is optional if the changelog mentions the break."),
            ("Internal monorepo callers can still need a migration plan when many teams share a library.",
             "Internal monorepo callers never need a migration plan."),
        ]),
        ("observability", [
            ("A green average latency can hide a small cohort with multi-second tails.",
             "A green average latency proves every cohort is fine."),
            ("Without customer-facing signals, users may discover an outage before the on-call does.",
             "Passing release tests make customer-facing signals unnecessary."),
            ("Alert fatigue from noisy pages can be as dangerous as missing a real page.",
             "More alerts always mean a safer system."),
            ("Structured logs with request ids beat dumping entire payloads that contain secrets.",
             "Dumping entire payloads including secrets is required for proper debugging."),
            ("A dashboard that only shows success rate can miss empty successful runs.",
             "Success rate alone proves the pipeline produced correct business results."),
        ]),
        ("deps", [
            ("A major dependency upgrade without reading breaking changes is a gamble even if CI is green once.",
             "A single green CI run proves a major dependency upgrade is safe forever."),
            ("Pinning versions and reading advisories is part of owning the supply chain.",
             "Floating on latest tags is the safest supply-chain default."),
            ("Security patches can justify an upgrade that a cosmetic API polish cannot.",
             "Cosmetic API polish justifies the same freeze-break as a critical security patch."),
            ("Vendoring without a update plan creates a silent lag behind upstream fixes.",
             "Vendoring permanently removes the need to track upstream fixes."),
            ("License and security review of copied code still matters when tests pass.",
             "Tests passing make license and security review of copied code unnecessary."),
        ]),
        ("rollout", [
            ("A canary that only hits internal employees can miss a regional customer failure mode.",
             "Any canary that hits someone proves the rollout is safe for every region."),
            ("Feature flags need owners and removal dates or they become permanent product forks.",
             "Feature flags are free forever and need no removal plan."),
            ("Rollback plans should be tested before you need them under pressure.",
             "Rollback plans only need to exist as a wiki paragraph."),
            ("Mixed-version fleets during a rolling deploy can expose protocol mismatches.",
             "Rolling deploys never expose protocol mismatches if each build passed tests."),
            ("Dark-launching a write path still needs correctness checks on shadowed results.",
             "Dark-launching a write path needs no correctness checks because users do not see it."),
        ]),
        ("data", [
            ("A migration that locks a hot table can freeze the app at peak traffic.",
             "Table locks during migration never affect peak traffic if the change is additive."),
            ("Backfills without rate limits can overload primaries that online traffic still needs.",
             "Backfills can always run at full speed because they are offline work."),
            ("Null-heavy joins after a dimension miss can silently distort KPIs.",
             "Null-heavy joins never distort KPIs if SQL runs without error."),
            ("Schema and code must ship in an order that old binaries can survive.",
             "Schema and code can always ship in any order if both are eventually correct."),
            ("Time zone naive timestamps corrupt daily aggregates across regions.",
             "Time zone naive timestamps are fine for global daily aggregates."),
        ]),
        ("ownership", [
            ("If only one person can release, vacations become delivery and incident risks.",
             "Single-person release ownership is fine if that person is senior."),
            ("A change that crosses team boundaries needs an explicit owner for the blast radius.",
             "Cross-team changes need no explicit owner if the ticket has two watchers."),
            ("On-call without runbooks pushes tribal knowledge into pages at 3am.",
             "On-call without runbooks is fine when the team is small."),
            ("Deleting a deprecated path still needs a check for silent external callers.",
             "Deprecated paths can be deleted whenever the owning team is ready."),
            ("Error budgets exist to force trade-offs between velocity and reliability.",
             "Error budgets exist to justify ignoring reliability when a launch date slips."),
        ]),
        ("perf", [
            ("N+1 queries often dominate latency before CPU hotspots do.",
             "CPU hotspots always dominate latency before query patterns do."),
            ("p99 latency SLOs can be green while a small tenant still sees multi-second tails.",
             "A green p99 SLO proves every tenant is within the target."),
            ("Connection pool exhaustion can look like an application deadlock.",
             "Connection pool exhaustion cannot look like an application deadlock."),
            ("Caching without a TTL policy can freeze bad data in place.",
             "Caching without a TTL policy is safe if the cache hit rate is high."),
            ("Batch size tuning can move a job from hours to minutes without changing algorithms.",
             "Batch size tuning never matters if the algorithm is asymptotically optimal."),
        ]),
        ("security_basics", [
            ("Trusting client-supplied roles for authorization is a classic broken access control.",
             "Client-supplied roles are a fine source of truth for authorization."),
            ("CSRF protections still matter for cookie-authenticated browser sessions.",
             "CSRF protections are obsolete for all cookie-authenticated browser sessions."),
            ("Storing long-lived secrets in repo history is a leak even after a later scrub.",
             "Removing a secret in a later commit fully erases it from repo history risk."),
            ("SSRF risk rises when server-side fetchers accept user-controlled URLs.",
             "Server-side fetchers that accept user-controlled URLs have no SSRF risk."),
            ("Least privilege for service accounts reduces blast radius when a key leaks.",
             "Wide privilege for service accounts is fine if the key is rotated yearly."),
        ]),
    ])


def _level_failures(tag: str):
    return _ten([
        ("load", [
            ("A poison message that retries forever can stall an entire consumer group.",
             "A poison message that retries forever only affects that one message offset."),
            ("Hot keys can make a sharded job crawl while other shards sit idle.",
             "Hot keys cannot affect sharded jobs if the cluster has spare CPU."),
            ("Thread or connection pool exhaustion can take down paths that look CPU-healthy.",
             "If CPU is low, pool exhaustion cannot be the outage cause."),
            ("A slow dependency can starve workers and look like your service is the outage.",
             "A slow dependency cannot make your service look down if your process is up."),
            ("Unbounded retries can turn a brief blip into a self-inflicted retry storm.",
             "Unbounded retries are the safest default during dependency blips."),
        ]),
        ("time", [
            ("Clock skew between nodes can break lease-based leader election.",
             "Clock skew between nodes cannot affect lease-based leader election."),
            ("Late-arriving events can corrupt period-close metrics if windows are sealed early.",
             "Late-arriving events cannot affect period-close metrics once a window is coded."),
            ("DST transitions can double-bill or skip intervals when schedules assume fixed offsets.",
             "DST transitions never affect schedules that store local times only."),
            ("A deploy during a peak window can amplify a small regression into a major outage.",
             "Deploy timing relative to peak traffic does not change regression blast radius."),
            ("Stale caches can serve wrong answers long after the source of truth changed.",
             "Stale caches always refresh before serving any answer."),
        ]),
        ("partial", [
            ("Mixed-version fleets during rolling deploys can expose protocol mismatches.",
             "Mixed-version fleets never appear if each build passed CI."),
            ("Config drift between nodes creates works-on-some-boxes failures.",
             "Config drift cannot create works-on-some-boxes failures if images are identical."),
            ("A backup never restored is an unverified recovery story.",
             "A backup that completed without error is proven restorable."),
            ("Swallowing errors without signals hides failure until users churn.",
             "Swallowing errors is fine if the happy path returns 200."),
            ("Partial writes without compensating actions can leave durable corruption.",
             "Partial writes always roll back automatically in every datastore."),
        ]),
        ("data_corruption", [
            ("Idempotency gaps under at-least-once delivery can double-charge.",
             "At-least-once delivery cannot double-charge if the broker is replicated."),
            ("Schema reads by old binaries after an incompatible write can crash a fleet.",
             "Old binaries always ignore new fields safely without a plan."),
            ("Unique index races can surface as intermittent 500s under concurrency.",
             "Unique index races cannot appear if the happy path is tested once."),
            ("Truncated file reads during a still-open write can load partial data as truth.",
             "Reading a file while it is still being written always yields complete data."),
            ("Silent truncation of Unicode can corrupt names and tokens without a hard error.",
             "Silent Unicode truncation always raises before data is stored."),
        ]),
        ("cascade", [
            ("One upstream miss can cascade into dozens of red tasks that hide the root cause.",
             "Downstream red tasks always point at the true root cause first."),
            ("Retrying a failing fan-out without jitter can synchronize thundering herds.",
             "Synchronized retries are the best way to clear a dependency backlog."),
            ("A shared library deadlock can freeze multiple services that look unrelated.",
             "Shared library deadlocks only affect the service that deployed last."),
            ("Disk full on a logging volume can freeze request handling in surprising ways.",
             "Disk full on a logging volume cannot affect request handling."),
            ("Certificate expiry can look like a random network outage across clients.",
             "Certificate expiry always presents as a clear certificate error to operators."),
        ]),
        ("human", [
            ("Metric gaming can improve a dashboard while worsening the user outcome.",
             "If the dashboard metric improves, the user outcome necessarily improved."),
            ("Runbook-free pages push tribal knowledge into the worst moment to learn it.",
             "Runbook-free pages are fine when seniors are on the rotation."),
            ("Feature flags left forever create unknown product combinations in production.",
             "Feature flags left forever have no combinatorial risk."),
            ("Quiet Fridays still need review on secret-handling changes.",
             "Quiet Fridays make self-merge of secret-handling changes safe."),
            ("Blame-first incident reviews reduce the signal you need to prevent repeats.",
             "Blame-first incident reviews are the fastest path to prevention."),
        ]),
        ("scale", [
            ("A design that works for 100 users can fail at 100,000 without architectural change.",
             "A design that works for 100 users will scale to 100,000 without changes."),
            ("N+1 query patterns explode only after data growth makes them obvious.",
             "N+1 query patterns are obvious in the first unit test."),
            ("Global locks that were fine at low QPS become outages at high QPS.",
             "Global locks that pass functional tests cannot become outages at high QPS."),
            ("Fan-out amplification can turn one user action into thousands of downstream calls.",
             "Fan-out amplification cannot occur if each downstream call is individually cheap."),
            ("Memory that grows with request size will eventually OOM under a large upload.",
             "Memory that grows with request size is safe if the average upload is small."),
        ]),
        ("release", [
            ("A release that passed tests can still need a fast undo path.",
             "If a release passed tests, a way to undo it is unnecessary."),
            ("Canaries that only check HTTP 200 can miss silent corruption.",
             "HTTP 200 canaries prove the release did not corrupt data."),
            ("Database migrations and code deploys ordered wrong can brick a fleet.",
             "Migration and code order never matters if both artifacts are correct."),
            ("Feature freeze does not remove the need for a rollback rehearsal.",
             "Feature freeze removes the need for rollback rehearsal."),
            ("Hotfixes without regression on neighboring paths recreate the next incident.",
             "Hotfixes that stop complaints never need neighboring-path regression."),
        ]),
        ("multi_tenant", [
            ("Noisy-neighbor load from one tenant can starve others on a shared cluster.",
             "Tenant isolation is automatic on any shared cluster."),
            ("Per-tenant rate limits can still leave a shared dependency overloaded.",
             "Per-tenant rate limits fully protect shared dependencies."),
            ("A tenant-specific config flag can create a one-off failure mode nobody tests.",
             "Tenant-specific config flags cannot create untested failure modes."),
            ("Cross-tenant caching without keys can leak data between customers.",
             "Caches without tenant keys cannot leak data between customers."),
            ("Quota exhaustion for one tenant can surface as intermittent 429s that look random.",
             "Quota exhaustion always surfaces as a clear per-tenant dashboard first."),
        ]),
        ("recovery", [
            ("Recovery time objectives are fiction until restore drills succeed.",
             "Recovery time objectives are proven by backup success logs alone."),
            ("Point-in-time recovery still needs application-level consistency checks.",
             "Point-in-time recovery always yields application-consistent state."),
            ("Corrupted replicas can pass shallow health checks and fail on real queries.",
             "Shallow health checks prove replicas can serve real queries."),
            ("Partial region failover can split brains if leadership is not fenced.",
             "Partial region failover cannot split brains if DNS is updated."),
            ("Replay of an event log without idempotent consumers can duplicate side effects.",
             "Event log replay cannot duplicate side effects if the log is immutable."),
        ]),
    ])


def _level_traps(tag: str):
    return _ten([
        ("best_practice_myths", [
            ("Microservices do not automatically make a system more reliable than a modular monolith.",
             "Splitting into microservices automatically makes a system more reliable."),
            ("100% statement coverage can still miss the bug if assertions check the wrong outcome.",
             "100% statement coverage proves the important behaviors are correct."),
            ("More dashboards do not equal better situational awareness if nobody owns triage.",
             "More dashboards always equal better situational awareness."),
            ("Agile ceremonies do not replace an explicit ownership map for production paths.",
             "Agile ceremonies replace the need for an explicit ownership map."),
            ("Cloud managed services still need failure-mode design for quotas and regional outages.",
             "Cloud managed services remove the need to design for failure modes."),
        ]),
        ("metrics", [
            ("When a number becomes a target, teams may improve the number without improving the outcome.",
             "When a number becomes a target, the underlying outcome always improves with it."),
            ("Ticket-throughput metrics can push people to split work into many tiny tickets.",
             "Ticket-throughput metrics cannot distort how work is sliced."),
            ("Error-rate SLOs can be green while a critical admin path is fully broken.",
             "Error-rate SLOs being green proves every critical path works."),
            ("MTTR can look better if you stop detecting subtle failures.",
             "Lower MTTR always means users are healthier."),
            ("Cache hit rate can rise while serving increasingly stale wrong answers.",
             "Rising cache hit rate proves answers are fresher and more correct."),
        ]),
        ("process", [
            ("A polished RFC can still ship a design that fails the user under edge load.",
             "A polished RFC proves the design will not fail users under edge load."),
            ("Mandatory approvals can create rubber stamps that hide missing technical review.",
             "Mandatory approvals always improve technical review quality."),
            ("Blameless language without follow-up actions is theater.",
             "Blameless language alone prevents repeats."),
            ("Freeze windows do not help if emergency hotfixes skip the same checks.",
             "Freeze windows guarantee quality even when hotfixes skip checks."),
            ("Copying an industry reference architecture without constraints matching is cosplay.",
             "Copying an industry reference architecture always fits your constraints."),
        ]),
        ("platform", [
            ("A shared platform team can become a bottleneck if every change requires their merge.",
             "A shared platform team cannot become a bottleneck by design."),
            ("Golden paths that are hard to use will be bypassed with shadow systems.",
             "Golden paths are never bypassed if they are documented."),
            ("Self-service without guardrails pushes risk to the least experienced caller.",
             "Self-service without guardrails reduces risk by removing tickets."),
            ("Inner-source libraries without owners become unmaintained critical path code.",
             "Inner-source libraries without owners stay healthy through community magic."),
            ("Platform SLAs must include the tools teams use to ship, not only runtime APIs.",
             "Platform SLAs only need to cover runtime APIs."),
        ]),
        ("data_traps", [
            ("A single source of truth still fails if writers bypass it with side tables.",
             "Declaring a single source of truth makes bypass impossible."),
            ("Event sourcing does not remove the need for privacy deletion strategies.",
             "Event sourcing automatically solves privacy deletion."),
            ("CDC pipelines can amplify schema mistakes into every downstream store.",
             "CDC pipelines isolate schema mistakes to the source system."),
            ("Data catalogs that are stale become confidence theater.",
             "Data catalogs stay accurate without ownership and freshness checks."),
            ("PII classification that is wrong is worse than no classification if it blocks detection.",
             "Any PII classification is better than none even when systematically wrong."),
        ]),
        ("security_traps", [
            ("Perimeter firewalls do not replace least-privilege service identities inside the network.",
             "Perimeter firewalls replace the need for least-privilege service identities."),
            ("Annual pen tests do not prove continuous control effectiveness.",
             "Annual pen tests prove continuous control effectiveness."),
            ("Encryption at rest does not help if application roles can read all plaintext.",
             "Encryption at rest makes application role mistakes irrelevant."),
            ("SSO adoption does not remove the need to review OAuth scopes and token lifetimes.",
             "SSO adoption removes the need to review OAuth scopes and token lifetimes."),
            ("Security questionnaires can pass while production secrets still live in chat logs.",
             "Passing security questionnaires proves production secrets are well handled."),
        ]),
        ("ai_traps", [
            ("A higher offline benchmark does not guarantee better online user outcomes.",
             "A higher offline benchmark guarantees better online user outcomes."),
            ("LLM judges can share the same biases as the system under test.",
             "LLM judges are unbiased by construction."),
            ("Prompt injection risk remains when tools can fetch untrusted content.",
             "Prompt injection risk disappears when the model is frontier-tier."),
            ("Eval sets that leak into training make progress look fake.",
             "Eval sets that leak into training still measure true generalization."),
            ("RAG citation displays can look grounded while retrieving the wrong passage.",
             "Showing citations proves the answer is grounded in the right passage."),
        ]),
        ("org_traps", [
            ("Headcount added to a late project can slow it further without a clear ownership cut.",
             "Headcount added to a late project always speeds delivery."),
            ("Reorgs can break implicit interfaces that were never written down.",
             "Reorgs cannot break interfaces that were never written down."),
            ("OKRs that ignore reliability create rational under-investment in toil reduction.",
             "OKRs that ignore reliability still produce reliable systems."),
            ("Hero culture hides missing platform investment behind individual sacrifice.",
             "Hero culture is a sustainable reliability strategy."),
            ("Vendor lock-in can be a deliberate trade, but pretending it is free is the trap.",
             "Vendor lock-in is always free if the vendor is popular."),
        ]),
        ("testing_traps", [
            ("Passing CI does not prove the canary population matches production diversity.",
             "Passing CI proves the canary population matches production diversity."),
            ("Flake quarantine without expiry dates becomes a junk drawer.",
             "Flake quarantine without expiry dates is a complete flake strategy."),
            ("Load tests against empty datasets miss contention that real data creates.",
             "Load tests against empty datasets prove production contention behavior."),
            ("Contract tests stale against a moved producer become false confidence.",
             "Contract tests never go stale if they once passed."),
            ("Snapshot tests can lock in accidental UI bugs as the new goldens.",
             "Snapshot tests cannot lock in accidental UI bugs."),
        ]),
        ("product_traps", [
            ("A polished dashboard can still drive harmful decisions if the metric definition is wrong.",
             "A polished dashboard proves the metric definition is right."),
            ("Growth experiments without holdouts can claim wins that seasonality caused.",
             "Growth experiments without holdouts still identify causal wins."),
            ("Accessibility fixes late in the cycle cost more than designing for them early.",
             "Accessibility can always be bolted on cheaply at the end."),
            ("Dark patterns can raise short-term metrics while destroying trust.",
             "Dark patterns that raise metrics cannot destroy trust."),
            ("Launch checklists that ignore data deletion paths ship privacy debt.",
             "Launch checklists that ignore data deletion paths are still complete."),
        ]),
    ])


def _level_edge(tag: str):
    return _ten([
        ("multi_constraint", [
            ("You can meet a latency SLO and still fail a privacy obligation if logs retain raw PII.",
             "Meeting a latency SLO proves privacy obligations are met."),
            ("A correct algorithm can still be the wrong choice if it blows the cost envelope at target QPS.",
             "A correct algorithm is always the right choice regardless of cost at target QPS."),
            ("Region failover that preserves availability can still violate data-residency constraints.",
             "Region failover that preserves availability cannot violate data-residency constraints."),
            ("A secure-by-default change can break partner integrations that depended on lax behavior.",
             "Secure-by-default changes never break partner integrations."),
            ("Improving one tenant's throughput can violate fairness objectives for others on a shared pool.",
             "Improving one tenant's throughput cannot violate fairness on a shared pool."),
        ]),
        ("process_vs_user", [
            ("Every acceptance box can be ticked while the feature still fails the user's real job.",
             "Every acceptance box ticked means the feature is good by definition."),
            ("A temporary workaround often becomes permanent when incentives reward closing the ticket.",
             "A temporary workaround never becomes permanent because everyone remembers it."),
            ("Polite consensus in design review can still ship a foot-gun if dissent is socially costly.",
             "Polite consensus in design review proves dissent was unnecessary."),
            ("Compliance evidence can be complete while users remain exposed to a known class of abuse.",
             "Complete compliance evidence proves users are not exposed to known abuse classes."),
            ("Handoffs across time zones can satisfy process while dropping the only person who understood a risk.",
             "Handoffs across time zones cannot drop critical risk knowledge if tickets exist."),
        ]),
        ("irreversible", [
            ("Publishing a public API without a deprecation policy creates multi-year drag.",
             "Publishing a public API without a deprecation policy is free if adoption is high."),
            ("Hard-deleting backup history can satisfy one request while destroying audit recoverability.",
             "Hard-deleting backup history cannot affect audit recoverability."),
            ("Widening a shared schema column type can be easy forward and painful to reverse under load.",
             "Widening a shared schema column type is always easy to reverse."),
            ("Granting broad production PII access just this once often becomes the permanent path.",
             "Just this once production PII grants do not become permanent."),
            ("Changing historical metric definitions without notice can break audits and partner trust.",
             "Changing historical metric definitions without notice is safe if the new definition is better."),
        ]),
        ("incident_edge", [
            ("During an incident, calling for help early can be better than preserving personal heroics.",
             "During an incident, struggling alone first always looks stronger than calling for help."),
            ("Mitigate first can be right even when the root cause is still unknown.",
             "You must fully know the root cause before any mitigation."),
            ("Status pages that stay silent to avoid alarm can destroy trust faster than the outage.",
             "Status pages should stay silent until root cause is certain."),
            ("Feature-flag kill switches fail if nobody can reach the flag console during the outage.",
             "Feature-flag kill switches work even when the flag console is unreachable."),
            ("Postmortems that omit customer impact numbers train the org to underweight harm.",
             "Postmortems can omit customer impact numbers without changing incentives."),
        ]),
        ("cross_team", [
            ("A platform change that is locally optimal can globally stall every product team.",
             "A platform change that is locally optimal cannot stall product teams."),
            ("Contracts between teams need explicit error semantics, not only happy-path payloads.",
             "Contracts between teams only need happy-path payload shapes."),
            ("Dual-running two sources of truth without a cutover owner creates permanent ambiguity.",
             "Dual-running two sources of truth without a cutover owner is sustainable."),
            ("Shared on-call across products without clear routing creates dropped pages.",
             "Shared on-call across products without routing cannot drop pages."),
            ("A migration tax paid only by consumers will be rationally deferred forever.",
             "A migration tax paid only by consumers will be paid promptly."),
        ]),
        ("ethics_product", [
            ("Optimizing a growth metric can harm users even when legal review is still pending.",
             "If legal review is pending, growth optimizations cannot harm users yet."),
            ("Model outputs that look helpful can still be unsafe under adversarial prompts.",
             "Helpful-looking model outputs are safe under adversarial prompts."),
            ("Personalization that ignores consent boundaries can fail users while raising engagement.",
             "Engagement rising proves personalization respected consent boundaries."),
            ("Accessibility debt compounds into legal and product exclusion over multi-year horizons.",
             "Accessibility debt cannot compound into exclusion if a launch checklist passed once."),
            ("Quietly changing a disclosed retention period breaks the bargain users thought they had.",
             "Quietly changing a disclosed retention period is fine if storage costs require it."),
        ]),
        ("econ", [
            ("A cheaper architecture can be more expensive once operational toil is priced in.",
             "Sticker price of infrastructure always equals total cost of ownership."),
            ("Reserved capacity that assumes perfect forecasts can strand spend under demand shifts.",
             "Reserved capacity cannot strand spend if the vendor is large."),
            ("Premature sharding can cost more than vertical scale for years.",
             "Premature sharding is always cheaper than vertical scale."),
            ("Build-vs-buy must include exit cost, not only year-one license price.",
             "Build-vs-buy can ignore exit cost if year-one license price is low."),
            ("Free tiers can create product dependence that later pricing shocks exploit.",
             "Free tiers cannot create dependence that later pricing shocks exploit."),
        ]),
        ("subtle_correctness", [
            ("Exactly-once end-to-end is often a marketing phrase for at-least-once plus idempotency.",
             "Exactly-once end-to-end is commonly free without idempotent consumers."),
            ("Read-your-writes can fail across devices even when a single device session looks consistent.",
             "Read-your-writes across devices is guaranteed if one device session looks consistent."),
            ("Monotonic reads can break when switching replicas without session stickiness.",
             "Monotonic reads cannot break when switching replicas."),
            ("Snapshot isolation does not prevent all write-skew anomalies in every engine.",
             "Snapshot isolation prevents all write-skew anomalies in every engine."),
            ("A unique constraint is not a substitute for a clear conflict-resolution policy in UX.",
             "A unique constraint fully substitutes for conflict-resolution UX."),
        ]),
        ("people_systems", [
            ("Bus factor of one on a payment path is a reliability defect, not a staffing preference.",
             "Bus factor of one on a payment path is acceptable if that person is strong."),
            ("After an outage, studying how process allowed the mistake teaches more than blaming a person.",
             "After an outage, blaming a person teaches more than studying process."),
            ("Hiring freezes can make toil reduction the only remaining capacity strategy.",
             "Hiring freezes remove the need for toil reduction."),
            ("Onboarding that skips production access patterns produces paper engineers.",
             "Onboarding that skips production access patterns is fine if slides are good."),
            ("Knowledge in chat scrolls away; durable runbooks survive rotations.",
             "Knowledge in chat is as durable as runbooks for rotations."),
        ]),
        ("final_traps", [
            ("A green canary on synthetic traffic can miss auth failures that only real users hit.",
             "A green canary on synthetic traffic proves auth works for real users."),
            ("Deleting a field from a public interface without telling consumers is a break, not a cleanup.",
             "Deleting a field from a public interface without notice is a cleanup if unused in your repo."),
            ("Usage numbers alone do not show who depends on a feature or how critical it is.",
             "Usage numbers alone show who depends on a feature and how critical it is."),
            ("If every gate is green, you can still be wrong about the user's job-to-be-done.",
             "If every gate is green, the user's job-to-be-done is satisfied."),
            ("Documented daily grain while the table is weekly quietly betrays consumers.",
             "Documented daily grain while the table is weekly is harmless if SQL runs."),
        ]),
    ])


def _se_l1():
    return _ten([
        ("tests_coverage", [
            ("Statement coverage of 100% does not prove every important branch outcome was asserted.",
             "Statement coverage of 100% proves every important branch outcome was asserted."),
            ("Integration checks can catch contract breaks that pure unit tests miss.",
             "Pure unit tests catch every contract break integration checks would find."),
            ("Flaky tests that are ignored train the team to dismiss real failures.",
             "Flaky tests that are ignored have no effect on how real failures are treated."),
            ("Testing the exact reported failure case is part of closing a defect.",
             "A green compile is enough testing to close a defect."),
            ("Property tests can reveal edge cases example lists miss.",
             "Example lists always cover what property tests would find."),
        ]),
        ("review_release", [
            ("Small diffs that touch auth still need careful review.",
             "Small diffs that touch auth can skip review because they are small."),
            ("Releasing small changes often usually makes faults easier to localize.",
             "Releasing giant batches rarely makes faults easier to localize."),
            ("Feature flags still need a test of the enabled path.",
             "Feature flags remove the need to test the enabled path."),
            ("Rollback capability remains valuable after a green test plan.",
             "Rollback capability is unnecessary after a green test plan."),
            ("Release notes that omit a known user-facing bug hide risk from support.",
             "Omitting a known user-facing bug from release notes is fine if it seems minor."),
        ]),
        ("observability", [
            ("Logs without correlation ids make multi-service incidents harder to untangle.",
             "Logs without correlation ids are just as easy to untangle in multi-service incidents."),
            ("Customers may discover an outage first if there is no monitoring on the user path.",
             "Passing QA means customers cannot discover an outage first."),
            ("High cardinality labels can make metrics systems expensive or slow.",
             "High cardinality labels never affect metrics systems."),
            ("Error budgets exist to force reliability trade-offs, not to ignore them.",
             "Error budgets exist to ignore reliability when launches slip."),
            ("A backup never restored is unverified.",
             "A completed backup job proves restore will work."),
        ]),
        ("data_privacy", [
            ("Collect only the personal data the feature needs.",
             "Collecting extra personal data is fine for possible future features."),
            ("A copy of data on the same disk is not a full backup strategy.",
             "A copy of data on the same disk counts as a full backup strategy."),
            ("Client-supplied roles are not a safe authorization source of truth.",
             "Client-supplied roles are a safe authorization source of truth."),
            ("Secrets in git history remain a leak after a later delete commit.",
             "A later delete commit fully removes secrets from git history risk."),
            ("PII in logs is still a problem when only engineers can open the tool.",
             "PII in logs is fine when only engineers can open the tool."),
        ]),
        ("design", [
            ("Writing down why a design was chosen helps future engineers avoid repeating debates.",
             "Design rationale notes are wasted if the code already ships."),
            ("Talking to the people who will use the product usually improves the build.",
             "Engineers build best when they never speak to the people who will use the product."),
            ("Automated tests are not merely a luxury that only slows teams down.",
             "Automated tests are a luxury that slows a team down with no benefit."),
            ("Code review can catch mistakes and spread knowledge when done with care.",
             "Code review only slows delivery and never catches mistakes."),
            ("Honest status including bad news helps planning.",
             "Hiding bad news until the demo is a sound planning strategy."),
        ]),
        ("concurrency", [
            ("Two writers without concurrency control can overwrite each other.",
             "Two writers without concurrency control cannot overwrite each other if both succeed."),
            ("Race conditions can pass local tests and fail under CI parallelism.",
             "Race conditions that pass local tests cannot fail under CI parallelism."),
            ("Idempotent handlers reduce damage from duplicate deliveries.",
             "Idempotent handlers are unnecessary under at-least-once delivery."),
            ("Mutexes held during remote calls can create distributed deadlocks of progress.",
             "Mutexes held during remote calls cannot harm progress."),
            ("Optimistic locking needs a defined UX when versions conflict.",
             "Optimistic locking needs no UX when versions conflict."),
        ]),
        ("api", [
            ("Breaking a public response shape without a version plan can break silent clients.",
             "Breaking a public response shape without a version plan is safe for silent clients."),
            ("Optional additive fields are usually safer than in-place renames of required fields.",
             "In-place renames of required fields are usually safer than optional additive fields."),
            ("Pagination defaults that are unbounded can become an accidental DoS.",
             "Unbounded pagination defaults cannot become an accidental DoS."),
            ("Time-out values that are longer than caller patience create retry amplification.",
             "Time-out values longer than caller patience cannot create retry amplification."),
            ("Idempotency keys belong on money-moving POSTs that may be retried.",
             "Idempotency keys are unnecessary on money-moving POSTs that may be retried."),
        ]),
        ("deps", [
            ("Pinning dependencies makes builds reproducible.",
             "Floating latest tags make builds more reproducible than pins."),
            ("Reading changelogs before major upgrades is part of engineering diligence.",
             "Reading changelogs before major upgrades is optional if CI is green once."),
            ("Copied snippets still need license and security review.",
             "Copied snippets need no license or security review if tests pass."),
            ("Transitive dependency CVEs can still be your production risk.",
             "Transitive dependency CVEs are never your production risk."),
            ("Abandonware libraries on a critical path are a risk even if they work today.",
             "Abandonware libraries on a critical path are fine if they work today."),
        ]),
        ("perf_basics", [
            ("Measure before micro-optimizing readable code.",
             "Micro-optimize every function before measuring."),
            ("N+1 queries often dominate before CPU hotspots.",
             "CPU hotspots always dominate before N+1 queries."),
            ("Indexes that match query filters can cut latency by orders of magnitude.",
             "Indexes that match query filters rarely affect latency."),
            ("Payload size affects mobile users more than desktop lab tests suggest.",
             "Payload size cannot affect mobile users differently than desktop lab tests."),
            ("Connection pools need sizing relative to datastore limits.",
             "Connection pools can be unbounded if the app is horizontally scaled."),
        ]),
        ("team", [
            ("Fixing another team's code without telling them can create ownership gaps.",
             "Fixing another team's code without telling them is always the fastest healthy path."),
            ("Bus factor of one on a critical path is a reliability issue.",
             "Bus factor of one on a critical path is fine for strong engineers."),
            ("On-call without a runbook pushes learning into the incident.",
             "On-call without a runbook is fine for senior rotations."),
            ("Cross-team interfaces need explicit error semantics.",
             "Cross-team interfaces only need happy-path examples."),
            ("Estimates are forecasts with uncertainty, not carved promises.",
             "Estimates are carved promises rather than forecasts with uncertainty."),
        ]),
    ])


def _arch_level(prefix: str, level: int):
    if level == 1:
        return _ten([
            ("boundaries", [
                ("Clear service boundaries should match change frequency and ownership, not only noun lists.",
                 "Service boundaries should be split by every noun in the domain model."),
                ("Synchronous chains across many services amplify latency and failure.",
                 "Synchronous chains across many services reduce latency and failure."),
                ("A modular monolith can be a rational architecture under a small team.",
                 "A modular monolith is never rational once microservices exist as an option."),
                ("Public contracts need versioning discipline even inside one company.",
                 "Public contracts inside one company never need versioning discipline."),
                ("Data ownership should be explicit or every team will write shadow copies.",
                 "Data ownership can stay implicit if the ERD looks clean."),
            ]),
            ("consistency", [
                ("Choosing eventual consistency requires UX that tolerates stale reads.",
                 "Choosing eventual consistency needs no UX changes for stale reads."),
                ("Distributed transactions are not free; sagas trade complexity for coupling reduction.",
                 "Distributed transactions are free in modern clouds."),
                ("Idempotency belongs at money and inventory boundaries.",
                 "Idempotency is optional at money and inventory boundaries."),
                ("Caching authorization decisions without TTL can freeze revoked access.",
                 "Caching authorization decisions without TTL is safe."),
                ("Read replicas can serve stale data relative to a primary write.",
                 "Read replicas always reflect primary writes immediately."),
            ]),
            ("nfr", [
                ("Availability goals need error budgets to be actionable.",
                 "Availability goals need no error budgets to be actionable."),
                ("RPO and RTO are unverified without restore drills.",
                 "RPO and RTO are verified by backup success logs alone."),
                ("Threat models should include insider and supply-chain paths, not only external scanners.",
                 "Threat models only need external scanner findings."),
                ("Cost is an architectural constraint alongside latency and safety.",
                 "Cost is not an architectural constraint if latency targets are met."),
                ("Multi-region active-active needs conflict rules, not only DNS failover.",
                 "Multi-region active-active needs only DNS failover."),
            ]),
            ("integration", [
                ("Anti-corruption layers protect a core model from vendor schemas.",
                 "Vendor schemas should become the core model to reduce mapping code."),
                ("Contract tests reduce integration surprise between producers and consumers.",
                 "Contract tests add no value beyond producer unit tests."),
                ("Batch interfaces still need poison-message and replay strategies.",
                 "Batch interfaces need no poison-message strategy if files are small."),
                ("Shared databases across product teams create hidden coupling.",
                 "Shared databases across product teams reduce coupling."),
                ("Event names are part of the contract, including payload evolution rules.",
                 "Event names are not part of the contract if topics are private."),
            ]),
            ("evolution", [
                ("Expand-contract migrations reduce downtime versus big-bang renames.",
                 "Big-bang renames are usually safer than expand-contract migrations."),
                ("Feature flags can separate deploy from release when used with discipline.",
                 "Feature flags remove the need for migration discipline."),
                ("Deprecation windows should match real consumer upgrade speed.",
                 "Deprecation windows can ignore consumer upgrade speed."),
                ("Technical runway for compliance changes must be scheduled like features.",
                 "Compliance changes can always be squeezed into the last sprint."),
                ("Architecture decision records help when trade-offs are revisited months later.",
                 "Architecture decision records are wasted once code ships."),
            ]),
            ("obs", [
                ("Golden signals should cover the user journey, not only host CPU.",
                 "Host CPU is a sufficient golden signal for user journeys."),
                ("Tracing helps when logs alone cannot reconstruct a cross-service path.",
                 "Tracing never helps when logs exist."),
                ("SLOs should be bound to user-visible journeys.",
                 "SLOs should be bound only to internal queue depths."),
                ("Saturation metrics catch problems before hard errors appear.",
                 "Saturation metrics are unnecessary if error rate is watched."),
                ("Synthetic checks miss some auth paths that only real users exercise.",
                 "Synthetic checks cover every auth path real users exercise."),
            ]),
            ("team", [
                ("Inverse Conway advice: org structure will pressure your architecture either way.",
                 "Org structure cannot pressure architecture if diagrams are clean."),
                ("Platform golden paths need to be easier than bypasses.",
                 "Platform golden paths will be used even when bypasses are easier."),
                ("Clear on-call ownership maps belong in the architecture pack.",
                 "On-call ownership maps are unrelated to architecture."),
                ("Interfaces without owners become unowned critical path.",
                 "Interfaces without owners stay healthy through documentation alone."),
                ("Cross-team latency budgets must be negotiated, not assumed.",
                 "Cross-team latency budgets can be assumed from averages."),
            ]),
            ("data", [
                ("PII flow diagrams are part of architecture, not only legal paperwork.",
                 "PII flow diagrams are only legal paperwork."),
                ("Retention and deletion paths must be designed with write paths.",
                 "Retention and deletion paths can be designed after launch."),
                ("Reporting stores often need different consistency than transactional stores.",
                 "Reporting stores should use the same consistency as transactional stores always."),
                ("Backfill strategy is part of schema change design.",
                 "Backfill strategy is optional in schema change design."),
                ("Reference data ownership fights create silent metric forks.",
                 "Reference data ownership fights cannot create metric forks."),
            ]),
            ("risk", [
                ("Single points of failure include people and vendors, not only servers.",
                 "Single points of failure are only servers."),
                ("Blast radius should guide cell or shard boundaries.",
                 "Blast radius is unrelated to cell or shard boundaries."),
                ("Chaos experiments validate assumptions that diagrams cannot.",
                 "Chaos experiments add nothing beyond diagrams."),
                ("Dependency on a single region is a risk even with multi-AZ inside it.",
                 "Multi-AZ inside one region removes single-region risk."),
                ("Secrets distribution design is an architectural concern.",
                 "Secrets distribution design is only an ops concern after go-live."),
            ]),
            ("fit", [
                ("Solutions should fit constraints, not a vendor slide deck.",
                 "Vendor slide decks are sufficient constraints for solutions."),
                ("Buy-vs-build must include exit cost and data gravity.",
                 "Buy-vs-build can ignore exit cost and data gravity."),
                ("Reference architectures still need constraint mapping.",
                 "Reference architectures can be copied without constraint mapping."),
                ("Non-functional tests belong in the Definition of Done for interfaces.",
                 "Non-functional tests are optional for interfaces if functional tests pass."),
                ("Over-fetching chatty APIs can dominate mobile cost.",
                 "Over-fetching chatty APIs cannot dominate mobile cost."),
            ]),
        ])
    if level == 2:
        return _level_tradeoffs(prefix)
    if level == 3:
        return _level_failures(prefix)
    if level == 4:
        return _level_traps(prefix)
    return _level_edge(prefix)


def _de_level(level: int):
    if level <= 1:
        return _ten([
            ("freshness", [
                ("Consumers should know the intended freshness SLA of a dataset.",
                 "If yesterday's pipeline job succeeded, today's tables are automatically correct."),
                ("Re-running a load should not double-count facts if the job is designed for idempotent loads.",
                 "Re-running a load always doubles facts and cannot be designed otherwise."),
                ("Partition filters that are wrong can silently drop an entire day.",
                 "Partition filters that are wrong always raise hard errors."),
                ("Watermarks exist because event time and processing time diverge.",
                 "Event time and processing time never diverge in modern warehouses."),
                ("Late data policies must be explicit or period-close becomes fiction.",
                 "Late data policies are unnecessary if the scheduler is reliable."),
            ]),
            ("schema", [
                ("Producers renaming columns without contracts breaks consumers.",
                 "Producers can rename columns anytime because consumers will adapt."),
                ("Schema evolution needs expand-contract discipline across readers.",
                 "Schema evolution needs no discipline if Spark jobs are resilient."),
                ("A short data dictionary for key fields prevents wrong joins.",
                 "Data dictionaries are optional when column names look obvious."),
                ("Type widening can be easy forward and hard to reverse under load.",
                 "Type widening is always easy to reverse under load."),
                ("Nullability changes can break downstream not-null assumptions.",
                 "Nullability changes cannot break downstream not-null assumptions."),
            ]),
            ("quality", [
                ("SQL that runs once on a sample is not fully tested.",
                 "SQL that runs once on a sample is fully tested."),
                ("Knowing which upstream table feeds a report helps when numbers look wrong.",
                 "Upstream lineage is unnecessary when dashboards look polished."),
                ("A query that is fine on a week of data can fail on a year.",
                 "A query that is fine on a week of data will be fine on a year."),
                ("Personal data in pipelines needs the same care as in apps.",
                 "Personal data in pipelines needs less care than in apps."),
                ("Failed tasks need an owner who knows whether to rerun, skip, or fix.",
                 "Failed tasks can stay red without owners if the next schedule might heal them."),
            ]),
            ("joins", [
                ("Many-to-many joins can explode row counts and inflate metrics.",
                 "Many-to-many joins cannot inflate metrics if SQL is valid."),
                ("Facts referencing missing dimensions produce wrong or null-heavy reports.",
                 "Facts referencing missing dimensions are automatically dropped safely."),
                ("Fan-out from duplicated dimension keys corrupts aggregates.",
                 "Duplicated dimension keys cannot corrupt aggregates."),
                ("Slow-changing dimensions need an explicit policy for historical truth.",
                 "Slow-changing dimensions need no policy if the latest row looks right."),
                ("Broadcast joins that exceed memory fail differently than sort-merge joins.",
                 "Broadcast joins that exceed memory fail the same way as sort-merge joins."),
            ]),
            ("ops", [
                ("Not knowing how long a full rebuild takes is a hidden failure mode.",
                 "Full rebuild time is irrelevant if incremental jobs usually succeed."),
                ("Backfills without rate limits can harm the primary serving store.",
                 "Backfills without rate limits cannot harm serving stores."),
                ("Expired credentials can stop loads while looking like a source outage.",
                 "Expired credentials always present as credential errors, never like source outages."),
                ("A transform change can shift a KPI slowly without a hard crash.",
                 "A transform change cannot shift a KPI without a hard crash."),
                ("Consuming a file still being written can load truncated data.",
                 "Consuming a file still being written always yields complete data."),
            ]),
            ("partitioning", [
                ("One hot key can make a distributed job crawl while others sit idle.",
                 "One hot key cannot skew distributed jobs if the cluster is large."),
                ("Time partitioning that does not match query filters forces full scans.",
                 "Time partitioning that does not match query filters still avoids full scans."),
                ("Small-file problems can dominate job time after years of tiny partitions.",
                 "Small-file problems cannot dominate job time in cloud object stores."),
                ("Compaction is part of table health, not optional cleanup theater.",
                 "Compaction is optional cleanup theater with no query impact."),
                ("Z-order or clustering choices should follow actual filter patterns.",
                 "Z-order or clustering choices can ignore actual filter patterns."),
            ]),
            ("privacy", [
                ("PII columns need classification and access controls in the lake too.",
                 "PII columns in the lake need less control than in OLTP."),
                ("Retention jobs must actually delete, not only stop new writes.",
                 "Stopping new writes is enough to satisfy retention deletion."),
                ("Derived features can re-identify people even after raw IDs are hashed poorly.",
                 "Hashing raw IDs always prevents re-identification in derived features."),
                ("Exports to vendors need the same purpose limitation as primary stores.",
                 "Exports to vendors are outside purpose limitation rules."),
                ("Access just this once to production PII often becomes permanent.",
                 "Access just this once to production PII does not become permanent."),
            ]),
            ("orchestration", [
                ("Sensor-based scheduling still needs timeout and stuck-sensor alarms.",
                 "Sensor-based scheduling needs no timeout if the sensor eventually fires."),
                ("Clear upstream/downstream edges beat hidden cron spaghetti.",
                 "Hidden cron spaghetti is fine if each job has a name."),
                ("Idempotent task design makes safe retries possible.",
                 "Idempotent task design is unnecessary if retries are rare."),
                ("Priority queues can starve low-priority critical compliance jobs.",
                 "Priority queues cannot starve compliance jobs."),
                ("Catchup mode after an outage can overload sources without pacing.",
                 "Catchup mode after an outage cannot overload sources."),
            ]),
            ("metrics", [
                ("Pipeline success rate can be green while emitting empty datasets.",
                 "Pipeline success rate being green proves datasets are non-empty and correct."),
                ("Freshness SLOs can be green while a critical table is stale if monitors are wrong.",
                 "Freshness SLOs being green proves every critical table is fresh."),
                ("Business KPIs need definitions that match the grain of the table.",
                 "Business KPIs need no grain match if the dashboard is pretty."),
                ("Reconciliation checks against a source system catch silent drift.",
                 "Reconciliation checks against a source system are redundant with job success."),
                ("Cost per successful partition is a useful operational metric.",
                 "Cost per successful partition is irrelevant to data engineering."),
            ]),
            ("contracts", [
                ("Producer-consumer contracts should include grain, keys, and late-data rules.",
                 "Producer-consumer contracts only need a table name."),
                ("Breaking a downstream BI contract needs a versioned migration plan.",
                 "Breaking a downstream BI contract needs no migration plan if SQL still parses."),
                ("Dataset owners must be reachable humans, not only distribution lists.",
                 "Dataset owners can be unreachable distribution lists."),
                ("SLAs without paging routes are wishes.",
                 "SLAs without paging routes are still enforceable."),
                ("Documented daily grain while the table is weekly betrays consumers.",
                 "Documented daily grain while the table is weekly is harmless."),
            ]),
        ])
    if level == 2:
        return _level_tradeoffs("DE")
    if level == 3:
        return _level_failures("DE")
    if level == 4:
        return _level_traps("DE")
    return _level_edge("DE")


def _do_level(level: int):
    if level == 1:
        return _ten([
            ("deploy", [
                ("Rollback plans should be rehearsed before peak traffic incidents.",
                 "Rollback plans only need to exist as unread wiki text."),
                ("Canaries that only check HTTP 200 can miss silent corruption.",
                 "HTTP 200 canaries prove a deploy did not corrupt data."),
                ("Mixed-version fleets during rolling deploys can expose protocol mismatches.",
                 "Mixed-version fleets never appear if CI passed."),
                ("Database migrations and app deploys ordered wrong can brick a fleet.",
                 "Migration and app order never matters if both artifacts are correct."),
                ("Feature flags need owners and expiry or they become permanent forks.",
                 "Feature flags need no owners or expiry."),
            ]),
            ("ci", [
                ("Flaky CI without quarantine expiry becomes ignored signal.",
                 "Flaky CI without quarantine expiry is a complete strategy."),
                ("Secrets in CI logs are still secrets.",
                 "Secrets in CI logs are fine because logs are internal."),
                ("Reproducible builds require pinned toolchains.",
                 "Reproducible builds do not require pinned toolchains."),
                ("Required checks that everyone can skip are not required.",
                 "Required checks that everyone can skip are still required."),
                ("Artifact provenance matters for supply-chain defense.",
                 "Artifact provenance is optional for supply-chain defense."),
            ]),
            ("obs", [
                ("Pages without runbooks push learning into the worst moment.",
                 "Pages without runbooks are fine for senior on-call."),
                ("Saturation metrics catch issues before hard errors.",
                 "Saturation metrics are unnecessary if error rate is watched."),
                ("High cardinality labels can take down a metrics stack.",
                 "High cardinality labels cannot take down a metrics stack."),
                ("Customer journey SLOs beat host CPU as a primary page signal.",
                 "Host CPU is a better primary page signal than customer journey SLOs."),
                ("Alert fatigue can be as dangerous as missing a real page.",
                 "More alerts always mean a safer system."),
            ]),
            ("iac", [
                ("IaC drift means the running system is not what was reviewed.",
                 "IaC drift is harmless if the UI console still works."),
                ("State locking prevents concurrent apply corruption.",
                 "State locking is optional for concurrent applies."),
                ("Blast radius of apply should be limited with workspaces or projects.",
                 "Blast radius of apply cannot be limited and should not be."),
                ("Secrets in Terraform state need hardened storage and access control.",
                 "Secrets in Terraform state are fine in any shared bucket."),
                ("Manual console changes create snowflake risk beside IaC.",
                 "Manual console changes beside IaC create no snowflake risk."),
            ]),
            ("capacity", [
                ("Autoscaling needs the right metric or it scales on noise.",
                 "Autoscaling on any metric is fine."),
                ("Load tests against empty data miss contention.",
                 "Load tests against empty data prove production contention."),
                ("Noisy neighbors on shared clusters can starve other tenants.",
                 "Tenant isolation is automatic on shared clusters."),
                ("Connection pools must respect datastore limits.",
                 "Connection pools can be unbounded if pods scale out."),
                ("Disk full on logging volumes can freeze request handling.",
                 "Disk full on logging volumes cannot freeze request handling."),
            ]),
            ("secrets", [
                ("Short-lived credentials beat long-lived static keys when feasible.",
                 "Long-lived static keys are preferable to short-lived credentials."),
                ("Secret rotation without dual-read windows can cause outages.",
                 "Secret rotation never needs dual-read windows."),
                ("Least privilege for deploy roles reduces blast radius of CI compromise.",
                 "Wide privilege for deploy roles is fine if CI is private."),
                ("Chat is not an acceptable secret distribution channel.",
                 "Chat is an acceptable secret distribution channel for emergencies forever."),
                ("Broken secret stores should fail closed for sensitive paths.",
                 "Broken secret stores should fail open for sensitive paths."),
            ]),
            ("network", [
                ("Egress allowlists reduce SSRF and data exfil paths.",
                 "Egress allowlists provide no security value."),
                ("mTLS between services reduces reliance on a flat trusted network.",
                 "mTLS between services is unnecessary on a flat trusted network."),
                ("DNS TTLs affect how fast failover is perceived by clients.",
                 "DNS TTLs do not affect failover perception."),
                ("Idle timeouts that disagree across hops create mystery disconnects.",
                 "Idle timeouts that disagree across hops cannot create disconnects."),
                ("Public admin interfaces need stronger controls than private ones.",
                 "Public admin interfaces can match private ones in controls."),
            ]),
            ("k8s", [
                ("Resource requests and limits that are wrong create noisy-neighbor or throttle pain.",
                 "Resource requests and limits that are wrong cannot affect neighbors."),
                ("Liveness probes that hit business dependencies can kill healthy pods in dependency blips.",
                 "Liveness probes that hit business dependencies are always ideal."),
                ("PodDisruptionBudgets matter during node drains.",
                 "PodDisruptionBudgets never matter during node drains."),
                ("Image tags like latest make rollbacks ambiguous.",
                 "Image tags like latest make rollbacks clearer."),
                ("Sidecars share fate with the main container in subtle failure modes.",
                 "Sidecars cannot share fate with the main container."),
            ]),
            ("dr", [
                ("Multi-AZ is not multi-region.",
                 "Multi-AZ is the same as multi-region."),
                ("Failover DNS without dependency failover can still strand users.",
                 "Failover DNS alone always completes dependency failover."),
                ("Restore drills prove RPO/RTO more than backup success checkmarks.",
                 "Backup success checkmarks prove RPO/RTO."),
                ("Config and secrets must be restorable with the data.",
                 "Config and secrets need not be restorable with the data."),
                ("Partial failover can split brain without fencing.",
                 "Partial failover cannot split brain if DNS flipped."),
            ]),
            ("culture", [
                ("Error budgets should gate launch velocity discussions.",
                 "Error budgets should not gate launch velocity discussions."),
                ("Toil inventories are required to improve platform leverage.",
                 "Toil inventories are optional theater."),
                ("Self-service without guardrails pushes risk to the least experienced.",
                 "Self-service without guardrails reduces risk."),
                ("Blameless postmortems still need owners and due dates for actions.",
                 "Blameless postmortems need no owners or due dates."),
                ("Hero culture hides missing automation behind sacrifice.",
                 "Hero culture is a sustainable operations strategy."),
            ]),
        ])
    if level == 2:
        return _level_tradeoffs("DO")
    if level == 3:
        return _level_failures("DO")
    if level == 4:
        return _level_traps("DO")
    return _level_edge("DO")


def _pa_level(level: int):
    return _arch_level("PA", level)


def _le_level(level: int):
    base = [
        ("goldens", [
            ("Goldens that leak into training make measured gains look fake.",
             "Goldens that leak into training still measure true generalization."),
            ("Small eval N can make leaderboard noise look like progress.",
             "Small eval N cannot make leaderboard noise look like progress."),
            ("Rubrics that the model can see can be gamed.",
             "Rubrics that the model can see cannot be gamed."),
            ("Inter-annotator agreement matters before trusting human goldens.",
             "Inter-annotator agreement is optional when judges are experts."),
            ("Slice metrics can reveal failures that overall averages hide.",
             "Overall averages cannot hide slice failures if the mean is high."),
        ]),
        ("judges", [
            ("LLM judges can share biases with the system under test.",
             "LLM judges are unbiased by construction."),
            ("Pairwise preferences can still be intransitive and noisy.",
             "Pairwise preferences are always transitive and low-noise."),
            ("Judge prompts need versioning like code.",
             "Judge prompts need no versioning."),
            ("Position bias in pairwise UI can skew preferences.",
             "Position bias in pairwise UI cannot skew preferences."),
            ("Calibration of judges should be checked against held-out human labels.",
             "Calibration of judges need not be checked against humans if scores look smooth."),
        ]),
        ("online", [
            ("Offline wins can fail online under distribution shift.",
             "Offline wins guarantee online wins."),
            ("Online metrics need holdouts to separate seasonality from lifts.",
             "Online metrics need no holdouts if dashboards move up."),
            ("Latency and cost are product metrics for LLM features, not only quality.",
             "Latency and cost are unrelated to LLM product quality."),
            ("Safety failures can be rare yet unacceptable.",
             "Rare safety failures are acceptable if average quality is high."),
            ("Tool-using agents need evals that include tool failure modes.",
             "Tool-using agents need only string-match answer evals."),
        ]),
        ("data", [
            ("Contamination checks should include paraphrases, not only exact string overlap.",
             "Contamination checks only need exact string overlap."),
            ("Synthetic data can amplify artifacts if not validated.",
             "Synthetic data cannot amplify artifacts."),
            ("PII in eval logs is still PII.",
             "PII in eval logs is fine because it is for measurement."),
            ("Vendor eval suites may not match your domain distribution.",
             "Vendor eval suites always match your domain distribution."),
            ("Refresh of goldens is required as product behavior drifts.",
             "Goldens never need refresh once published."),
        ]),
        ("process", [
            ("Eval gates in CI need flake budgets or they get disabled.",
             "Eval gates in CI need no flake budgets."),
            ("Owners must exist for failing slices, not only for the mean score.",
             "Owners only need to exist for the mean score."),
            ("Prompt changes are product changes and need eval diffs.",
             "Prompt changes need no eval diffs if demos look better."),
            ("Regression sets should include known historical failures.",
             "Regression sets should exclude known historical failures to stay green."),
            ("Reporting should include confidence intervals when N is small.",
             "Reporting can ignore uncertainty when N is small."),
        ]),
    ]
    # pad to 10 themes by densifying
    while len(base) < 10:
        base.append(base[len(base) % 5])
    # make unique theme names
    out = []
    for i, (name, pairs) in enumerate(base[:10]):
        out.append((f"{name}_{i+1}", pairs))
    if level == 1:
        return _ten(out)
    if level == 2:
        return _level_tradeoffs("LE")
    if level == 3:
        return _level_failures("LE")
    if level == 4:
        return _level_traps("LE")
    return _level_edge("LE")


def _ml_level(level: int):
    if level == 1:
        return _ten([
            ("skew", [
                ("Train/serving skew can make a strong offline model fail online.",
                 "Train/serving skew cannot make a strong offline model fail online."),
                ("Feature pipelines must match between training and serving.",
                 "Feature pipelines can differ freely between training and serving."),
                ("Label leakage can inflate offline metrics unrealistically.",
                 "Label leakage cannot inflate offline metrics."),
                ("Time-based splits often beat random splits for temporal data.",
                 "Random splits are always better than time-based splits for temporal data."),
                ("Calibration matters when scores drive thresholds or ranking.",
                 "Calibration never matters when scores drive thresholds."),
            ]),
            ("data", [
                ("Class imbalance can make accuracy a misleading headline metric.",
                 "Accuracy is never misleading under class imbalance."),
                ("Data drift monitors belong beside model accuracy monitors.",
                 "Data drift monitors are unnecessary if accuracy is watched."),
                ("PII in training sets needs the same controls as production stores.",
                 "PII in training sets needs fewer controls than production stores."),
                ("Annotation guidelines must be versioned with the labels.",
                 "Annotation guidelines need no versioning."),
                ("Hard negatives often teach more than more easy negatives.",
                 "More easy negatives always teach more than hard negatives."),
            ]),
            ("serving", [
                ("Model latency is a product constraint, not only an infra metric.",
                 "Model latency is only an infra metric."),
                ("Shadow deployment can compare models without user impact when designed carefully.",
                 "Shadow deployment needs no careful design to avoid user impact."),
                ("Feature store freshness SLAs affect online quality.",
                 "Feature store freshness SLAs cannot affect online quality."),
                ("Fallback behavior when the model is down must be explicit.",
                 "Fallback behavior when the model is down can be improvised during the outage."),
                ("Batch scoring and online scoring can disagree if code paths diverge.",
                 "Batch scoring and online scoring cannot disagree if both use the same model file."),
            ]),
            ("eval", [
                ("Business metrics can diverge from ML proxy metrics.",
                 "Business metrics always move with ML proxy metrics."),
                ("Slice evaluation can reveal subgroup failures averages hide.",
                 "Averages cannot hide subgroup failures."),
                ("Offline A/B proxies still need online confirmation.",
                 "Offline A/B proxies replace online confirmation."),
                ("Seed sensitivity can make small gains look real.",
                 "Seed sensitivity cannot make small gains look real."),
                ("Human eval is still needed for many generative tasks.",
                 "Automatic metrics fully replace human eval for generative tasks."),
            ]),
            ("ops", [
                ("Model cards and change logs help when incidents need lineage.",
                 "Model cards and change logs are unnecessary when incidents need lineage."),
                ("Rollback to a previous model artifact should be a rehearsed path.",
                 "Rollback to a previous model artifact need not be rehearsed."),
                ("Training job idempotency avoids duplicate expensive runs.",
                 "Training job idempotency is unnecessary because runs are rare."),
                ("GPU utilization dashboards without quality signals can optimize the wrong thing.",
                 "GPU utilization dashboards without quality signals are sufficient."),
                ("Cost per successful prediction belongs in capacity planning.",
                 "Cost per successful prediction is irrelevant to capacity planning."),
            ]),
            ("features", [
                ("Point-in-time correct features are required to avoid leakage.",
                 "Point-in-time correctness is optional to avoid leakage."),
                ("Categorical explosions can blow memory and latency.",
                 "Categorical explosions cannot blow memory and latency."),
                ("Missing-value policies must match between train and serve.",
                 "Missing-value policies can differ between train and serve."),
                ("Feature importance alone does not prove causality.",
                 "Feature importance alone proves causality."),
                ("Raw IDs as features can overfit to historical entities.",
                 "Raw IDs as features cannot overfit to historical entities."),
            ]),
            ("safety", [
                ("Abuse and jailbreak evals belong in release gates for user-facing models.",
                 "Abuse and jailbreak evals are optional for user-facing models."),
                ("Output filtering is not a substitute for upstream threat modeling.",
                 "Output filtering fully substitutes for upstream threat modeling."),
                ("Training data licenses can block commercial use even if quality is high.",
                 "Training data licenses cannot block commercial use if quality is high."),
                ("Feedback loops can amplify biased decisions over time.",
                 "Feedback loops cannot amplify biased decisions over time."),
                ("Human override paths matter when models act on users.",
                 "Human override paths are unnecessary when models act on users."),
            ]),
            ("exp", [
                ("Holdout users protect you from seasonality illusions.",
                 "Holdout users are unnecessary if metrics move up."),
                ("Peeking at experiments repeatedly inflates false wins.",
                 "Peeking at experiments repeatedly cannot inflate false wins."),
                ("Interaction effects between concurrent experiments need planning.",
                 "Interaction effects between concurrent experiments need no planning."),
                ("Guardrail metrics should be watched alongside primary metrics.",
                 "Guardrail metrics are optional when primary metrics rise."),
                ("Underpowered experiments waste org attention.",
                 "Underpowered experiments cannot waste org attention."),
            ]),
            ("pipeline", [
                ("Reproducible training needs pinned data snapshots and code versions.",
                 "Reproducible training needs only the final model weights."),
                ("Failed training retries can duplicate side effects without care.",
                 "Failed training retries cannot duplicate side effects."),
                ("Schema checks on feature inputs catch many silent serving breaks.",
                 "Schema checks on feature inputs catch nothing useful."),
                ("Model registry stage transitions should be gated.",
                 "Model registry stage transitions need no gates."),
                ("Offline debug dumps can leak PII if not redacted.",
                 "Offline debug dumps cannot leak PII."),
            ]),
            ("product", [
                ("Confidence displays can mislead if calibration is poor.",
                 "Confidence displays cannot mislead if the UI is pretty."),
                ("Explanations that are wrong can be worse than no explanation.",
                 "Explanations that are wrong are still better than no explanation always."),
                ("Latency budgets affect which model classes are viable.",
                 "Latency budgets do not affect which model classes are viable."),
                ("Human-in-the-loop design changes error costs.",
                 "Human-in-the-loop design cannot change error costs."),
                ("Silent model swaps can break user mental models.",
                 "Silent model swaps cannot break user mental models."),
            ]),
        ])
    if level == 2:
        return _level_tradeoffs("ML")
    if level == 3:
        return _level_failures("ML")
    if level == 4:
        return _level_traps("ML")
    return _level_edge("ML")


def _fe_level(level: int):
    if level == 1:
        return _ten([
            ("a11y", [
                ("Keyboard access and semantic HTML are part of correctness, not polish.",
                 "Keyboard access and semantic HTML are polish that can wait forever."),
                ("Color alone should not be the only way to convey state.",
                 "Color alone is enough to convey state."),
                ("Focus management matters in modal flows.",
                 "Focus management does not matter in modal flows."),
                ("Accessible names on icon buttons are required.",
                 "Accessible names on icon buttons are optional."),
                ("Motion that cannot be reduced can harm some users.",
                 "Motion that cannot be reduced cannot harm users."),
            ]),
            ("perf", [
                ("Largest Contentful Paint regressions are user-visible performance bugs.",
                 "Largest Contentful Paint regressions are not user-visible."),
                ("Layout shift from late-loading media is a quality defect.",
                 "Layout shift from late-loading media is not a quality defect."),
                ("Bundle size affects mobile users more than desktop lab machines suggest.",
                 "Bundle size cannot affect mobile users differently than desktop labs."),
                ("Unnecessary re-renders can dominate interaction latency.",
                 "Unnecessary re-renders cannot dominate interaction latency."),
                ("Caching headers that are wrong can freeze broken UI for returning users.",
                 "Caching headers that are wrong cannot freeze broken UI."),
            ]),
            ("security", [
                ("innerHTML with untrusted strings is a classic XSS sink.",
                 "innerHTML with untrusted strings cannot be an XSS sink in modern browsers."),
                ("CSP can reduce XSS impact when designed carefully.",
                 "CSP cannot reduce XSS impact."),
                ("Tokens in localStorage are more XSS-exposed than httpOnly cookies in many designs.",
                 "Tokens in localStorage are never more XSS-exposed than httpOnly cookies."),
                ("Open redirects can turn phishing into a first-party looking URL.",
                 "Open redirects cannot help phishing."),
                ("Dependency XSS in UI libraries is still your user risk.",
                 "Dependency XSS in UI libraries is never your user risk."),
            ]),
            ("state", [
                ("Client state that diverges from server truth creates heisenbugs.",
                 "Client state that diverges from server truth cannot create bugs."),
                ("Optimistic UI needs rollback when the server rejects the write.",
                 "Optimistic UI needs no rollback when the server rejects the write."),
                ("URL state that is shareable beats hidden-only client memory for many flows.",
                 "Hidden-only client memory always beats shareable URL state."),
                ("Race conditions between slow responses can show stale screens.",
                 "Race conditions between slow responses cannot show stale screens."),
                ("Forms need explicit dirty and submit semantics under concurrency.",
                 "Forms need no explicit dirty semantics under concurrency."),
            ]),
            ("hydration", [
                ("Server/client HTML mismatches can break hydration and event handlers.",
                 "Server/client HTML mismatches cannot break hydration."),
                ("Random IDs generated differently on server and client cause mismatch warnings.",
                 "Random IDs generated differently on server and client are harmless."),
                ("Auth-gated SSR content needs a clear story for bots and users.",
                 "Auth-gated SSR content needs no clear story for bots and users."),
                ("Streaming SSR still needs error boundaries for partial failure.",
                 "Streaming SSR needs no error boundaries for partial failure."),
                ("Caching personalized SSR without vary rules can leak data across users.",
                 "Caching personalized SSR without vary rules cannot leak data."),
            ]),
            ("ux", [
                ("Empty, loading, and error states are part of the feature.",
                 "Empty, loading, and error states are optional if the happy path works."),
                ("Destructive actions need confirmation or undo when stakes are high.",
                 "Destructive actions never need confirmation or undo."),
                ("Offline or flaky network UX matters for mobile.",
                 "Offline or flaky network UX does not matter for mobile."),
                ("Time zones and locales break naive date formatting.",
                 "Time zones and locales cannot break date formatting."),
                ("Internationalized strings change layout assumptions.",
                 "Internationalized strings cannot change layout assumptions."),
            ]),
            ("testing", [
                ("Tests that assert on implementation class names are brittle.",
                 "Tests that assert on implementation class names are ideal."),
                ("Visual regression can lock in accidental bugs as goldens.",
                 "Visual regression cannot lock in accidental bugs."),
                ("Accessibility linting catches some issues automation still misses in flows.",
                 "Accessibility linting catches every issue automation would miss."),
                ("Contract tests with backend schemas catch many UI breaks early.",
                 "Contract tests with backend schemas catch nothing beyond UI unit tests."),
                ("Flaky Playwright tests need root-cause work, not only retries.",
                 "Flaky Playwright tests only need more retries."),
            ]),
            ("architecture", [
                ("Design systems need versioning when many apps consume them.",
                 "Design systems need no versioning when many apps consume them."),
                ("CSS specificity wars are a maintainability defect.",
                 "CSS specificity wars are not a maintainability defect."),
                ("Microfrontends add isolation and also operational complexity.",
                 "Microfrontends add isolation with no operational complexity."),
                ("Public UI events are contracts, including versioning.",
                 "Public UI events are not contracts."),
                ("Feature flags in UI still need cleanup plans.",
                 "Feature flags in UI need no cleanup plans."),
            ]),
            ("network", [
                ("Pagination and filtering belong on the server for large collections.",
                 "Pagination and filtering can always stay only on the client for large collections."),
                ("Timeouts and retries in the UI can amplify backend load.",
                 "Timeouts and retries in the UI cannot amplify backend load."),
                ("Uploads need size limits and clear failure messaging.",
                 "Uploads need no size limits if the backend is strong."),
                ("Stale-while-revalidate can show old data that looks authoritative.",
                 "Stale-while-revalidate cannot show old data that looks authoritative."),
                ("CORS misconfig can block legitimate apps or open risky origins.",
                 "CORS misconfig cannot open risky origins."),
            ]),
            ("release", [
                ("Source maps in production need access control.",
                 "Source maps in production need no access control."),
                ("Canary UI releases should watch error rates and Core Web Vitals.",
                 "Canary UI releases need only a screenshot check."),
                ("Breaking change communication is required for shared component libraries.",
                 "Breaking change communication is optional for shared component libraries."),
                ("Client-side feature kill switches help during incidents.",
                 "Client-side feature kill switches do not help during incidents."),
                ("Asset cache busting is required when filenames are reused.",
                 "Asset cache busting is optional when filenames are reused."),
            ]),
        ])
    if level == 2:
        return _level_tradeoffs("FE")
    if level == 3:
        return _level_failures("FE")
    if level == 4:
        return _level_traps("FE")
    return _level_edge("FE")


def _sec_level(level: int):
    if level == 1:
        return _ten([
            ("auth", [
                ("Authentication is not the same as authorization.",
                 "Authentication is the same as authorization."),
                ("Broken object-level authorization is a common API failure mode.",
                 "Broken object-level authorization is rare and unimportant in APIs."),
                ("Session fixation and token theft need distinct mitigations.",
                 "Session fixation and token theft need the same single mitigation."),
                ("MFA reduces account takeover but does not remove phishing risk entirely.",
                 "MFA removes phishing risk entirely."),
                ("Service accounts need least privilege and rotation.",
                 "Service accounts can keep admin forever if used rarely."),
            ]),
            ("injection", [
                ("Parameterized queries are the baseline defense against SQL injection.",
                 "Parameterized queries are optional if you sanitize quotes yourself."),
                ("Command injection risk rises when shelling out with user input.",
                 "Command injection risk does not rise when shelling out with user input."),
                ("ORM use does not automatically eliminate injection if raw SQL is embedded.",
                 "ORM use automatically eliminates injection even with raw SQL embeds."),
                ("Header injection can enable response splitting in poorly designed stacks.",
                 "Header injection cannot enable response splitting."),
                ("Template injection can be as dangerous as classic XSS in some engines.",
                 "Template injection cannot be as dangerous as classic XSS."),
            ]),
            ("xss_csrf", [
                ("CSP is defense in depth, not a reason to skip output encoding.",
                 "CSP is a reason to skip output encoding."),
                ("CSRF protections matter for cookie-authenticated state-changing requests.",
                 "CSRF protections never matter for cookie-authenticated state-changing requests."),
                ("DOM XSS can occur entirely in client-side JavaScript sinks.",
                 "DOM XSS cannot occur entirely in client-side JavaScript sinks."),
                ("TrustedTypes can reduce DOM XSS when adopted carefully.",
                 "TrustedTypes cannot reduce DOM XSS."),
                ("Markdown rendering without sanitization can become XSS.",
                 "Markdown rendering without sanitization cannot become XSS."),
            ]),
            ("ssrf_supply", [
                ("SSRF risk rises when servers fetch user-supplied URLs.",
                 "SSRF risk does not rise when servers fetch user-supplied URLs."),
                ("Dependency pinning and advisories are part of vulnerability management.",
                 "Dependency pinning and advisories are unrelated to vulnerability management."),
                ("Build provenance helps detect tampered artifacts.",
                 "Build provenance cannot help detect tampered artifacts."),
                ("Signing alone does not prove an artifact is free of vulns.",
                 "Signing alone proves an artifact is free of vulns."),
                ("Egress controls reduce SSRF usefulness to attackers.",
                 "Egress controls cannot reduce SSRF usefulness to attackers."),
            ]),
            ("secrets", [
                ("Secrets in chat and tickets are still secrets.",
                 "Secrets in chat and tickets are fine because access is limited."),
                ("Git history can retain secrets after a later delete.",
                 "Git history cannot retain secrets after a later delete."),
                ("Short-lived credentials reduce blast radius versus static keys.",
                 "Static keys reduce blast radius versus short-lived credentials."),
                ("Logging tokens is a credential leak.",
                 "Logging tokens is fine for debugging."),
                ("Secret stores should fail closed for sensitive operations when unavailable.",
                 "Secret stores should fail open for sensitive operations when unavailable."),
            ]),
            ("threat", [
                ("Threat models should include abuse by authenticated users.",
                 "Threat models can ignore abuse by authenticated users."),
                ("Data-flow diagrams help find trust-boundary crossings.",
                 "Data-flow diagrams do not help find trust-boundary crossings."),
                ("Security questionnaires cannot replace testing of real controls.",
                 "Security questionnaires replace testing of real controls."),
                ("Annual pen tests are snapshots, not continuous assurance.",
                 "Annual pen tests are continuous assurance."),
                ("Insider risk belongs in the model for privileged tools.",
                 "Insider risk can be ignored for privileged tools."),
            ]),
            ("crypto", [
                ("Home-grown crypto is usually a defect, not a differentiator.",
                 "Home-grown crypto is usually a differentiator, not a defect."),
                ("TLS misconfig can leave you with encryption theater.",
                 "TLS misconfig cannot leave you with encryption theater."),
                ("Encryption at rest does not fix over-broad application read access.",
                 "Encryption at rest fixes over-broad application read access."),
                ("Password hashing needs modern slow hashes and parameters.",
                 "Password hashing can use fast general-purpose hashes."),
                ("IV or nonce misuse can destroy semantic security.",
                 "IV or nonce misuse cannot destroy semantic security."),
            ]),
            ("detect", [
                ("Detection without response playbooks is incomplete.",
                 "Detection without response playbooks is complete."),
                ("High false-positive alert streams train people to ignore pages.",
                 "High false-positive alert streams improve security culture."),
                ("Audit logs need integrity protections and retention.",
                 "Audit logs need no integrity protections if stored somewhere."),
                ("Canary tokens can detect some credential misuse.",
                 "Canary tokens cannot detect any credential misuse."),
                ("Time to contain matters as much as time to detect.",
                 "Time to contain matters less than time to detect always."),
            ]),
            ("appsec", [
                ("Security review for money and auth paths should be harder to skip than for copy changes.",
                 "Security review for money and auth paths can be skipped like copy changes."),
                ("SAST without triage ownership becomes noise.",
                 "SAST without triage ownership is still fully effective."),
                ("DAST complements SAST; neither replaces the other alone.",
                 "DAST fully replaces SAST alone."),
                ("Threat modeling early is cheaper than redesign after build.",
                 "Threat modeling early is more expensive than redesign after build."),
                ("Bypass of security control for a demo often becomes the production path.",
                 "Bypass of security control for a demo never becomes the production path."),
            ]),
            ("privacy", [
                ("Purpose limitation still applies when engineering wants richer logs.",
                 "Purpose limitation does not apply to engineering logs."),
                ("Deletion requests need engineered paths, not only policy text.",
                 "Deletion requests need only policy text, not engineered paths."),
                ("Vendor subprocessors inherit your privacy obligations in practice.",
                 "Vendor subprocessors do not inherit your privacy obligations in practice."),
                ("Minimization beats collecting everything for possible future ML.",
                 "Collecting everything for possible future ML beats minimization."),
                ("Access reviews for production PII should be recurring.",
                 "Access reviews for production PII can be one-time at hire."),
            ]),
        ])
    if level == 2:
        return _level_tradeoffs("SEC")
    if level == 3:
        return _level_failures("SEC")
    if level == 4:
        return _level_traps("SEC")
    return _level_edge("SEC")


def _qa_level(level: int):
    if level == 1:
        return _ten([
            ("oracle", [
                ("Knowing the expected outcome is required; automation without an oracle is incomplete.",
                 "Automation without an oracle is complete if it clicks through screens."),
                ("Exploratory testing finds classes of bugs scripted paths miss.",
                 "Exploratory testing finds nothing beyond scripted paths."),
                ("Risk-based test selection beats attempting infinite coverage.",
                 "Attempting infinite coverage beats risk-based test selection."),
                ("Production signals are part of quality evidence, not only pre-prod suites.",
                 "Production signals are not part of quality evidence."),
                ("Flakes that are ignored become cultural debt.",
                 "Flakes that are ignored have no cultural effect."),
            ]),
            ("coverage", [
                ("Coverage percent is not the same as confidence in important behaviors.",
                 "Coverage percent is the same as confidence in important behaviors."),
                ("Asserting the wrong property can make green tests lie.",
                 "Asserting the wrong property cannot make green tests lie."),
                ("Boundary cases often fail where mid-range examples pass.",
                 "Boundary cases never fail where mid-range examples pass."),
                ("Contract tests catch producer/consumer drift early.",
                 "Contract tests catch nothing beyond unit tests."),
                ("Snapshot goldens can lock accidental bugs in place.",
                 "Snapshot goldens cannot lock accidental bugs in place."),
            ]),
            ("automation", [
                ("UI automation that is brittle to CSS selectors will thrash teams.",
                 "UI automation that is brittle to CSS selectors is ideal."),
                ("API-level checks often give faster signal than full UI paths.",
                 "Full UI paths always give faster signal than API-level checks."),
                ("Test data management is part of automation design.",
                 "Test data management is outside automation design."),
                ("Parallel test runs can reveal races that serial runs hide.",
                 "Parallel test runs cannot reveal races that serial runs hide."),
                ("Quarantine without expiry dates becomes a junk drawer.",
                 "Quarantine without expiry dates is a complete strategy."),
            ]),
            ("release", [
                ("Exit criteria should include known risk acceptance with owners.",
                 "Exit criteria need no risk acceptance with owners if executives want to ship."),
                ("Canary observation is part of release testing.",
                 "Canary observation is not part of release testing."),
                ("Rollback drills belong in quality strategy.",
                 "Rollback drills do not belong in quality strategy."),
                ("Hotfix regression should include neighboring paths.",
                 "Hotfix regression need not include neighboring paths."),
                ("Release notes that omit known defects hide support load.",
                 "Release notes that omit known defects reduce noise usefully always."),
            ]),
            ("envs", [
                ("Environment drift between test and prod creates false greens.",
                 "Environment drift between test and prod cannot create false greens."),
                ("Synthetic data that lacks real edge shapes misses bugs.",
                 "Synthetic data that lacks real edge shapes still finds all bugs."),
                ("PII in test environments is still a privacy issue.",
                 "PII in test environments is not a privacy issue."),
                ("Service virtualization can help and can also hide contract changes.",
                 "Service virtualization cannot hide contract changes."),
                ("Time travel and clock control matter for schedule-sensitive tests.",
                 "Time travel and clock control never matter for schedule-sensitive tests."),
            ]),
            ("perf_a11y", [
                ("Performance budgets are quality requirements.",
                 "Performance budgets are not quality requirements."),
                ("Accessibility checks are quality requirements, not optional polish.",
                 "Accessibility checks are optional polish, not quality requirements."),
                ("Load tests against empty datasets miss contention.",
                 "Load tests against empty datasets prove contention behavior."),
                ("Chaos and failure injection validate monitoring and recovery.",
                 "Chaos and failure injection validate nothing beyond happy-path functional tests."),
                ("Mobile network constraints change what desktop green means.",
                 "Mobile network constraints cannot change what desktop green means."),
            ]),
            ("process", [
                ("Bugs need reproducible steps and expected vs actual.",
                 "Bugs need no reproducible steps if severity is high."),
                ("Severity and priority are not identical.",
                 "Severity and priority are identical."),
                ("Test plans should track requirements traceability for regulated paths.",
                 "Test plans need no requirements traceability for regulated paths."),
                ("Pairing testers early with design reduces late rework.",
                 "Pairing testers early with design increases late rework."),
                ("Definition of Done without testability criteria ships debt.",
                 "Definition of Done without testability criteria is still complete."),
            ]),
            ("security_privacy", [
                ("Security test charters belong in QA for auth and money flows.",
                 "Security test charters never belong in QA."),
                ("Privacy deletion paths need tests, not only policy statements.",
                 "Privacy deletion paths need only policy statements."),
                ("Permission matrix tests catch broken access control.",
                 "Permission matrix tests catch nothing important."),
                ("Logging assertions should include secret non-presence checks where relevant.",
                 "Logging assertions should never include secret non-presence checks."),
                ("Dependency vulnerability gates are part of release quality.",
                 "Dependency vulnerability gates are not part of release quality."),
            ]),
            ("metrics", [
                ("Escape rate of defects to prod is a useful quality signal.",
                 "Escape rate of defects to prod is not a useful quality signal."),
                ("MTTR after user-visible failures belongs on the quality dashboard.",
                 "MTTR after user-visible failures does not belong on the quality dashboard."),
                ("Flake rate of CI is a first-class metric.",
                 "Flake rate of CI is not a first-class metric."),
                ("Counting test cases alone can incentivize shallow tests.",
                 "Counting test cases alone cannot incentivize shallow tests."),
                ("Customer support themes can guide regression mining.",
                 "Customer support themes cannot guide regression mining."),
            ]),
            ("collab", [
                ("QA owning quality alone without engineering partnership fails.",
                 "QA owning quality alone without engineering partnership succeeds."),
                ("Shift-left still needs shift-right production evidence.",
                 "Shift-left removes the need for shift-right production evidence."),
                ("Clear bug ownership beats bugs bouncing between teams.",
                 "Bugs bouncing between teams is a healthy process."),
                ("Testability reviews of designs prevent untestable features.",
                 "Testability reviews of designs cannot prevent untestable features."),
                ("Celebrating only ship dates underweights prevented incidents.",
                 "Celebrating only ship dates correctly weights prevented incidents."),
            ]),
        ])
    if level == 2:
        return _level_tradeoffs("QA")
    if level == 3:
        return _level_failures("QA")
    if level == 4:
        return _level_traps("QA")
    return _level_edge("QA")


def build_role_batch(role_key: str, label: str, prefix: str) -> dict:
    levels_out = {}
    for lv in ("1", "2", "3", "4", "5"):
        title, blurb = LEVEL_META[lv]
        theme_list = BANKS[role_key][lv]
        slots = []
        for si, (theme, variants_tf) in enumerate(theme_list, start=1):
            variants = []
            for vi in range(5):
                want_true = bool(PATTERNS[vi][si - 1])
                true_s, false_s = variants_tf[vi]
                text = true_s if want_true else false_s
                variants.append(
                    {
                        "id": f"{prefix}-L{lv}-S{si:02d}-V{vi+1}",
                        "text": text,
                        "answer": want_true,
                    }
                )
            slots.append({"slot": si, "theme": theme, "variants": variants})
        levels_out[lv] = {"title": title, "blurb": blurb, "slots": slots}
    return {"label": label, "levels": levels_out}


def write_batches() -> dict:
    build_banks()
    all_roles = {}
    batches = [
        ROLE_ORDER[0:4],
        ROLE_ORDER[4:8],
        ROLE_ORDER[8:12],
    ]
    for bi, group in enumerate(batches, start=1):
        roles = {}
        for key, label, prefix in group:
            roles[key] = build_role_batch(key, label, prefix)
            all_roles[key] = roles[key]
        path = BATCH_DIR / f"roles_batch_{bi}.json"
        path.write_text(
            json.dumps({"batch": bi, "roles": roles}, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
        print("wrote", path)
    return all_roles


def to_runtime(roles: dict) -> dict:
    variants_out = {}
    for vi, vname in enumerate(["V1", "V2", "V3", "V4", "V5"], start=1):
        role_map = {}
        for key, label, _prefix in ROLE_ORDER:
            src = roles[key]
            levels_out = {}
            for lv, meta in LEVEL_META.items():
                slots = src["levels"][lv]["slots"]
                items = []
                for slot in slots:
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
                levels_out[lv] = {
                    "title": meta[0],
                    "blurb": meta[1],
                    "items": items,
                }
            role_map[key] = {"label": label, "levels": levels_out}
        variants_out[vname] = {
            "variant": vname,
            "variantIndex": vi,
            "roles": role_map,
        }
    return {
        "version": 6,
        "format": "true_false",
        "maxLevel": 5,
        "variantCount": 5,
        "totalItems": 3000,
        "note": (
            "Challenge v6: five levels × 10 questions × 5 variant packs × 12 roles. "
            "Technical stems; True-count gated to 5/10 per pack via patterns; "
            "always-True can no longer score ~100% on failure-mode-only packs."
        ),
        "levelMeta": {
            k: {"title": v[0], "blurb": v[1]} for k, v in LEVEL_META.items()
        },
        "variants": variants_out,
    }


def gate(runtime: dict) -> list[str]:
    issues = []
    soft_re = re.compile(
        r"\b(professional|teammate|basic duty|skip reading the ticket|"
        r"code review helps|trusted reviewer|clearly more productive)\b",
        re.I,
    )
    soft = 0
    total = 0
    extreme = 0
    for vn, v in runtime["variants"].items():
        for role, rdata in v["roles"].items():
            for lv, pack in rdata["levels"].items():
                items = pack["items"]
                t = sum(1 for i in items if i["answer"] is True)
                if t < 3 or t > 7:
                    issues.append(f"{role} {vn} L{lv} True={t}")
                    extreme += 1
                for it in items:
                    total += 1
                    if soft_re.search(it["text"] or ""):
                        soft += 1
                    if "\u2014" in (it["text"] or ""):
                        issues.append(f"emdash {it['id']}")
    if total != 3000:
        issues.append(f"total {total}")
    soft_rate = 100.0 * soft / max(total, 1)
    if soft_rate > 5:
        issues.append(f"soft rate {soft_rate:.1f}%")
    print("gate extreme packs", extreme, "soft_rate", round(soft_rate, 2), "issues", len(issues))
    return issues


def bump_cache() -> None:
    text = PRICKLY_JS.read_text(encoding="utf-8")
    text2 = text.replace(
        "prickly-dev-banks-variants.json?v=5",
        "prickly-dev-banks-variants.json?v=6",
    )
    if text2 == text:
        # already bumped or different
        text2 = re.sub(
            r"prickly-dev-banks-variants\.json\?v=\d+",
            "prickly-dev-banks-variants.json?v=6",
            text,
        )
    PRICKLY_JS.write_text(text2, encoding="utf-8")
    print("bumped prickly.js cache to v=6")


def main() -> int:
    BATCH_DIR.mkdir(parents=True, exist_ok=True)
    roles = write_batches()
    runtime = to_runtime(roles)
    issues = gate(runtime)
    RUNTIME.write_text(json.dumps(runtime, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print("wrote", RUNTIME)
    bump_cache()
    # sample proof
    se = runtime["variants"]["V1"]["roles"]["software_engineer"]["levels"]
    print("SE L1 V1 True", sum(1 for i in se["1"]["items"] if i["answer"]), se["1"]["items"][0]["text"][:90])
    print("SE L5 V1 True", sum(1 for i in se["5"]["items"] if i["answer"]), se["5"]["items"][0]["text"][:90])
    sec = runtime["variants"]["V1"]["roles"]["security_engineer"]["levels"]["3"]["items"]
    print("SEC L3 V1 True", sum(1 for i in sec if i["answer"]), "(was 10)")
    if issues:
        print("GATE FAIL")
        for i in issues[:30]:
            print(" -", i)
        return 1
    print("GATE PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
