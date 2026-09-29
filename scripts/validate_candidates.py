#!/usr/bin/env python3
"""Validate the local Track 3 candidate CSV contract using only the standard library."""

import argparse
import csv
import json
from pathlib import Path
import sys

SCHEMA_PATH = Path(__file__).resolve().parents[1] / "data/candidates.schema.json"


def validate_csv(path, *, allow_empty=False):
    """Return (rows, errors), preserving row order and never rewriting input."""
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    errors = []
    rows = []
    seen = {field: set() for field in schema["unique_fields"]}
    try:
        with Path(path).open(newline="", encoding="utf-8-sig") as handle:
            reader = csv.DictReader(handle, strict=True)
            header = reader.fieldnames
            if not header:
                return [], ["Missing CSV header."]
            if len(header) != len(set(header)) or any(not h.strip() for h in header):
                errors.append("Column names must be nonempty and unique.")
            missing = set(schema["required_columns"]) - set(header)
            if missing:
                return [], errors + [f"Missing required columns: {', '.join(sorted(missing))}."]
            for row in reader:
                rows.append(row)
                prefix = f"Line {reader.line_num}"
                if None in row or any(value is None for value in row.values()):
                    errors.append(f"{prefix}: field count does not match header.")
                    continue
                name, sequence, kind = (row[key] for key in schema["required_columns"])
                if not name or name != name.strip():
                    errors.append(f"{prefix}: name must be nonempty without surrounding whitespace.")
                for field in schema["unique_fields"]:
                    value = row[field]
                    if value in seen[field]:
                        errors.append(f"{prefix}: duplicate {field}.")
                    seen[field].add(value)
                if kind not in schema["molecule_classes"]:
                    errors.append(f"{prefix}: invalid molecule_class {kind!r}.")
                chains = sequence.split(":") if kind in schema["fab_classes"] else [sequence]
                if kind in schema["fab_classes"] and len(chains) != 2:
                    errors.append(f"{prefix}: Fab sequence must be VH:VL (exactly two chains).")
                if any(not chain for chain in chains):
                    errors.append(f"{prefix}: sequence/chains must not be empty.")
                invalid = set("".join(chains)) - set(schema["amino_acid_alphabet"])
                if invalid:
                    errors.append(f"{prefix}: invalid sequence characters {''.join(sorted(invalid))!r}; use uppercase canonical amino acids.")
                limits = schema["length_limits"].get(kind)
                if limits and not limits["min"] <= len(sequence) <= limits["max"]:
                    errors.append(f"{prefix}: {kind} length must be {limits['min']}–{limits['max']} residues; got {len(sequence)}.")
    except (OSError, UnicodeError, csv.Error) as exc:
        errors.append(f"Cannot read CSV: {exc}")
    if not rows and not allow_empty:
        errors.append("No candidates; use --allow-empty only for scaffold checks.")
    if len(rows) > schema["max_candidates"]:
        errors.append(f"Track 3 permits at most {schema['max_candidates']} candidates; got {len(rows)}.")
    return rows, errors


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("csv_path", type=Path)
    parser.add_argument("--allow-empty", action="store_true", help="Permit a header-only scaffold")
    args = parser.parse_args(argv)
    rows, errors = validate_csv(args.csv_path, allow_empty=args.allow_empty)
    if errors:
        for error in errors:
            print(error, file=sys.stderr)
        return 1
    print(f"CSV checks passed ({len(rows)} candidates). Biological eligibility is not assessed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
