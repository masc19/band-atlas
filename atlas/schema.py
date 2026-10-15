"""Load and validate profiles and records against the JSON Schemas in schema/."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

try:  # jsonschema >= 4.18
    from jsonschema import Draft202012Validator as _Validator
except ImportError:  # older system jsonschema (e.g. macOS / Debian python3-jsonschema)
    from jsonschema import Draft7Validator as _Validator  # the schemas only use draft-7-compatible keywords

ROOT = Path(__file__).resolve().parent.parent
SCHEMA_DIR = ROOT / "schema"


def _validator(name: str) -> _Validator:
    schema = json.loads((SCHEMA_DIR / name).read_text(encoding="utf-8"))
    return _Validator(schema)


PROFILE = _validator("profile.schema.json")
RECORD = _validator("record.schema.json")


class ValidationError(ValueError):
    pass


def _check(validator: _Validator, obj: Any, label: str) -> None:
    errors = sorted(validator.iter_errors(obj), key=lambda e: list(e.path))
    if errors:
        msgs = [f"{label}: {'/'.join(str(p) for p in e.path) or '<root>'}: {e.message}" for e in errors[:10]]
        raise ValidationError("\n".join(msgs))


def load_profile(path: Path) -> dict:
    obj = json.loads(Path(path).read_text(encoding="utf-8"))
    _check(PROFILE, obj, f"profile {path}")
    return obj


def load_records(path: Path) -> list[dict]:
    obj = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(obj, list):
        raise ValidationError(f"{path}: expected a JSON array of records")
    for i, rec in enumerate(obj):
        _check(RECORD, rec, f"{path}[{i}]")
    return obj


def validate_record(rec: dict) -> None:
    _check(RECORD, rec, rec.get("id", "<record>"))


def load_facts_dir(directory: Path) -> dict[str, list[dict]]:
    """Return {category: [records]} from every *.json in a facts directory."""
    out: dict[str, list[dict]] = {}
    for p in sorted(Path(directory).glob("*.json")):
        for rec in load_records(p):
            out.setdefault(rec["category"], []).append(rec)
    return out
