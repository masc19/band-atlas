"""Render scored records into a single-file HTML atlas.

No external assets: the page works offline and can be emailed or dropped behind
a password gate. The design is deliberately neutral; theme it for your brand.
"""
from __future__ import annotations

import html
import json
from datetime import date
from pathlib import Path

from . import CATEGORIES

ROOT = Path(__file__).resolve().parent.parent
TEMPLATE = Path(__file__).resolve().parent / "template.html"

LABELS = {
    "labels": "Labels", "distributors": "Distributors", "collabs": "Collabs", "open_stages": "Open Stages",
    "festivals": "Festivals", "showcases": "Showcases", "bookers": "Bookers", "promoters": "Promoters", "agents": "Agents",
}
GROUPS = {
    "now": "Approach now", "reach": "Reach — 12–24 months", "attend": "Attend / network, don't apply",
    "above": "Above current level", "avoid": "Avoid", "dead": "Folded, dormant or unverified",
}
SUBS = {
    "labels": "Labels in the lane, grouped by how open the door is for this act right now: demo route, roster trace, who runs it.",
    "distributors": "Distributors compared for this act's needs — dance-store delivery, splits, year-one cost — and what the catches are.",
    "collabs": "Collaboration and support-slot targets one to three tiers up, scored for reach, fit and the odds of a reply.",
    "open_stages": "Places within the travel radius where a short set can be had through sign-up, application or a light pitch, tagged for rig, sound and genre.",
    "festivals": "Fan-facing festivals that program the lane, grouped by what the act can actually do about them this year.",
    "showcases": "Conferences, showcase festivals and application series where industry is in the room; grouped by strategy.",
    "bookers": "Named buyers and curators who book beyond a single room, with the level they book at and the published route in.",
    "promoters": "Event brands and collectives that book this sound, with whether they give early slots to locals.",
    "agents": "The booking-agency map for the lane: who develops emerging acts, and the majors as the long-game context.",
}
STAGE_GROUPS = {"now": "P1 · Act this month", "reach": "P2 · Next 1–3 months", "attend": "P3 · Rehearsal / networking", "avoid": "Avoid", "dead": "Closed", "above": "Above level"}


def render(records: list[dict], profile: dict, out: Path, title: str | None = None) -> Path:
    scored = [r for r in records if "judgment" in r]
    cats = [c for c in CATEGORIES if any(r["category"] == c for r in scored)]
    payload = {
        "title": title or f"{profile['artist']} — Atlas",
        "artist": profile["artist"],
        "lane": profile["lane"],
        "home": f"{profile['home']['city']} · {profile['home']['travel_radius_minutes']} min radius",
        "built": date.today().isoformat(),
        "categories": [{"id": c, "label": LABELS.get(c, c), "sub": SUBS.get(c, "")} for c in cats],
        "groups": GROUPS, "stageGroups": STAGE_GROUPS,
        "records": [
            {
                "id": r["id"], "category": r["category"],
                "name": r["facts"]["name"], "city": r["facts"].get("city", ""), "country": r["facts"].get("country", ""),
                "summary": r["facts"].get("summary", ""), "apply": r["facts"].get("apply_how", ""),
                "contact": r["facts"].get("contact", ""), "url": r["facts"].get("url", ""),
                "when": r["facts"].get("when", ""), "cost": r["facts"].get("cost", ""),
                "verify": r["facts"].get("verify", ""), "sources": r["facts"].get("sources", []),
                "seen": r["facts"].get("seen_date", ""), "act": r["facts"].get("act_level", 0),
                "trace": r["facts"].get("roster_trace", []),
                "stage": r["facts"].get("stage", {}),
                "j": r["judgment"],
            } for r in scored
        ],
    }
    page = TEMPLATE.read_text(encoding="utf-8")
    page = page.replace("/*__DATA__*/{}", json.dumps(payload, ensure_ascii=False))
    page = page.replace("__TITLE__", html.escape(payload["title"]))
    out = Path(out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(page, encoding="utf-8")
    return out
