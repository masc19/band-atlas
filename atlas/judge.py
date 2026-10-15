"""Judgment pass: score cached fact records for one artist profile.

Two scorers share one interface:

* ``MockScorer`` — a deterministic implementation of the rubrics in
  ``config/rules.md``. It exists so the whole pipeline runs with no API key, so
  tests are reproducible, and so prompt changes can be compared against a
  fixed baseline. It is deliberately simple; it is not the product.
* ``ModelScorer`` — sends ``config/rules.md`` as the system prompt and
  ``prompts/judge.md`` as the user turn to Claude, one category at a time, and
  parses the JSON array it returns.
"""
from __future__ import annotations

import json
import os
from dataclasses import dataclass
from datetime import date, datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

RIG_NEEDED = {
    "dj": 1, "laptop_live": 2, "laptop_vocal": 3, "laptop_vocal_instrument": 3,
    "full_band": 3, "acoustic": 2,
}
CATALOGUE_RANK = {"none": 0, "singles": 1, "ep": 2, "album": 3}
FORMAT_LABEL = {"dj": "DJ", "laptop_live": "laptop live", "laptop_vocal": "laptop + vocal", "laptop_vocal_instrument": "laptop + vocal + instrument", "full_band": "full band", "acoustic": "acoustic"}


def _clamp(x: float, lo: int = 0, hi: int = 10) -> int:
    return int(max(lo, min(hi, round(x))))


def _lane_fit(facts: dict, profile: dict) -> int:
    """0–10 from lane tags and roster overlap with reference artists."""
    tags = set(facts.get("lane_tags", []))
    score = 2
    if profile["lane"] in tags:
        score = 8
    elif tags:
        score = 5
    refs = {r.lower() for r in profile.get("reference_artists", [])}
    trace = {t.lower() for t in facts.get("roster_trace", [])}
    overlap = len(refs & trace)
    score += min(2, overlap)
    return _clamp(score)


def _named_in(name: str, names: list[str]) -> bool:
    """Case-insensitive substring match so 'Harbor Collective' matches 'Harbor Collective early slots'."""
    n = name.lower()
    return any(x.lower() in n or n in x.lower() for x in names if x)


def _group_from(likelihood: int, impact: int, act_level: int, warm: bool) -> str:
    if (likelihood >= 6 and act_level >= 2) or (likelihood >= 7 and warm):
        return "now"
    if 3 <= likelihood <= 5:
        return "reach"
    if likelihood <= 2 and impact >= 7:
        return "above"
    return "reach" if likelihood >= 3 else "above"


@dataclass
class Judgment:
    impact: int
    fit: int
    likelihood: int
    group: str
    why: str
    route: str
    flags: list[str]


class MockScorer:
    name = "mock"

    def __init__(self, today: date | None = None):
        self.today = today or date.today()

    # --- hard filters -----------------------------------------------------
    def _hard_filter(self, rec: dict, profile: dict) -> Judgment | None:
        f = rec["facts"]
        name = f["name"]
        if f["status"] != "active":
            return Judgment(0, 0, 0, "dead", f"{name} is {f['status']} per {f['sources'][0]}.", "Do not pitch.", [])
        if _named_in(name, profile.get("existing", {}).get("do_not_contact", [])):
            return Judgment(0, 0, 0, "avoid", "On your do-not-contact list.", "Skipped at your request.", ["do-not-contact"])
        p2p = f.get("pay_to_play", "unknown")
        tol = profile["red_lines"]["pay_to_play"]
        if (p2p == "quota" and tol != "quotas_ok") or (p2p == "fee" and tol == "none"):
            return Judgment(0, 0, 0, "avoid", f"Pay-to-play ({p2p}) conflicts with your red line ({tol}).", "Skip.", [])
        min_age = f.get("min_age")
        max_ok = profile["red_lines"].get("min_age_ok")
        if min_age and max_ok and min_age > max_ok:
            return Judgment(0, 0, 0, "avoid", f"{min_age}+ room; you said {max_ok}+ is the most you can play.", "Skip.", [])
        avoid_scenes = {a.lower().replace(" ", "-") for a in profile["red_lines"].get("avoid_scenes", [])}
        hit = avoid_scenes & {t.lower() for t in f.get("lane_tags", [])}
        if hit:
            return Judgment(0, 0, 0, "avoid", f"Scene you said you won't play: {', '.join(sorted(hit))}.", "Skip.", [])
        dist = f.get("distance_minutes")
        radius = profile["home"]["travel_radius_minutes"]
        if dist is not None and rec["category"] in ("open_stages", "promoters", "bookers") and dist > radius:
            return Judgment(0, 0, 0, "avoid", f"{dist} min away; your radius is {radius} min.", "Revisit if you extend your radius.", [])
        return None

    # --- category rubrics -------------------------------------------------
    def _score(self, rec: dict, profile: dict) -> Judgment:
        f = rec["facts"]
        cat = rec["category"]
        st = profile["standing"]
        perf = profile["performance"]
        act = f["act_level"]
        draw = st["draw_band"]
        gap = max(0, f.get("min_draw_band", 0) - draw)
        same_city = f.get("city", "").lower() == profile["home"]["city"].lower()
        warm = _named_in(f["name"], profile.get("existing", {}).get("in_conversation_with", []))
        flags: list[str] = []
        if warm:
            flags.append("in-conversation")
        if act <= 2 and not f.get("contact"):
            flags.append("contact-unpublished")
        seen = f.get("seen_date")
        if seen and (self.today - date.fromisoformat(seen)).days > 180:
            flags.append("re-verify")
        fit = _lane_fit(f, profile)
        reasons: list[str] = []

        if cat == "open_stages":
            s = f.get("stage", {})
            need = RIG_NEEDED[perf["format"]]
            rig = s.get("rig_support", 0)
            if rig == 1 and not perf["also_djs"]:
                return Judgment(2, 1, 1, "avoid", "DJ-only night and you don't DJ.", "Skip.", flags)
            if rig < need and not (rig == 1 and perf["also_djs"]):
                fit = min(fit, 4)
                reasons.append(f"rig support {rig} is below what your {FORMAT_LABEL[perf['format']]} set needs")
            fit = _clamp(fit + s.get("genre_focus", 0) + s.get("sound", 0) - 1)
            setm = s.get("set_minutes", 0)
            if setm and not any(l <= setm for l in perf["set_lengths"]):
                reasons.append(f"{setm}-minute slot is shorter than your shortest set")
            impact = _clamp(3 + s.get("sound", 0) * 2 + s.get("genre_focus", 0) + (1 if (f.get("capacity") or 0) >= 150 else 0))
            lik = _clamp(7 - gap * 2 + (1 if act == 3 else 0) - (1 if (s.get("format") == "showcase_apply" and not perf["has_live_video"]) else 0))
            if s.get("format") == "showcase_apply" and not perf["has_live_video"]:
                reasons.append("application-based and you have no live video yet")
            group = {"now": "now", "reach": "reach", "above": "attend"}[_group_from(lik, impact, act, warm)]
            if s.get("format") in ("scene_networking",) or fit <= 3:
                group = "attend"
            route = f.get("apply_how") or "Turn up and ask."
        elif cat == "labels":
            if st["team"].get("label"):
                return Judgment(0, fit, 0, "attend", "You already have a label.", "Category skipped.", flags)
            sign_stage = f.get("summary", "").lower()
            cat_rank = CATALOGUE_RANK[st["catalogue"]]
            need_rank = 3 if "touring" in sign_stage else (2 if "ep" in sign_stage else 1)
            lik = _clamp(6 + (act - 2) * 2 - max(0, need_rank - cat_rank) * 2 + (2 if warm else 0))
            impact = _clamp(5 + (2 if "mid" in sign_stage else 0) + (3 if "major" in sign_stage else 0))
            if need_rank > cat_rank:
                reasons.append(f"they sign at {['demo','singles','EP','touring'][need_rank]} stage; you're at {st['catalogue']}")
            group = _group_from(lik, impact, act, warm)
            if fit < 6 and group == "now":
                group = "reach"
                reasons.append("lane fit is only partial")
            route = f.get("apply_how") or ("Management only — no open door." if act <= 1 else "Use the published demo route.")
        elif cat == "distributors":
            d = f.get("distribution", {})
            fit = 5
            if st.get("needs_dance_store_delivery"):
                fit += 3 if d.get("dance_store_delivery") else -3
                reasons.append("you need Beatport/Traxsource delivery" + ("" if d.get("dance_store_delivery") else " and this one doesn't deliver there"))
            if st.get("has_split_collaborators"):
                fit += 2 if d.get("splits_tooling") else -1
            budget = profile.get("capacity", {}).get("budget_per_month", 0) * 12
            cost = f.get("cost_amount")
            over_budget = cost is not None and budget and cost > budget
            if over_budget:
                fit -= 3
                reasons.append(f"year-one cost ${cost:.0f} exceeds your ${budget:.0f} annual budget")
            fit = _clamp(fit)
            impact, lik = 5, _clamp(8 if act == 3 else 4)
            group = "now" if fit >= 6 and act == 3 and not over_budget else ("reach" if fit >= 4 else "avoid")
            route = f.get("apply_how") or f.get("url", "")
        elif cat == "collabs":
            ab = f.get("audience_band", 2)
            lik = _clamp(6 - max(0, ab - st.get("listeners_band", 0) - 1) * 2 + (2 if same_city else 0) + (1 if act == 3 else 0) + (2 if warm else 0))
            impact = _clamp(3 + ab * 1.5)
            if same_city:
                reasons.append("same city")
            group = _group_from(lik, impact, act, warm)
            route = f.get("apply_how") or ("Published management contact." if act == 3 else "Meet them at a show first.")
        elif cat in ("festivals", "showcases"):
            if cat == "showcases" and not f.get("lane_tags"):
                fit = 5  # industry-wide events are lane-neutral
            budget = profile.get("capacity", {}).get("showcase_budget_per_year", 0)
            cost = f.get("cost_amount") or 0
            lik = _clamp(6 - gap * 2 - (2 if not perf["has_live_video"] else 0) - (1 if CATALOGUE_RANK[st["catalogue"]] < 1 else 0) + (1 if act == 3 else 0))
            if not perf["has_live_video"]:
                reasons.append("no live video")
            if gap:
                reasons.append(f"wants draw band {f.get('min_draw_band')}; you're at {draw}")
            impact = _clamp(5 + (2 if (f.get("capacity") or 0) >= 2000 else 0) + (2 if cat == "showcases" else 0))
            if cost > budget:
                reasons.append(f"costs ${cost:.0f} against a ${budget:.0f} showcase budget")
                lik = _clamp(lik - 2)
            far = f.get("country") != profile["home"]["country"] and not profile["home"]["will_fly_for_showcase"]
            group = _group_from(lik, impact, act, warm)
            if act <= 1 and cat == "showcases":
                group = "attend"
            if far:
                group = "above"
                reasons.append("outside your travel radius and you won't fly")
            route = f.get("apply_how") or "Attend as a delegate with meetings booked, or skip."
        elif cat in ("bookers", "promoters"):
            lik = _clamp(6 - gap * 2 + (2 if same_city else 0) + (1 if act == 3 else -1 if act <= 1 else 0) + (2 if warm else 0))
            impact = _clamp(4 + f.get("min_draw_band", 0) * 1.5)
            if gap:
                reasons.append(f"books acts at draw band {f.get('min_draw_band')}; you're at {draw}")
            if act <= 1:
                reasons.append("no open door")
            group = _group_from(lik, impact, act, warm)
            route = f.get("apply_how") or ("Be visible on the bills that feed their undercards." if act <= 1 else "Use the published route.")
        elif cat == "agents":
            if st["team"].get("agent"):
                return Judgment(0, fit, 0, "attend", "You already have an agent.", "Category skipped.", flags)
            ready = perf["has_live_video"] and CATALOGUE_RANK[st["catalogue"]] >= 1 and draw >= 2
            lik = _clamp((5 if ready else 2) + (1 if act == 3 else 0) - gap)
            impact = _clamp(6 + f.get("min_draw_band", 0))
            if not ready:
                reasons.append("agents want a release, a live video and a draw band ≥ 2")
            group = _group_from(lik, impact, act, warm)
            route = f.get("apply_how") or "No open door — build receipts first."
        else:
            impact, lik, group, route = 5, 5, "reach", ""

        if same_city and cat in ("open_stages", "promoters", "bookers", "collabs") and "same city" not in reasons:
            reasons.append("same city")
        why = ("; ".join(reasons) if reasons else "meets the rubric with no blocking gap")
        why = why[0].upper() + why[1:] + "."
        return Judgment(impact, fit, lik, group, why, route, flags)

    def score(self, records: list[dict], profile: dict) -> list[dict]:
        out = []
        for rec in records:
            if rec["category"] not in profile["categories"]:
                continue
            j = self._hard_filter(rec, profile) or self._score(rec, profile)
            r = dict(rec)
            r["judgment"] = {
                "profile_id": profile.get("profile_id", profile["artist"]),
                "impact": j.impact, "fit": j.fit, "likelihood": j.likelihood,
                "group": j.group, "why": j.why, "route": j.route, "flags": j.flags,
                "scored_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
                "scorer": self.name,
            }
            out.append(r)
        return out


class ModelScorer:
    """Scores with Claude. Requires ANTHROPIC_API_KEY and the `anthropic` package."""

    def __init__(self, model: str | None = None, batch_size: int = 25):
        import anthropic  # imported lazily so the mock path has no dependency

        self.client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
        self.model = model or os.environ.get("ATLAS_MODEL", "claude-sonnet-5-5")
        self.batch_size = batch_size
        self.name = model
        self.system = (ROOT / "config" / "rules.md").read_text(encoding="utf-8")
        self.template = (ROOT / "prompts" / "judge.md").read_text(encoding="utf-8").split("---", 1)[1]

    def _call(self, category: str, batch: list[dict], profile: dict) -> dict[str, dict]:
        facts_only = [{"id": r["id"], "category": r["category"], "facts": r["facts"]} for r in batch]
        user = self.template.format(
            today=date.today().isoformat(), category=category,
            profile_json=json.dumps(profile, ensure_ascii=False, indent=1),
            records_json=json.dumps(facts_only, ensure_ascii=False, indent=1),
        )
        msg = self.client.messages.create(
            model=self.model, max_tokens=8000, temperature=0,
            system=[{"type": "text", "text": self.system, "cache_control": {"type": "ephemeral"}}],
            messages=[{"role": "user", "content": user}],
        )
        text = "".join(b.text for b in msg.content if getattr(b, "type", "") == "text")
        start, end = text.find("["), text.rfind("]")
        arr = json.loads(text[start:end + 1])
        return {o["id"]: o for o in arr}

    def score(self, records: list[dict], profile: dict) -> list[dict]:
        out = []
        by_cat: dict[str, list[dict]] = {}
        for r in records:
            if r["category"] in profile["categories"]:
                by_cat.setdefault(r["category"], []).append(r)
        for cat, recs in by_cat.items():
            for i in range(0, len(recs), self.batch_size):
                batch = recs[i:i + self.batch_size]
                got = self._call(cat, batch, profile)
                for r in batch:
                    j = got.get(r["id"])
                    if not j:
                        continue
                    rr = dict(r)
                    rr["judgment"] = {
                        "profile_id": profile.get("profile_id", profile["artist"]),
                        "impact": int(j["impact"]), "fit": int(j["fit"]), "likelihood": int(j["likelihood"]),
                        "group": j["group"], "why": j["why"], "route": j.get("route", ""),
                        "flags": j.get("flags", []),
                        "scored_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
                        "scorer": self.name,
                    }
                    out.append(rr)
        return out


def get_scorer(mode: str, model: str | None = None):
    if mode == "mock":
        return MockScorer()
    if mode == "model":
        return ModelScorer(model=model)
    raise ValueError(f"unknown scorer mode: {mode}")
