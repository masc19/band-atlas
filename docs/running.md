# Running band-atlas

Two paths. Pick by who you are, not by which is "better".

## Path A — inside Claude, no code (artists, managers, anyone)

What you need: a Claude plan with web search; the ability to attach files or connect a folder; this repository as a zip, a connected folder, or its GitHub URL.

1. Open a new conversation and give Claude the repository.
2. Paste as your first message: *"Read `prompts/run-in-claude.md` in the attached band-atlas package and follow it exactly, starting with the interview. Ask me one question at a time."* In Cowork or Claude Code with the folder open, "build my band atlas" is enough (`CLAUDE.md` routes it). If your app lets you add skills, add `skill/band-atlas/SKILL.md` once.
3. Answer the questions (about five minutes) — one at a time in the chat with options to pick, or open `intake/form.html` in your browser, tap through it and paste the JSON it builds. Claude must not install or run anything on this path; if it starts running tests or `pip`, tell it to stop and follow `prompts/run-in-claude.md`. For a standard or deep run you are asked whether to run it all now or spread it over sessions in three category batches (or as a scheduled task doing one batch per run) — choose "spread" on a Pro plan.
4. Wait. A full nine-category run for a new city and lane takes 20–40 minutes; Claude reports which category it is on. Research runs faster where the app can run sub-agents in parallel.
5. You get a single HTML file (open it in any browser, works offline) and a next-30-days plan in the chat. After a quick or standard run Claude offers the next depth with the specific gaps it found; say yes, schedule it, or stop.

**Which model runs it:** on this path the whole run uses the model your conversation is set to — the package cannot switch models mid-chat. Set the chat to a mid-tier model (Sonnet class) before you start; the largest models add little here and use your allowance several times faster. Where the app can spawn sub-agents with a chosen model (Cowork, Claude Code), the procedure asks for Sonnet-class research agents and Haiku-class clean-up agents on its own.

What it costs: nothing beyond your plan. Long runs use a lot of your plan's usage allowance; expect one full atlas to be a noticeable share of a day's budget on consumer plans.

Known friction:

- **Site approvals.** The desktop app asks you to approve a website the first time Claude opens one, and *Automatically approve* mode does not switch those prompts off — it only stops Claude asking about every other step. What works: set the permission selector (in the message box) to **Automatically approve** so nothing else interrupts, and on each website prompt click **Always allow for this website**, never *Allow once*. The procedure keeps the count low by opening pages only through URLs that came back from a search (a URL Claude types from memory is what triggers a prompt), reading all pages from one site together, and opening sites only to verify "approach now" candidates. Expect a handful of prompts on a standard run. In Claude Code the equivalent is **Yes, and don't ask again** per site, or an allow rule `WebFetch(domain:*)` via `/permissions`. For a fully unattended run, use a scheduled task with its **Automatically approve** setting on; a task that cannot answer a prompt falls back to search snippets and says so in the verify notes.
- **Search allowance.** The Claude apps cap how many web searches a single session or sub-agent can make, and the cap is per session, not per plan — a bigger subscription does not raise it, and it is not a charge. A standard run for a new city can hit it. The procedure handles this by doing actionable records first, stopping cleanly when the cap is reached, and resuming in a new session or scheduled-task run where the cap is fresh; the saved facts carry over. Spreading a standard or deep run across sessions (the interview offers it) is also how a Pro-plan user stays inside the five-hour usage window.
- **Blocked sites.** Instagram, Facebook events, LinkedIn and some ticketing pages cannot be read unattended. Claude is told to say so in each record's verify note rather than guess. Expect promoters and collabs to be thinner than labels and festivals.
- **No files?** If your app cannot write files, ask Claude to put the HTML in a code block and save it yourself as `atlas.html`.

## Path B — the CLI with an API key (developers, operators)

```bash
git clone <this repo> && cd band-atlas
python -m venv .venv && source .venv/bin/activate
pip install -e ".[model,dev]"
pytest                                   # 7 tests, no network

# 1. Try it with no key on the fictional demo city
band-atlas build --facts data/demo/facts --profile intake/example-profile.json --out build/
open build/atlas.html

# 2. Define your lane in config/lanes.md, then research a real city
export ANTHROPIC_API_KEY=sk-ant-...
band-atlas research --category open_stages --lane live-electronic-downtempo --geo "Berlin + 2h" --city Berlin --out data/cache
band-atlas research --category all --lane live-electronic-downtempo --geo "Germany" --city Berlin --out data/cache

# 3. Score for an artist and render
band-atlas build --facts data/cache --profile my-profile.json --scorer model --out build/

# 4. Keep a golden set and check every rules change against it
band-atlas eval --golden ~/private/golden.json --candidate build/scored.json --min-group-agreement 0.85
```

`band-atlas research` uses the hosted web-search tool from the Messages API. Set `ATLAS_MODEL` to pick the model (default `claude-sonnet-5-5`, the current Sonnet ID on the Anthropic models page at time of writing; names change, so check that page). Research runs are single-call per category with a search budget (`--max-searches`); for better coverage run a category three times with narrower `--geo` / `--city` scopes and merge by `id`.

### Suggested models

| Step | Model class | Why |
|---|---|---|
| Research sweeps | Sonnet | Needs judgment about sources and tolerance for long tool loops; Haiku cuts corners on verification |
| Record normalisation / de-duplication | Haiku | Mechanical; cheap |
| Judgment pass | Sonnet (Opus for a golden-set build) | Rubric application with calibrated prose; the `why` sentence quality is the product |
| Cache builds you don't need today | Batch API | Half price, results within a day |

### What it costs (API path)

Based on list prices at time of writing — Sonnet $3 / $15 per million input / output tokens, Haiku $1 / $5, web search $10 per 1,000 searches, prompt-cache reads at 10% of input, Batch API 50% off. Check Anthropic's pricing page before budgeting; these move.

| Unit of work | Typical usage | Approx. cost |
|---|---|---|
| One category sweep, one city/lane, 40 records | 60–150 searches, 1–2M input, 50–100k output | $8–20 |
| Full nine-category sweep for a new city/lane | 9 × above | $80–150 |
| Judgment pass for one artist over ~500 cached records | 300–500k input (mostly cache hits), 30–60k output | $1–3 (Haiku for mechanical parts: under $1) |
| Rebuild of a cache category via Batch API | as sweep | half |

By depth (API path, Sonnet): **quick** ≈ $3–6 and 10–15 min · **standard** ≈ $10–25 and 25–40 min parallel · **deep** ≈ $60–150 and several hours (run via Batch API overnight for half price). On a subscription the same levels cost nothing extra but consume roughly 0.4M / 1–1.5M / 4–6M tokens of your usage allowance.

The research sweep is the cost that matters and it is paid once per city and lane, then shared. Per-artist cost is small.

### Rate limits

New Console accounts start on a low usage tier with modest requests-per-minute and tokens-per-minute limits that rise with cumulative spend. The first few parallel sweeps may throttle; run categories sequentially at first, or use the Batch API for the initial cache.

## Keeping facts fresh

Facts carry `seen_date`. The renderer and judge flag anything older than 180 days with `re-verify`. Re-run a category sweep when more than a third of its records carry the flag; stages and promoters rot fastest.
