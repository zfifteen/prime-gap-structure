# Insight 001 Experiment Design: Modular Congestion Scaling

## Executive Summary

This experiment tests whether extreme prime-gap growth is preceded by a local
increase in modular congestion computed without using primality inside the
target interval.

The falsifiable claim is:

> A prime-gap record or champagne gap occurs within `1,000,000` integers of a
> coordinate where a local modular saturation ratio reaches a new running
> maximum.

The experiment can conclusively validate or falsify that finite claim on a
chosen domain `[X0, N]`. It does not prove a universal theorem. It answers the
direct operational question: does the proposed modular pressure field identify
the finite regions where the next record-scale gaps actually occur?

The strongest falsification is one counterexample:

> a record or champagne gap whose left endpoint is not within `1,000,000`
> integers of any new running maximum of the pressure field.

The strongest finite validation is:

1. every record or champagne gap in `[X0, N]` lies inside the predicted zones;
2. the predicted zones cover a minority of the searched domain;
3. the pressure field is computed only from modular residue constraints, not
   from prime-gap outcomes.

## Insight Under Test

The insight says that large prime gaps arise when modular constraints create
local saturation. In ordinary terms, many small-prime residue classes exclude
candidate integers in the same local region. If the surviving coprime slots
become scarce enough, the system enters a locked state and a record-scale gap
can appear.

The proposed measurable object is a ratio:

$$\text{pressure} = \frac{\text{active modular constraints}}{\text{local coprime density}}.$$

High pressure means many active modular exclusions divided by few locally open
slots.

## Operational Definitions

### Domain

Use a deterministic finite domain:

$$[X_0, N].$$

Recommended first domain:

$$X_0 = 10^6,\quad N = 10^9.$$

This is large enough to contain many prime-gap records beyond small-number
noise while remaining practical for exact segmented generation.

### Prime-Gap Record

For consecutive primes `(p, q)`, define the gap:

$$g = q - p.$$

The gap is a record if:

$$g > \max\{q' - p' : q' < p\}.$$

Only records with `p >= X0` and `q <= N` are tested.

### Champagne Gap

A champagne gap is a record gap whose normalized excess improves the previous
record-normalized excess by at least `15%`.

For each record gap at left endpoint `p`, compute:

$$E(p, g) = \frac{g}{\log(p)^2}.$$

The record is champagne if:

$$E(p, g) > 1.15 \cdot \max E(p', g')$$

over earlier record gaps in the run.

This definition avoids fitting a trend line after observing the data. The trend
normalizer is fixed before the experiment.

### Active Constraint Scale

For each coordinate `x`, define the local gap-scale window:

$$H(x) = \lceil \log(x)^2 \rceil.$$

Use all prime constraints up to that local window length:

$$Y(x) = H(x).$$

Let:

$$W(x) = \prod_{\ell \leq Y(x),\ \ell\ \text{prime}} \ell.$$

The active constraint count is:

$$k(x) = \pi(Y(x)).$$

This uses the primes that can impose residue exclusions at the expected
record-gap scale. It is deterministic and independent of whether numbers in
`[x, x + H(x)]` are prime.

### Local Coprime Density

Count the locally open slots:

$$A(x) = \#\{m : x < m \leq x + H(x),\ \gcd(m, W(x)) = 1\}.$$

The local coprime density is:

$$D(x) = \frac{A(x)}{H(x)}.$$

### Modular Congestion Scaling Pressure

Define:

$$MCS(x) = \frac{k(x)}{D(x)} = \frac{k(x)H(x)}{A(x)}.$$

If `A(x) = 0`, set `MCS(x) = infinity` and mark the coordinate as a complete
small-prime modular lock.

## Prediction Rule

Walk coordinates `x` from `X0` to `N` in increasing order.

A modular interference zone center is any coordinate where:

$$MCS(x) > \max_{X_0 \leq t < x} MCS(t).$$

For each center `c`, define the predicted zone:

$$[c - 1{,}000{,}000,\ c + 1{,}000{,}000].$$

Merge overlapping predicted zones before measuring coverage.

## Primary Pass/Fail Criteria

### Falsification

The insight fails on `[X0, N]` if any prime-gap record or champagne gap with
left endpoint `p` satisfies:

$$p \notin \bigcup \text{predicted zones}.$$

This directly tests the insight's stated prediction that major new gaps occur
within `10^6` units of a coordinate where local modular saturation reaches a
new local maximum.

### Finite Validation

The insight passes the finite experiment if all conditions hold:

1. every tested record gap lies inside the predicted zones;
2. every tested champagne gap lies inside the predicted zones;
3. merged predicted-zone coverage is less than `25%` of `[X0, N]`;
4. median `MCS(p)` for record gaps is above the `90th` percentile of `MCS(x)`
   over all tested coordinates.

The coverage condition prevents a vacuous pass where the predicted zones cover
almost everything.

## Secondary Tests

### Low-Pressure Counterexample Test

For each tested record or champagne gap, compute the percentile rank of
`MCS(p)` among all coordinates in `[X0, N]`.

The structural disconfirmation condition is:

$$\text{percentile}(MCS(p)) < 50.$$

One record or champagne gap below the median pressure field is evidence that a
new extreme gap occurred in a high-coprime-density region, contradicting the
stated disconfirmation criterion.

### Lead-Time Test

For each record or champagne gap at `p`, find the nearest earlier modular
interference zone center `c <= p`.

Record:

$$\Delta = p - c.$$

The useful-prediction version of the insight requires:

$$0 \leq \Delta \leq 1{,}000{,}000.$$

If most successful hits use centers after the gap, the metric is explanatory
but not predictive.

### Phase-Blind Control

Compute a phase-blind pressure:

$$MCS_0(x) = k(x)\frac{W(x)}{\phi(W(x))}.$$

This removes local residue alignment and keeps only the average density of
coprime slots. In implementation, compute `W(x) / phi(W(x))` as
`product(ell / (ell - 1))` over active primes; do not materialize the
primorial. If `MCS_0` performs as well as `MCS`, the local collision claim has
not added predictive information beyond ordinary small-prime density.

## Required Artifacts

The implementation should emit three LF-delimited artifacts:

1. `pressure_zones.csv`
   - `center`
   - `mcs`
   - `h`
   - `constraint_count`
   - `open_slots`
   - `running_rank`

2. `gap_events.csv`
   - `p`
   - `q`
   - `gap`
   - `is_record`
   - `is_champagne`
   - `mcs_at_p`
   - `mcs_percentile`
   - `nearest_prior_zone_center`
   - `distance_to_prior_zone`
   - `inside_predicted_zone`

3. `summary.json`
   - `x0`
   - `n`
   - `record_count`
   - `champagne_count`
   - `missed_record_count`
   - `missed_champagne_count`
   - `predicted_zone_coverage_fraction`
   - `record_median_mcs_percentile`
   - `champagne_median_mcs_percentile`
   - `phase_blind_control_hit_rate`
   - `verdict`

If Python's `csv` module is used, set `lineterminator="\n"` explicitly.

## Minimal Implementation Path

1. Generate primes up to `N` with a deterministic segmented Sieve of
   Eratosthenes in the experiment script only.
2. Extract consecutive prime gaps and running records.
3. For each segment and each distinct active scale `H`, build a deterministic
   open-slot bitset where an offset is open exactly when it is coprime to every
   active prime `ell <= H`.
4. Compute `A(x)` with a sliding window sum over that bitset. This is the same
   quantity as the gcd definition above, but it avoids materializing the
   primorial and avoids one gcd per candidate slot.
5. Mark running maxima of `MCS(x)` as modular interference zone centers.
6. Merge `1,000,000`-radius zones.
7. Join gap events to the merged zone set.
8. Emit the three artifacts.
9. Print the verdict from the primary pass/fail criteria.

The experiment script must not call the Minimal PGS Generator or modify
generator behavior. This is an external falsification probe.

## Expected Outcomes And Interpretation

### Outcome A: Clean Finite Validation

All records and champagne gaps are inside predicted zones, zone coverage is
below `25%`, and record endpoints have high pressure percentiles.

Interpretation:

The modular congestion field carries finite predictive signal on `[X0, N]`.
The next experiment should raise `N` and reduce the zone radius until the first
miss or the practical selectivity limit is found.

### Outcome B: Direct Falsification

At least one record or champagne gap lies outside all predicted zones.

Interpretation:

The stated `10^6` proximity prediction is false on `[X0, N]`. The insight can
only survive if the pressure definition, active constraint scale, or champagne
definition is changed and then tested as a new claim.

### Outcome C: Vague Success

All records are inside predicted zones, but merged coverage is at least `25%`.

Interpretation:

The pressure field did not provide a useful search contraction. It may still
describe modular structure, but it does not validate the claimed search
strategy.

### Outcome D: Phase-Blind Equivalence

The phase-blind control performs as well as the local `MCS` metric.

Interpretation:

The experiment does not support the collision-and-locking part of the insight.
The signal is explainable by ordinary average coprime density.

## Obstruction Cases

The design attacks these failure modes directly:

1. **Monotone pressure artifact.** Running maxima alone may occur near the far
   right edge because `log(x)` grows. The phase-blind control detects this.
2. **Vacuous coverage.** A `10^6` radius around too many centers may cover most
   of the domain. The `25%` coverage cap prevents that from counting as a pass.
3. **Post-hoc trend fitting.** Champagne status uses a fixed $\log(p)^2$
   normalizer and running prior excess, not a fitted curve learned from the
   same events.
4. **Prime leakage.** `MCS(x)` uses only small-prime modular constraints and
   gcd against the active primorial. Prime outcomes are used only for the
   downstream gap-event audit.

## Decision Table

| Condition | Verdict |
|---|---|
| Any record miss | `falsified_record_miss` |
| Any champagne miss | `falsified_champagne_miss` |
| Coverage >= `25%` | `not_predictive_coverage_too_large` |
| Record median pressure percentile < `90` | `not_predictive_pressure_rank_low` |
| Phase-blind control matches local MCS | `not_distinguished_from_average_density` |
| All primary criteria pass | `finite_validated` |

## Exact Claim Boundary

A `finite_validated` result supports this bounded statement:

> On `[X0, N]`, record-scale prime gaps occurred inside low-coprime-density
> modular interference zones computed from small-prime residue constraints, and
> those zones reduced the search domain to less than `25%` of the interval.

It does not by itself establish that all future record gaps must behave this
way. A single miss in a larger deterministic run is sufficient to falsify the
stronger universal version.
