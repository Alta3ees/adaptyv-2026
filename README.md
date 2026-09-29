# Anthropic × Adaptyv 2026 — Track 3 / EGFR

First-step workspace for candidate bookkeeping and environment checks. Python 3.10+
and its standard library are sufficient. No model installation, weights, folding,
or design generation is included. `data/candidates.csv` intentionally has only a header.

## Official requirements

Read on **2026-09-29**: [Challenge 1 and FAQ](https://proteinbase.com/competitions/anthropic-adaptyv-2026/challenges/egfr)
and [competition / Track 3](https://proteinbase.com/competitions/anthropic-adaptyv-2026).
Recheck these live sources before submission.

- Target: human EGFR extracellular region, residues 25–645 (P00533-1);
  domain III is recommended, not mandatory.
- Objectives: human binding, mouse cross-reactivity, and human binding at pH 6.5
  with no detectable binding at pH 7.4. Ranking prioritizes pH selectivity,
  then cross-reactivity, then affinity.
- Track 3: at most 20 designs, ranked best first; testing is not guaranteed.
- Deadline: October 4, 2026, 23:59 AoE (UTC−12).
- Designs must be unique, de novo and zero-shot, not modifications of existing
  binders. Antibody frameworks are permitted; antibody annotation and novelty
  need separate review.

## Candidate CSV contract

The machine-readable local schema is [`data/candidates.schema.json`](data/candidates.schema.json).
It is a CSV contract, not JSON Schema or an organizer-provided file.

| Column | Contract |
| --- | --- |
| `name` | Nonempty, unique identifier |
| `sequence` | Uppercase canonical amino acids; Fabs use `VH:VL` |
| `molecule_class` | `protein`, `nanobody`, `scfv`, `fab_kappa`, `fab_lambda` |

Extra metadata columns are allowed; row order is preserved. Quote fields containing
commas or newlines using standard CSV quoting.

### Assumptions and limits

The page's summary gives 10–250 amino acids; FAQ 1 explicitly scopes that range
to single-chain proteins. This validator applies it to `protein` only. No numeric
antibody length limit is inferred; nanobody/scFv sequences and both Fab chains
must be nonempty. Confirm this interpretation with the organizers before submitting
antibody formats. A valid class label does not establish antibody identity (e.g.
ANARCI annotation); that review is outside this setup.

Local hygiene rules require the 20-letter alphabet `ACDEFGHIKLMNPQRSTVWY`, exact
case-sensitive unique names and sequences, and no surrounding name whitespace.
No sequence normalization is performed: lowercase, spaces, gaps, stop symbols,
ambiguous residues, and separators outside Fab notation fail. Duplicate sequences
are rejected across classes. These checks cannot establish novelty or detect
near-duplicates. Empty files fail; header-only files pass only with `--allow-empty`.

Passing validation establishes CSV hygiene only. Folding confidence or a folding
score does **not** prove binding, mouse cross-reactivity, or pH-selective binding.
Those properties require appropriate experimental measurements. This workspace
does not assess expression, affinity, novelty, eligibility, or submission readiness.

## Local commands

Run from the repository root:

```sh
python3 scripts/validate_candidates.py data/candidates.csv --allow-empty
# After adding actual reviewed candidates, require a nonempty CSV:
python3 scripts/validate_candidates.py data/candidates.csv
python3 -m unittest discover -s tests -v
```

Exit status is 0 for passing checks and 1 for invalid/unreadable CSV input.
Diagnostics identify the affected CSV line. No command submits data.

## Colab

Open [`notebooks/01_environment.ipynb`](notebooks/01_environment.ipynb) in Colab
(File → Upload notebook, or open it from your GitHub copy). Optionally select
Runtime → Change runtime type → GPU. Run cells in order. The first cell clones this repository into
`/content/adaptyv-2026` if absent and changes into it; an existing checkout is not
updated automatically. All future notebooks must start with this cell, as recorded
in [`AGENTS.md`](AGENTS.md). If repository files cannot be found, upload these
three repository files when prompted: `candidates.csv`, `candidates.schema.json`,
and `validate_candidates.py`. They remain in temporary runtime storage.

The notebook reports Python and NVIDIA GPU availability via `nvidia-smi`, reads
and validates the CSV, and previews rows. CPU-only execution is sufficient for
this step. Locally, skip the Colab bootstrap cell and open it in an existing Jupyter environment from the repository
root or `notebooks/`; files are found automatically. The initial empty scaffold
is explicitly permitted and reported. Set `ALLOW_EMPTY = False` once candidates
exist. No packages or models are installed by the notebook.
