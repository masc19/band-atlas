# Architecture

```
                 intake (questions.md → profile.json)
                               │
      ┌────────────────────────┼────────────────────────┐
      │                        │                        │
 lanes.md              research prompts            rules.md
 (editorial)           (_common + category)        (rubrics, groups, policy)
      │                        │                        │
      └───────► research.py ◄──┘                        │
              (Claude + web search)                     │
                      │                                 │
              fact cache  (JSON per category · lane · city; seen_date, sources, verify)
                      │                                 │
                      └──────────► judge.py ◄───────────┘
                               MockScorer | ModelScorer
                                       │
                             scored.json (facts + judgment)
                                 │              │
                            render.py        eval/compare.py ◄── golden set (private)
                                 │
                            atlas.html (single file)
```

Invariants:

1. `facts` never contains an opinion about a specific artist. If a research prompt produces one, that is a bug in the prompt.
2. `judgment` is a pure function of (profile, facts, rules). Two artists never share a judgment.
3. Every rendered record has at least one source URL and a seen date.
4. The mock scorer and the model scorer implement the same `config/rules.md`; divergence is measured, not hidden.

## Score names on the page

The data, `config/rules.md`, the judge and the eval use one triple everywhere: `impact`, `fit`, `likelihood`. The renderer shows them under tab-specific names that describe the evidence each tab actually uses, without promising more than the rubric knows:

| Tab | impact | fit | likelihood |
|---|---|---|---|
| Labels | Impact | Sound fit | Demo odds |
| Distributors | Value | Needs match | Ease |
| Collabs | Reach | Sound fit | Reply odds |
| Open Stages | Slot value | Fit (sound + rig) | Odds this month |
| Festivals | Career impact | Sound fit | Odds this year |
| Showcases | Career impact | Relevance | Odds this year |
| Bookers / Promoters | Impact | Lane fit | Booking odds |
| Agents | Impact | Lane fit | Signing odds |

That is the `SCORE_NAMES` map at the top of the script in `atlas/template.html` — change wording there, never in the schema.
