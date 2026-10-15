"""Research pass: build the shared fact layer for one category, lane and place.

Calls Claude with the hosted web-search tool, using the category prompt in
``prompts/research/`` prefixed by ``_common.md``. Writes a JSON array of fact
records to the cache directory, validated against ``schema/record.schema.json``.
Invalid records are written to a ``.rejected.json`` sibling instead of being
silently dropped.

This module is intentionally thin. The quality of the fact layer comes from the
prompts and from running three narrower sweeps rather than one broad one
(see ``docs/running.md``). It needs ``ANTHROPIC_API_KEY``; nothing else in the
package does.
"""
from __future__ import annotations

import json
import os
from datetime import date
from pathlib import Path

from . import CATEGORIES
from .schema import ValidationError, validate_record

ROOT = Path(__file__).resolve().parent.parent
PROMPTS = ROOT / "prompts" / "research"
DEFAULT_MODEL = os.environ.get("ATLAS_MODEL", "claude-sonnet-5-5")


def load_lane(lane_id: str) -> dict:
    """Minimal lane loader: reads the YAML block for `lane_id` from config/lanes.md.

    Lanes are kept in Markdown so the file reads as a document; this parser only
    handles the flat key: value and list forms used there.
    """
    text = (ROOT / "config" / "lanes.md").read_text(encoding="utf-8")
    blocks = text.split("```yaml")
    for b in blocks[1:]:
        body = b.split("```", 1)[0]
        lane: dict = {}
        key = None
        for line in body.splitlines():
            if not line.strip():
                continue
            if line.startswith("  - ") and key:
                lane.setdefault(key, []).append(line[4:].strip())
            elif ":" in line and not line.startswith(" "):
                key, _, val = line.partition(":")
                key = key.strip()
                val = val.strip()
                if val.startswith("[") and val.endswith("]"):
                    lane[key] = [v.strip().strip('"') for v in val[1:-1].split(",") if v.strip()]
                elif val in ("", ">"):
                    lane[key] = [] if val == "" else ""
                else:
                    lane[key] = val.strip('"')
            elif key and isinstance(lane.get(key), str):
                lane[key] = (lane[key] + " " + line.strip()).strip()
        if lane.get("id") == lane_id:
            return lane
    raise KeyError(f"lane not found in config/lanes.md: {lane_id}")


def build_prompt(category: str, lane: dict, geo_scope: str, city: str, target_count: int) -> str:
    common = (PROMPTS / "_common.md").read_text(encoding="utf-8").split("---", 1)[1]
    specific = (PROMPTS / f"{category}.md").read_text(encoding="utf-8")
    fill = {
        "lane_label": lane.get("label", lane["id"]),
        "reference_artists": ", ".join(lane.get("reference_artists", [])),
        "search_terms": ", ".join(lane.get("search_terms", [])),
        "geo_scope": geo_scope, "city": city or geo_scope,
        "today": date.today().isoformat(), "target_count": target_count,
    }
    return (common + "\n\n" + specific).format(**fill)


def run(category: str, lane_id: str, geo_scope: str, out_dir: Path, city: str = "",
        target_count: int = 40, model: str = DEFAULT_MODEL, max_searches: int = 60) -> Path:
    if category not in CATEGORIES:
        raise ValueError(f"category must be one of {CATEGORIES}")
    import anthropic

    client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
    lane = load_lane(lane_id)
    prompt = build_prompt(category, lane, geo_scope, city, target_count)
    msg = client.messages.create(
        model=model,
        max_tokens=16000,
        temperature=0,
        tools=[{"type": "web_search_20250305", "name": "web_search", "max_uses": max_searches}],
        messages=[{"role": "user", "content": prompt}],
    )
    text = "".join(b.text for b in msg.content if getattr(b, "type", "") == "text")
    start, end = text.find("["), text.rfind("]")
    if start < 0 or end < 0:
        raise RuntimeError("model returned no JSON array; raw text saved to " + str(out_dir / f"{category}.raw.txt"))
    arr = json.loads(text[start:end + 1])

    good, bad = [], []
    for item in arr:
        rec = {"id": item.get("id", ""), "category": category, "facts": item.get("facts", item)}
        rec["facts"].setdefault("seen_date", date.today().isoformat())
        try:
            validate_record(rec)
            good.append(rec)
        except ValidationError as e:
            bad.append({"error": str(e), "item": item})

    out_dir.mkdir(parents=True, exist_ok=True)
    slug = f"{category}.{lane_id}.{(city or geo_scope).lower().replace(' ', '-')}"
    out = out_dir / f"{slug}.json"
    out.write_text(json.dumps(good, ensure_ascii=False, indent=1), encoding="utf-8")
    if bad:
        (out_dir / f"{slug}.rejected.json").write_text(json.dumps(bad, ensure_ascii=False, indent=1), encoding="utf-8")
    usage = getattr(msg, "usage", None)
    print(f"{category}: {len(good)} records, {len(bad)} rejected → {out}" + (f" · tokens in/out {usage.input_tokens}/{usage.output_tokens}" if usage else ""))
    return out
