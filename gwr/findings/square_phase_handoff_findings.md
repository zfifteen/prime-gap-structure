# Square-Phase Underuse Predicts Next-Triad Return

This note records a new one-step handoff finding for the `d = 4` winner
surface.

The strongest supported result is:

current `d = 4` square-phase utilization is not only a endpoint observable of
the current gap. It is also a next-gap handoff variable.

When current `d = 4` gaps are matched by the same local winner geometry, the
lower-utilization half returns the next gap to the odd-semiprime triad more
often than the higher-utilization half does.

Here square-phase utilization means

$$U_{\square}(w, q) = \frac{q - w}{S_{+}(w) - w},$$

where:

- $w$ is the current `d = 4` winner,
- $q$ is the right endpoint prime of that same gap,
- and $S_{+}(w)$ is the next prime square after $w$.

This ratio was introduced earlier as a endpoint-placement coordinate. The new
result is that it also carries one-step transition information.

## Probe Surface

Artifacts:

- runner:
  [`../../benchmarks/python/predictor/gwr_square_phase_handoff_probe.py`](../../benchmarks/python/predictor/gwr_square_phase_handoff_probe.py)
- tests:
  [`../../tests/python/predictor/test_gwr_square_phase_handoff_probe.py`](../../tests/python/predictor/test_gwr_square_phase_handoff_probe.py)
- summary JSON:
  [`../../output/gwr_square_phase_handoff_summary.json`](../../output/gwr_square_phase_handoff_summary.json)
- stratum CSV:
  [`../../output/gwr_square_phase_handoff_strata.csv`](../../output/gwr_square_phase_handoff_strata.csv)

The current executed surface uses the already-committed gap-type catalog detail
CSV and extracts only transitions whose current gap has `d = 4` winner:

- exact baseline through `current_right_prime <= 10^6`,
- pooled sampled decade windows from `10^12` through `10^18`.

## Main Controlled Readout

The primary matched comparison keeps current carrier family, current winner
offset, and current first-open offset fixed, then compares the lower-
utilization half of each stratum against the higher-utilization half of the
same stratum.

### All Current `d = 4` Winners

| Surface | Matched half-pairs | Low-utilization next-triad share | High-utilization next-triad share | Lift |
|---|---:|---:|---:|---:|
| exact `<=10^6` | `29,119` | `0.5876` | `0.5673` | `+0.0203` |
| pooled windows `10^12..10^18` | `652` | `0.6994` | `0.6595` | `+0.0399` |

So after matching on the same current local geometry, the lower-utilization
half still feeds the next gap back into the odd-semiprime triad more often.

### Width-Added Confirmatory Split

Adding current gap width to the same stratum key leaves the sign unchanged:

| Surface | Matched half-pairs | Low-utilization next-triad share | High-utilization next-triad share | Lift |
|---|---:|---:|---:|---:|
| exact `<=10^6` | `28,617` | `0.5866` | `0.5692` | `+0.0174` |
| pooled windows `10^12..10^18` | `134` | `0.7164` | `0.6567` | `+0.0597` |

So the effect is not removed by conditioning on width in addition to family,
winner offset, and first-open offset.

## Odd-Semiprime-Only Check

The dominant family shows the same sign after removing the family mixture
entirely.

Match only on current winner offset and current first-open offset inside the
odd-semiprime `d = 4` population:

| Surface | Matched half-pairs | Low-utilization next-triad share | High-utilization next-triad share | Lift |
|---|---:|---:|---:|---:|
| exact `<=10^6` | `22,617` | `0.5823` | `0.5638` | `+0.0184` |
| pooled windows `10^12..10^18` | `572` | `0.6976` | `0.6521` | `+0.0455` |

So the handoff effect is not only an even-versus-odd family mix story.

## Tail Readout

The low-versus-high utilization tails show the same direction without matching.

On the odd-semiprime current population:

- exact `<=10^6`:
  low tail next-triad share `0.5919`,
  high tail next-triad share `0.5454`;
- pooled windows `10^12..10^18`:
  low tail next-triad share `0.7149`,
  high tail next-triad share `0.6529`.

The high-utilization odd-semiprime tail also leaks more often into non-triad
families. On the exact surface, the next-family share of `higher_divisor_even`
rises from `0.1661` on the low-utilization tail to `0.2026` on the
high-utilization tail, and prime-square re-entry appears only on the
high-utilization tail at about `1.05%`.

## Reading

This changes the most natural one-step scheduler story.

The earlier parity note and reset probes showed that a current discrete label
can carry one-step memory. This new probe says the current gap also carries a
continuous local budget variable.

Low utilization means the current gap closed while using only a small fraction
of the available square-threat budget before the next prime square could enter.
That leaves the right endpoint in a lower-pressure local regime, and the next
gap more often returns to the dominant odd-semiprime triad.

High utilization means the current gap spent more of that same local square
budget before closing. The next gap then starts closer to the same square
threat horizon and leaks more often into non-triad or higher-divisor states.

So the next-gap handoff is not only a finite-state memory problem. It also
depends on how much of the current square phase was actually consumed before
closure.

## Decision Rule

For current `d = 4` gaps, if two rows share the same current carrier family,
current winner offset, and current first-open offset, predict the row with
smaller `U_square(w, q)` to return the next gap to the odd-semiprime triad
more often than the row with larger `U_square(w, q)`.

On the current executed surface, that rule wins in the aggregate on both the
exact baseline and the pooled high-scale windows.

## Scope

This is a bounded transition claim on the current executed catalog surface. It
does not claim that square-phase utilization alone closes the full scheduler
problem, and it does not claim a universal theorem for all gap families.

What it does show is narrower and stronger:

pointwise square-phase utilization carries real one-step transition signal that
survives current local-geometry controls.
