# Hosting it for other artists (design, not code)

Nothing in this repository is a hosted service. This page describes how one would be built so that artists never see a terminal, an API key or a site-approval prompt. It is a design you can hand to a developer, not a promise.

## Why a plain website can't do it

A research run takes 10–40 minutes and makes hundreds of web requests. Static hosting (a GoDaddy site, GitHub Pages) can serve the intake form and the finished atlas, but cannot run the job. Serverless functions time out in seconds to minutes. You need a worker that can run for an hour.

## Architecture

```
intake form (static site)  →  POST /jobs  →  queue  →  worker (band-atlas CLI + Claude API)
                                                           ↓
                                             Postgres: profiles, fact cache, jobs, atlases
                                                           ↓
                                 renderer → locked single-file HTML → object storage → email link
```

- **Intake**: the questions in `intake/questions.md` as a form; posts a JSON profile. Magic-link login so a person can come back.
- **Queue + worker**: a small always-on container (Railway, Fly.io, Render, Cloud Run with a long timeout) running `band-atlas` per job. One worker handles tens of artists a day; the limit is API rate tier, not compute.
- **Fact cache**: Postgres (Supabase, Neon) keyed by category + lane + city/country, with `seen_date`. A job first checks the cache; only missing or stale categories trigger a research sweep. This is what keeps per-artist cost at a dollar or two.
- **Judgment**: per job, over the cached facts, with the rules file as a cached system prompt.
- **Delivery**: render to HTML, encrypt with a per-artist code (the template is a single file; a password gate like the one used by locked HTML exports is a few lines of Web Crypto), store, email the link.
- **Payments**: Stripe Checkout per atlas or a subscription; a run is only queued after payment or an allowance check.
- **Abuse control**: cap runs per email and per IP; never run a sweep on an unpaid, unverified request; a new city is the expensive event, so gate it.

## Accounts and keys

- An Anthropic Console (API) account, separate from any chat subscription. Pay-as-you-go against prepaid credits; keep the key on the worker only, never in the browser.
- Email provider (Resend, Postmark), Stripe, object storage (S3-compatible), a Postgres host. All have free or near-free tiers at this scale.

## Costs at small scale

Using the per-unit numbers in `docs/running.md`:

| Line | Monthly, quiet month | Monthly, busy month |
|---|---|---|
| Infra (worker, DB, storage, email, domain) | $20–40 | $40–80 |
| New city/lane sweeps (the content investment) | 0–2 → $0–300 | 10 → $800–1,500 |
| Per-artist judgment + render | 20 artists → $20–60 | 200 artists → $150–400 |
| Re-verification sweeps of stale categories | $50–150 | $150–400 |

A per-atlas price in the tens of dollars clears per-artist cost many times over; the sweeps are what a scene-coverage strategy costs.

## Operational rules worth keeping

- One editorial review of the "now" group before the first atlas ships in a new city. Twenty minutes; catches most research errors.
- Keep the golden set per lane and run the eval on every rubric change.
- Store the `fetch_blocked` domains per record; route those through a browser-based fetch in the next sweep rather than retrying blind.
- Privacy: a profile is personal data (city, goals, draw). Show a notice, keep a deletion path, and don't keep profiles longer than the atlas is served.
