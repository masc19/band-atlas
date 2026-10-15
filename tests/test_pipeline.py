import json
from datetime import date
from pathlib import Path

import pytest

from atlas.judge import MockScorer
from atlas.render import render
from atlas.schema import ValidationError, load_facts_dir, load_profile, load_records, validate_record

ROOT = Path(__file__).resolve().parent.parent
FACTS = ROOT / "data" / "demo" / "facts"
PROFILE = ROOT / "intake" / "example-profile.json"


@pytest.fixture
def profile():
    return load_profile(PROFILE)


@pytest.fixture
def records():
    return [r for recs in load_facts_dir(FACTS).values() for r in recs]


def test_demo_facts_validate(records):
    assert len(records) >= 40
    for r in records:
        assert r["facts"]["sources"], r["id"]
        assert "judgment" not in r


def test_invalid_record_rejected():
    with pytest.raises(ValidationError):
        validate_record({"id": "x", "category": "labels", "facts": {"name": "No sources"}})


def test_mock_scorer_covers_every_record(records, profile):
    scored = MockScorer(today=date(2026, 10, 14)).score(records, profile)
    assert len(scored) == len(records)
    for r in scored:
        validate_record(r)
        j = r["judgment"]
        assert j["group"] in {"now", "reach", "attend", "above", "avoid", "dead"}
        assert 0 <= j["likelihood"] <= 10


def test_hard_filters(records, profile):
    scored = {r["id"]: r["judgment"] for r in MockScorer(today=date(2026, 10, 14)).score(records, profile)}
    assert scored["emergenza"]["group"] == "avoid"                      # do-not-contact
    assert scored["colossus"]["group"] == "avoid"                       # application fee vs pay-to-play red line
    assert scored["stella"]["group"] == "avoid"                         # outside travel radius
    assert scored["signal"]["group"] == "avoid"                         # DJ-only night, band does not DJ
    assert scored["nachtdigital"]["group"] == "dead"                    # folded
    assert "in-conversation" in scored["deep-root-records-deep-root-tribe"]["flags"]
    stale = {r["id"]: r["judgment"] for r in MockScorer(today=date(2027, 4, 1)).score(records, profile)}
    assert "re-verify" in stale["beem"]["flags"]                        # facts older than 180 days


def test_likelihood_not_inflated_by_impact(records, profile):
    scored = {r["id"]: r["judgment"] for r in MockScorer().score(records, profile)}
    key = "wasserman-music-now-operating-as-the-team"
    assert scored[key]["impact"] >= 8
    assert scored[key]["likelihood"] <= 2
    assert scored[key]["group"] == "above"


def test_render_single_file(tmp_path, records, profile):
    scored = MockScorer().score(records, profile)
    out = render(scored, profile, tmp_path / "atlas.html")
    html = out.read_text(encoding="utf-8")
    assert "The Hollow Tide" in html and "/*__DATA__*/" not in html and "<script src" not in html


def test_eval_roundtrip(records, profile):
    import sys
    sys.path.insert(0, str(ROOT))
    from eval.compare import compare
    scored = MockScorer().score(records, profile)
    res = compare(scored, json.loads(json.dumps(scored)))
    assert res["group_agreement"] == 1.0 and res["mae"]["likelihood"] == 0.0
