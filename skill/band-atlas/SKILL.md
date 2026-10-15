---
name: band-atlas
description: Build a personalised scene atlas for a developing music act — labels, distributors, collaborators, open stages, festivals, showcases, bookers, promoters and agents — by interviewing the artist, researching the facts with web search under a published-contacts-only policy, scoring every record for that artist, and delivering a single HTML atlas plus a 30-day plan. Use when someone says "build my band atlas", "where should my band play", "which labels fit my music", "who should I pitch", or asks for a scene map for a city and genre.
---

# band-atlas

You are running the band-atlas engine without code. The repository (attached, connected or linked) holds the rules; this skill is the procedure. Read these before starting: `config/rules.md` (rubrics, groups, contact policy), `config/lanes.md`, `intake/questions.md`, `prompts/research/_common.md`, `prompts/judge.md`, `atlas/template.html`.

## Procedure

0. **Setup** — do not install, test or run any code; read the Markdown and schema only. Do not pre-fill answers from files, memory or the demo. Offer two ways: questions here one at a time (use a structured-question tool with options when available), or `intake/form.html` → paste the JSON. A pasted profile skips the interview.
1. **Interview** — ask the questions in `intake/questions.md` one at a time, offering fixed choices. Build the lane from the person's own reference artists (anchors + 8–15 research neighbours, named as promoters would say it) and confirm it in one positive question; `config/lanes.md` is a cache to reuse facts from, not a catalogue to match, and a new lane is the normal case. Skip questions earlier answers make irrelevant. Summarise the profile as JSON (shape: `schema/profile.schema.json`) and get a yes.
1b. **Setup message** — after the profile is confirmed: ask the person to switch the chat to a mid-tier model (Sonnet) if you are larger, explain how to avoid per-site approvals (session auto-approval, "always allow" per site, or a scheduled task with auto-approval), state the duration, wait for go.
2. **Research** — honour `depth` (quick / standard / deep: see the table in `prompts/run-in-claude.md`) and tell the person the expected duration first. For standard or deep, ask whether to run it all now or spread it across sessions (category batches, or a scheduled task doing one batch per run); if spread, save the profile and batch plan, do batch one, and say exactly how to resume. For each kept category, combine `prompts/research/_common.md` with the category prompt, fill the braces, and research with web search. Published contacts only; one source URL and a verify note per record; keep folded or dormant entries with their status. Run categories in parallel with sub-agents when available; otherwise one at a time, reporting progress. Never fill a gap with a guess; record blocked sites in `verify`.
3. **Judge** — score each record for this profile using `config/rules.md` as the rubric and `prompts/judge.md` as the procedure. Hard filters first. Likelihood is never raised because impact is high. Every `why` names the facts and profile fields behind it.
4. **Deliver** — fill `atlas/template.html` (replace `/*__DATA__*/{}` with the payload described in `atlas/render.py`, `__TITLE__` with the title) and hand over the HTML. Then give a "next 30 days" plan: the five to eight `now` items in order, each with its route, plus the single unlock for the most `reach` items. List blocked sources and what to verify by hand. After a quick or standard run, offer the next depth with concrete reasons from this run (skipped categories, thin tabs, re-verify flags) and the expected time; on yes, add to the existing facts rather than redoing them.

## Guardrails

- No constructed email addresses, no personal contacts scraped from third parties, nothing from behind a login.
- Say "nothing books your format at your draw in this city yet" when that is the truth, and show the three steps that change it.
- Do not reuse one artist's judgments for another; facts are shared, judgments are not.
