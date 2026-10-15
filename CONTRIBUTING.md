# Contributing

Most valuable contributions, in order:

1. **Per-country source lists** for a category (where promoters, open stages and bookers are actually listed in Germany, Spain, Japan…), added to the category prompt as guidance.
2. **Rubric refinements** in `config/rules.md` — phrased so a person and a model read them the same way — with the matching change in `MockScorer` and the eval numbers before and after.
3. **Lane definitions** in `config/lanes.md`, with the reference artists that define them.
4. Fixes to the renderer or CLI.

Please do not contribute real fact caches or golden sets: they contain contact details and editorial judgment that belong with whoever researched them. Demo data must stay fictional.
