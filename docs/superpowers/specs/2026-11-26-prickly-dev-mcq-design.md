# PRICKLY Developer L&R - Multiple Choice (five packs)

Date: 2026-11-26. Status: approved (#2 five MCQ packs).

## Goal

Keep existing True/False banks unchanged. Add a Developer L&R format picker (True/False | Multiple Choice) and ship five rotatable MCQ packs aligned to the fifteen specializations × five levels × ten questions.

## Shape

- Source of truth for T/F: `ui/v2/assets/prickly-dev-banks-variants.json` (unchanged).
- New bank: `ui/v2/assets/prickly-dev-mcq-banks-variants.json`
  - `format: multiple_choice`
  - Variants V1–V5
  - 15 roles × 5 levels × 10 items = 3750 MCQ items
  - Each item: `id`, `stem`, `choices` (exactly 5), `answerIndex` (0–4), `theme`, `slot`, `source_id`, `polarity` (`sound` | `trap`)
- Generator: `scripts/generate_prickly_dev_mcq_banks.py` builds MCQ from each T/F item.
- Validator: same script `--validate` (or post-write check) enforces completeness, uniqueness, answer key alignment.

## Conversion rule

- If T/F `answer` is true: stem asks for the **sound practice**; correct choice = that statement; distractors = unsound statements from the role pool.
- If T/F `answer` is false: stem asks for the **unsound / trap**; correct choice = that statement; distractors = sound statements from the role pool.
- Choices are seeded-shuffled so `answerIndex` is not always 0.
- Distractor pool expands across same-role packs/levels when a single level lacks four opposite-polarity items.

## GUI

- After Developer profile: format step → countdown → sit.
- T/F buttons unchanged; MCQ shows five choice buttons (A–E).
- Results store `format: "tf" | "mcq"`; miss review prints choice text / letter.

## Trust

Same HOLD / corridor labels as T/F. Practice feedback only until SME dual-key.
