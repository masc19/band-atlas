# The golden-set test

A **golden set** is one atlas you trust: a scored record file for one profile that a person with industry judgment has reviewed card by card and corrected. It is the reference the engine is measured against. Nothing in this folder contains a real artist's golden set; `eval/demo/golden.json` is the mock scorer's output for the fictional demo band over the demo facts, included only so the comparison runs out of the box.

## Why it exists

Every change to `config/rules.md`, `prompts/judge.md`, the mock scorer or the model behind `ModelScorer` changes judgments. Without a reference you cannot tell whether an edit made the atlas better or just different. With one you get numbers:

- **Group agreement** — share of records placed in the same group (now / reach / attend / above / avoid / dead). The headline metric; the group is what the artist acts on.
- **Adjacent agreement** — same or one step away on the now → reach → attend → above ladder. Separates "slightly conservative" from "wrong".
- **MAE per score** — mean absolute error of impact, fit and likelihood. Watch likelihood: it is the honesty score and the one a model is most tempted to inflate.
- **Spearman of likelihood within each category** — whether the *ordering* matches even when absolute scores drift.
- **Confusion matrix** — which groups get confused with which. `now` ↔ `reach` confusion is tolerable; `now` ↔ `avoid` is a bug.

## How to build your own

1. Run the pipeline for a real profile (`band-atlas build …`) with whichever scorer you trust least.
2. Open `scored.json` next to the rendered atlas and correct every judgment you disagree with: scores, group, `why`. Be strict about `why` — it must name the facts.
3. Save the corrected file as your golden set **outside this repository** (it contains a real person's profile and your editorial judgment, which is the valuable part).
4. From then on, after any rules or prompt change: `band-atlas build …` for the same profile and facts, then `band-atlas eval --golden <your file> --candidate build/scored.json`.

Keep the fact files frozen for the golden profile; otherwise you measure research drift and judgment drift at once.

## Reading the numbers

For a rubric change, expect group agreement to move a few points; a drop of more than ten points means the change did something you did not intend. A new model should be held to the previous model's agreement before it replaces it. When the mock scorer and the model disagree systematically on one category, the rubric for that category is underspecified — fix the words in `config/rules.md`, not the code.

## Demo

```
band-atlas build --facts data/demo/facts --profile intake/example-profile.json --out build/
band-atlas eval  --golden eval/demo/golden.json --candidate build/scored.json
```

prints 100% agreement, because the candidate is the golden set. Change a rubric in the mock scorer and run it again to see the metrics move.
