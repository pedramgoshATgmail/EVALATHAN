"""Curated fallback generator for PRICKLY 12×5×10×5 = 3000 T/F items.

Writes roles_batch_{1,2,3}.json if missing or --force.
Each stem is role- and level-specific; variants within a slot share a theme
but use distinct scenarios (not noun-swap clones across roles).
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "ui" / "v2" / "assets" / "prickly_variants"

LEVEL_META = {
    "1": ("Level 1 - Foundations", "Clear basics. Spot obvious false comfort."),
    "2": ("Level 2 - Trade-offs", "Two good-looking options; only one is sound."),
    "3": ("Level 3 - Failure modes", "What breaks under load, time, or bad incentives."),
    "4": ("Level 4 - Precedents & traps", "Industry-familiar traps dressed as best practice."),
    "5": ("Level 5 - Edge judgment", "Subtle cases where polite process still fails the user."),
}

# Role packs: each level has 10 themes; each theme has 5 (text, answer) variants.
# Answers mix True/False; aim ~5/5 when reading a single variant index across slots.


def _pack(prefix: str, label: str, levels: dict) -> dict:
    out_levels = {}
    for lv, themes in levels.items():
        title, blurb = LEVEL_META[lv]
        slots = []
        for i, (theme, variants) in enumerate(themes, start=1):
            assert len(variants) == 5, (prefix, lv, theme, len(variants))
            slots.append(
                {
                    "slot": i,
                    "theme": theme,
                    "variants": [
                        {
                            "id": f"{prefix}-L{lv}-S{i:02d}-V{j}",
                            "text": text.replace("\u2014", "-").replace("\u2013", "-"),
                            "answer": bool(ans),
                        }
                        for j, (text, ans) in enumerate(variants, start=1)
                    ],
                }
            )
        assert len(slots) == 10, (prefix, lv, len(slots))
        out_levels[lv] = {"title": title, "blurb": blurb, "slots": slots}
    return {"label": label, "levels": out_levels}


def programmer() -> dict:
    return _pack(
        "PG",
        "Programmer",
        {
            "1": [
                (
                    "readiness_gate",
                    [
                        ("If the code runs without crashing, that alone proves it is ready for paying users.", False),
                        ("Green unit tests with zero integration checks are enough to ship to paying users.", False),
                        ("A feature that only works on the author's laptop is ready for every customer machine.", False),
                        ("Skipping a smoke check is fine when the change is under ten lines and touches login.", False),
                        ("Shipping behind a feature flag still needs a basic readiness check for the flagged path.", True),
                    ],
                ),
                (
                    "intermittent_bugs",
                    [
                        ("A bug that only shows up once a week is still worth tracking before a release.", True),
                        ("Flaky failures that vanish on retry can be ignored forever if the dashboard looks green.", False),
                        ("If a defect is hard to reproduce, documenting the known trigger is better than pretending it does not exist.", True),
                        ("Rare production crashes are acceptable if they have never happened in a demo.", False),
                        ("Logging enough context to reproduce an intermittent bug is part of fixing it.", True),
                    ],
                ),
                (
                    "copied_code",
                    [
                        ("Pasting a Stack Overflow snippet into production without reading it is fine if tests pass later.", False),
                        ("Using an unread library sample that touches secrets is still unsafe even when the build is green.", True),
                        ("License and security review of copied code can wait until after launch day.", False),
                        ("Understanding a borrowed algorithm before shipping it is part of responsible programming.", True),
                        ("If a snippet 'worked for someone online', it automatically fits your threat model.", False),
                    ],
                ),
                (
                    "naming_clarity",
                    [
                        ("Clear names for variables and functions help the next person, including future you.", True),
                        ("Short cryptic names are fine in hot paths because reviewers never read them anyway.", False),
                        ("Renaming a confusing public function is wasted work if the code already runs.", False),
                        ("A name that states intent reduces the chance of a wrong edit later.", True),
                        ("Comments that restate a bad name are a substitute for fixing the name.", False),
                    ],
                ),
                (
                    "env_parity",
                    [
                        ("If a feature works on your laptop, it will automatically work the same way for customers.", False),
                        ("Different OS, locale, or dependency versions can change behavior even when local demos pass.", True),
                        ("Matching production config in a staging check is optional for small edits.", False),
                        ("A missing environment variable that only exists on your machine is a release risk.", True),
                        ("Customer machines can be assumed identical to the developer workstation.", False),
                    ],
                ),
                (
                    "design_before_edit",
                    [
                        ("Writing down what a tricky function should do can save more time than jumping straight into edits.", True),
                        ("For a money-moving change, a one-paragraph intent note before coding is wasted ceremony.", False),
                        ("Sketching edge cases before coding reduces surprise failures in review.", True),
                        ("If you already know the language well, design notes are never useful.", False),
                        ("A short acceptance checklist before coding helps you know when you are done.", True),
                    ],
                ),
                (
                    "dead_code",
                    [
                        ("Deleting unused code is riskier than leaving dead code forever, so dead code should never be removed.", False),
                        ("Dead paths that still compile can confuse the next fix and hide real bugs.", True),
                        ("Keeping commented-out blocks for years is a valid substitute for version control history.", False),
                        ("Removing unreachable code after confirming nothing calls it is normal hygiene.", True),
                        ("Dead feature flags that always evaluate one way should stay forever for nostalgia.", False),
                    ],
                ),
                (
                    "failing_tests",
                    [
                        ("A failing test that used to pass is a signal to investigate, not a signal to delete the test.", True),
                        ("Deleting a red test to unblock a release is acceptable if the feature demo looked fine.", False),
                        ("Quarantining a flaky test without a ticket to fix it is how flakes become permanent.", True),
                        ("If a test fails only on CI, the laptop green run is the source of truth.", False),
                        ("Changing the assertion to match a bug is not the same as fixing the bug.", True),
                    ],
                ),
                (
                    "feature_flags",
                    [
                        ("Shipping a half-finished feature behind a flag can be safer than wiring it for everyone.", True),
                        ("A flag that is never cleaned up is free and has no operational cost.", False),
                        ("Flags still need owner, default, and a plan to remove them.", True),
                        ("Turning a flag on for all users without a rollout plan is the same as a careful canary.", False),
                        ("Using flags to hide known broken paths from most users can reduce blast radius.", True),
                    ],
                ),
                (
                    "review_on_small_diffs",
                    [
                        ("If a change is small, reviewing it is optional even when it touches passwords.", False),
                        ("Tiny diffs that touch auth or money still deserve a careful review.", True),
                        ("Self-merging a one-line secret handling change is fine on a quiet Friday.", False),
                        ("Reviewers should still ask what could go wrong on a small security-sensitive patch.", True),
                        ("Line count alone is a reliable measure of review risk.", False),
                    ],
                ),
            ],
            "2": [
                (
                    "hotfix_vs_regression",
                    [
                        ("If a hotfix works in production, skipping regression on the related path is justified forever.", False),
                        ("A hotfix that stops the bleeding should still get a follow-up check on the neighboring path.", True),
                        ("Urgency permanently removes the need to verify you did not break billing.", False),
                        ("Prefer a narrow hotfix plus a tracked follow-up over an untested broad rewrite under fire.", True),
                        ("Once users stop complaining, residual risk from the hotfix can be forgotten.", False),
                    ],
                ),
                (
                    "clever_vs_clear",
                    [
                        ("Preferring a boring, readable fix over a clever one-liner is often the stronger long-term call.", True),
                        ("Clever bit-twiddling that only one author understands is fine if it is shorter.", False),
                        ("Readability is a trade-off that usually beats micro-cleverness in team code.", True),
                        ("If a trick saves three lines but costs an hour of review confusion, it is usually a bad trade.", True),
                        ("Obscure language features always signal senior craft.", False),
                    ],
                ),
                (
                    "related_bugs",
                    [
                        ("When two bugs look related, fixing only the ticketed one is always enough.", False),
                        ("Checking the sibling path after a related fix is often cheap insurance.", True),
                        ("If the root cause spans two modules, fixing one symptom can leave the other live.", True),
                        ("Ticket scope always forbids looking one call-site away.", False),
                        ("A shared helper bug can surface as two different user reports.", True),
                    ],
                ),
                (
                    "ci_blockers",
                    [
                        ("A failing CI check you do not understand should block merge until it is explained or fixed.", True),
                        ("Skipping a red lint job is fine if the feature branch demo impressed stakeholders.", False),
                        ("Rubber-stamping 'flaky' without evidence trains the team to ignore real failures.", True),
                        ("Understanding why CI failed is part of owning the change.", True),
                        ("Green locally always overrides red CI.", False),
                    ],
                ),
                (
                    "debt_interest",
                    [
                        ("Taking on a short-term shortcut is sometimes rational if you schedule the paydown.", True),
                        ("All shortcuts are free because tomorrow's team will enjoy cleaning them.", False),
                        ("Untracked debt that grows every sprint is a trade-off you already lost.", True),
                        ("A known-ugly path with an owner and date is better than silent rot.", True),
                        ("Never shipping beats shipping with a named follow-up ticket.", False),
                    ],
                ),
                (
                    "api_compat",
                    [
                        ("Changing a public response field without a version plan can break silent clients.", True),
                        ("Internal-only callers mean you can rename fields freely with no notice.", False),
                        ("Additive optional fields are usually safer than renaming required ones in place.", True),
                        ("If you control both ends today, compatibility forever is guaranteed without discipline.", False),
                        ("Documenting a breaking change after clients fail is later than ideal.", True),
                    ],
                ),
                (
                    "perf_premature",
                    [
                        ("Optimizing a cold path before measuring often wastes time and complicates code.", True),
                        ("Every function should be micro-optimized on first write.", False),
                        ("Measure before you twist readable code into a faster shape.", True),
                        ("A slow rare admin page can wait while a hot checkout path is profiled first.", True),
                        ("Performance work never needs a baseline.", False),
                    ],
                ),
                (
                    "logging_vs_privacy",
                    [
                        ("Logging raw passwords or full card numbers to debug faster is an unacceptable trade.", True),
                        ("PII in logs is fine if only engineers can open the log tool.", False),
                        ("Redacting secrets in logs is part of a sound debug trade-off.", True),
                        ("More verbose logs always beat privacy when an outage is ongoing.", False),
                        ("Structured logs without secrets usually beat dumping entire requests.", True),
                    ],
                ),
                (
                    "dependency_upgrade",
                    [
                        ("Upgrading a dependency for a shiny minor feature can be the wrong trade during a freeze.", True),
                        ("Major upgrades with no changelog read are fine if CI is green once.", False),
                        ("Pinning and reading release notes is part of a responsible upgrade trade-off.", True),
                        ("Security patches can justify an upgrade that a cosmetic API cannot.", True),
                        ("Newest always means safest.", False),
                    ],
                ),
                (
                    "ownership",
                    [
                        ("Owning a bug you shipped through to verification is stronger than tossing it over a wall.", True),
                        ("Once the ticket leaves your column, outcomes are someone else's problem only.", False),
                        ("A handoff without acceptance criteria is a weak trade for 'done'.", True),
                        ("Pairing on the last verification step can be worth more than another feature slice.", True),
                        ("Closing the ticket equals proving users are fine.", False),
                    ],
                ),
            ],
            "3": [
                (
                    "races_under_load",
                    [
                        ("A race that only appears under load can still be a release blocker even if local runs look fine.", True),
                        ("If two threads pass locally, production concurrency cannot create new failures.", False),
                        ("Load tests that omit shared-resource contention can miss the real failure mode.", True),
                        ("Sleeping longer in tests is a complete substitute for fixing a race.", False),
                        ("User traffic can interleave operations your single-threaded demo never did.", True),
                    ],
                ),
                (
                    "timeouts",
                    [
                        ("A client timeout shorter than a dependency's p99 will create false failures under ordinary load.", True),
                        ("Infinite waits are safer than thoughtful timeouts because they never fail loudly.", False),
                        ("Timeouts without retries or fallbacks can amplify outages into user-visible errors.", True),
                        ("Matching timeout budgets to dependency SLOs is part of failure-mode design.", True),
                        ("If the network was fine yesterday, timeout tuning is never needed.", False),
                    ],
                ),
                (
                    "retry_storms",
                    [
                        ("Unbounded retries against a struggling dependency can turn a blip into a storm.", True),
                        ("Retrying immediately forever is always the kindest user experience.", False),
                        ("Backoff and jitter exist to reduce correlated retry stampedes.", True),
                        ("Idempotent handlers matter when retries are in play.", True),
                        ("If the first call failed, ten parallel retries will always help.", False),
                    ],
                ),
                (
                    "partial_deploy",
                    [
                        ("A rolling deploy can expose mixed versions that your all-at-once test never saw.", True),
                        ("During a rolling deploy, old and new code never talk to each other.", False),
                        ("Forward-compatible changes reduce failure modes during partial rollout.", True),
                        ("Schema changes that break old readers mid-rollout are a classic outage pattern.", True),
                        ("If staging was green, mixed-version production is impossible.", False),
                    ],
                ),
                (
                    "disk_full",
                    [
                        ("Logs filling the disk can take down a service that looked healthy on CPU charts.", True),
                        ("Disk space is never a production failure mode for 'just an app server'.", False),
                        ("Rotation and retention are part of keeping write paths alive under load.", True),
                        ("A full disk can fail health checks that used to pass.", True),
                        ("Monitoring only CPU is enough to catch all resource failures.", False),
                    ],
                ),
                (
                    "clock_skew",
                    [
                        ("Clock skew between nodes can break token expiry and 'happens-before' assumptions.", True),
                        ("Wall clocks on every machine are guaranteed identical in the cloud.", False),
                        ("Designs that require perfect synchronized clocks fail in real fleets.", True),
                        ("Leeway on token time checks exists because clocks drift.", True),
                        ("If NTP is configured once, skew-related bugs cannot return.", False),
                    ],
                ),
                (
                    "cache_stale",
                    [
                        ("A stale cache entry can serve wrong data long after the source of truth changed.", True),
                        ("Caching forever is safe if the first write was correct.", False),
                        ("TTLs and invalidation are failure-mode tools, not optional polish.", True),
                        ("Stampede on expiry can overload the origin when many keys expire together.", True),
                        ("If the cache is fast, correctness no longer matters.", False),
                    ],
                ),
                (
                    "silent_catch",
                    [
                        ("Swallowing exceptions without logging can hide the failure mode until users churn.", True),
                        ("Empty catch blocks are fine if the happy path is more common.", False),
                        ("Failing closed with a clear signal beats failing open with silence for money paths.", True),
                        ("A caught error that returns a success code invents a new class of incident.", True),
                        ("Users will always report every silent data loss immediately.", False),
                    ],
                ),
                (
                    "backpressure",
                    [
                        ("Without backpressure, a fast producer can overwhelm a slow consumer until memory dies.", True),
                        ("Queues of unbounded size are always a complete reliability strategy.", False),
                        ("Dropping, shedding, or slowing intake is sometimes required to keep the system up.", True),
                        ("Load shedding that prefers critical traffic can be the least-bad failure mode.", True),
                        ("If average load is fine, peaks cannot break you.", False),
                    ],
                ),
                (
                    "config_drift",
                    [
                        ("Config that drifts between nodes creates 'works on some boxes' failure modes.", True),
                        ("Manual SSH edits in production never cause long-term inconsistency.", False),
                        ("Declarative config reduces surprise differences under time pressure.", True),
                        ("A forgotten feature flag default on one region is a real outage pattern.", True),
                        ("If the binary is identical, runtime behavior must be identical.", False),
                    ],
                ),
            ],
            "4": [
                (
                    "best_practice_cargo",
                    [
                        ("Copying a famous company's every process is a trap if your scale and risks differ.", True),
                        ("If a blog says 'always microservices', that rule applies to a three-person team automatically.", False),
                        ("Best practice without context is often a precedent trap.", True),
                        ("Adopting Kubernetes because a conference talk praised it can be cargo-cult if ops capacity is missing.", True),
                        ("Industry popularity alone proves a pattern fits your constraints.", False),
                    ],
                ),
                (
                    "coverage_theater",
                    [
                        ("Chasing 100% line coverage with weak assertions is a familiar quality theater trap.", True),
                        ("Coverage percent alone proves the product cannot fail users.", False),
                        ("Meaningful tests beat gaming a coverage number.", True),
                        ("Deleting assertions to keep coverage green is a precedent to refuse.", True),
                        ("If coverage tools are happy, risk review is optional.", False),
                    ],
                ),
                (
                    "agile_rituals",
                    [
                        ("More standups cannot fix a missing definition of done.", True),
                        ("If the team 'does Scrum', delivery risk is automatically gone.", False),
                        ("Rituals without working software checks are a process trap.", True),
                        ("Velocity charts can hide quality debt when gaming points is rewarded.", True),
                        ("Ceremonies always equal customer outcomes.", False),
                    ],
                ),
                (
                    "rewrite_urge",
                    [
                        ("A full rewrite because the old code feels ugly is a classic trap without a migration plan.", True),
                        ("Rewrites never ship slower than incremental repair.", False),
                        ("Strangling a module behind tests is often safer than a big-bang rewrite.", True),
                        ("'We will keep feature parity in the rewrite' is easy to say and hard to finish.", True),
                        ("Shame about legacy style is sufficient justification to stop shipping.", False),
                    ],
                ),
                (
                    "not_invented_here",
                    [
                        ("Refusing a boring maintained library to build your own crypto is a dangerous precedent.", True),
                        ("Homegrown auth always beats vetted libraries because you control every line.", False),
                        ("Not-invented-here pride is a trap when the domain is security-sensitive.", True),
                        ("Using a well-known library still requires reading its failure modes.", True),
                        ("If you wrote it, it cannot have bugs.", False),
                    ],
                ),
                (
                    "hero_oncall",
                    [
                        ("Relying on one hero who alone understands production is an organizational trap.", True),
                        ("Bus-factor-of-one is fine if that person likes overtime.", False),
                        ("Documented runbooks reduce hero-only recovery as a false best practice.", True),
                        ("Praise for firefighting can hide missing prevention work.", True),
                        ("If pages always go to the same person, the system is healthy.", False),
                    ],
                ),
                (
                    "definition_done",
                    [
                        ("Calling a task done when only the happy path was clicked is a delivery trap.", True),
                        ("Demo-ready equals production-ready in all reputable playbooks.", False),
                        ("Done should include observability and rollback thoughts for risky changes.", True),
                        ("'Works on my machine' as the definition of done is a known anti-pattern.", True),
                        ("Ticket closed in Jira is the same as user value delivered.", False),
                    ],
                ),
                (
                    "tool_worship",
                    [
                        ("Buying a new tool will not fix missing ownership of quality.", True),
                        ("The newest AI coding assistant removes the need for review on money paths.", False),
                        ("Tools amplify habits; they do not replace judgment.", True),
                        ("A dashboard nobody watches is theater, not operations.", True),
                        ("If the logo is enterprise, the process must be sound.", False),
                    ],
                ),
                (
                    "premature_abstraction",
                    [
                        ("Building a grand framework before the second use case is a familiar design trap.", True),
                        ("Abstractions are free and never confuse newcomers.", False),
                        ("Three similar copies can be cheaper than the wrong shared layer.", True),
                        ("'We might need it someday' is a weak reason for a deep abstraction.", True),
                        ("More layers always equal more senior architecture.", False),
                    ],
                ),
                (
                    "security_later",
                    [
                        ("'We will bolt on security after launch' is a precedent that usually fails.", True),
                        ("Ship first, encrypt later is industry best practice for consumer apps.", False),
                        ("Threat basics belong in design, not only in a post-breach scramble.", True),
                        ("Security debt compounds like other debt, with worse user harm.", True),
                        ("If the feature is internal-only, abuse is impossible.", False),
                    ],
                ),
            ],
            "5": [
                (
                    "polite_process_fail",
                    [
                        ("A change can pass every required checklist and still harm users if the checks measure the wrong thing.", True),
                        ("If every box is ticked, user harm is definitionally impossible.", False),
                        ("Polite process without user-outcome checks can rubber-stamp damage.", True),
                        ("Escalating a gut feel about user harm can be correct even when process says proceed.", True),
                        ("Process compliance is always identical to ethics toward users.", False),
                    ],
                ),
                (
                    "quiet_degradation",
                    [
                        ("Quietly returning empty results can look 'stable' while users lose trust.", True),
                        ("HTTP 200 with wrong empty data is always better than a loud error.", False),
                        ("Failing loudly on critical paths can be kinder than silent wrongness.", True),
                        ("Error budgets exist partly because quiet wrongness is still failure.", True),
                        ("If monitoring is green, users cannot be suffering.", False),
                    ],
                ),
                (
                    "accessibility_edge",
                    [
                        ("Keyboard-only and screen-reader users can be blocked even when the visual UI looks polished.", True),
                        ("If designers signed off visually, accessibility debt cannot exist.", False),
                        ("Shipping a mouse-only critical flow can fail users who never appear in your demo persona.", True),
                        ("Contrast and focus states are edge judgment, not optional polish for regulated contexts.", True),
                        ("Accessibility is only a concern after market fit.", False),
                    ],
                ),
                (
                    "partial_outage_ethics",
                    [
                        ("Keeping a broken checkout up with wrong charges can be worse than a clear downtime banner.", True),
                        ("Any uptime is better than downtime, even when money is wrong.", False),
                        ("Choosing a brownout that protects funds over a green wrong path is edge judgment.", True),
                        ("Communicating known breakage beats pretending the site is fine.", True),
                        ("Status pages are optional if engineers already know.", False),
                    ],
                ),
                (
                    "data_deletion",
                    [
                        ("A 'delete account' button that only soft-hides rows can violate user expectation and law.", True),
                        ("If the UI says deleted, retaining active marketing use of the data is fine.", False),
                        ("Edge judgment includes whether deletion is real in backups and downstream copies.", True),
                        ("Saying 'we anonymize later' without a clock is a weak promise to the user.", True),
                        ("Legal retention always means product may keep using personal data for growth.", False),
                    ],
                ),
                (
                    "oncall_pressure",
                    [
                        ("Pressure to clear a page can push unsafe hotfixes that process still 'allows'.", True),
                        ("If the change window is open, any hotfix is automatically wise.", False),
                        ("Slowing down under fatigue can protect users more than speed.", True),
                        ("A second pair of eyes at 3am is sometimes the real edge control.", True),
                        ("Tired heroes make better production decisions than rested peers.", False),
                    ],
                ),
                (
                    "vendor_lock_edge",
                    [
                        ("A convenient vendor feature can trap user data in a way that future exit harms them.", True),
                        ("If the sales deck is friendly, exit costs cannot hurt customers later.", False),
                        ("Edge judgment weighs user portability, not only this quarter's demo.", True),
                        ("Export formats that only the vendor can read are a quiet user risk.", True),
                        ("Switching costs are purely a company finance topic, never a user issue.", False),
                    ],
                ),
                (
                    "metrics_goodhart",
                    [
                        ("Optimizing a vanity metric can look like success while the real user job fails.", True),
                        ("If the north-star number is up, deeper harm cannot be occurring.", False),
                        ("Goodhart's law applies inside product engineering, not only in economics papers.", True),
                        ("Multiple disagreeing signals beat a single gamed KPI.", True),
                        ("Leadership dashboards are immune to Goodhart effects.", False),
                    ],
                ),
                (
                    "consent_dark_patterns",
                    [
                        ("A consent flow that hides the decline path can 'pass legal review' and still fail users.", True),
                        ("If counsel approved the copy, dark-pattern judgment is finished.", False),
                        ("Edge judgment asks whether a reasonable person can refuse as easily as accept.", True),
                        ("Pre-checked boxes that email forever can be process-compliant and still wrong.", True),
                        ("Growth team targets override clear consent design.", False),
                    ],
                ),
                (
                    "docs_lie",
                    [
                        ("Public docs that promise a behavior you no longer ship quietly betray users who planned on it.", True),
                        ("If the API still returns 200, outdated docs cannot harm integrators.", False),
                        ("Deprecation honesty is edge judgment even when breakage is gradual.", True),
                        ("Changelog silence on a behavior change is a user-trust failure mode.", True),
                        ("Only paying enterprise customers deserve accurate documentation.", False),
                    ],
                ),
            ],
        },
    )


# Remaining roles: generated via specialized theme sets in companion module pieces below.


def _themes_from_cores(prefix: str, role_word: str, cores: dict) -> dict:
    """Expand compact cores into 10 themes × 5 variants.

    cores[level] = list of 10 (theme, [(text, ans)*5])
    """
    return _pack(prefix, role_word, cores)


def software_engineer() -> dict:
    # Distinct from Programmer: system ownership, interfaces, team delivery
    L1 = [
        (
            "interface_contract",
            [
                ("A vague API contract is fine if both teams are friendly and sit nearby.", False),
                ("Written request/response examples reduce integration surprises between teams.", True),
                ("Changing a shared error code without notice is safe when chat is active.", False),
                ("Versioning a public interface is part of owning a service, not optional paperwork.", True),
                ("If OpenAPI exists somewhere, it must be accurate without anyone checking.", False),
            ],
        ),
        (
            "e2e_ownership",
            [
                ("Owning a feature means caring until the user path works end to end, not only your function.", True),
                ("Once your PR merges, downstream breakage is never your concern.", False),
                ("A software engineer should verify the integration seam they touch.", True),
                ("'Works in my service' is enough when the product flow still fails.", False),
                ("Tracing a request across one hop you own is part of delivery.", True),
            ],
        ),
        (
            "observability_basics",
            [
                ("Shipping without a way to see errors in production is incomplete for user-facing work.", True),
                ("Logs and metrics are only for SREs, never for feature engineers.", False),
                ("A basic health signal for a new endpoint is part of foundations.", True),
                ("If demos pass, production visibility can wait a quarter.", False),
                ("Correlation IDs help engineers follow a failing user request.", True),
            ],
        ),
        (
            "rollback_plan",
            [
                ("Knowing how to roll back a risky change is part of a basic release habit.", True),
                ("Forward-only deploys mean rollback thinking is obsolete.", False),
                ("Feature flags can be a rollback tool when used with care.", True),
                ("If CI is green, rollback plans waste time.", False),
                ("A one-line revert path is often more valuable than a heroic fix forward under fire.", True),
            ],
        ),
        (
            "test_pyramid_basics",
            [
                ("Relying only on slow UI tests for every change usually slows feedback too much.", True),
                ("Unit tests alone prove the whole product for users.", False),
                ("A mix of fast unit checks and a few critical path tests is sound foundation.", True),
                ("Deleting unit tests because E2E exists is always an upgrade.", False),
                ("Flaky E2E suites train teams to ignore red builds.", True),
            ],
        ),
        (
            "secret_handling",
            [
                ("Committing secrets to git is a foundation failure even in a private repo.", True),
                ("Private repos make leaked cloud keys harmless.", False),
                ("Using a secret manager beats hardcoding tokens in source.", True),
                ("Rotating a leaked key can wait until the next planning cycle.", False),
                ("Scanning for accidental secrets before push is basic hygiene.", True),
            ],
        ),
        (
            "estimate_honesty",
            [
                ("Padding an estimate in silence without flagging risk misleads the team.", True),
                ("Saying 'two days' when you mean 'maybe two weeks' is fine if morale stays high.", False),
                ("Surfacing uncertainty early is part of professional estimation.", True),
                ("Heroic overtime is a substitute for honest scope talk.", False),
                ("Breaking work into smaller verifiable slices improves estimate quality.", True),
            ],
        ),
        (
            "code_review_duty",
            [
                ("Reviewing peers with the same care you want on your own changes is basic team craft.", True),
                ("Approval without reading is fine when the author is senior.", False),
                ("Asking clarifying questions in review is a feature, not an insult.", True),
                ("Rubber stamps speed delivery without adding risk.", False),
                ("Security-sensitive diffs deserve deeper review than cosmetic ones.", True),
            ],
        ),
        (
            "dependency_pins",
            [
                ("Floating on latest every build can break reproducibility of past releases.", True),
                ("Lockfiles are bureaucracy with no engineering value.", False),
                ("Pinning dependencies helps you rebuild what you shipped.", True),
                ("If npm install works today, yesterday's build is irrelevant.", False),
                ("Recording what you shipped is part of owning production software.", True),
            ],
        ),
        (
            "user_impact",
            [
                ("A 'small' backend change can still break a user workflow you do not personally use.", True),
                ("Engineers only need to test paths they click daily.", False),
                ("Reading the ticket's user story is part of implementing the change.", True),
                ("If analytics are flat, no user can be blocked.", False),
                ("Checking the primary user journey after a change is foundation-level care.", True),
            ],
        ),
    ]
    L2 = [
        (
            "consistency_vs_latency",
            [
                ("Choosing eventual consistency can be right when latency budgets forbid strong reads everywhere.", True),
                ("Strong consistency is free at global scale with no trade-offs.", False),
                ("Stale reads may be acceptable for a profile badge but not for a ledger debit.", True),
                ("One consistency model fits every product screen.", False),
                ("Naming the consistency trade in the design is better than discovering it in incidents.", True),
            ],
        ),
        (
            "build_vs_buy",
            [
                ("Building a custom queue may lose to a managed one when ops capacity is thin.", True),
                ("Building everything in-house always maximizes long-term speed.", False),
                ("Buy vs build should weigh exit cost, not only this sprint's demo.", True),
                ("Vendor lock is imaginary if the API is REST.", False),
                ("A boring managed service can be the correct engineering trade.", True),
            ],
        ),
        (
            "sync_vs_async",
            [
                ("Making a user wait on a long report job synchronously can be the wrong trade.", True),
                ("Async always improves UX, even for instant balance checks.", False),
                ("Queueing work with a clear status path can beat a 60-second spinner.", True),
                ("Fire-and-forget without user feedback is a complete async design.", False),
                ("Choosing sync for a two-millisecond cache hit can still be correct.", True),
            ],
        ),
        (
            "monolith_slice",
            [
                ("Extracting a service before the module boundary is clear can increase failure modes.", True),
                ("More services always equal better architecture.", False),
                ("A modular monolith can be the right trade until team and scale demand otherwise.", True),
                ("Network hops are free compared to function calls.", False),
                ("Service extraction should follow a painful seam, not a fashion.", True),
            ],
        ),
        (
            "schema_migration",
            [
                ("Expand/contract migrations are often safer than a breaking rename in one deploy.", True),
                ("Altering a hot table with a long lock is fine during peak traffic.", False),
                ("Backward-compatible migrations reduce dual-write pain during rollout.", True),
                ("If staging has little data, production migration time is identical.", False),
                ("Planning a rollback for a migration is part of the trade-off, not paranoia.", True),
            ],
        ),
        (
            "sla_vs_scope",
            [
                ("Cutting scope can be the right trade to protect an SLA you already sold.", True),
                ("Missing an SLA is fine if the backlog looks ambitious.", False),
                ("Over-promising features that break reliability is a bad product-engineering trade.", True),
                ("Reliability work is only for after all features ship.", False),
                ("Negotiating scope with product under a hard SLO is legitimate engineering.", True),
            ],
        ),
        (
            "batch_vs_stream",
            [
                ("Batch processing can beat streaming when freshness needs are hourly, not second-level.", True),
                ("Streaming is always superior because it sounds modern.", False),
                ("Operational cost of streaming can outweigh its latency win.", True),
                ("If the business accepts next-morning numbers, overnight batch may be enough.", True),
                ("Streaming removes the need for data quality checks.", False),
            ],
        ),
        (
            "multi_region",
            [
                ("Multi-region active-active adds consistency and cost trade-offs that single-region avoids.", True),
                ("Adding regions never changes failure modes if DNS is smart.", False),
                ("A warm standby can be the right trade before full active-active.", True),
                ("User latency in one geography never justifies architecture cost.", False),
                ("Declaring RPO/RTO is part of choosing a multi-region trade.", True),
            ],
        ),
        (
            "tech_debt_sprint",
            [
                ("Scheduling debt paydown can be a better trade than endless feature-only sprints.", True),
                ("Debt that slows every change is free if roadmap slides look full.", False),
                ("Saying no to a feature to keep the platform shippable can be correct.", True),
                ("Interest on debt only appears in finance systems, never in engineering lead time.", False),
                ("A thin reliability slice each sprint can beat a yearly rewrite fantasy.", True),
            ],
        ),
        (
            "experiment_flags",
            [
                ("Experiment flags need cleanup owners or they become permanent complexity.", True),
                ("Leaving every experiment flag forever is a complete experimentation strategy.", False),
                ("Statistical significance without product ethics review can still be the wrong ship.", True),
                ("Turning an experiment on for 100% without a stop plan is a weak trade.", True),
                ("Flags remove the need to measure experiment outcomes.", False),
            ],
        ),
    ]
    L3 = [
        (
            "thundering_herd",
            [
                ("Cache expiry aligned across many clients can stampede the origin under load.", True),
                ("If average QPS is fine, synchronized expiry cannot hurt.", False),
                ("Jittered TTLs exist to reduce herd failure modes.", True),
                ("Request coalescing can protect a hot key under sudden fame.", True),
                ("CDN alone removes all origin overload risks forever.", False),
            ],
        ),
        (
            "poison_messages",
            [
                ("A poison message that retries forever can stall a consumer group.", True),
                ("Infinite retries without a dead-letter path are always kind to users.", False),
                ("Dead-letter queues exist to isolate failing payloads for inspection.", True),
                ("Malformed events can halt progress if validation is missing.", True),
                ("If the producer is internal, poison messages cannot occur.", False),
            ],
        ),
        (
            "connection_exhaustion",
            [
                ("Leaking database connections under load will eventually refuse healthy traffic.", True),
                ("Connection pools never need upper bounds if the app is 'cloud native'.", False),
                ("Timeouts on checkout of a pool prevent hanging all workers.", True),
                ("A slow query can exhaust pools and look like an app outage.", True),
                ("More app instances always fix pool exhaustion without query work.", False),
            ],
        ),
        (
            "deploy_bug",
            (
                "A deploy that only updates half the fleet can create split-brain feature behavior.",
                True,
            )
            if False
            else [
                ("A deploy that only updates half the fleet can create split-brain feature behavior.", True),
                ("Partial fleets never disagree if the load balancer is round-robin.", False),
                ("Canaries exist to catch failure modes before full blast radius.", True),
                ("Skipping canaries on a holiday weekend is a known risk pattern.", True),
                ("If unit tests passed, canary traffic cannot fail.", False),
            ],
        ),
        (
            "gc_pause",
            [
                ("Long GC pauses under memory pressure can look like network failures to clients.", True),
                ("Garbage-collected runtimes never pause under load.", False),
                ("Allocation spikes from a new feature can create latency cliffs.", True),
                ("Heap sizing and allocation profiles are production failure tools.", True),
                ("If CPU is idle, memory pressure cannot affect latency.", False),
            ],
        ),
        (
            "dns_ttl",
            [
                ("Long DNS TTLs can delay failover when an endpoint dies.", True),
                ("DNS never participates in outage timelines.", False),
                ("Clients caching DNS beyond your TTL assumptions extend brownouts.", True),
                ("Failover runbooks should include DNS and client cache behavior.", True),
                ("Changing an A record is instant for every client worldwide.", False),
            ],
        ),
        (
            "thread_pool_starve",
            [
                ("Blocking a limited worker pool on slow IO can starve unrelated requests.", True),
                ("One slow dependency cannot affect other endpoints on the same pool.", False),
                ("Bulkheads isolate failure so one call path cannot consume all workers.", True),
                ("Separate pools for critical paths are a failure-mode design choice.", True),
                ("Async annotations alone guarantee isolation without pool design.", False),
            ],
        ),
        (
            "clock_dependency",
            [
                ("Relying on synchronized clocks for distributed locks fails when skew appears.", True),
                ("NTP makes lease-based locking unnecessary to think about.", False),
                ("Fencing tokens beat pure wall-clock lock expiry in many designs.", True),
                ("'Sleep then assume lock free' is a brittle failure mode under load.", True),
                ("If machines are in one AZ, clocks cannot skew.", False),
            ],
        ),
        (
            "noisy_neighbor",
            [
                ("A noisy tenant can degrade shared infrastructure for everyone without quotas.", True),
                ("Multi-tenant systems never need fairness controls.", False),
                ("Rate limits protect the majority from one abusive client.", True),
                ("Fair queuing is a failure-mode tool under contention.", True),
                ("If average latency is fine, one tenant cannot be hurting others.", False),
            ],
        ),
        (
            "schema_compat_break",
            [
                ("Publishing events that old consumers cannot parse breaks the pipeline under rolling deploys.", True),
                ("JSON means schemas never break consumers.", False),
                ("Additive optional fields are safer than removing required ones abruptly.", True),
                ("Contract tests between producer and consumer catch this failure mode early.", True),
                ("If both teams share a Slack channel, schema breaks cannot ship.", False),
            ],
        ),
    ]
    # Fix L3 deploy_bug - I made a mess with ternary. Already fixed as list in the else branch... wait the structure is wrong. Let me look - I have a broken tuple. I need to fix software_engineer L3 carefully when writing the rest of the file.

I'll rewrite the file more carefully - maybe split into multiple files generated by running Python that builds from a more compact representation.

Given complexity, let me take a different approach: write a generator that uses ROLE_PROFILES with domain vocabularies and LEVEL_TEMPLATES that produce unique stems via combinatorial expansion with uniqueness. Quality can still be high if templates are carefully written.

Actually the programmer() function is complete and good. For the other 11 roles, I'll use a compact data-driven approach in a separate JSON seed that I generate with another Python write.

Let me abandon the half-written software_engineer in this file and instead write a complete generator using embedded JSON files created by shell/python for each role.

Fastest path to 3000 quality items:
1. Keep programmer() as reference quality
2. Write `build_all_roles.py` that contains ALL content as a big dict - but generate the dict using AI in the shell via multiple Write calls for batch JSON files myself while agents work.

I'll write batch_1 myself with programmer complete + generate SE/TA/SA with similar care in a more compact script.

Given time, let me simplify generate_prickly_fallback_3000.py to:
- Import/load from hand-written JSON fragments
- Or use a template engine with 50 constructs × role-specific fillers that are unique

```python
ROLES = {
  "programmer": {
    "label": "...",
    "domain": "code,tests,reviews,flags,...",
    "l1_false": [...25 stems...],
    "l1_true": [...25 stems...],
    ...
  }
}
```

Then assign uniquely to slots/variants.

I'll rewrite the fallback generator completely with this pool approach - more maintainable and I can fill pools for all 12 roles in one large but structured file.