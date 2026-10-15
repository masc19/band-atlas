# Judgment prompt — score cached facts for one artist

Used by `atlas/judge.py` (model mode). The system prompt is `config/rules.md` verbatim; this file is the user turn. The model receives the profile and a batch of fact records for one category and returns a judgment per record. It never sees other artists' judgments.

---

Today is {today}. Score the following **{category}** records for the artist profile below, applying the rubrics and groups in the rules exactly.

**Profile**

```json
{profile_json}
```

**Records** (facts only)

```json
{records_json}
```

**Instructions**

1. Apply hard filters first (age limits, pay-to-play red lines, travel radius, rig support, `do_not_contact`). A record that fails a hard filter goes to `avoid` (or `dead` if its status is not active) with a one-line `why`.
2. For the rest, give `impact`, `fit` and `likelihood` on 0–10 using the anchors. Likelihood is never raised because impact is high.
3. Assign `group` by the group rules.
4. Write `why` in one or two sentences that **name the profile fields and facts** behind the call (draw band, catalogue, live video, rig, distance, act level, roster trace). No adjectives without a fact behind them.
5. Write `route`: the concrete next action, in the imperative, or "No open door — build toward it via …".
6. Add `flags` for anything the artist should check before acting: `re-verify` for facts older than 180 days, `contact-unpublished`, `mirror-only`, `in-conversation` when the record matches `existing.in_conversation_with`.
7. Return a JSON array, one object per record, with `id` and the `judgment` fields (`impact`, `fit`, `likelihood`, `group`, `why`, `route`, `flags`). No prose outside the JSON.
