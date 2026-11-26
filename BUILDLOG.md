# Evalathan BUILDLOG

Plain version history. Dates are the day each version landed on `main` (git commit date). Newest is at the bottom.

| Version | Date | What shipped |
| :--- | :--- | :--- |
| **start** | **10/16/26** | First commit. Repo opens. |
| **v0.2.0** | **10/16/26** | Hydra runs sixteen software evalers on a local folder. CLI scan. Blank cell is not a fail and not a zero. |
| **v0.2 window** | **10/26/26** | Tk Hydra GUI. Paste a GitHub link or pick a folder. `launch.bat` for Windows clones. |
| **v0.3.0** | **10/31/26** | PRETRUWs room. Dehydrus conducts eight LuDaTs evalers (Copernly … Newtonly). HabTwin named, not scored yet. Still opens the Tk Hydra window by default. |
| **v0.3.1** | **11/02/26** | Browser/`ui/v2` desk wired to real `prepare()` + `conduct()`. Install blocks hard-reset an existing folder to published `main`. Local desktop window + Desktop Evalathan icon. Nell rewrite on detail memos (cards + evidence, no path walls). Glossary auto-links (SASPIANT, M3, evalers, …). Saved runs persist on disk under `~/.evalathan/`. Desktop icon shows a centered FUSS launching splash (animated dots) until the desk window opens. |
| **v0.3.2** | **11/20/26** | Benchrex and Biasrex glossary rooms in Hydra/Dehydrus depth. Benchrex ten cells (seven paper criteria + Assessly / Reportly / Notifyly) credit San Joaquin, Gipiškis, Staufer, Gil (*Deprecating Benchmarks*, arXiv:2507.06434). Biasrex six cells from the Cognitive Bias Codex four problems plus Confirmly / Automately. Ed Slop card art for all ten Benchrex and all six Biasrex evalers. Conductors still not live-wired in the default desk. |
| **v0.3.3** | **11/20/26** | Desk memo eye-comfort palette under [**4Uvals** (Ultimate User-User-User evaluations)](GLOSSARY.md#user-content-4uvals) + [**Menschly** (limited-use / well-being evaler)](GLOSSARY.md#user-content-menschly) policy: memo sheet `#FFF4E5`, evaler bevel cards `#E8F3E8`, body text `#2B2B2B` (hyperlinks stay blue). Same mandate covers FUSS (For-User Session Switch) Irish-orange controls and Prickly accent hues. See one-line detail below. |
| **v0.3.4** | **11/21/26** | [**PRICKLY**](GLOSSARY.md#user-content-prickly) desk live (no Coming soon): FUSS-simple picker → profile → timed True/False (Developer L&R + [**JaPoP**](GLOSSARY.md#user-content-japop) L&R) or JaPoP Static timestamped-comms heuristic. Soft 3-week / 6-month duration guidance only. Glossary entries for PRICKLY + JaPoP. |
| **v0.3.5** | **11/21/26** | PRICKLY Developer L&R wires 3000-item True/False banks (12 roles × 5 levels × 10 × 5 packs V1-V5) with local pack rotation; final FUSS + PRICKLY circular logos on desk, glossary, and README; memo/FUSS/PRICKLY palette polish; scalable PRICKLY popup + Irish-green circular countdown twin of FUSS. |
| **v0.3.6** | **11/21/26** | Desk copy/UI: PRICKLY/FUSS italic title tags, drop "sit" language, PRICKLY RESULTS rail matches history latest-run chips, Nell (agent) rewrite label; mint panel colors kept. |
| **v0.3.7** | **11/22/26** | [EVOLVER](GLOSSARY.md#user-content-evolver) right-rail nest ([RefineX](GLOSSARY.md#user-content-refinex), [SpunkworX](GLOSSARY.md#user-content-spunkworx), [ConneX](GLOSSARY.md#user-content-connex), [TOKEX](GLOSSARY.md#user-content-tokex), Hi0); PRICKLY fifteen specializations + practice policy labels + governance packs; selective bank hygiene (HOLD; rebuild = authoring + [SME](https://en.wikipedia.org/wiki/Subject-matter_expert) dual-key + pilot). |
| **v0.3.7.1** | **11/26/26** (current) | Developer [L&R](GLOSSARY.md#user-content-lr) [MCQ](GLOSSARY.md#user-content-mcq) (five A-E packs derived from T/F; format picker; grey choice frames); clearer [L&R](GLOSSARY.md#user-content-lr) / [JaPoP](GLOSSARY.md#user-content-japop) glossary explainers. |

## One-line each

### 10/16/26 - start
First commit on GitHub.

### 10/16/26 - v0.2.0
Sixteen Hydra evalers grade what is on disk. No opaque single score.

### 10/26/26 - v0.2 window
Desktop Tk window for link-or-folder evaluates. This is the “old Hydra GUI.”

### 10/31/26 - v0.3.0
Adds Dehydrus + eight LuDaTs worlds under PRETRUWs. Hydra’s sixteen stay sixteen. Default UI is still Tk.

### 11/02/26 - v0.3.1
Default desk is local `ui/v2` (native window + Desktop dragon icon). Same Hydra sixteen, live evaluate path. Install blocks always replace an old clone with published `main`. Nell cards for detail memos. Glossary term auto-links. Saved runs survive restart via `~/.evalathan/run_sets.json`. Double-clicking the Desktop icon pops a centered FUSS logo splash with launching... and three fading dots until the desk window is ready.

### 11/20/26 - v0.3.2
Glossary + desk names for Benchrex (10) and Biasrex (6) match Hydra/Dehydrus writing structure (Score Constitution / Simplespeak / Techspeak). Paper people and Codex lineage are cited. Ed Slop card art lands for all ten Benchrex and all six Biasrex evalers (Filterly, Meaningly, Hastely, Memoryly, Confirmly, Automately). Biasrex conductor emblem ships in glossary + desktop desk (same logo/title scale as Benchrex). Live `conduct()` for those rooms is still held.

### 11/21/26 - v0.3.4
**PRICKLY + JaPoP on the desk.** `#btn-prickly` opens a FUSS-simple panel (`ui/v2/prickly.js`): pick Developer L&R, JaPoP L&R, or JaPoP Static; collect who-is-sitting; run True/False banks or paste dated lines for a reciprocity/span heuristic. Soft duration note (~3 weeks provisional, ~6 months stronger) on the upload surface - not a hard 2-year gate. Blank/undated uploads defer. Glossary: [PRICKLY](GLOSSARY.md#user-content-prickly), [JaPoP](GLOSSARY.md#user-content-japop) (Just-a-Professional-or-Partnerable; formerly ToP).

### 11/21/26 - v0.3.5
**PRICKLY banks + final logos.** Developer L&R loads [prickly-dev-banks-variants.json](ui/v2/assets/prickly-dev-banks-variants.json) (3000 True/False items; rotates packs V1-V5). Final circular FUSS and PRICKLY logos on the desk rail, glossary, and README. Memo / FUSS / PRICKLY shared palette; PRICKLY countdown matches FUSS circular splash in Irish-flag green.

### 11/22/26 - v0.3.7
**EVOLVER + PRICKLY expansion.** Right history rail gains TOKEX - Token Expenditure strip and EVOLVER nest: RefineX (Paid/Bring-your-own API option), SpunkworX (freemium MoE option; staged Delphic rounds), ConneX (provider/model/guardrails). Hi0 lossless pack utility + `/api/evolver/*` on the local desk. PRICKLY Developer L&R grows to fifteen specializations (adds Enterprise AI Governance, AI Tokenomics, Data & AI Guardrails) with trusted-corridor / use-with-care / new & work-in-progress labels. Bank posture: selective rebuild, not scrap-all; prior review HOLD; wired work is policy + structural hygiene; next rebuild steps are authoring, [SME](https://en.wikipedia.org/wiki/Subject-matter_expert) (Subject-Matter Expert) dual-key, then a practitioner pilot - not more UI.

### 11/26/26 - v0.3.7.1 (current)
**Developer [L&R](GLOSSARY.md#user-content-lr) MCQ + glossary clarity.** Format picker after specialty: True/False (unchanged packs) or Multiple Choice (five rotatable A-E packs keyed to the T/F bank). Light-grey choice frames with darker hover. Glossary: clearer [L&R](GLOSSARY.md#user-content-lr) and [JaPoP](GLOSSARY.md#user-content-japop) intro/simplespeak; new [MCQ](GLOSSARY.md#user-content-mcq) entry (one MCQ hyperlink from PRICKLY simplespeak).

### 11/21/26 - v0.3.6
**Desk GUI polish.** Centered italic PRICKLY/FUSS title tags; replace user-facing "sit" copy; PRICKLY RESULTS list uses the same latest-run chip structure as history; Full details kicker says Nell (agent) rewrite. Panel wash stays mint (`#D1E6DE`).

### 11/20/26 - v0.3.3
**Memo eye-comfort palette ([4Uvals](GLOSSARY.md#user-content-4uvals) / [Menschly](GLOSSARY.md#user-content-menschly) mandate).** Sheet/bevel placements: warm cream #FFF4E5 on the memo background, soft green #E8F3E8 on evaler rectangles (swapped from the first cut). Brief and detail memos on the local desk (`ui/v2`) use three fixed hues chosen for long technical reading on a computer desktop, not for brand decoration:

| Surface | Hex | Role |
| :--- | :--- | :--- |
| Memo sheet background | `#FFF4E5` | Warm cream wash - reduces glare vs pure white for long memo reads |
| Evaler bevel rectangles (Nell cards) | `#E8F3E8` | Soft green sash - softer nested panels without harsh white-on-white |
| Body font (non-link) | `#2B2B2B` | Near-black ink - high legibility without pure `#000` glare; hyperlinked words stay blue |

**Why these two sheet hues.** Operator ask (desktop research cue): *[two safest color hues/shades for reading memos on computer desktop](https://www.google.com/search?q=two+safest+color+hues%2Fsahes+for+reading+memoms+on+computer+dekstop)*. Soft green and warm cream/ivory are the classic pair recommended for reduced eye strain on long on-screen reading (green calms glare; cream avoids harsh white contrast). Evalathan locks that pair as sheet `#FFF4E5` (warm cream) + bevel `#E8F3E8` (soft green), with `#2B2B2B` body text. Policy home: [**4Uvals**](GLOSSARY.md#user-content-4uvals) U9 (well-being axis) and U6 (**FUSS** instrument), enforced in product spirit by [**Menschly**](GLOSSARY.md#user-content-menschly) - sourced from the SEISMO (AZ Signal Engine) pack `docs/evals/4UVALS.md` (sibling project pack) and mirrored in this repo's [4Uvals](GLOSSARY.md#user-content-4uvals) / [Menschly](GLOSSARY.md#user-content-menschly) glossary entries.

**Buttons under the same mandate.** FUSS panel accents (`#c45c26` title / live counter, `#ff7900` Irish-flag orange Start / countdown disk) and Prickly desk accent (lime `--accent` / mascot rail) were meticulously selected the same way - readable at a glance, not neon-on-white, so session controls stay comfortable during long sittings. PDF download HTML for memos mirrors the same three memo hexes.

## Next (not shipped)

| Version | Planned |
| :--- | :--- |
| v0.4 | HabTwin scoring engine (lab-only twin fidelity). |
| v0.5 | Later Hydra-side interpersonal exam family (held). |

Roadmap detail that is not a ship date lives in [docs/BUILDLOG.md](docs/BUILDLOG.md).

