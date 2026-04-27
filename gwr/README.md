# Gap Winner Rule

This subtree is the forward home for the `Gap Winner Rule` (`GWR`).

`GWR` is the preferred name going forward for the rule previously recorded in
this repo as the `Lexicographic Winner-Take-All Peak Rule`. The legacy name is
retained in older artifacts so existing reports, figures, scripts, and links do
not have to be rewritten.

## Core Statement

Inside a prime gap $(p, q)$ with at least one composite interior, define the
raw-$Z$ score of an interior integer $n$ by

$$
Z(n) = \left(1 - \frac{d(n)}{2}\right)\ln(n).
$$

The `Gap Winner Rule` says the raw-$Z$ maximizer is exactly the lexicographic
selected integer:

1. minimize the interior divisor count $d(n)$,
2. among ties, choose the leftmost interior integer.

Any gap where the raw-$Z$ argmax differs from that selected integer is a counterexample.

## Current Headline Status

`GWR` is proved and closed on the repository's current proof surface.

The public proof-facing summary is:

- [../GWR_PROOF.md](../GWR_PROOF.md)
- [../docs/current_headline_results.md](../docs/current_headline_results.md)

The live earlier-side route is the local admissibility program plus residual
class closure and exact no-early-spoiler audit.

Bridge-era BHP/Robin notes and certificate scripts are retained under
[`experiments/proof/`](./experiments/proof/README.md) as historical comparison
material. They are not the current proof-critical path for the theorem status
presented in the repo headline files.

## Subtree Layout

- [`findings/`](./findings/README.md): Statements of the rule and synthesized
  findings.
- [`experiments/`](./experiments/README.md): Validation entry points, outputs,
  and experiment registry.
- [`literature/`](./literature/README.md): Novelty search notes and external
  positioning.

## Current Source Of Truth

The historical executable validation path remains in the existing gap-ridge
code:

- [`benchmarks/python/gap_ridge/lexicographic_rule_revalidation.py`](../benchmarks/python/gap_ridge/lexicographic_rule_revalidation.py)
- [`benchmarks/python/gap_ridge/lexicographic_peak_validation.py`](../benchmarks/python/gap_ridge/lexicographic_peak_validation.py)
- [`src/python/z_band_prime_gap_ridge/runs.py`](../src/python/z_band_prime_gap_ridge/runs.py)

The current validated summaries and reports are:

- [`output/lexicographic_rule_revalidation_report.md`](../output/lexicographic_rule_revalidation_report.md)
- [`output/lexicographic_rule_revalidation_summary.json`](../output/lexicographic_rule_revalidation_summary.json)
- [`docs/findings/lexicographic_winner_take_all_peak_rule.md`](../docs/findings/lexicographic_winner_take_all_peak_rule.md)

## Naming Convention

Use this form on first mention in new artifacts:

`Gap Winner Rule (GWR; legacy: Lexicographic Winner-Take-All Peak Rule)`

After first mention, use `GWR`.
