# RSA Experiment Working Cells

This folder is organized by working cell. Do not recreate the old
`rsa/v2` monolith.

## Active Cells

- `live-solver/rsa-v2/`: current public RSA v2 resolver, resolver contracts,
  default live output, and downstream audit output.
- `live-solver/qu-certificate-to-factor-map/`: QU-only research packet
  (certificate-to-factor map). Not live inference. Not PROOF.md. Do not
  wire into the resolver.
- `data-ladder/rsa-v2/`: rung specs, fixture builders, generated rung
  provenance, public fixture rows, and physically separate audit fixtures.
- `transported-sidecars/rsa-v2/`: transported story law, d4 budget, d4 trace,
  exclusion debt, threat-tail, and width diagnostics.
- `certificate-mechanics/rsa-v2/`: commitment-story certificate projections and
  transported commitment ledger diagnostics.
- `grammar-evidence/rsa-v2/`: grammar expansion, compatibility catalogs,
  hidden-coordinate scans, inverse-word findings, and recursive grammar output.
- `modulus-recursive-catalogs/rsa-v2/`: modulus-gap catalogs, public RSA modulus
  notes, solved-challenge evidence, and exact catalog outputs.
- `frontier-holdouts/rsa-v2/`: normalized frontier and toy holdout closure
  probes.
- `order-entropy-sidecars/rsa-v2/`: Shor/order entropy comparison evidence.
- `proof-workbenches/rsa-v2/`: transported certificate and story-law proof
  obligation documents.
- `recursive-sidecars/rsa-v2/`: OECC recursive side-by-side runner and related
  scalability checklist.
- `reviews-automation/rsa-v2/`: automation notes and Grok session records.
- `invalidated-solvers/rsa-v2/`: falsified or non-live solver-shape artifacts.
- `archive/rsa-v2/`: scratch and tmp material only.

## Contract

Live inference starts in `live-solver/rsa-v2/` and reads public cases from
`data-ladder/rsa-v2/fixtures/ladder_cases.jsonl`. Audit reads physically
separate factors only downstream.

`resolved` means at least one factor was found by the public PGS inference
surface and then audited downstream. If the live PGS invariant does not expose
a factor, report unresolved.

Sidecars are evidence surfaces. They do not become resolver logic unless a
public PGS theorem promotes them.

Do not add compatibility wrappers, old-path shims, random construction,
classical inference gates, hidden factors, gcd selectors, divisibility checks,
product closure, or fallback branches.

## Reproduce Current Live Surface

Run from the repository root:

```bash
python3 research/06-cryptology-rsa/experiments/data-ladder/rsa-v2/build_ladder_fixtures.py
python3 research/06-cryptology-rsa/experiments/live-solver/rsa-v2/run_experiment.py
python3 research/06-cryptology-rsa/experiments/live-solver/rsa-v2/audit_experiment.py
python3 research/06-cryptology-rsa/experiments/transported-sidecars/rsa-v2/transported_story_law_probe.py --cases research/06-cryptology-rsa/experiments/data-ladder/rsa-v2/fixtures/ladder_cases.jsonl --measured-rows 256 --recursive-depth 4 --output-dir research/06-cryptology-rsa/experiments/transported-sidecars/rsa-v2/output/transported_story_law_current
python3 research/06-cryptology-rsa/experiments/transported-sidecars/rsa-v2/transported_d4_budget_probe.py --story-rows research/06-cryptology-rsa/experiments/transported-sidecars/rsa-v2/output/transported_story_law_current/story_law_rows.jsonl --recursive-rows research/06-cryptology-rsa/experiments/transported-sidecars/rsa-v2/output/transported_story_law_current/recursive_rows.jsonl --output-dir research/06-cryptology-rsa/experiments/transported-sidecars/rsa-v2/output/transported_d4_budget_current
python3 research/06-cryptology-rsa/experiments/transported-sidecars/rsa-v2/transported_d4_budget_trace.py --budget-rows research/06-cryptology-rsa/experiments/transported-sidecars/rsa-v2/output/transported_d4_budget_current/budget_rows.jsonl --recursive-budget-rows research/06-cryptology-rsa/experiments/transported-sidecars/rsa-v2/output/transported_d4_budget_current/recursive_budget_rows.jsonl --output-dir research/06-cryptology-rsa/experiments/transported-sidecars/rsa-v2/output/transported_d4_budget_trace_current
```
