# Rules — scoring rubrics, groups, policies

Read by the judgment prompt on every run and by humans when they disagree with an output. Edit sentences, not code. The mock scorer in `atlas/judge.py` implements the same rubrics deterministically so the pipeline runs without an API key; when you change a rubric here, change the mock too, and the golden-set eval tells you whether the change helped.

## 1. The three scores (0–10, calibrated within each category)

**Impact** — how much this would move the artist if it happened. Anchors: 2 = a rehearsal-grade slot or a listing nobody sees; 5 = a real show, a release on a small label, a useful contact; 8 = a slot or signing that changes the next twelve months (a 200+ cap room, a label whose roster tours, a festival that industry attends); 10 = a career-defining outcome.

**Fit** — how naturally the artist's sound and live format sit in what this records / books / signs. Anchors: 2 = different genre world; 5 = adjacent lane, occasional bookings in the artist's lane; 8 = the lane is their core programming or roster; 10 = the roster trace reads like the artist's reference list. Format matters for stages and promoters: a `rig_support` below what the artist needs caps fit at 4.

**Likelihood** — odds of a positive outcome at the artist's current stage. Anchors: 1 = no open door and the roster is several levels up; 3 = open door exists but the artist is at least two draw bands or one catalogue stage short; 5 = open door, requirements roughly met, competitive; 7 = open door, artist meets or exceeds what they typically take; 9 = warm route or explicit call for acts at this level.

Likelihood is where honesty lives. Never raise it because impact is high.

## 2. Groups

| Group | Meaning | Rule of thumb |
|---|---|---|
| `now` | Approach this month | likelihood ≥ 6 and act_level ≥ 2, or likelihood ≥ 7 with a warm route |
| `reach` | 12–24 months | likelihood 3–5, and the gap is something the artist can close (a release, a video, draw) |
| `attend` | Go, don't apply | events whose stages are booked only through partners, or open calls structurally closed to the artist (wrong country, wrong format); value is the room, not the slot |
| `above` | Above current level | likelihood ≤ 2 with impact ≥ 7; keep as the map of where this ends up |
| `avoid` | Don't | pay_to_play conflicts with the profile's red line, format rules exclude the act, or terms are predatory |
| `dead` | Folded / dormant / unverified | status ≠ active; keep so stale aggregator listings don't send anyone chasing them |

For open stages the groups render as P1 (`now`), P2 (`reach`), P3 (`attend`, repurposed as "rehearsal / networking") and Avoid.

## 3. Category-specific rules

- **Labels.** Fit from `lane_tags` and `roster_trace` against the profile's lane and reference artists. Likelihood from `act_level` (demo form or published A&R contact), label tier against `goal_detail.label_tier`, and catalogue stage: a label that signs finished EPs is `reach` for an artist with no releases. Skip the category entirely when the profile already has a label.
- **Distributors.** Not scored on fit/likelihood in the usual sense; ranked by fit to needs: `needs_dance_store_delivery` requires `distribution.dance_store_delivery`; `has_split_collaborators` rewards `splits_tooling`; `cost_amount` against `capacity.budget_per_month × 12`. Skip when the profile has a distributor.
- **Collabs.** Fit from shared lane and reference overlap; likelihood from audience-size gap (a collaborator more than two bands up rarely answers) and geography (same city doubles likelihood). Impact from their audience size and label ties.
- **Open stages.** Hard filters first: `min_age` vs `red_lines.min_age_ok`; `pay_to_play` vs red line; travel time implied by city vs `travel_radius_minutes`; `rig_support` vs `performance.format` (a laptop + vocal + instrument act needs 3; DJ-only nights score only if `also_djs`). Then P1/P2/P3 by sound, genre focus and set length against `set_lengths`.
- **Festivals / showcases.** Likelihood from `min_draw_band`, catalogue stage and `has_live_video`; `attend` when `act_level` ≤ 1 and the event is industry-facing; `cost_amount` against `capacity.showcase_budget_per_year`; `will_fly_for_showcase` gates anything outside the travel radius.
- **Bookers / promoters.** Fit from lane; likelihood from `min_draw_band` vs `draw_band` and `act_level`; `above` when they book touring headliners only. Same-city promoters get +2 likelihood.
- **Agents.** Mostly `reach` or `above` by construction; `now` only for independents with a published development policy and an artist with a release, a video and a draw band ≥ 2.

## 4. The `why` sentence

Must name the facts and profile fields it relies on, so a user can see why: "P2 because the room takes a full rig and has subs, but it wants a live video first and you don't have one yet." Never "great fit!".

## 5. Contact and data policy (applies to research prompts and to the judgment pass)

- Published business contacts only. An email or form that appears on the organisation's own site or an official listing. Never construct an address from a naming pattern. Never copy a personal email from a third-party scrape.
- Instagram or other handles only when a source outside that platform names them as the booking channel.
- Every fact record carries `sources` (URLs), `seen_date` and `verify` (what was and was not confirmed; which fetches were blocked).
- No record is rendered without at least one source.
- Private groups, paywalled databases and anything behind a login are out of scope.
- `do_not_contact` entries from the profile are rendered greyed out with the artist's note, never deleted from the cache.

## 5b. Unverified records

An `unverified` record is a lead that did not get verified, not a finding. A category tab may hold at most one unverified record for every three settled ones (unverified-ratio ≤ 25%); beyond that, the extras go to the run's gaps list rather than the atlas. A deeper run spends its first effort converting `unverified` into `active`, `dormant` or `folded` before it adds anything new.

## 6. Freshness

Facts older than 180 days render with a "re-verify" badge. Stages and promoters rot fastest; labels and agents slowest.
