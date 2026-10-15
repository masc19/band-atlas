"""Command-line entry point.

    band-atlas research --category labels --lane live-electronic-downtempo --geo "Germany" --out data/cache
    band-atlas judge    --facts data/demo/facts --profile intake/example-profile.json --scorer mock --out build/scored.json
    band-atlas render   --scored build/scored.json --profile intake/example-profile.json --out build/atlas.html
    band-atlas build    --facts data/demo/facts --profile intake/example-profile.json --out build/   (judge + render)
    band-atlas eval     --golden eval/demo/golden.json --candidate build/scored.json
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from . import CATEGORIES, __version__
from .schema import load_facts_dir, load_profile, load_records


def _judge(args) -> list[dict]:
    from .judge import get_scorer

    profile = load_profile(Path(args.profile))
    facts = load_facts_dir(Path(args.facts))
    records = [r for recs in facts.values() for r in recs]
    scorer = get_scorer(args.scorer, getattr(args, "model", None))
    scored = scorer.score(records, profile)
    print(f"scored {len(scored)} of {len(records)} records with {scorer.name}", file=sys.stderr)
    return scored


def cmd_research(args):
    from .research import run

    cats = CATEGORIES if args.category == "all" else [args.category]
    presets = {"quick": (15, 25), "standard": (40, 60), "deep": (60, 120)}
    if args.depth:
        args.target, args.max_searches = presets[args.depth]
        if args.depth == "quick" and args.category == "all":
            cats = ["open_stages", "promoters", "labels", "collabs"]
    for c in cats:
        run(c, args.lane, args.geo, Path(args.out), city=args.city, target_count=args.target, model=args.model, max_searches=args.max_searches)


def cmd_judge(args):
    scored = _judge(args)
    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    Path(args.out).write_text(json.dumps(scored, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"wrote {args.out}")


def cmd_render(args):
    from .render import render

    profile = load_profile(Path(args.profile))
    scored = load_records(Path(args.scored))
    out = render(scored, profile, Path(args.out))
    print(f"wrote {out}")


def cmd_build(args):
    from .render import render

    scored = _judge(args)
    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "scored.json").write_text(json.dumps(scored, ensure_ascii=False, indent=1), encoding="utf-8")
    profile = load_profile(Path(args.profile))
    page = render(scored, profile, out_dir / "atlas.html")
    groups: dict[str, int] = {}
    for r in scored:
        groups[r["judgment"]["group"]] = groups.get(r["judgment"]["group"], 0) + 1
    print(f"wrote {page} · groups: {groups}")


def cmd_eval(args):
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
    from eval.compare import compare, report

    golden = load_records(Path(args.golden))
    cand = load_records(Path(args.candidate))
    res = compare(golden, cand)
    print(report(res))
    if args.min_group_agreement is not None and res["group_agreement"] < args.min_group_agreement:
        sys.exit(1)


def main(argv=None):
    ap = argparse.ArgumentParser(prog="band-atlas", description=f"band-atlas {__version__}")
    sub = ap.add_subparsers(dest="cmd", required=True)

    r = sub.add_parser("research", help="build the shared fact layer for a category (needs ANTHROPIC_API_KEY)")
    r.add_argument("--category", default="all", choices=CATEGORIES + ["all"])
    r.add_argument("--lane", required=True)
    r.add_argument("--geo", required=True, help='geographic scope, e.g. "Germany" or "Lisbon + 2h"')
    r.add_argument("--city", default="", help="anchor city for open stages / promoters")
    r.add_argument("--out", default="data/cache")
    r.add_argument("--target", type=int, default=40)
    r.add_argument("--model", default=None)
    r.add_argument("--max-searches", type=int, default=60)
    r.add_argument("--depth", default=None, choices=["quick", "standard", "deep"], help="preset for --target/--max-searches (quick 15/25, standard 40/60, deep 60/120 per sweep)")
    r.set_defaults(func=cmd_research)

    for name, fn in (("judge", cmd_judge), ("build", cmd_build)):
        j = sub.add_parser(name, help="score facts for a profile" + (" and render" if name == "build" else ""))
        j.add_argument("--facts", required=True, help="directory of fact JSON files")
        j.add_argument("--profile", required=True)
        j.add_argument("--scorer", default="mock", choices=["mock", "model"])
        j.add_argument("--model", default=None)
        j.add_argument("--out", required=True)
        j.set_defaults(func=fn)

    v = sub.add_parser("render", help="render a scored JSON file to HTML")
    v.add_argument("--scored", required=True)
    v.add_argument("--profile", required=True)
    v.add_argument("--out", required=True)
    v.set_defaults(func=cmd_render)

    e = sub.add_parser("eval", help="compare a candidate judgment file against a golden set")
    e.add_argument("--golden", required=True)
    e.add_argument("--candidate", required=True)
    e.add_argument("--min-group-agreement", type=float, default=None)
    e.set_defaults(func=cmd_eval)

    args = ap.parse_args(argv)
    args.func(args)


if __name__ == "__main__":
    main()
