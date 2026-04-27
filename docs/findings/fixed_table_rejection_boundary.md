# Fixed-Table Rejection Is a Number-Theory Endpoint

This note records the finding that the current `~91%` prefilter rejection rate
is not primarily an engineering plateau. It is the measured small-factor layer
available to the current fixed odd-prime table depth.

## Finding

The strongest supported claim is:

the current fixed-table prefilter is already sitting near the finite-regime
endpoint set by the density of odd integers carrying at least one covered small
odd-prime factor.

On the current deterministic table-depth surface, deeper tables do increase
the structural rejection ceiling, but only by small fractions of a percentage
point at the repo's existing depths:

| Covered odd-prime limit | Structural rejection ceiling | Structural survivor share | Gain from previous row |
|---:|---:|---:|---:|
| `300,007` | `91.096550%` | `8.903450%` | |
| `600,014` | `91.560859%` | `8.439141%` | `+0.464309 pp` |
| `1,000,003` | `91.872366%` | `8.127634%` | `+0.311507 pp` |
| `2,000,006` | `92.260741%` | `7.739259%` | `+0.388375 pp` |
| `3,000,000` | `92.471037%` | `7.528963%` | `+0.210296 pp` |
| `10,000,000` | `93.033245%` | `6.966755%` | `+0.562208 pp` |

The direct doubling probe is the cleanest falsifiable statement:

- from `1,000,003` to `2,000,006`, the structural ceiling rises by only
  `0.388375` percentage points;
- a measured gain of `2` or more percentage points from merely doubling the
  covered table depth would invalidate this framing.

## Observable Mechanism

The production prefilter rejects an odd candidate only when it finds a concrete
factor in the gated odd-prime tables. For an arbitrary odd candidate stream, the
survivor share after screening all odd primes up to a finite limit $L$ is

$$S(L)=\prod_{3 \le p \le L}(1 - 1/p).$$

The corresponding structural rejection ceiling is

$$R(L)=1-S(L).$$

That product is the invariant endpoint for this mechanism at one fixed table
depth. Implementation quality can change the time required to evaluate the
table. It cannot make the same table reject candidates that have no covered
small odd-prime factor.

The product does not converge to a positive survivor floor as $L$ tends to
infinity. Formally, $S(L)$ keeps drifting downward and $R(L)$ tends toward
`100%`. The operational endpoint here is finite-regime, not infinite-regime:
near the repo's current table depths, the remaining numerator has already
shrunk enough that ordinary table widening is not a route to a new rejection
regime.

## Relation to Current Benchmarks

The current validated benchmark surface reports about `91%` candidate rejection
before Miller-Rabin and end-to-end deterministic RSA speedups of `2.09x` at
`2048` bits and `2.82x` at `4096` bits. See
[prefilter benchmarks](../prefilter/benchmarks.md).

The table-depth structural sweep already measures the same endpoint:

- covered odd primes through `300,007`: theory `91.096550%`;
- covered odd primes through `1,000,003`: theory `91.872366%`;
- covered odd primes through `3,000,000`: theory `92.471037%`.

The sweep report and plot are:

- [TABLE_DEPTH_SWEEP_REPORT.md](../../benchmarks/output/python/prefilter/table_depth_sweep/TABLE_DEPTH_SWEEP_REPORT.md)
- [table_depth_collapse.svg](../../benchmarks/output/python/prefilter/table_depth_sweep/table_depth_collapse.svg)

The end-to-end `8192`-bit RSA table-depth sweep shows the same practical
pressure: `1,000,003` was the fastest measured cell even though `3,000,000` had
a higher structural rejection ceiling. At that scale, the extra rejection exists
but is too small to dominate the added proxy work on the measured Python path.
See
[RSA_TABLE_DEPTH_SWEEP_REPORT.md](../../benchmarks/output/python/prefilter/rsa_table_depth_sweep/RSA_TABLE_DEPTH_SWEEP_REPORT.md).

## Architectural Consequence

The current table is not merely a tunable engineering knob. It has already
consumed most of the small-factor density layer available at this depth.

That changes the next design question. To push rejection materially above the
current `~91%` to `~92%` finite-table regime, the mechanism must change.
Wider tables, faster lookups, and deeper sieves are refinements inside the same
endpoint.

A different mechanism would change the candidate stream before the fixed table
runs. In this repository's vocabulary, the live candidate is a deterministic
`GWR`-informed generator that produces candidates already biased toward the
prime fixed-point band, rather than generating arbitrary odd candidates and
then consuming the small-factor layer with a table.

The fixed-table path remains valuable. It rejects composites only on concrete
factor discovery and preserves the public deterministic contract. The finding
is narrower: table depth is not the frontier for a new rejection regime.

## Falsifier

This framing makes a concrete prediction:

- doubling the covered odd-prime table depth from the current deep-table regime
  should produce less than `1` percentage point of additional rejection;
- a reproducible gain of `2` or more percentage points from table doubling
  alone would falsify the finite-regime endpoint reading;
- a gain of `2` or more percentage points at fixed table depth would point to a
  mechanism shift in candidate generation, not to ordinary table deepening.

So the practical test is not whether a deeper table can reject more. It can.
The practical test is whether its marginal numerator is large enough to change
the architecture. At the current depth, the measured and computed answer is no.
