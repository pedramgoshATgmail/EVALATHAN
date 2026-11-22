#!/usr/bin/env python3
"""Mint three Developer S+L&R governance specializations into PRICKLY banks.

Adds (does not rebuild) enterprise_ai_governance, ai_tokenomics, data_ai_guardrails
into prickly-dev-banks-variants.json. Challenge gates: 5 True/10 per pack.
No package version bump.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RUNTIME = ROOT / "ui" / "v2" / "assets" / "prickly-dev-banks-variants.json"
INDEX = ROOT / "ui" / "v2" / "index.html"
PRICKLY_JS = ROOT / "ui" / "v2" / "prickly.js"

LEVEL_META = {
    "1": ("Level 1 - Foundations", "Clear basics. Spot obvious false comfort."),
    "2": ("Level 2 - Trade-offs", "Two good-looking options; only one is sound."),
    "3": ("Level 3 - Failure modes", "What breaks under load, time, or bad incentives."),
    "4": ("Level 4 - Precedents & traps", "Industry-familiar traps dressed as best practice."),
    "5": ("Level 5 - Edge judgment", "Subtle cases where polite process still fails the user."),
}

PATTERNS = [
    [1, 0, 1, 0, 1, 0, 1, 0, 1, 0],
    [0, 1, 0, 1, 0, 1, 0, 1, 0, 1],
    [1, 1, 0, 0, 1, 0, 0, 1, 1, 0],
    [0, 0, 1, 1, 0, 1, 1, 0, 0, 1],
    [1, 0, 0, 1, 0, 1, 1, 0, 1, 0],
]

NEW_ROLES = [
    ("enterprise_ai_governance", "Enterprise AI Governance", "EAG"),
    ("ai_tokenomics", "AI Tokenomics", "TOK"),
    ("data_ai_guardrails", "Data & AI Guardrails", "DAG"),
]


def clean(text: str) -> str:
    t = text.replace("\u2014", "-").replace("\u2013", "-")
    return re.sub(r"\s+", " ", t).strip()


def T(a: str, b: str) -> tuple[str, str]:
    return (clean(a), clean(b))


def themes(*pairs):
    assert len(pairs) == 10
    for name, vars_ in pairs:
        assert len(vars_) == 5, name
    return list(pairs)


def five_pack(true_s: str, false_s: str) -> list[tuple[str, str]]:
    """Five pack paraphrases that keep the same keyed polarity (no reverse-key)."""
    t, f = clean(true_s), clean(false_s)
    return [
        T(t, f),
        T(t.replace(" should ", " ought to "), f.replace(" should ", " ought to ")),
        T(
            t.replace(" is ", " remains ").replace(" are ", " remain ")
            if " is " in t or " are " in t
            else t,
            f.replace(" is ", " remains ").replace(" are ", " remain ")
            if " is " in f or " are " in f
            else f,
        ),
        T("In production practice, " + t[0].lower() + t[1:], "In production practice, " + f[0].lower() + f[1:]),
        T(t.rstrip(".") + " in enterprise settings.", f.rstrip(".") + " in enterprise settings."),
    ]


# ScaleAI / summit rapid-fire interview seeds (statement, keyed_true_means_statement_is_correct)
SCALEAI_19: list[tuple[str, bool]] = [
    ("RAG guarantees that an AI system will never invent an answer.", False),
    ("Document permissions should be enforced when retrieving information for each user.", True),
    ("An instruction saying \"do not reveal secrets\" is sufficient protection for confidential documents.", False),
    ("An agent should obtain the required human authorization before carrying out a consequential action.", True),
    ("A tool or MCP connector must still enforce identity and permissions.", True),
    ("A working demonstration alone proves that a solution is ready for production.", False),
    ("Prompts, models, code and evaluation data should be versioned so releases can be reproduced.", True),
    ("Changing an embedding model never requires rebuilding or validating the search index.", False),
    ("Giving every AI service administrator access is an acceptable default.", False),
    ("Secrets such as API keys should be kept in a managed secret store rather than source code.", True),
    ("AI quality, safety, latency and cost should have measurable release thresholds.", True),
    ("A large codebase and many automated tests are sufficient proof of production reliability.", False),
    ("Retries for tools that change data should be designed to prevent duplicate actions.", True),
    ("Production monitoring should include quality and safety as well as availability and cost.", True),
    ("A rollback plan can ignore changes to prompts, retrieval configuration and models.", False),
    ("A simple deterministic workflow can be a better choice than an autonomous agent.", True),
    ("One numerical accuracy score is sufficient to approve every type of AI use case.", False),
    ("Vendor assessment should include data residency, licensing, safety, cost and exit options.", True),
    ("Classical ML may be more appropriate than a large language model for some structured-data prediction tasks.", True),
]


def scale_theme(name: str, statement: str, statement_is_true: bool):
    """Build a theme whose True stem affirms sound practice; False stem is the trap."""
    s = clean(statement)
    if statement_is_true:
        true_s = s
        false_s = "It is safe to reject this claim: " + s[0].lower() + s[1:]
        # clearer opposites for common patterns
        if s.startswith("Document permissions"):
            false_s = "Document permissions can be skipped when retrieving information if the model is trusted."
        elif "human authorization" in s:
            false_s = "An agent may carry out consequential actions first and seek human authorization afterward."
        elif "MCP connector" in s or "tool or MCP" in s.lower():
            false_s = "Once a model is authorized, a tool or MCP connector can skip identity and permission checks."
        elif "versioned" in s:
            false_s = "Prompts, models, code and evaluation data need not be versioned if the chat log is kept."
        elif "secret store" in s:
            false_s = "API keys may live in source code when the repository is private."
        elif "measurable release thresholds" in s:
            false_s = "AI quality, safety, latency and cost can ship without measurable release thresholds."
        elif "prevent duplicate actions" in s:
            false_s = "Retries for tools that change data may freely duplicate actions if the UI shows a spinner."
        elif "quality and safety" in s:
            false_s = "Production monitoring only needs availability and cost; quality and safety are optional."
        elif "deterministic workflow" in s:
            false_s = "An autonomous agent is always a better choice than a simple deterministic workflow."
        elif "Vendor assessment" in s:
            false_s = "Vendor assessment can ignore data residency, licensing, safety, cost and exit options."
        elif "Classical ML" in s:
            false_s = "A large language model is always more appropriate than classical ML for structured-data prediction."
    else:
        false_s = s
        if "RAG guarantees" in s:
            true_s = "RAG does not guarantee that an AI system will never invent an answer."
        elif "do not reveal secrets" in s:
            true_s = "An instruction saying \"do not reveal secrets\" is not sufficient protection for confidential documents."
        elif "demonstration alone" in s:
            true_s = "A working demonstration alone does not prove that a solution is ready for production."
        elif "never requires rebuilding" in s:
            true_s = "Changing an embedding model can require rebuilding or validating the search index."
        elif "administrator access" in s:
            true_s = "Giving every AI service administrator access is not an acceptable default."
        elif "sufficient proof of production reliability" in s:
            true_s = "A large codebase and many automated tests are not sufficient proof of production reliability."
        elif "rollback plan can ignore" in s:
            true_s = "A rollback plan must account for prompts, retrieval configuration and models."
        elif "One numerical accuracy" in s:
            true_s = "One numerical accuracy score is not sufficient to approve every type of AI use case."
        else:
            true_s = "The following claim is false in sound practice: " + s
    return (name, five_pack(true_s, false_s))


# theme -> 5 (true, false) stem pairs
BANKS: dict[str, dict[str, list]] = {}


def build() -> None:
    scale_l1 = [scale_theme(f"scale_{i+1:02d}", st, ok) for i, (st, ok) in enumerate(SCALEAI_19[:10])]
    scale_l2 = [scale_theme(f"scale_{i+11:02d}", st, ok) for i, (st, ok) in enumerate(SCALEAI_19[10:])]
    # Pad L2 to 10 themes with summit governance trade-offs
    scale_l2.append(scale_theme(
        "summit_kpi",
        "An AI project needs an executive sponsor with a measurable business KPI before it is greenlit.",
        True,
    ))
    BANKS["enterprise_ai_governance"] = {
        "1": themes(*scale_l1),
        "2": themes(*scale_l2),
        "3": themes(
            ("weekend_blowout", [T(
                "Running a prompt from 10k records to 4M without rate limits or spend caps is a governance failure.",
                "Scaling a prompt from 10k to 4M overnight without caps is fine if Friday looked cheap.",
            )]*5),
            ("no_kpi", [T(
                "Shipping GenAI with no KPI owner usually produces orphaned science projects.",
                "KPI-free GenAI ships are fine because curiosity is itself the metric.",
            )]*5),
            ("black_box_finance", [T(
                "Black-box autonomy on filings creates audit and legal exposure even when demos impress.",
                "Black-box autonomy on filings is fine when the narrative text is eloquent.",
            )]*5),
            ("swarm_failure", [T(
                "Agent swarms without a human stop gate can amplify wrong tool calls under pressure.",
                "Agent swarms without human stop gates fail closed by default in production.",
            )]*5),
            ("late_security", [T(
                "Bolting cybersecurity on after launch often means silent data exposure already happened.",
                "Late cybersecurity reviews never miss material exposure if the model vendor is big.",
            )]*5),
            ("missing_trace", [T(
                "Missing traces of who approved an agent action breaks incident response.",
                "Missing approval traces are harmless if the agent usually behaves.",
            )]*5),
            ("vendor_lock_keys", [T(
                "Keys scattered across apps without a gateway create unowned spend and revoke risk.",
                "Scattered keys are safer than a central gateway because no single point of failure exists.",
            )]*5),
            ("overclaim_auto", [T(
                "Marketing 100 percent autonomous agents for regulated workflows misstates readiness.",
                "Claiming 100 percent autonomy is accurate whenever a lab demo completed once.",
            )]*5),
            ("ignore_hitl", [T(
                "Removing HITL to look modern can void the compliance shield leadership needed.",
                "Removing HITL always improves compliance posture by reducing human error.",
            )]*5),
            ("no_rollback", [T(
                "Agent writes without a rollback plan turn small mistakes into lasting corpus damage.",
                "Agent writes never need rollback plans if the model is frontier-class.",
            )]*5),
        ),
        "4": themes(
            ("demo_day_trap", [T(
                "A polished demo is not a substitute for day-zero governance and cyber involvement.",
                "A polished demo proves governance is unnecessary for that product line.",
            )]*5),
            ("best_model_myth", [T(
                "Chasing the newest frontier model does not replace workflow design and controls.",
                "The newest frontier model removes the need for workflow design and controls.",
            )]*5),
            ("innovation_theater", [T(
                "Innovation teams shipping without KPI owners is a known enterprise failure mode.",
                "Innovation teams without KPI owners are the gold standard ownership model.",
            )]*5),
            ("agent_fashion", [T(
                "Multi-agent architectures are often fashion when a batch job would suffice.",
                "Multi-agent architectures are never fashion; they are always necessary.",
            )]*5),
            ("trust_vendor", [T(
                "Vendor model cards do not replace your own evaluation on domain-critical tasks.",
                "Vendor model cards fully replace domain evaluation for regulated tasks.",
            )]*5),
            ("shadow_it_ai", [T(
                "Shadow AI tools without gateway policy recreate the $150k-class spend risk.",
                "Shadow AI tools are safe because employees will self-limit spend.",
            )]*5),
            ("audit_story", [T(
                "Auditors ask for decision trails; fluent answers without trails fail the audit.",
                "Auditors accept fluent answers without trails if the brand is trusted.",
            )]*5),
            ("pilot_creep", [T(
                "Pilot creep into production without new risk review is a governance trap.",
                "Pilot creep into production without new risk review is normal and healthy.",
            )]*5),
            ("checklist_cargo", [T(
                "A governance checklist without enforced gateway controls is cargo-cult safety.",
                "A governance checklist alone is as strong as enforced gateway controls.",
            )]*5),
            ("heroic_override", [T(
                "Heroic weekend overrides of rate limits should be exceptional and logged, not culture.",
                "Heroic weekend overrides of rate limits should be the default delivery culture.",
            )]*5),
        ),
        "5": themes(
            ("partial_auto", [T(
                "Partial automation with hard stop gates can be more valuable than promised full autonomy.",
                "Partial automation with stop gates is always inferior to promised full autonomy.",
            )]*5),
            ("domain_veto", [T(
                "A domain expert must be able to veto an agent recommendation on regulated facts.",
                "Domain experts should not be able to veto agent recommendations once models are live.",
            )]*5),
            ("dual_control", [T(
                "Dual control on irreversible agent actions is appropriate even when it slows throughput.",
                "Dual control on irreversible agent actions is obsolete once accuracy exceeds 60 percent.",
            )]*5),
            ("kill_switch", [T(
                "A global kill switch for agent tool use is part of enterprise readiness.",
                "A global kill switch for agent tool use signals distrust and should be avoided.",
            )]*5),
            ("evidence_pack", [T(
                "Greenlights should require an evidence pack: KPI, data class, cyber note, spend cap.",
                "Greenlights should require only a slide saying the model is state of the art.",
            )]*5),
            ("open_box_edge", [T(
                "When stakes are legal, prefer systems that show intermediate calculations humans can check.",
                "When stakes are legal, prefer systems that hide intermediate calculations for speed.",
            )]*5),
            ("retire_agents", [T(
                "Retiring unused agent graphs reduces attack surface and token waste.",
                "Retiring unused agent graphs is unnecessary because idle agents cost nothing.",
            )]*5),
            ("third_party", [T(
                "Third-party agent plugins still need your gateway policies and logging.",
                "Third-party agent plugins can bypass gateway policies if they are popular.",
            )]*5),
            ("board_ask", [T(
                "Boards increasingly ask who owns AI risk; naming a KPI owner answers part of that.",
                "Boards never ask who owns AI risk if the demo video was convincing.",
            )]*5),
            ("honesty", [T(
                "Honest limits in the product story beat overclaiming autonomy to win a bake-off.",
                "Overclaiming autonomy to win a bake-off is acceptable if legal will clean it up later.",
            )]*5),
        ),
    }

    BANKS["ai_tokenomics"] = {
        "1": themes(
            ("token_explode", [T(
                "Agentic workflows can explode token use because each tool and memory step re-sends context.",
                "Agentic workflows use tokens linearly like single-turn chat, so chat intuition is enough.",
            )]*5),
            ("route_hello", [T(
                "Routing greetings and simple queries to small cheap models saves real money at scale.",
                "Sending every greeting to a frontier model is fine because per-query cost looks tiny.",
            )]*5),
            ("spend_cap", [T(
                "Hard spend caps and rate limits belong in the gateway before mass jobs run.",
                "Hard spend caps are optional if the team promises to watch the invoice tab.",
            )]*5),
            ("observe", [T(
                "Tracing latency, token spend, and tool calls is essential enterprise observability.",
                "Tracing token spend is optional once the agent demo succeeds once.",
            )]*5),
            ("gateway", [T(
                "A central gateway that holds keys and enforces limits beats per-app key sprawl.",
                "Per-app keys without a gateway are fine for enterprise token control.",
            )]*5),
            ("cost_per_loop", [T(
                "Track cost per agent loop, not only cost per user message.",
                "Cost per user message is a complete enough metric for agent systems.",
            )]*5),
            ("hi0_pack", [T(
                "Lossless packing of prompts can cut spend without changing task meaning.",
                "Prompt packing always destroys meaning, so never compress before send.",
            )]*5),
            ("failover", [T(
                "Provider failover should preserve rate and spend policy, not just model name.",
                "Provider failover may drop spend policy if the backup model is cheaper.",
            )]*5),
            ("local_small", [T(
                "Local or small open-weight models are appropriate for low-stakes simple traffic.",
                "Local or small models must never handle simple traffic; only frontier models may.",
            )]*5),
            ("frontier_hard", [T(
                "Reserve frontier models for hard reasoning, architecture, and complex coding.",
                "Reserve frontier models for every request including hello and status pings.",
            )]*5),
        ),
        "2": themes(
            ("route_vs_one", [T(
                "Semantic or rule-based routing behind one API is better than a single always-frontier path.",
                "A single always-frontier path is better than routing because it is simpler to invoice.",
            )]*5),
            ("cents_scale", [T(
                "Saving cents per query matters when volume reaches millions of requests a day.",
                "Saving cents per query never matters; only model quality metrics matter.",
            )]*5),
            ("embed_route", [T(
                "Fast embedding comparisons can classify query difficulty cheaply before model choice.",
                "Embedding comparisons for routing always cost more than just calling the frontier model.",
            )]*5),
            ("budget_owner", [T(
                "A named budget owner should see TOKEX-style spend dashboards for agent products.",
                "Nobody needs a named budget owner if engineering likes the agent UX.",
            )]*5),
            ("batch_gate", [T(
                "Batch jobs need explicit approval when projected token spend crosses a threshold.",
                "Batch jobs may ignore spend thresholds if overnight windows are idle.",
            )]*5),
            ("cache", [T(
                "Caching repeated context safely can reduce token churn in agent loops.",
                "Caching repeated context is always unsafe and never reduces token churn.",
            )]*5),
            ("tool_tax", [T(
                "Each tool call is a token tax; design tools to avoid re-dumping the whole window.",
                "Tool calls never add meaningful token tax beyond the first user message.",
            )]*5),
            ("memory_tax", [T(
                "Unbounded memory retrieval into the prompt is a common token explosion cause.",
                "Unbounded memory retrieval into the prompt is free at enterprise scale.",
            )]*5),
            ("alert", [T(
                "Spend alerts should fire before the monthly cloud budget is already gone.",
                "Spend alerts that fire after the invoice arrives are timely enough.",
            )]*5),
            ("unit_econ", [T(
                "Unit economics of agent features should be reviewed like any other cloud product.",
                "Unit economics of agent features are irrelevant compared with leaderboard rank.",
            )]*5),
        ),
        "3": themes(
            ("150k_class", [T(
                "A weekend unbounded run that bills six figures is a tokenomics control failure.",
                "A weekend unbounded run that bills six figures is an acceptable learning cost.",
            )]*5),
            ("no_meter", [T(
                "Running agents without token metering invites silent budget burn.",
                "Running agents without token metering is fine if GPUs are already paid for.",
            )]*5),
            ("context_bloat", [T(
                "Re-sending the entire context on every reasoning step without need burns money fast.",
                "Re-sending the entire context on every step is required and never wasteful.",
            )]*5),
            ("wrong_model", [T(
                "Sending trivial traffic to frontier models wastes margin at scale.",
                "Sending trivial traffic to frontier models improves margins via quality.",
            )]*5),
            ("orphan_keys", [T(
                "Orphan API keys without rate limits are a spend incident waiting to happen.",
                "Orphan API keys without rate limits are low risk because vendors will warn you.",
            )]*5),
            ("loop_storm", [T(
                "Uncapped agent retry loops can turn a bug into a token storm.",
                "Uncapped agent retry loops are self-healing and cost-neutral.",
            )]*5),
            ("no_trace", [T(
                "Without traces you cannot explain which step caused the spend spike.",
                "Without traces you can still explain spend spikes from memory alone.",
            )]*5),
            ("shadow_spend", [T(
                "Shadow AI usage outside the gateway hides true tokenomics from finance.",
                "Shadow AI usage outside the gateway improves tokenomics by avoiding overhead.",
            )]*5),
            ("free_tier_lie", [T(
                "Freemium model calls still need metering when they sit on critical paths.",
                "Freemium model calls never need metering because the sticker price is zero.",
            )]*5),
            ("burst", [T(
                "Burst traffic without concurrency caps can blow token budgets in minutes.",
                "Burst traffic without concurrency caps is safe if average daily spend looked fine.",
            )]*5),
        ),
        "4": themes(
            ("tiny_cost_myth", [T(
                "Per-query costs that look tiny still sum to large bills at enterprise volume.",
                "Per-query costs that look tiny can be ignored forever at enterprise volume.",
            )]*5),
            ("sota_tax", [T(
                "Paying SOTA prices for every request is a prestige tax, not a strategy.",
                "Paying SOTA prices for every request is always the cheapest long-term strategy.",
            )]*5),
            ("log_everything", [T(
                "Logging full prompts without retention policy can create storage and privacy cost too.",
                "Logging full prompts forever has no tokenomics or privacy downside.",
            )]*5),
            ("one_model", [T(
                "One-model-for-all is a common trap that ignores routing savings.",
                "One-model-for-all is optimal because routing engineering never pays back.",
            )]*5),
            ("ignore_observ", [T(
                "Skipping observability until after launch hides the first spend crisis.",
                "Skipping observability until after launch speeds value with no spend risk.",
            )]*5),
            ("credit_card", [T(
                "Personal credit cards for team model spend break accountability.",
                "Personal credit cards for team model spend improve accountability.",
            )]*5),
            ("unlimited_plan", [T(
                "Unlimited plan marketing does not remove the need for internal rate limits.",
                "Unlimited plan marketing removes the need for internal rate limits.",
            )]*5),
            ("eval_spam", [T(
                "Nightly eval grids without caps can rival production token spend.",
                "Nightly eval grids never need caps because they are not user traffic.",
            )]*5),
            ("agent_badge", [T(
                "Shipping more agents for a press badge can destroy unit economics.",
                "Shipping more agents for a press badge always improves unit economics.",
            )]*5),
            ("finance_late", [T(
                "Bringing finance in only after the surprise invoice is a process failure.",
                "Bringing finance in only after the surprise invoice is normal agile practice.",
            )]*5),
        ),
        "5": themes(
            ("tiered_sla", [T(
                "Tiered model SLAs by query class balance cost and quality better than one tier.",
                "One tier for all queries always balances cost and quality best.",
            )]*5),
            ("budget_as_code", [T(
                "Budgets enforced in code at the gateway beat slideware limits.",
                "Slideware limits beat budgets enforced in code at the gateway.",
            )]*5),
            ("canary_spend", [T(
                "Canary a new agent path on a spend budget before wide rollout.",
                "Wide rollout before a spend canary is fine if quality canaries passed.",
            )]*5),
            ("chargeback", [T(
                "Chargeback of token spend to product teams changes behavior faster than lectures.",
                "Chargeback of token spend to product teams never changes behavior.",
            )]*5),
            ("compress_tools", [T(
                "Tool schemas and results should be trimmed to what the next step needs.",
                "Tool schemas and results should always be dumped in full for safety.",
            )]*5),
            ("idle_agents", [T(
                "Idle scheduled agents that wake and re-read huge contexts waste money.",
                "Idle scheduled agents that re-read huge contexts are free if nobody clicks.",
            )]*5),
            ("multi_provider", [T(
                "Multi-provider routing needs a unified spend ledger, not separate tribal totals.",
                "Multi-provider routing should keep spend ledgers siloed per vendor forever.",
            )]*5),
            ("kill_on_budget", [T(
                "Hard-stop when budget is hit is preferable to soft warnings alone.",
                "Soft warnings alone are preferable to hard-stops when budget is hit.",
            )]*5),
            ("tokex_surface", [T(
                "Surfacing live token expenditure next to the agent UI is a control, not vanity.",
                "Surfacing live token expenditure next to the agent UI is vanity chrome.",
            )]*5),
            ("postmortem", [T(
                "Spend incidents deserve postmortems with concrete gateway fixes.",
                "Spend incidents deserve only a joke in standup and no gateway fixes.",
            )]*5),
        ),
    }

    BANKS["data_ai_guardrails"] = {
        "1": themes(
            ("day_zero", [T(
                "Data classification and access rules for AI features start at ideation.",
                "Data classification for AI features can wait until after users love the demo.",
            )]*5),
            ("rate_limit", [T(
                "Rate limits are a safety control against runaway jobs and cost spikes.",
                "Rate limits only hurt innovation and should be disabled for AI teams.",
            )]*5),
            ("secrets", [T(
                "Secrets and keys must fail closed; agents must not print them into prompts or logs.",
                "Secrets may be pasted into prompts if it makes debugging faster.",
            )]*5),
            ("rag_chunk", [T(
                "Blind vector search over huge corpora can silently truncate context and hallucinate.",
                "Blind vector search over huge corpora never truncates or hallucinates.",
            )]*5),
            ("graph_rag", [T(
                "Strict chunking or Graph RAG can be required for high-volume enterprise retrieval.",
                "Strict chunking or Graph RAG is unnecessary once embeddings exist.",
            )]*5),
            ("pii", [T(
                "PII in prompts and retrieval indexes needs explicit policy and redaction paths.",
                "PII in prompts is fine if the model vendor's terms look friendly.",
            )]*5),
            ("least_priv", [T(
                "Agents should hold least privilege to tools and data stores.",
                "Agents should hold admin privilege so they never block on permissions.",
            )]*5),
            ("audit_log", [T(
                "Immutable audit logs of agent tool use are part of data guardrails.",
                "Immutable audit logs of agent tool use are optional for internal tools.",
            )]*5),
            ("dry_run", [T(
                "Dry-run or sample-scale gates should precede full-corpus AI jobs.",
                "Full-corpus AI jobs should start immediately after a tiny sample succeeds.",
            )]*5),
            ("cyber_pair", [T(
                "Cybersecurity partners with data governance on AI features from day zero.",
                "Cybersecurity should stay out of AI features until a breach is reported.",
            )]*5),
        ),
        "2": themes(
            ("rag_vs_dump", [T(
                "Curated retrieval with chunk budgets beats dumping thousands of docs into context.",
                "Dumping thousands of docs into context is safer than curated retrieval.",
            )]*5),
            ("tool_scope", [T(
                "Narrow tool scopes reduce blast radius when an agent is prompt-injected.",
                "Wide tool scopes are safer because the agent can always recover.",
            )]*5),
            ("egress", [T(
                "Control egress of sensitive data to external model APIs with policy.",
                "Any internal data may egress to external model APIs without policy.",
            )]*5),
            ("retention", [T(
                "Retention limits on prompts and embeddings are a data-guardrail requirement.",
                "Retention limits on prompts and embeddings only create compliance friction.",
            )]*5),
            ("eval_data", [T(
                "Evaluation sets need the same access controls as production data classes.",
                "Evaluation sets may ignore production data classes because they are tests.",
            )]*5),
            ("canary_data", [T(
                "Canary on a low-sensitivity slice before touching crown-jewel datasets.",
                "Crown-jewel datasets are the best first canary because they show value fast.",
            )]*5),
            ("human_approve", [T(
                "Bulk exports or mass updates via agents need human approval gates.",
                "Bulk exports or mass updates via agents should skip human approval for speed.",
            )]*5),
            ("schema_guard", [T(
                "Schema and type checks should gate agent writes to structured stores.",
                "Schema and type checks should be skipped so agents stay creative.",
            )]*5),
            ("tenant", [T(
                "Multi-tenant AI retrieval must enforce tenant isolation hard.",
                "Multi-tenant AI retrieval can soft-share indexes if embeddings look distinct.",
            )]*5),
            ("vendor_dpa", [T(
                "Vendor DPAs and data residency constraints still apply to agent pipelines.",
                "Vendor DPAs do not apply once traffic is labeled experimental AI.",
            )]*5),
        ),
        "3": themes(
            ("silent_trunc", [T(
                "Silent context truncation in RAG is a failure mode that looks like fluency.",
                "Silent context truncation in RAG is harmless if answers remain fluent.",
            )]*5),
            ("leak_log", [T(
                "Logging raw prompts can leak secrets and customer data into ops systems.",
                "Logging raw prompts never leaks because logs are only for engineers.",
            )]*5),
            ("inject", [T(
                "Prompt injection can turn an over-privileged agent into a data exfiltration path.",
                "Prompt injection cannot exfiltrate data if the model is frontier-class.",
            )]*5),
            ("weekend_job", [T(
                "Unattended weekend AI jobs without caps are a classic guardrail miss.",
                "Unattended weekend AI jobs without caps show healthy ownership culture.",
            )]*5),
            ("wrong_index", [T(
                "Retrieving from the wrong index can mix tenants or classifications silently.",
                "Retrieving from the wrong index is obvious to users and self-corrects.",
            )]*5),
            ("stale_embed", [T(
                "Stale embeddings of deleted or restricted docs keep serving forbidden content.",
                "Stale embeddings of deleted docs are automatically inert.",
            )]*5),
            ("over_share", [T(
                "Agents that summarize across ACL boundaries break access control intent.",
                "Agents that summarize across ACL boundaries improve collaboration safely.",
            )]*5),
            ("no_rate", [T(
                "Missing rate limits turn a bug into a data scrape or cost incident.",
                "Missing rate limits cannot turn a bug into a scrape or cost incident.",
            )]*5),
            ("shadow_rag", [T(
                "Shadow RAG indexes outside governance recreate unmanaged data lakes.",
                "Shadow RAG indexes outside governance are agile and therefore preferred.",
            )]*5),
            ("fail_open", [T(
                "Fail-open on auth errors for agent tools is a data guardrail anti-pattern.",
                "Fail-open on auth errors for agent tools keeps UX smooth and is preferred.",
            )]*5),
        ),
        "4": themes(
            ("trust_embed", [T(
                "Trusting embedding similarity alone without citation checks is a known trap.",
                "Trusting embedding similarity alone without citation checks is best practice.",
            )]*5),
            ("move_fast", [T(
                "Move-fast AI on production data without class review is a precedent to reject.",
                "Move-fast AI on production data without class review is a badge of honor.",
            )]*5),
            ("vendor_safe", [T(
                "Assuming a big vendor makes your misuse safe is a governance trap.",
                "A big vendor fully absorbs your misuse risk for free.",
            )]*5),
            ("copy_prod", [T(
                "Copying production databases into AI sandboxes without scrubbing is a classic fail.",
                "Copying production databases into AI sandboxes without scrubbing is standard.",
            )]*5),
            ("open_web", [T(
                "Letting agents browse openly without DLP rules can leak internal context.",
                "Letting agents browse openly without DLP rules is always safe internally.",
            )]*5),
            ("one_index", [T(
                "One shared index for all sensitivity levels is a convenient and dangerous trap.",
                "One shared index for all sensitivity levels is the secure default.",
            )]*5),
            ("ignore_delete", [T(
                "Ignoring right-to-delete in vector stores leaves forbidden residuals.",
                "Ignoring right-to-delete in vector stores is fine because vectors are not data.",
            )]*5),
            ("chat_ops", [T(
                "ChatOps agent commands without authz checks are an incident pattern.",
                "ChatOps agent commands without authz checks speed response safely.",
            )]*5),
            ("benchmark_leak", [T(
                "Leaking proprietary eval data into public model training paths is a guardrail miss.",
                "Leaking proprietary eval data into public training paths is a free marketing win.",
            )]*5),
            ("checkbox", [T(
                "A privacy checkbox without technical enforcement is theater.",
                "A privacy checkbox without technical enforcement is sufficient control.",
            )]*5),
        ),
        "5": themes(
            ("cite_or_abstain", [T(
                "When retrieval confidence is low, abstain or escalate instead of guessing fluently.",
                "When retrieval confidence is low, guess fluently to avoid user friction.",
            )]*5),
            ("dual_gate", [T(
                "Dual approval for mass data mutations by agents is appropriate.",
                "Dual approval for mass data mutations by agents is bureaucratic waste.",
            )]*5),
            ("red_team", [T(
                "Red-team prompt injection and exfil paths before wide agent rollout.",
                "Red-team prompt injection only after a public incident for realism.",
            )]*5),
            ("data_contracts", [T(
                "Data contracts for AI features should state allowed fields, purpose, and retention.",
                "Data contracts for AI features are optional if the embedding model is strong.",
            )]*5),
            ("break_glass", [T(
                "Break-glass access for agents must be time-bound, logged, and rare.",
                "Break-glass access for agents may be standing and lightly logged.",
            )]*5),
            ("cross_border", [T(
                "Cross-border model routing must respect residency and transfer rules.",
                "Cross-border model routing may ignore residency if latency improves.",
            )]*5),
            ("poison", [T(
                "Poisoned documents in RAG can steer agents; integrity checks matter.",
                "Poisoned documents in RAG cannot steer agents if embeddings are normalized.",
            )]*5),
            ("egress_allow", [T(
                "Allowlists for tool egress destinations beat open internet for agents.",
                "Open internet egress for agents beats allowlists for learning speed.",
            )]*5),
            ("delete_propagates", [T(
                "Deletes must propagate to caches, embeddings, and agent memories.",
                "Deletes need only clear the source DB; derivatives may remain forever.",
            )]*5),
            ("gov_board", [T(
                "A standing AI data governance forum beats ad-hoc Slack decisions under pressure.",
                "Ad-hoc Slack decisions under pressure beat a standing AI data governance forum.",
            )]*5),
        ),
    }


def expand_role(key: str, label: str, prefix: str) -> dict:
    levels = {}
    for lv, theme_list in BANKS[key].items():
        slots = []
        for si, (theme, pairs) in enumerate(theme_list, start=1):
            variants = []
            for vi, pat in enumerate(PATTERNS, start=1):
                want_true = bool(pat[si - 1])
                true_s, false_s = pairs[vi - 1]
                text = true_s if want_true else false_s
                variants.append(
                    {
                        "id": f"{prefix}-L{lv}-S{si:02d}-V{vi}",
                        "text": text,
                        "answer": want_true,
                    }
                )
            slots.append({"theme": theme, "slot": si, "variants": variants})
        title, blurb = LEVEL_META[lv]
        levels[lv] = {"title": title, "blurb": blurb, "slots": slots}
    return {"label": label, "levels": levels}


def merge_into_runtime(runtime: dict, role_payloads: dict[str, dict]) -> dict:
    for vname, vdata in runtime["variants"].items():
        vi = int(vname[1])
        for key, payload in role_payloads.items():
            levels_out = {}
            for lv, ldata in payload["levels"].items():
                items = []
                for slot in ldata["slots"]:
                    var = slot["variants"][vi - 1]
                    items.append(
                        {
                            "id": var["id"],
                            "text": var["text"],
                            "answer": bool(var["answer"]),
                            "theme": slot["theme"],
                            "slot": slot["slot"],
                        }
                    )
                levels_out[lv] = {
                    "title": ldata["title"],
                    "blurb": ldata["blurb"],
                    "items": items,
                }
            vdata["roles"][key] = {"label": payload["label"], "levels": levels_out}
    n_roles = len(runtime["variants"]["V1"]["roles"])
    runtime["version"] = 7
    runtime["totalItems"] = n_roles * 5 * 10 * 5
    runtime["note"] = (
        f"Challenge v7: five levels × 10 × 5 packs × {n_roles} roles "
        "(adds Enterprise AI Governance, AI Tokenomics, Data & AI Guardrails). "
        "True-count gated to 5/10 per pack."
    )
    return runtime


def gate_new(runtime: dict, keys: list[str]) -> list[str]:
    issues = []
    for vn, v in runtime["variants"].items():
        for key in keys:
            for lv, pack in v["roles"][key]["levels"].items():
                t = sum(1 for i in pack["items"] if i["answer"] is True)
                if t != 5:
                    issues.append(f"{key} {vn} L{lv} True={t}")
                for i in pack["items"]:
                    if "\u2014" in i["text"]:
                        issues.append(f"emdash {i['id']}")
    return issues


def wire_html() -> None:
    html = INDEX.read_text(encoding="utf-8")
    needle = '              <option value="solutions_architect">Solutions Architect</option>\n'
    insert = (
        needle
        + '              <option value="enterprise_ai_governance">Enterprise AI Governance</option>\n'
        + '              <option value="ai_tokenomics">AI Tokenomics</option>\n'
        + '              <option value="data_ai_guardrails">Data &amp; AI Guardrails</option>\n'
    )
    if "enterprise_ai_governance" not in html:
        if needle not in html:
            raise SystemExit("index.html select needle missing")
        html = html.replace(needle, insert, 1)
        INDEX.write_text(html, encoding="utf-8")
        print("wired index.html options")
    else:
        print("index.html already wired")


def bump_cache() -> None:
    text = PRICKLY_JS.read_text(encoding="utf-8")
    text2 = re.sub(
        r"prickly-dev-banks-variants\.json\?v=\d+",
        "prickly-dev-banks-variants.json?v=7",
        text,
    )
    if text2 != text:
        PRICKLY_JS.write_text(text2, encoding="utf-8")
        print("bumped prickly.js cache to v=7")
    else:
        print("prickly.js cache already v=7 or pattern missing")


def main() -> int:
    build()
    payloads = {
        key: expand_role(key, label, prefix) for key, label, prefix in NEW_ROLES
    }
    runtime = json.loads(RUNTIME.read_text(encoding="utf-8"))
    runtime = merge_into_runtime(runtime, payloads)
    keys = [k for k, _, _ in NEW_ROLES]
    issues = gate_new(runtime, keys)
    RUNTIME.write_text(json.dumps(runtime, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print("wrote", RUNTIME, "totalItems", runtime["totalItems"], "version", runtime["version"])
    wire_html()
    bump_cache()
    for key in keys:
        pack = runtime["variants"]["V1"]["roles"][key]["levels"]["1"]["items"]
        trues = [i["text"] for i in pack if i["answer"]][:1]
        falses = [i["text"] for i in pack if not i["answer"]][:1]
        print(key, "L1 sample T:", trues[0][:80])
        print(key, "L1 sample F:", falses[0][:80])
    if issues:
        print("GATE FAIL")
        for i in issues[:40]:
            print(" -", i)
        return 1
    print("GATE PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
