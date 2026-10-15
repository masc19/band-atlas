# Lanes

A **lane** is the unit of research for labels, collabs, promoters, agents, festivals and showcases. It is defined by reference artists, not by a genre label, because bookers and A&Rs think in rosters.

**Every artist's lane comes from their own reference list.** The interview asks for three to five artists; the lane is built from those (widened to 8–15 neighbours so the research has enough rosters to trace), named, and confirmed in one line. There is no fixed catalogue of genres to match against, and "no lane fits" is never a valid outcome.

This file is the **cache index**: it lists lanes whose facts have already been researched, so a new artist whose references overlap an existing lane can reuse its facts instead of paying for a new sweep. An operator with ears curates it; an artist never has to pick from it. When no cached lane overlaps, the engine defines a new one from the profile and (on the CLI path) appends it here after the first research pass.

Fields per lane: `id`, `label`, `reference_artists` (8–15 well-known acts whose rosters, lineups and label histories define the lane), `adjacent_lanes` (ids), `search_terms` (what promoters and labels call it), `store_terms` (Beatport / Bandcamp / Spotify editorial names), `notes`.

## Cached lanes

One example is included so the format is clear. Replace or extend it with the lanes you have actually researched.

### live-electronic-downtempo (example)

```yaml
id: live-electronic-downtempo
label: Live electronic / downtempo (instrument-led)
reference_artists:
  - Bonobo
  - Caribou
  - Jon Hopkins
  - Maribou State
  - Tourist
  - Floating Points
  - Kiasmos
  - Rival Consoles
  - Max Cooper
  - Nils Frahm
adjacent_lanes: [melodic-house-techno, organic-house, ambient-modern-classical]
search_terms: ["live electronic", "downtempo live", "electronica live band", "ambient techno live"]
store_terms: ["Electronica", "Organic House / Downtempo", "Ambient"]
notes: >
  Live acts with instruments over electronics share bills with DJ-led brands;
  labels split into artist-run boutiques with open demo routes and larger houses
  that only sign through management. Festival stages for the lane are often
  booked by partner promoters rather than open calls.
```

## Deriving a lane from a profile (what the interview does)

1. Take the artist's 3–5 reference artists as the **anchor**: fit is always judged against these.
2. Widen to 8–15 **research neighbours** — acts that share bills, labels or agents with the anchors — so roster tracing has enough surface. Show the artist the neighbours and let them strike any that feel wrong.
3. Name it from what promoters and labels call the sound (`search_terms`), not from a genre taxonomy. Add `adjacent_lanes` only as search hints.
4. Check this file: if a cached lane shares at least three anchors, offer to reuse its facts ("facts for a very similar lane were researched on {date}; reuse them and only research the gaps?"). Otherwise the lane is new, which is normal.
5. On the CLI path, run `prompts/research/labels.md` once, prune neighbours that pulled in the wrong rosters, then run the other categories and append the lane here. If two people with ears disagree on more than a third of the neighbours, it is two lanes.
