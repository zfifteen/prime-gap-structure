# PGS `127`-Bit Official Gate Breakthrough

## Result

The semiprime branch now has one committed full-stage recovery result that was
not present in the repository before:

- the official centered `PGS` audit on the full committed `127`-bit
  `12`-case surface passes at rung `2`
- routed-window recall is `1.0` at top `1` and `1.0` at top `4`
- exact recovery recall is `0.75`
- the archived exact `127`-bit case is recovered on the official path

The measured summary is
[../../../output/semiprime_branch/pgs_127_official_audit_summary.json](../../../output/semiprime_branch/pgs_127_official_audit_summary.json),
and the per-case rows are
[../../../output/semiprime_branch/pgs_127_official_audit_rows.jsonl](../../../output/semiprime_branch/pgs_127_official_audit_rows.jsonl).

## What The Official Audit Is

The official `127`-bit audit is the family-conditioned, centered `PGS` route
implemented in
[../../../benchmarks/python/predictor/pgs_geofac_scaleup.py](../../../benchmarks/python/predictor/pgs_geofac_scaleup.py).

It uses one narrow deterministic path:

- the committed `127`-bit corpus has `12` known-factor semiprimes
- the cases are split into `4` `balanced`, `4` `moderate_unbalanced`, and `4`
  `archived_shape`
- each rung emits one fixed centered four-window lattice around the family
  center
- local exact recovery uses the repo `PGS` seed contract
  `gwr_predict(seed, d=None)` on deterministic center-out composite seeds
- the first passing rung wins

The official audit helper is `run_127_official_audit(0)`.

## First Passing Rung

Rung `1` does not pass the stage. It reaches:

- `0.6666666666666666` exact recovery recall
- `1.0` top-4 routed-window recall
- archived exact case not recovered

Rung `2` is the first passing rung. It reaches:

- `0.75` exact recovery recall
- `1.0` top-1 routed-window recall
- `1.0` top-4 routed-window recall
- archived exact case recovered
- `384` total local prime tests
- `182` total router probes

That is the committed gate result for this stage.

## What Changed

This result comes from making the `127`-bit scale-up path fully `PGS`-driven.

- `tau` was removed from the active `127` harness
- the `127` corpus was rebuilt into coherent `balanced`,
  `moderate_unbalanced`, and `archived_shape` families
- routing was narrowed to one centered four-window family-conditioned lattice
- official exact recovery was reduced to final-window `PGS` seed recovery,
  rather than mixed midpoint heuristics or broad history-window unions

The focused regression surface is
[../../../tests/python/predictor/test_pgs_geofac_scaleup.py](../../../tests/python/predictor/test_pgs_geofac_scaleup.py).

## What This Means

The branch now has one full audited `127`-bit recovery result built from local
prime-gap `PGS` structure rather than from the archived geofac search path.

That is the current breakthrough:

- one deterministic `PGS` route clears the full committed `127`-bit gate
- the archived exact case is recovered on that same official path
- the stage closes at rung `2`, not only on an isolated sentinel case

## Endpoint

This result is a `127`-bit known-factor audit result.

It is not yet:

- a blind factorization claim
- a generic all-regime semiprime recovery theorem
- an RSA `4096` break

The next scaling question is whether the same narrow `PGS` path can carry exact
recovery beyond `127` bits and then continue collapsing routed windows at the
higher committed stages.
