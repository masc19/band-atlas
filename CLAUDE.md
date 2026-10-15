# Instructions for Claude working in this folder

This is **band-atlas**: an engine that builds a personalised scene atlas for a developing music act.

- When the person asks for an atlas, a scene map, where to play, which labels or promoters fit, or says "build my band atlas": **read `prompts/run-in-claude.md` and follow it exactly**, starting with the interview in `intake/questions.md`, one question at a time. Do not research before the interview is complete.
- Rules, rubrics and the contact policy are in `config/rules.md`. Published contacts only; a source URL and a verify note on every record; never guess.
- **Never install packages, run tests or run the CLI for the no-code path.** Nothing needs to be executed; the Python package is for developers only. Do not pre-fill interview answers from files, memory or the demo — every answer comes from the person, in this conversation (or as a pasted profile JSON from `intake/form.html`).
- Ask interview questions with a structured-question tool when one is available (options for every fixed-choice field, one question at a time); otherwise as numbered lists.
- The no-code path needs no API key and no terminal. Only suggest the CLI (`atlas/`, `docs/running.md` Path B) if the person says they are a developer or asks about the API.
- The demo data in `data/demo/` is real New York research scored for a fictional band; it is an example, not the person's atlas.
- The same procedure is packaged as a skill in `skill/band-atlas/SKILL.md`.
