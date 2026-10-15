# band-atlas

**A personalised scene atlas for a developing music act.** Answer about twenty short questions — what you sound like, how you perform, where you are, how big your draw really is, what you want in twelve months, what you refuse to do — and get a single-page atlas of the labels, distributors, collaborators, open stages, festivals, showcases, bookers, promoters and agents that matter for *you*, each scored for impact, fit and likelihood and grouped into **approach now / reach in 12–24 months / attend, don't apply / above your level / avoid**, with a one-sentence reason that names the facts behind it.

The engine separates two things that scene guides usually mix up:

- **Facts** about a label, a night, a promoter — who runs it, what it books, how you apply, what it costs, who's on the roster, when it was last verified. Researched once per lane and city by an LLM agent with web search under a *published-contacts-only* policy, and shared by every artist.
- **Judgments** — how much it would move *this* artist, how well their sound and live format fit, how likely a yes is at their current stage, and what to do next. Computed per artist from their profile and the facts. Never shared.

Facts are cached; judgments are cheap. That is the whole trick.

## For artists — start here (no code, no API key)

1. Open a new Claude conversation (claude.ai, the desktop app, Cowork or Claude Code), set its model to Sonnet, and attach this package — the zip or the unzipped folder.
2. Paste as your first message:

   > Read `prompts/run-in-claude.md` in the attached band-atlas package and follow it exactly, starting with the interview. Ask me one question at a time.

3. Answer about twenty short questions — in the chat with options to pick, or by filling in `intake/form.html` in your browser and pasting the JSON it produces. Choose **quick** the first time (10–15 minutes). You get one HTML file — open it in any browser — and a 30-day plan in the chat. Claude then offers to go deeper.

In Cowork or Claude Code with this folder open, step 2 can be just *build my band atlas* — `CLAUDE.md` routes it. If your app lets you add skills, `skill/band-atlas/SKILL.md` makes it a standing command. If Claude asks you to approve websites during research, approve them; it happens once per site. Runs cost nothing beyond your Claude plan; a standard or deep run can be spread across sessions, and the workflow asks.

`START_HERE.md` says the same in six lines.

---

## For developers

### Try the engine in a minute (no API key)

```bash
pip install -e ".[dev]"
band-atlas build --facts data/demo/facts --profile intake/example-profile.json --out build/
open build/atlas.html
pytest
```

The demo scores 48 real New York records (open stages, promoters, bookers) plus real labels, distributors, agents, festivals and showcases — researched from official pages in Aug–Sep 2026 — for a fictional three-piece band. It runs the deterministic mock scorer so you can see the whole pipeline — filters, scores, groups, reasons, the rendered page — without spending anything. See `data/demo/README.md` before contacting anyone in it.

### Run it for real from the command line

`band-atlas research` builds the fact cache for a lane and city with the Claude API's web search (this is the only step that needs an API key); `band-atlas build --scorer model` scores and renders for a profile; `band-atlas eval` compares a run against a golden set. Costs, model suggestions and rate-limit notes are in `docs/running.md`; a design for hosting it for other artists is in `docs/hosting.md`.

## What's in the box

```
START_HERE.md                the six-line version for artists
CLAUDE.md / AGENTS.md        routes "build my band atlas" to the procedure when Claude works in this folder
intake/questions.md          the interview, with the reason each question exists
intake/form.html             the same interview as a tap-through form that outputs the profile JSON
schema/profile.schema.json   the profile contract
schema/record.schema.json    the record contract: facts (shared) and judgment (per artist), kept apart
config/rules.md              scoring rubrics with anchors, group rules, contact & verification policy
config/lanes.md              what a "lane" is (derived from each artist's references, never a genre catalogue) and the cache of researched lanes
prompts/research/*.md        one research prompt per category + a common preamble
prompts/judge.md             the judgment procedure
prompts/run-in-claude.md     the no-code path
skill/band-atlas/SKILL.md    the same, as an installable skill
atlas/                       Python package: schema validation, research, judge (mock + model), renderer, CLI
eval/                        the golden-set method and comparison script
data/demo/                   demo facts: real NYC records, fictional band
docs/                        running, hosting design, limits, architecture
tests/                       pytest, no network
```

## The golden-set test

Any change to the rules or prompts changes judgments. `eval/golden.md` describes how to keep one hand-reviewed atlas as a reference and measure every change against it: group agreement, adjacent agreement, score error, rank correlation, confusion matrix. `band-atlas eval` prints the numbers and can fail CI below a threshold. Your golden set stays private; it contains a real profile and your editorial judgment, which is the valuable part.

## Design choices

- **Rules in prose.** The consumers are a language model and a person; "a label that signs finished EPs is a reach for an artist with no releases" is clearer in English than in YAML, and the eval tells you when the English is ambiguous.
- **A mock scorer that implements the same rubrics.** Tests are reproducible, the pipeline runs offline, and the gap between mock and model is itself diagnostic.
- **Honesty as a scoring rule.** Likelihood is never raised because impact is high; "above your level" is a group, not a deletion; folded venues stay in the data so stale listings don't send anyone chasing them.
- **No constructed contacts.** If the contact isn't published, the record says so.
- **Single-file output.** The atlas is one HTML file: works offline, emails, locks behind a code.

## Limits

Read `docs/limits.md`. In one line: coverage is uneven (promoters and open stages live on sites that block unattended reading), facts rot, and the output applies written rules to the artist's own answers — honest answers in, honest atlas out.

## Author

Built by Martin, a music-industry executive working across recorded music, streaming, partnerships and AI, after building a version of this by hand for one act and deciding the method was the product. The lane example, the demo data and the rubric anchors are one practitioner's view; change them.

## License

MIT.
