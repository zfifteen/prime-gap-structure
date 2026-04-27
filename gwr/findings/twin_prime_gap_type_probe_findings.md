# Twin Prime Outer Gap-Type Probe

This note records one narrow test of a specific hypothesis:

Do twin primes sit inside distinctive outer `GWR`/`DNI` gap-type patterns?

The strongest supported finding is:

On the exact `10^6` surface, twin primes do show repeated outer-gap types, but
that repetition does **not** collapse to a narrow twin-specific family law.
Once the comparison is conditioned on the residue classes forced by twin-prime
admissibility, most family-level differences become small.

So the current probe supports a weaker reading:

- twin primes live in a constrained structural corridor,
- but the corridor appears to be driven mostly by the admissible residue
  classes and the forced middle gap width `2`,
- not by one sharp twin-specific outer gap type on both sides.

## Why The Probe Uses Outer Gaps

For a twin pair `(p, p + 2)`, the middle gap has width `2`, so it has no
interior composite and therefore no `GWR` winner type.

The meaningful typed object is therefore the **outer pair**:

- the preceding nontrivial gap ending at `p`,
- the forced width-`2` middle gap,
- the following nontrivial gap starting at `p + 2`.

This probe measures the two outer typed gaps directly.

## Artifacts

- runner:
  [`../../benchmarks/python/predictor/gwr_dni_twin_prime_gap_type_probe.py`](../../benchmarks/python/predictor/gwr_dni_twin_prime_gap_type_probe.py)
- tests:
  [`../../tests/python/predictor/test_gwr_dni_twin_prime_gap_type_probe.py`](../../tests/python/predictor/test_gwr_dni_twin_prime_gap_type_probe.py)
- JSON summary:
  [`../../output/gwr_dni_twin_prime_gap_type_probe_summary.json`](../../output/gwr_dni_twin_prime_gap_type_probe_summary.json)
- detail CSV:
  [`../../output/gwr_dni_twin_prime_gap_type_probe_details.csv`](../../output/gwr_dni_twin_prime_gap_type_probe_details.csv)

## Exact Surface

The current run uses the exact type surface through
`current_right_prime <= 10^6`.

That surface contains:

- `78,497` typed prime-start rows,
- `8,169` twin-prime pairs,
- `8,168` defined preceding outer gaps
  (the pair `(3, 5)` has no preceding nontrivial gap).

For twin primes greater than `3`, the admissible residue classes are forced:

- left twin residues: `11, 17, 29 (mod 30)`,
- right twin residues: `1, 13, 19 (mod 30)`.

The probe therefore compares twin-pair outer gaps against **residue-conditioned
baselines** rather than against all primes indiscriminately.

## Main Counts

On the twin-pair surface:

- distinct preceding exact types: `117`
- distinct following exact types: `88`
- distinct outer-pair signatures: `1,312`

So the twin surface is structured, but it is not narrow.

The top preceding exact type is:

- `o2_d4_a2_odd_semiprime` with share `18.51%`

The top following exact type is:

- `o4_d4_a4_odd_semiprime` with share `21.59%`

The most common full outer signature is:

- `o2_d4_a2_odd_semiprime -> o4_d4_a4_odd_semiprime`
  with share `3.86%`

That is the largest repeated signature, but it is still far from a dominant
collapse law.

## Family-Level Comparison Against Residue-Conditioned Baselines

### Preceding Side

Twin-pair preceding outer families versus the residue-conditioned baseline
over primes with residues `11, 17, 29 (mod 30)`:

| Family | Twin share | Baseline share | Delta | Lift |
|---|---:|---:|---:|---:|
| prime square | `0.220%` | `0.194%` | `+0.027%` | `1.138x` |
| even semiprime | `18.266%` | `18.706%` | `-0.439%` | `0.977x` |
| odd semiprime | `60.553%` | `60.104%` | `+0.449%` | `1.007x` |
| higher-divisor even | `12.255%` | `12.524%` | `-0.269%` | `0.979x` |
| higher-divisor odd | `8.705%` | `8.466%` | `+0.239%` | `1.028x` |

These deviations are small.

### Following Side

Twin-pair following outer families versus the residue-conditioned baseline
over primes with residues `1, 13, 19 (mod 30)`:

| Family | Twin share | Baseline share | Delta | Lift |
|---|---:|---:|---:|---:|
| prime square | `0.220%` | `0.207%` | `+0.013%` | `1.063x` |
| even semiprime | `23.540%` | `24.790%` | `-1.250%` | `0.950x` |
| odd semiprime | `55.062%` | `54.138%` | `+0.923%` | `1.017x` |
| higher-divisor even | `13.111%` | `13.155%` | `-0.044%` | `0.997x` |
| higher-divisor odd | `8.055%` | `7.699%` | `+0.356%` | `1.046x` |

Again, the deviations are modest.

The largest family-level shift on the following side is the even-semiprime
share drop of about `1.25` percentage points. That is real, but it is still
small relative to the full mass of the conditioned baseline.

## Interpretation

Attached to the tested scope, the current evidence says:

1. Twin primes do not sit in arbitrary outer gap structure.
2. But the visible family-level structure around twin primes is already mostly
   explained by the narrow residue corridor required for twin-prime
   admissibility.
3. The twin condition does not force one sharp outer gap family on the left,
   one sharp outer gap family on the right, or one narrow two-sided signature.

One additional summary statistic makes that clear:

- the two outer gaps share the same coarse family in only `38.28%` of defined
  twin pairs.

So the outer pair is structured, but not rigid in the sense of a near-unique
typed shell.

## Reading The Prime-Type Hypothesis Carefully

On your actual claim, this does make sense as a hypothesis.

The exact `GWR`/`DNI` program already shows that prime location is tightly tied
to local gap structure. It is therefore reasonable to ask whether special prime
subfamilies inherit a correspondingly special local type environment.

What this twin-prime probe adds is a endpoint on that idea:

- **supported:** twin primes live in a typed outer-gap corridor;
- **not supported here:** a narrow twin-specific outer-type collapse;
- **best current reading:** the residue-admissibility corridor seems to do most
  of the forcing, with only modest extra deformation at the family level.

## Conclusion

The exact `10^6` twin-prime probe does not show a strong unique outer gap-type
law around twin primes.

It does show something weaker and still useful:

twin primes sit inside a constrained outer-gap corridor, but most of that
constraint appears to be inherited from the residue classes and the forced
middle gap width `2`, not from a sharply distinctive twin-only outer type.
