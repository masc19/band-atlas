# Intake — the questions an artist answers before any agent runs

Structured answers only (tap, pick, number). The only free text is names, links, places and amounts. Two ways to answer: in the chat one question at a time, or in `intake/form.html` — a standalone page that produces the profile JSON to paste back. The JSON Schema in `schema/profile.schema.json` is the contract; this file is the human-readable form. About twenty-five taps, three to five minutes.

**One field per question.** Where a row below has parts (a, b, c), each part is its own question with its own answer control. Never bundle parts into one prose question, and never pre-fill a part from anything but the person's own answer. Ask every question neutrally; never add warnings about honesty or motives — the *Why* column is for the person reading this file, not text to say to the artist. **Every multi-select has an explicit "none of these" option**, so an empty answer is a choice and not a skip. **If the question tool caps the number of options (four in some apps), split the list across two questions in the listed order — never merge two options into one, never drop one, and never push options into "Other".** Single-choice lists longer than the cap are asked coarse-then-fine (e.g. draw: none yet · under 20 · 20–50 · more than 50 → then 50–150 · 150+). The **Ask as** column is the control to use: *free* = text entry (in the question widget: one "None"/"Skip" option plus the widget's free-text field); *pick* = single choice from the listed options; *multi* = several choices; *number* = a number; *yes/no*.

## 1. Who you are musically

| # | Question | Ask as | Field | Why it matters |
|---|---|---|---|---|
| 1 | Artist or band name | free | `artist` | Title of the atlas. |
| 2 | Three to five artists your music sits next to | free (one line) | `reference_artists` | Labels, collabs, promoters and agents are organised around rosters, not genre words. This is the single most important answer. |
| 3 | Confirm the lane built from your references: a name, your anchors, and 8–15 research neighbours you can strike | pick: confirm · strike some (say which) | `lane`, `lane_definition` | The lane is always derived from the artist's own list — there is no genre catalogue to match. `config/lanes.md` is only checked to reuse facts already researched for an overlapping lane. |
| 4 | A link to your music | free (optional) | `links.audio` | Lets the research agent sanity-check the lane. |

## 2. How you perform

| # | Question | Ask as | Field | Why |
|---|---|---|---|---|
| 5 | Live format | pick: DJ · laptop live · laptop + vocal · laptop + vocal + instrument · full band · acoustic | `performance.format` | Rig fit for stages and venues. |
| 6 | How many people travel | pick: 1 · 2 · 3 · 4 · 5+ (then number) | `performance.members` | Travel cost; fee expectations. |
| 7 | Do you also DJ? (skip for full band / acoustic) | yes/no | `performance.also_djs` | Open decks are the fastest route into club-rig rooms. |
| 8a | Inputs you need from a room | multi: stereo line-in · vocal mic · instrument DI · none of these | `performance.rig_needs` | Hard filter on open stages. |
| 8b | Gear you need the room to provide | multi: backline · CDJs · none of these | `performance.rig_needs` | |
| 9a | Short sets you can deliver today | multi: 5 min · 15 min · 30 min · none of these | `performance.set_lengths` | Matches slots. |
| 9b | Long sets you can deliver today | multi: 45 min · 60 min · none of these | `performance.set_lengths` | |
| 10a | Do you have a full-set live video? | yes/no | `performance.has_live_video` | Showcases, Sofar-type series and most bookers judge on video. Changes the group of dozens of records. |
| 10b | (if yes) Link to it | free | `links.live_video` | |

## 3. Where you are

| # | Question | Ask as | Field | Why |
|---|---|---|---|---|
| 11a | Home city | free | `home.city` | Centre of the travel radius. Never assume it. |
| 11b | Country | pick from the most likely for that city, plus Other | `home.country` | ISO code in the profile. |
| 11c | How far you'll travel for a single slot | pick: up to 1 hour · up to 2 hours · up to 3 hours · up to 5 hours · anywhere I can drive in a day | `home.travel_radius_minutes` (stored as 60 / 120 / 180 / 300 / 600) | Filters stages and promoters. |
| 11d | Will you fly for a showcase conference? | yes/no | `home.will_fly_for_showcase` | Gates festivals and showcases outside the radius. |

## 4. Where you stand today

| # | Question | Ask as | Field | Why |
|---|---|---|---|---|
| 12 | Your draw in your home city today — people who come because it's you, not because of the night | pick: none yet · under 20 · 20–50 · 50–150 · 150+ | `standing.draw_band` | The main gate for bookers, promoters and rooms. A realistic number here is what makes the "approach now" list reliable; the question is asked without judgment and "none yet" is a normal answer for a new act. |
| 13 | Monthly listeners | pick: under 1k · 1–10k · 10–50k · 50–250k · 250k+ | `standing.listeners_band` | Collab and label tiers. |
| 14a | Released catalogue | pick: nothing yet · singles · EP · album | `standing.catalogue` | Labels, festivals and showcases keyed on release state. |
| 14b | When is your next release due? | pick: none fixed yet · this month · next month · in 2–3 months · later this year · next year — or type an exact date | `standing.next_release_date` (pick → first of that month; "none fixed" → omitted) | Timing for label and showcase pitches. |
| 15a | Business team you already have | multi: manager · label · distributor · none of these | `standing.team` | Skips categories you don't need. |
| 15b | Live and press team you already have | multi: booking agent · publicist · none of these | `standing.team` | |
| 16a | (electronic lanes) Need Beatport / Traxsource delivery? | yes/no | `standing.needs_dance_store_delivery` | Distributor comparison. |
| 16b | Collaborators or remixers who need royalty splits? | yes/no | `standing.has_split_collaborators` | Distributor comparison. |

## 5. What you want in 12 months

| # | Question | Ask as | Field | Why |
|---|---|---|---|---|
| 17a | Goals for the next 12 months — live side | multi: headline a room · booking agent · festival slots · residency / own night · none of these | `goals` | Shapes the 30-day plan and which "now" items lead it. Not ranked — pick what applies. |
| 17b | Goals — records and reach | multi: label deal · distribution deal · collaborators · press & radio · none of these | `goals` | |
| 17c | (if headline a room) Capacity you're aiming for | pick: 100 · 200 · 300 · 500 · 1000+ | `goal_detail.headline_capacity` | Sets which rooms count as the target. |
| 17d | (if label deal) Label tier | pick: DIY · indie · mid-size · major | `goal_detail.label_tier` | Label likelihood is judged against this tier. |
| 18 | Target markets beyond home (up to three) | free (optional) | `goal_detail.target_markets` | Extra cities for festivals, showcases, agents. |

## 6. Red lines and capacity

| # | Question | Ask as | Field | Why |
|---|---|---|---|---|
| 19 | Pay-to-play tolerance | pick: none, never · small fees OK · ticket quotas OK | `red_lines.pay_to_play` | Drives the Avoid group. |
| 20 | Highest age restriction you can play | pick: 21+ is fine · 18+ only · all-ages only | `red_lines.min_age_ok` (21 / 18 / 0) | Hard filter on rooms. |
| 21 | Scenes or nights you won't play | free (optional, comma-separated) | `red_lines.avoid_scenes` | Avoid group. |
| 22a | Hours per week for pitching | pick: 1 · 2–3 · 4–6 · 7+ | `capacity.hours_per_week` | Sizes the "now" list. |
| 22b | Monthly budget for applications, travel, fees | pick: 0 · up to 50 · up to 150 · up to 500 · more (then number) | `capacity.budget_per_month` | Cost filters. |
| 22c | Yearly budget for showcase conferences | pick: 0 · up to 500 · up to 1,500 · up to 5,000 · more (then number) | `capacity.showcase_budget_per_year` | Showcase group. |
| 23a | People, labels, promoters or companies you're already talking to | free: "None" option + type names | `existing.in_conversation_with` | Flags, never re-recommends. |
| 23b | Anyone we must not suggest | free: "None" option + type names | `existing.do_not_contact` | Hard filter. |

## 7. The run

| # | Question | Ask as | Field | Why |
|---|---|---|---|---|
| 24 | Which categories to run | pick: all that apply (default) · let me choose — then, if choosing, three multi questions of three categories each (open stages · promoters · collabs / labels · distributors · agents / festivals · showcases · bookers), each with "none of these". Categories the team already covers are dropped. | `categories` | |
| 25 | How deep | pick: **Quick** (open stages, promoters, labels, collabs; one pass, ~15 records each; 10–15 min) · **Standard** (all kept categories, one pass; 25–40 min with parallel agents, 1.5–2.5 h sequential) · **Deep** (three narrower sweeps per category plus verification of every record; several hours, best as a scheduled task) | `depth` | Sets research targets, sweep count and verification. API cost scales roughly 1× / 3× / 10×. |
| 26 | (standard or deep only) Run it all now, or spread it across sessions? | pick: all now · three batches over several sessions · scheduled task, one batch per run | `run_plan` | A standard or deep run is a large share of a subscription's usage window. Batches: A open stages + promoters + collabs · B labels + distributors + agents · C festivals + showcases + bookers. |

After a quick or standard run the workflow asks whether to go one level deeper, with the specific gaps from that run (skipped categories, thin tabs, records flagged re-verify) and the expected time.

See `intake/example-profile.json` for a filled-in fictional profile.
