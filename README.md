<p align="center">
  <img src="assets/evalathan-logo.png" alt="Evalathan logo: a red dragon curled into an e" width="280">
</p>

<h1 align="center">E V A L A T H A N</h1>

<p align="center"><i><a href="https://htmlpreview.github.io/?https://raw.githubusercontent.com/pedramgoshATgmail/EVALATHAN/main/docs/glossary.html?v=plgout#product-led-growth">Making your Product-led growth (PLG) more efficient, robust, and user-friendly!</a></i></p>

<p align="center">The one-stop evaluation platform for software, engines, agentics, codebases, compilers and languages.</p>

Evalathan grades a product across its life cycle. Evalathan is one evaluation harness; [Hydra](GLOSSARY.md#user-content-hydra) is the conductor - she orchestrates sixteen evaluators ('evalers'); each evaluator reports against a life-cycle gate.

**v0.3** is a local runner. Hydra still conducts sixteen software evalers. [Dehydrus](GLOSSARY.md#user-content-dehydrus) conducts eight [LuDaTs](GLOSSARY.md#user-content-ludats) (Limited-universe Data Test sets) evalers under [PRETRUWs](GLOSSARY.md#user-content-pretruws) (PREdiscovery TRuncated-Universes and Worlds) paradigm. LuDaTs methodology framework is a subset of PRETRUWs paradigm. LuDaTs does not award a state-of-the-art stamp at this point. A deferred evaluation cell is not a fail and not a zero. Roadmap: [docs/BUILDLOG.md](docs/BUILDLOG.md).

On Windows, clone the program, then run `launch.bat` inside that folder. On a Mac, run `bash launch.sh` in that same folder. Either one opens the Hydra window. If that folder already exists, skip the clone and run the launcher there. On Windows you can also double-click `launch.bat`. The Dehydrus window is `evalathan dehydrus`.

<p><img src="assets/readme/windows.png" alt="Windows" height="32" align="absmiddle"> <img src="assets/readme/command-prompt.png" alt="Command Prompt" height="32" align="absmiddle"> <strong>Command Prompt (Windows):</strong></p>

```bat
git clone https://github.com/pedramgoshATgmail/EVALATHAN.git evalathan-program
cd evalathan-program
launch.bat
```

<p><img src="assets/readme/windows.png" alt="Windows" height="32" align="absmiddle"> <img src="assets/readme/powershell.png" alt="PowerShell" height="32" align="absmiddle"> <strong>PowerShell (Windows)</strong> (the prompt starts with <code>PS</code>). <code>cd /d</code> works only in Command Prompt, so this block uses <code>Set-Location</code>:</p>

```powershell
git clone https://github.com/pedramgoshATgmail/EVALATHAN.git evalathan-program
Set-Location evalathan-program
.\launch.bat
```

<p><img src="assets/readme/mac.png" alt="Mac" height="43" align="absmiddle"> <img src="assets/readme/terminal.png" alt="Terminal" height="45" align="absmiddle"> <strong>Terminal (Mac)</strong> (the prompt ends with <code>%</code>). <code>launch.bat</code> is the Windows file. On a Mac the file is <code>launch.sh</code>.</p>

```bash
git clone https://github.com/pedramgoshATgmail/EVALATHAN.git evalathan-program
cd evalathan-program
bash launch.sh
```

<p><img src="assets/readme/mac.png" alt="Mac" height="43" align="absmiddle"> <img src="assets/readme/python.png" alt="Python" height="36" align="absmiddle"> If that Mac Python has no window library, install Python from <a href="https://www.python.org/downloads/macos/">https://www.python.org/downloads/macos/</a> and run <code>bash launch.sh</code> again. That installer includes the window library.</p>

`launch.bat` moves into `evalathan-program`, then runs:

```bat
cd evalathan-program
python -m venv .venv
.venv\Scripts\activate.bat
python -m pip install -U pip
python -m pip install -e .
evalathan
```

`cd evalathan-program` is required before `python -m pip install -e .`. The dot means the current folder. That folder must be the clone, because `pyproject.toml` is there. From a home folder, the dot is that home folder and pip stops. Python 3.10 or newer is required. Git is required to clone this program, and again when the window evaluates a GitHub link. A folder already on the PC can be evaluated without cloning it.

The window takes a GitHub link or a folder. The same grade from Command Prompt, after `launch.bat` has been run once in the clone:

```bat
cd evalathan-program
.venv\Scripts\activate.bat
evalathan scan . --json report.json
```


## Overview & Core Philosophy

EVALATHAN is an open-source, [reductoholistic](GLOSSARY.md#user-content-reductoholism) evaluation harness designed to audit and score software projects, codebases, compilers, and AI agent pipelines across their entire lifecycle.
)

The tool is a local runner (v0.3) aimed at Product-led growth (PLG) and codebase verification. Rather than generating a single aggregated or opaque score, EVALATHAN uses two conductors. [Hydra](GLOSSARY.md#user-content-hydra) orchestrates sixteen software evaluators ("evalers") and writes a transparent status matrix. [Dehydrus](GLOSSARY.md#user-content-dehydrus) orchestrates eight [LuDaTs](GLOSSARY.md#user-content-ludats) (Limited-universe Data Test sets) evalers under [PRETRUWs](GLOSSARY.md#user-content-pretruws). LuDaTs is a subset of PRETRUWs. The two rooms do not share a vector, and they are not folded into one number.

## Architecture & The 16 Evaluators

EVALATHAN evaluates a project by passing a local directory path (`evalathan scan <path> [--json report.json]`). Its 16 evaluators span four distinct operational categories:

| Category | Evalers | Functionality |
| :--- | :--- | :--- |
| Code Health & Repository Metrics | Devly, Archly, Codely, Refactorly, Mixly | Inspects Git history (commits), presence of architectural documentation, cyclomatic/branching complexity, dead code, code churn/duplication, and language breakdown. |
| Performance & Trade-offs | Runly, Pressly, Triadly | Times micro-benchmarks, reads compression and asset quality logs (image/video/file sizes), and documents the project's prioritization order across cost, latency, and impact. |
| AI Agents & LLM Observability | Tokely, Chorely, [Trajectly](GLOSSARY.md#user-content-trajectly), Domly, Warrantly | Tracks token delta/reduction metrics, maps multi-agent rosters and responsibilities, counts agent trace steps, tests domain-specific Q&A pairs, and audits whether factual claims link to verifiable evidence. |
| Human Ergonomics & Reporting | Levi, Menschly, Stackly | Evaluates user-centric scorecards, checks for built-in user break timers, and produces an itemized report of completed vs. deferred checks. |

Dehydrus's eight LuDaTs evalers sit in their own room. They are listed under [What v0.3 runs](#what-v03-runs). They are not a seventeenth Hydra score.

### Unique Features: SELFBELT, FUSS, and PRETRUWs

A standout aspect of EVALATHAN platform is its integration of developer and user wellness into the evaluation criteria:

[SELFBELT](GLOSSARY.md#user-content-selfbelt) / SELFBELTING: A methodology documented in docs/SELFBELT.md addressing developer fatigue and extended screen time.

[FUSS](GLOSSARY.md#user-content-fuss) (For-User Session Switch): A modular front-end/desktop widget inside the repository (fuss/) that developers can embed into software to enforce scheduled rest breaks.

[Menschly](GLOSSARY.md#user-content-menschly): The evaluator specifically tasked with verifying whether a codebase incorporates real session limiters/timers rather than just vague README promises.

[PRETRUWs](GLOSSARY.md#user-content-pretruws) / [LuDaTs](GLOSSARY.md#user-content-ludats) / [Dehydrus](GLOSSARY.md#user-content-dehydrus): The v0.3 physical-world room. PRETRUWs is the 4IR (Fourth Industrial Revolution) paradigm. LuDaTs methodology framework (Limited-universe Data Test sets) is a subset of PRETRUWs: the methodology framework inside that paradigm, not a [Trajectly](GLOSSARY.md#user-content-trajectly) exam. Dehydrus conducts eight LuDaTs evalers. A prompt cutoff is not a world. A blank is not a fail and not a zero.

[HabTwin](GLOSSARY.md#user-content-habtwin): A digital twin is a stand-in. HabTwin asks whether that stand-in keeps predicting what the real person or the real machine would do, in a safe lab, more than once. One lucky guess is not enough. Guessing a live password is not the prize. v0.3 does not run this exam yet. Dehydrus only looks for a lab file. If none is there, it prints `No HabTwin lab trace`. It does not invent a score.

[Deglove](GLOSSARY.md#user-content-deglove) (Refactoring): A name for a still-running codebase so old, messy, and complicated that a local tidy (light refactorying) is the wrong job and a big overhaul is the honest one. The proposed Deglove Rate is not computed in v0.3 and is not a seventeenth evaler.

## What v0.2 runs

Sixteen evalers always appear. Hydra is the conductor and is not a seventeenth score. Point the scan at the tree you want graded. A record that lives in another repository is read when that repository is the path you pass.

| Evaler | What it runs |
| :--- | :--- |
| [Archly](GLOSSARY.md#user-content-archly) | Checks for explicit system architecture blueprints and design specs to verify that structural documentation exists alongside the source code. |
| [Chorely](GLOSSARY.md#user-content-chorely) | Maps multi-agent AI ecosystems by inventorying agent roles, tool assignments, and explicit task boundaries. |
| [Codely](GLOSSARY.md#user-content-codely) | Measures structural complexity by scanning decision forks (if-statements, loops, conditionals) across supported language files. |
| [Devly](GLOSSARY.md#user-content-devly) | Audits version control activity by tallying commit history, branches, and timeline cadence without making subjective assumptions about programmer skill. |
| [Domly](GLOSSARY.md#user-content-domly) | Evaluates domain competency by matching domain-specific test questionnaires against reference golden-answer datasets. |
| [Levi](GLOSSARY.md#user-content-levi) | Parses verified user-first scorecards to validate that the software meets empirical usability and accessibility criteria. |
| [Menschly](GLOSSARY.md#user-content-menschly) | Inspects the codebase for real, programmable session limiters and rest timers (like FUSS) that promote developer and user well-being. |
| [Mixly](GLOSSARY.md#user-content-mixly) | Catalogs the exact breakdown of programming languages across the repository to reveal stack composition and maintenance footprints. |
| [Pressly](GLOSSARY.md#user-content-pressly) | Audits media and data compression efficiency by extracting perceptual quality scores (SSIM/PSNR) and file size deltas from pre-run logs. |
| [Refactorly](GLOSSARY.md#user-content-refactorly) | Detects codebase friction by identifying duplicated files, unused/dead code segments, and high-frequency churn hotspots. |
| [Runly](GLOSSARY.md#user-content-runly) | Measures runtime execution speed via quick local micro-benchmarks or by parsing pre-recorded benchmark logs. |
| [Stackly](GLOSSARY.md#user-content-stackly) | Synthesizes the full evaluation scan into a transparent status matrix showing passed, failed, and deferred checks without masking data behind an artificial composite number. |
| [Tokely](GLOSSARY.md#user-content-tokely) | Audits LLM prompt and completion token efficiency by calculating measured consumption reductions between baseline and optimized runs. |
| [Trajectly](GLOSSARY.md#user-content-trajectly) | Evaluates AI agent execution trajectories by parsing the step-by-step action logs, tool invocations, and completion paths of recorded runs. |
| [Triadly](GLOSSARY.md#user-content-triadly) | Validates engineering trade-off alignments by confirming that explicit priorities among cost, latency, and impact are formally documented. |
| [Warrantly](GLOSSARY.md#user-content-warrantly) | Verifies factual grounding by validating that assertions and benchmark results cite inspectable source artifacts, reproducible recipes, or citations. |

Each name opens its glossary entry. An entry has three parts: what is counted, simplespeak, and techspeak. Public agent exams, and why they are not pasted in, are in the [glossary](GLOSSARY.md#user-content-agentic-exams-that-are-not-on-the-vector-yet).

Levi reads a [4Uvals](GLOSSARY.md#user-content-4uvals) card when one is in the tree. 4Uvals (Ultimate User-User-User evaluations) is a 10-check list asking whether a session put the person first. The published card, v1.2, is a pass: 9 of 10 checks Solid or Strong, mean 3.4 out of 4.

## What v0.3 runs

[Dehydrus](GLOSSARY.md#user-content-dehydrus) conducts eight [LuDaTs](GLOSSARY.md#user-content-ludats) evalers. He is not an eighteenth Hydra score. The default local install still opens Hydra (`launch.bat` / `bash launch.sh`). The Dehydrus desk is a second command: `evalathan dehydrus`. A Dehydrus scan writes eight cells and a note about whether a [HabTwin](GLOSSARY.md#user-content-habtwin) lab file is in the folder. The report body starts with Evalathan v0.3.

Those eight cells are not fully wired into the install you get when you double-click the launcher. v0.3 looks for a sealed world file and names it when one is in the tree. It does not run the locked-year simulator, and it does not award Gold (the structural prize that wins this world, not a sports rank) from a filename. Until a sealed world is present, and until the simulator is the thing the local install runs, the cell stays deferred. A deferred cell is not a fail and not a zero. [Newtonly](GLOSSARY.md#user-content-newtonly) waits until [Keplerly](GLOSSARY.md#user-content-keplerly) and [Galileoly](GLOSSARY.md#user-content-galileoly) both show a sealed world.

| Evaler | What it does |
| :--- | :--- |
| [Copernly](GLOSSARY.md#user-content-copernly) | Rebuilds already-available 1542 (A.D.) sky/known universe numbers as a sun-centered picture. No new telescope. [Mode A](GLOSSARY.md#user-content-ludats-mode-a). |
| [Keplerly](GLOSSARY.md#user-content-keplerly) | Draws the ellipse and equal-area rule from Tycho's Mars table. Same instrument class, not a new optic. [Mode B](GLOSSARY.md#user-content-ludats-mode-b). |
| [Galileoly](GLOSSARY.md#user-content-galileoly) | Required physical-world flagship (pre 1609 A.D). New optic plus a bench on earth: moons, phases, a rough Moon, and the incline law. [Mode C](GLOSSARY.md#user-content-ludats-mode-c). |
| [Darwinly](GLOSSARY.md#user-content-darwinly) | Required long-horizon field world. Years of walking, breeding, and notes. Descent with modification, not the finch cartoon. [Mode D](GLOSSARY.md#user-content-ludats-mode-d). |
| [Mendly](GLOSSARY.md#user-content-mendly) | Arranges the 1868 A.D. set so the holes have the right shape. Later names stay hidden. [Mode E](GLOSSARY.md#user-content-ludats-mode-e). |
| [Einsteinly](GLOSSARY.md#user-content-einsteinly) | Writes the field equations from Mercury's leftover. General Relativity only. 1905 A.D. is another room. [Mode F](GLOSSARY.md#user-content-ludats-mode-f). |
| [CurCuriely](GLOSSARY.md#user-content-curcuriely) | Marie Curie and Pierre Curie. Two biography clocks and two agents. Gold is joint. A solo run stays deferred. [Mode Pair](GLOSSARY.md#user-content-ludats-mode-pair). |
| [Newtonly](GLOSSARY.md#user-content-newtonly) | Unites Kepler's sky with Galileo's ground under one inverse-square law. The apple story is not the method. [Mode Unification](GLOSSARY.md#user-content-ludats-mode-unification). Deferred to v2 until Keplerly and Galileoly are both sealed. |

Each name opens its glossary entry. An entry has the same three parts as the Hydra table: what is counted, simplespeak, and techspeak. Spec: [docs/PRETRUWs.md](docs/PRETRUWs.md), [docs/LuDaTs.md](docs/LuDaTs.md). Cards: [exams/ludats/](exams/ludats/).

## Key Strengths

Holistic Lifecycle View: Most evaluation tools are siloed into either static analysis (e.g., SonarQube, flake8), benchmark profiling (e.g., pytest-benchmark), or LLM (Large Language Model) observability (e.g., Promptfoo, DeepEval). EVALATHAN attempts to unify traditional software metrics, AI agent evaluations, and human-centric design under Hydra, and locked physical-world discovery under Dehydrus.

Two Rooms, Two Conductors: Hydra still writes sixteen software cells. Dehydrus writes eight LuDaTs cells. The rooms do not share a vector. Twenty-four cells are not folded into one number, and there is no state-of-the-art stamp.

Honest, Uninflated Scoring Methodology: The system adopts a strict policy that "a deferred cell is not a fail and not a zero," refusing to synthesize dissimilar metrics into an artificial 0-100 score. It reports what was actually measured versus what was skipped. A sealed-world filename is not Gold.

Locked-Year Honesty: PRETRUWs / LuDaTs refuse a prompt that only says "pretend it is 1610." Later facts have to be actually gone. ExAnte (ACL 2026) showed prompt cutoffs leak.

Clean Packaging: Structured as a modern Python package (pyproject.toml, src/evalathan, tests/), with CLI support and JSON export options for pipeline integration. `evalathan` opens Hydra. `evalathan dehydrus` opens Dehydrus.

Attention to Ergonomics/Ethics: Bringing developer wellness (FUSS/SELFBELT) into code grading is novel and addresses a real blind spot in typical CI/CD quality gates.

## Current Limitations & Areas for Growth

Early Stage (v0.3): The repository now has more than 150 commits and still has no public distribution (it is not on PyPI). Hydra is the window the launcher opens. Dehydrus is present as a second command.

Dehydrus Not Fully Wired: The eight LuDaTs evalers ship as desk cells and exam cards. v0.3 names a sealed world file when one is in the tree. It does not yet run the locked-year simulator inside a default local install, and it does not award Gold from a filename. Missing worlds stay deferred. That wait is part of the method, not a fail.

Passive Log Parsing vs. Active Execution: Several Hydra AI and performance evaluators (e.g., Tokely, [Trajectly](GLOSSARY.md#user-content-trajectly), Pressly) rely on reading pre-existing log files and saved run artifacts rather than executing live tracing or active benchmarking. If a project lacks standardized log outputs, those cells will simply remain blank/deferred.

AST and Language Parsing Depth: Running branching/decision checks (Codely) across arbitrary compilers and languages is non-trivial; depending on the parsers implemented in src/evalathan/, support for languages outside Python may be basic.

DevOps & Community Infrastructure: The repository would benefit from automated GitHub Actions workflows (CI for linting and running the test suite), documentation generation (Sphinx/MkDocs), and automated release pipelines.

## Current Assessment

[EVALATHAN](GLOSSARY.md#user-content-evalathan) is an ambitious, conceptually fresh evaluation harness. v0.3 keeps [Hydra](GLOSSARY.md#user-content-hydra)'s sixteen software evalers and adds the [PRETRUWs](GLOSSARY.md#user-content-pretruws) room: [Dehydrus](GLOSSARY.md#user-content-dehydrus) conducts eight [LuDaTs](GLOSSARY.md#user-content-ludats) brands ([Copernly](GLOSSARY.md#user-content-copernly), [Keplerly](GLOSSARY.md#user-content-keplerly), [Galileoly](GLOSSARY.md#user-content-galileoly), [Darwinly](GLOSSARY.md#user-content-darwinly), [Mendly](GLOSSARY.md#user-content-mendly), [Einsteinly](GLOSSARY.md#user-content-einsteinly), [CurCuriely](GLOSSARY.md#user-content-curcuriely), [Newtonly](GLOSSARY.md#user-content-newtonly)) under one 4IR paradigm. It still stands out for a balanced philosophy: modern AI agent auditing, classic static analysis, developer wellness ([FUSS](GLOSSARY.md#user-content-fuss)/[Menschly](GLOSSARY.md#user-content-menschly)), and locked-year physical-world exams that refuse a textbook title as Gold. The Dehydrus desk is on the tree, but a default local install does not yet run those worlds as live simulators. For production use, treat v0.3 as an experimental two-conductor baseline. The sixteen stay sixteen. The eight stay eight. A blank is not a fail and not a zero.

## SELFBELT

[SELFBELT](docs/SELFBELT.md) (aka Self-Safety or Self-Safetying) is the seatbelt write-up for people who sit with software for a long time. Self-check based ( motto: "It's up to YOU!"). The practice on that page is called SELFBELTING. The PDF itself is too large for GitHub to open in the browser, so the link shows the pages. It is not a seventeenth score. [Menschly](GLOSSARY.md#user-content-menschly) is the evaler that can see a timer. The analogy is the early car: lights and laws arrived before the belt. FUSS is a belt a developer can clip into a product.

## FUSS

[FUSS](fuss/README.md) (For-User Session Switch) is a small panel. The logo sits in the center. It asks whether to time this sitting, then lets a person set minutes, reminder spacing, days, and an optional end date. Copy the `fuss` folder into a web page or a desktop web view. The same files run on Windows and Mac. FUSS is optional. A sentence that merely names it is not a timer.

## [Ed Slop](GLOSSARY.md#user-content-ed-slop)

'Ed Slop' is an AI nom de plume found at the bottom of some of the art and illustrations in Evalathan glossary. Ed Slop is short for Educational Slop (Generative AI visuals) and it doesn't represent any living or human artist, nor does it support trivial slop. Ed Slop's purpose is illustrative imagery and art to help readers better understand complex topics, all through ethical, nontrivial Generative AI creations.

## License

Apache-2.0 for this runner and these rules. The name Evalathan is the product name. Hosted runs are not part of v0.3.

## Not in this version

No hosted site, no invented token percent, no leaderboard copied from somewhere else, and no grade for a tree that is not on disk.

## Roadmap

These are public evals that already exist. Hydra does not run them and does not copy their boards. A later version may print a number a project already saved, the way Pressly reads a compression log. The sixteen stay sixteen. A blank stays blank. Nothing here is blended into one number.

**Ragas.** The glossary entry is [Ragas](GLOSSARY.md#user-content-ragas). The retrieval list includes the four figures assessed for this runner: [Context Precision](GLOSSARY.md#user-content-context-precision), [Context Recall](GLOSSARY.md#user-content-context-recall), [Faithfulness](GLOSSARY.md#user-content-faithfulness), and [NDCG@k](GLOSSARY.md#user-content-ndcg-at-k) (Normalized Discounted Cumulative Gain at k). NDCG@k is a ranking measure. It is not a row on the Ragas list. The rest of that retrieval list is [catalogued with them](GLOSSARY.md#user-content-ragas-other-retrieval).

**SWE family.** [SWE-bench](GLOSSARY.md#user-content-swe-bench) (Software Engineering Benchmark), [SWE-bench Pro](GLOSSARY.md#user-content-swe-bench-pro), and [DeepSWE](GLOSSARY.md#user-content-deepswe).

**PRDBench.** [PRDBench](GLOSSARY.md#user-content-prdbench) grades an agent that builds from a [PRD](GLOSSARY.md#user-content-prd) (Product Requirements Document). Evalathan does not sit that exam and does not copy its board.

**[PRETRUWs](GLOSSARY.md#user-content-pretruws) / [LuDaTs](GLOSSARY.md#user-content-ludats) / [Dehydrus](GLOSSARY.md#user-content-dehydrus).** [PRETRUWs](GLOSSARY.md#user-content-pretruws) (PREdiscovery TRuncated-Universes and Worlds) is the v0.3 4IR (Fourth Industrial Revolution) paradigm. [LuDaTs](GLOSSARY.md#user-content-ludats) (Limited-universe Data Test sets) methodology framework is a subset of PRETRUWs. [Dehydrus](GLOSSARY.md#user-content-dehydrus) conducts eight LuDaTs evalers, including [CurCuriely](GLOSSARY.md#user-content-curcuriely) ([Mode Pair](GLOSSARY.md#user-content-ludats-mode-pair): Marie Curie and Pierre Curie, two agents). Spec: [docs/PRETRUWs.md](docs/PRETRUWs.md), [docs/LuDaTs.md](docs/LuDaTs.md). Cards: [exams/ludats/](exams/ludats/). v0.3 names a sealed world file and does not run the simulator. The sixteen stay sixteen.

**Follow-up paper.** Pedram Goshtasbpour will release *Until Artificial Intelligence Independently Eurekas on its own* and put it up for peer review in early 2027, thirty years after Jim Highsmith's [Messy, Exciting, and Anxiety-Ridden: Adaptive Software Development](https://web.archive.org/web/20171004140236/http://www.adaptivesd.com/articles/messy.htm) (American Programmer, 1997; also described at [Adaptive Software Development](https://en.wikipedia.org/wiki/Adaptive_software_development)). Highsmith called the second world messy, exciting, and anxiety-ridden: unpredictable, nonlinear, and fast. The follow-up does not replace that paper. It states the PRETRUWs third world.

**HabTwin.** A digital twin is a stand-in. [HabTwin](GLOSSARY.md#user-content-habtwin) asks whether that stand-in keeps predicting what the real person or the real machine would do, in a safe lab, more than once. One lucky guess is not enough. v0.3 does not run this exam yet. It only names a lab file if one is in the folder. The exam itself comes later (v0.4). Spec: [docs/HabTwin.md](docs/HabTwin.md).

**AOSE.** [AOSE](GLOSSARY.md#user-content-aose) (agent-oriented software engineering) is the field, not a score. The public catalog named on that entry includes [WildBench](GLOSSARY.md#user-content-wildbench).
