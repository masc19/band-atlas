"""Golden-set comparison.

A golden set is a scored record file that a human has reviewed and trusts for
one profile. `compare` measures how closely a candidate run matches it:

* group agreement — share of records placed in the same group
* adjacent agreement — share within one step on the now/reach/attend/above ladder
* mean absolute error per score (impact, fit, likelihood)
* Spearman rank correlation of likelihood within each category
* confusion matrix of groups

No external dependencies.
"""
from __future__ import annotations

from collections import defaultdict

LADDER = {"now": 0, "reach": 1, "attend": 2, "above": 3}


def _rank(xs: list[float]) -> list[float]:
    order = sorted(range(len(xs)), key=lambda i: xs[i])
    ranks = [0.0] * len(xs)
    i = 0
    while i < len(order):
        j = i
        while j + 1 < len(order) and xs[order[j + 1]] == xs[order[i]]:
            j += 1
        r = (i + j) / 2 + 1
        for k in range(i, j + 1):
            ranks[order[k]] = r
        i = j + 1
    return ranks


def spearman(a: list[float], b: list[float]) -> float | None:
    n = len(a)
    if n < 3:
        return None
    ra, rb = _rank(a), _rank(b)
    ma, mb = sum(ra) / n, sum(rb) / n
    num = sum((x - ma) * (y - mb) for x, y in zip(ra, rb))
    den = (sum((x - ma) ** 2 for x in ra) * sum((y - mb) ** 2 for y in rb)) ** 0.5
    return None if den == 0 else num / den


def compare(golden: list[dict], candidate: list[dict]) -> dict:
    g = {r["id"]: r for r in golden if "judgment" in r}
    c = {r["id"]: r for r in candidate if "judgment" in r}
    ids = sorted(set(g) & set(c))
    if not ids:
        raise ValueError("no overlapping record ids between golden and candidate")
    same = adj = 0
    abs_err = {"impact": 0.0, "fit": 0.0, "likelihood": 0.0}
    conf: dict[str, dict[str, int]] = defaultdict(lambda: defaultdict(int))
    per_cat: dict[str, tuple[list[float], list[float]]] = defaultdict(lambda: ([], []))
    for i in ids:
        gj, cj = g[i]["judgment"], c[i]["judgment"]
        conf[gj["group"]][cj["group"]] += 1
        if gj["group"] == cj["group"]:
            same += 1
        if gj["group"] in LADDER and cj["group"] in LADDER and abs(LADDER[gj["group"]] - LADDER[cj["group"]]) <= 1:
            adj += 1
        elif gj["group"] == cj["group"]:
            adj += 1
        for k in abs_err:
            abs_err[k] += abs(gj[k] - cj[k])
        a, b = per_cat[g[i]["category"]]
        a.append(gj["likelihood"])
        b.append(cj["likelihood"])
    n = len(ids)
    return {
        "n": n,
        "missing_in_candidate": sorted(set(g) - set(c)),
        "extra_in_candidate": sorted(set(c) - set(g)),
        "group_agreement": same / n,
        "adjacent_agreement": adj / n,
        "mae": {k: v / n for k, v in abs_err.items()},
        "spearman_likelihood": {cat: spearman(a, b) for cat, (a, b) in per_cat.items()},
        "confusion": {k: dict(v) for k, v in conf.items()},
    }


def report(res: dict) -> str:
    lines = [
        f"records compared: {res['n']}  (missing in candidate: {len(res['missing_in_candidate'])}, extra: {len(res['extra_in_candidate'])})",
        f"group agreement: {res['group_agreement']:.0%}   adjacent: {res['adjacent_agreement']:.0%}",
        "MAE  " + "  ".join(f"{k} {v:.2f}" for k, v in res["mae"].items()),
        "Spearman(likelihood) " + "  ".join(f"{k} {('n/a' if v is None else f'{v:.2f}')}" for k, v in res["spearman_likelihood"].items()),
        "confusion (golden → candidate):",
    ]
    for gk, row in res["confusion"].items():
        lines.append(f"  {gk:7s} → " + ", ".join(f"{ck} {n}" for ck, n in sorted(row.items())))
    return "\n".join(lines)
