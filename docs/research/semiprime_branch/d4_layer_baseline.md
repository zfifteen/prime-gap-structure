# d=4 Layer Baseline

## Purpose

This note defines the first measured baseline for the semiprime branch.

The goal is to quantify how much of the repo's practical large-RSA early-rejection advantage can plausibly be connected to the dominant `d=4` layer, rather than to generic shallow-factor filtering alone.

This is a baseline note, not a victory note.

## Live Mathematical Context

The repo's live arithmetic identity is

```text
Z(n) = n^(1 - d(n)/2)
L(n) = (1 - d(n)/2) ln(n)
```

Under this identity:

- primes satisfy `d(n)=2` and sit at `Z=1`
- distinct semiprimes satisfy `d(n)=4` and sit at `Z=1/n`
- prime squares satisfy `d(n)=3` and sit at `Z=1/sqrt(n)`

So the `d=4` layer is the exact arithmetic shell occupied by distinct semiprimes, together with the thin prime-cube residue that also has `d(n)=4`.

## Why This Layer Matters

The repo's current dominant-case GWR result says:

- if the selected integer has `d(w)=4`, the tested surface shows no interior prime square
- under that square exclusion, the selected integer is exactly the first interior `d=4` integer

So the dominant GWR regime is already a `d=4` regime.

The semiprime-only slogan is false on the current documented surface because a thin prime-cube exception family survives inside the broader `d=4` class.

Therefore the right baseline is not:

```text
semiprimes only
```

It is:

```text
d=4 layer = distinct semiprimes + thin prime-cube residue
```

## Baseline Questions

### B1 — Selected integer composition

What share of tested GWR-selected integers are:

- distinct semiprimes
- prime cubes
- other `d=4` forms, if any
- non-`d=4` selected integers

### B2 — Arrival structure

For `d=4` selected integer gaps, measure:

- offset of first interior `d=4`
- selected-integer offset distribution
- whether first-`d=4` and selected-integer offset always coincide on the committed surfaces
- conditional counts under square exclusion

### B3 — Dominance by scale

Measure the share of `d=4` selected integers across:

- exact small surfaces already in the repo
- sampled larger surfaces already in the repo
- any new surfaces added for this branch

### B4 — Large-RSA relevance

Map the arithmetic baseline to the algorithmering baseline by asking:

- which candidate classes are currently rejected by the production front end
- how much of that rejection is plausibly correlated with shallow evidence of the `d=4` layer
- whether explicit `d=4`-aware modeling improves rejection at equal cost

## Minimal Metrics Table

Every baseline artifact should report at least these fields.

| field | meaning |
|---|---|
| `gap_count` | tested prime-gap count |
| `winner_d4_count` | number of gaps whose selected integer has `d=4` |
| `winner_d4_share` | `winner_d4_count / gap_count` |
| `winner_semiprime_count` | number of selected integers that are distinct semiprimes |
| `winner_prime_cube_count` | number of selected integers that are prime cubes |
| `winner_other_d4_count` | number of selected integers in `d=4` not covered above |
| `first_d4_match_count` | number of `d=4` selected integer gaps where first-`d=4` equals selected integer |
| `interior_square_violation_count` | gaps where a `d=4` selected integer occurs despite an interior prime square |
| `median_winner_offset` | median selected-integer offset from left prime |
| `median_first_d4_offset` | median first-`d=4` offset from left prime |

## Immediate Data Sources Already In Repo

The first baseline pass should use existing committed surfaces before adding anything new.

Primary sources:

- `gwr/findings/dominant_d4_arrival_reduction_findings.md`
- `output/gwr_d4_arrival_validation_summary.json`
- `output/gwr_d4_arrival_validation_exact.csv`
- `output/gwr_d4_arrival_validation_even_bands.csv`
- `docs/prefilter/benchmarks.md`

## Baseline Reading From Current Repo Surface

The current repo already supports these baseline facts:

- the exact `2 x 10^7` surface reports `959,730` `d=4` selected integer gaps out of `1,163,198`
- that share is about `0.8251`
- the exact `2 x 10^7` surface reports `15` prime-cube selected integers inside the `d=4` selected divisor-count class
- the current documented `d=4` selected integer surface reports `0` interior-square violations
- the current documented `d=4` selected integer surface reports exact first-`d=4` agreement on all tested surfaces

These are the branch's starting facts, not the finish line.

## What This Baseline Must Not Claim

This baseline does **not** by itself show:

- a new factoring algorithm
- a new exact semiprime certification method
- a classical-complexity improvement for factor recovery
- that current RSA prefilter gains are already proven to come from explicit semiprime-layer exploitation

It only establishes the arithmetic and empirical starting surface for that research question.

## Next Required Artifact

The next artifact after this note should be a reproducible measured table such as:

```text
output/semiprime_branch/d4_layer_baseline_summary.json
```

paired with:

```text
output/semiprime_branch/d4_layer_baseline_by_scale.csv
```

and a runner that builds them from existing repo surfaces before introducing any new front-end proxy.

## Success Condition For This Baseline Stage

This baseline stage is complete when the repo has one committed table that cleanly separates:

- distinct semiprime selected integers
- prime-cube residue
- non-`d=4` selected integers
- first-`d=4` arrival behavior by scale

That table should be enough to decide whether semiprime-layer-aware proxy work is justified as the next experiment.
