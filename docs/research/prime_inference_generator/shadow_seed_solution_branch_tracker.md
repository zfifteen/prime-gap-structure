# Shadow Seed Recovery Solution Branch Tracker

This document tracks experimental branches created to evaluate proposed
replacements for `shadow_seed_trial_recovery_v1`.

The current generator state is honest:

- `pgs_chamber_closure_v2` is the current pure PGS selector.
- `shadow_seed_recovery` is operationally correct on the tested emitted
  high-scale samples, but it is not pure PGS because its terminal step uses
  exact divisor arithmetic.
- A proposed solution is promotable only if it raises pure PGS recovery on the
  high-scale shadow rows while keeping audit failures at zero.

The target surface for these branches is the current 388 high-scale
`shadow_seed_recovery` rows:

| Scale | Shadow rows |
|---|---:|
| $10^{12}$ | 102 |
| $10^{15}$ | 141 |
| $10^{18}$ | 145 |

Promotion requires:

- no generator contamination;
- no added fields in emitted records;
- no primality, factorization, `nextprime`, or full divisor exhaustion inside a
  pure PGS selector;
- zero audit failures if the rule is promoted;
- projected pure PGS at least `50%` at both $10^{15}$ and $10^{18}$.

## Branch Summary

| Branch | Commit | Status | Main result |
|---|---:|---|---|
| [`codex/solution-01-grok-shadow-state-contract`](https://github.com/zfifteen/prime-gap-structure/tree/codex/solution-01-grok-shadow-state-contract) | `c7a0456` | Rejected | Required state objects are absent from current artifacts. |
| [`codex/solution-01b-grok-reinvoke-closure`](https://github.com/zfifteen/prime-gap-structure/tree/codex/solution-01b-grok-reinvoke-closure) | `e07d776` | Rejected | Re-invoking chamber closure from `q0` selects too early on many rows. |
| [`codex/solution-01c-grok-gwr-later-side-closure`](https://github.com/zfifteen/prime-gap-structure/tree/codex/solution-01c-grok-gwr-later-side-closure) | `56d131f` | Rejected as drop-in | Existing GWR/NLSC selectors do not select a endpoint from only `p` and `q0`. |
| [`codex/solution-01d-grok-gwr-locked-chamber`](https://github.com/zfifteen/prime-gap-structure/tree/codex/solution-01d-grok-gwr-locked-chamber) | `d5d248d` | Rejected | GWR lock alone does not provide the missing next-prime offset. |
| [`codex/solution-01d-gwr-locked-integration`](https://github.com/zfifteen/prime-gap-structure/tree/codex/solution-01d-gwr-locked-integration) | `e81d287` | Not promotable | Fair locked-state integration found no safe replayable next-prime-margin key. |
| [`codex/solution-02-gemini-rst-law`](https://github.com/zfifteen/prime-gap-structure/tree/codex/solution-02-gemini-rst-law) | `4994dc2` | Rejected | Residual symmetry minimization selects many wrong endpoints. |
| [`codex/solution-03-meta-frontier-exhaustion`](https://github.com/zfifteen/prime-gap-structure/tree/codex/solution-03-meta-frontier-exhaustion) | `cba771c` | Rejected | Required mark-stream inputs are absent; materialized proxies are unsafe or abstain. |
| [`codex/solution-04-deepseek-square-grid-openq`](https://github.com/zfifteen/prime-gap-structure/tree/codex/solution-04-deepseek-square-grid-openq) | `343616d` | Rejected | The proposed square-grid sequence misses the audited endpoint on all 388 shadow rows. |
| [`codex/solution-05-claude-ssbrl-residue-advance`](https://github.com/zfifteen/prime-gap-structure/tree/codex/solution-05-claude-ssbrl-residue-advance) | `bfdab74` | Rejected | `q0 + r` never selects the endpoint; residue advance repeats the unsafe first-visible-open failure. |
| [`codex/solution-06-copilot-windowed-stabilization`](https://github.com/zfifteen/prime-gap-structure/tree/codex/solution-06-copilot-windowed-stabilization) | `fb1f18a` | Rejected | Windowed flux/pressure stabilization abstains on every target row. |
| [`codex/solution-07-seed-erasure-endpoint`](https://github.com/zfifteen/prime-gap-structure/tree/codex/solution-07-seed-erasure-boundary) | `973b3e3` | Rejected | Literal erasure collapses to first-visible-open; explicit seed-phase walls are unsafe. |
| `codex/solution-08-seed-pressure-gap` | `uncommitted` | Rejected | Bidirectional right-phase closure selects too early and too late; it adds no safe endpoint margin. |
| `codex/solution-09-seed-distance-closure` | `uncommitted` | Rejected | Seed-distance closure collapses to first-visible-open; the distance predicate is satisfied immediately on every target row. |
| `codex/solution-10-continued-chamber-ladder` | `uncommitted` | Rejected | Continued-chamber ladders show a weak 4m+2 distance signal but produce audit failures on every tested selector. |
| `codex/solution-11-carrier-threat-margin` | `uncommitted` | Rejected | Low-witness post-seed “threat” appears on every row but is too early; selecting the last visible-open before it abstains often and creates audit failures. |

## Solution 1: Full Chamber State Contract

Branch:
[`codex/solution-01-grok-shadow-state-contract`](https://github.com/zfifteen/prime-gap-structure/tree/codex/solution-01-grok-shadow-state-contract)

Commit: `c7a0456`

Proposed solution:

Compute the endpoint from a full chamber state:

- `S`, the chamber state;
- `gs`, a gap signature;
- `V`, visible closure data;
- `T`, a canonical terminal pattern;
- `PGS_state_transition`, a deterministic transition operator.

Test performed:

The branch added a state-contract probe to check whether the required objects
already exist in low exact diagnostics and high shadow-seed rows.

Artifacts:

- [probe script](https://github.com/zfifteen/prime-gap-structure/blob/codex/solution-01-grok-shadow-state-contract/benchmarks/python/predictor/simple_pgs_solution_01_state_contract_probe.py)
- [summary JSON](https://github.com/zfifteen/prime-gap-structure/blob/codex/solution-01-grok-shadow-state-contract/output/simple_pgs_solution_01_state_contract_probe/summary.json)
- [field availability CSV](https://github.com/zfifteen/prime-gap-structure/blob/codex/solution-01-grok-shadow-state-contract/output/simple_pgs_solution_01_state_contract_probe/field_availability.csv)

Result:

The solution is not testable as stated against the current minimal generator.

| Required object | Present rows |
|---|---:|
| `chamber_state` / `S` | 0 |
| `gap_signature` / `gs` | 0 |
| `pressure_vector` | 0 |
| `visible_closure_data` / `V` | 0 |
| `terminal_pattern` / `T` | 0 |
| named state transition operator | absent |

Strength:

The proposal identifies a plausible missing object: a richer chamber-state
transition system could, in principle, carry the next-prime state.

Weakness:

The required objects are not currently present. Adding them would be a new
state-capture experiment, not a drop-in test of the submitted law.

Limitation:

This branch does not falsify the mathematical idea. It rejects the submitted
implementation contract because the current generator artifacts cannot execute
it.

## Solution 1b: Reinvoke Chamber Closure From `q0`

Branch:
[`codex/solution-01b-grok-reinvoke-closure`](https://github.com/zfifteen/prime-gap-structure/tree/codex/solution-01b-grok-reinvoke-closure)

Commit: `e07d776`

Proposed solution:

Restart the existing chamber-closure procedure from the shadow seed:

```python
q = chamber_closure(p, start=q0)
```

Test performed:

The branch tested two literal interpretations:

- re-anchor chamber closure at `q0`;
- keep anchor `p` and restart closure after `q0`.

Artifacts:

- [probe script](https://github.com/zfifteen/prime-gap-structure/blob/codex/solution-01b-grok-reinvoke-closure/benchmarks/python/predictor/simple_pgs_solution_01b_reinvoke_closure_probe.py)
- [summary JSON](https://github.com/zfifteen/prime-gap-structure/blob/codex/solution-01b-grok-reinvoke-closure/output/simple_pgs_solution_01b_reinvoke_closure_probe/summary.json)
- [summary CSV](https://github.com/zfifteen/prime-gap-structure/blob/codex/solution-01b-grok-reinvoke-closure/output/simple_pgs_solution_01b_reinvoke_closure_probe/summary.csv)

Result:

Both interpretations selected too early on many high-scale rows.

| Scale | Shadow rows | Correct | Audit failures if promoted |
|---|---:|---:|---:|
| $10^{12}$ | 102 | 60 | 42 |
| $10^{15}$ | 141 | 76 | 65 |
| $10^{18}$ | 145 | 69 | 76 |

Strength:

The rule is minimal and uses only current chamber machinery.

Weakness:

It reproduces the known failure mode: the first visible-open candidate after
the seed is often another right-side impostor.

Limitation:

The rule has high projected PGS coverage only by accepting unsafe emissions.
It is not eligible for generator promotion.

## Solution 1c: GWR Later-Side Closure

Branch:
[`codex/solution-01c-grok-gwr-later-side-closure`](https://github.com/zfifteen/prime-gap-structure/tree/codex/solution-01c-grok-gwr-later-side-closure)

Commit: `56d131f`

Proposed solution:

Apply the documented GWR later-side closure and NLSC conditions after the
shadow seed:

```python
q = apply_gwr_later_side_closure(p, q0)
```

Test performed:

The branch checked the current GWR/NLSC implementation contracts:

- `select_next_boundary_prime(...)`;
- `select_d4_nlsc_boundary_prime(...)`.

Artifacts:

- [probe script](https://github.com/zfifteen/prime-gap-structure/blob/codex/solution-01c-grok-gwr-later-side-closure/benchmarks/python/predictor/simple_pgs_solution_01c_gwr_later_side_probe.py)
- [summary JSON](https://github.com/zfifteen/prime-gap-structure/blob/codex/solution-01c-grok-gwr-later-side-closure/output/simple_pgs_solution_01c_gwr_later_side_probe/summary.json)
- [summary CSV](https://github.com/zfifteen/prime-gap-structure/blob/codex/solution-01c-grok-gwr-later-side-closure/output/simple_pgs_solution_01c_gwr_later_side_probe/summary.csv)

Result:

The claimed drop-in function is not implemented, and the existing selector
contracts do not select a endpoint from only `p` and `q0`.

| Scale | Selector | Shadow rows | Correct | No selection | Projected PGS |
|---|---|---:|---:|---:|---:|
| $10^{12}$ | next-prime selector without offset | 102 | 0 | 102 | 59.68% |
| $10^{12}$ | d4 NLSC without margin | 102 | 0 | 102 | 59.68% |
| $10^{15}$ | next-prime selector without offset | 141 | 0 | 141 | 43.37% |
| $10^{15}$ | d4 NLSC without margin | 141 | 0 | 141 | 43.37% |
| $10^{18}$ | next-prime selector without offset | 145 | 0 | 145 | 42.00% |
| $10^{18}$ | d4 NLSC without margin | 145 | 0 | 145 | 42.00% |

Strength:

The proposal points at the correct theorem neighborhood. GWR later-side
closure and NLSC are relevant constraints after a placed selected integer.

Weakness:

The documented GWR later-side closure is a dominance and ceiling condition. It
does not itself return the endpoint.

Limitation:

The missing variable remains the exact next-prime offset or square-ceiling
margin.

## Solution 1d: GWR-Locked Chamber

Branch:
[`codex/solution-01d-grok-gwr-locked-chamber`](https://github.com/zfifteen/prime-gap-structure/tree/codex/solution-01d-grok-gwr-locked-chamber)

Commit: `d5d248d`

Proposed solution:

Add a probe-only `gwr_winner=q0` lock and resume chamber enumeration with the
shadow seed fixed as the selected integer:

```python
q = pgs_chamber_closure_v2(p, start=q0, gwr_winner=q0)
```

Test performed:

The branch tested three readings:

- weak visible closure after the locked seed;
- strict GWR lock with no additional terminal signal;
- NLSC locked-offset reading with missing margin.

Artifacts:

- [probe script](https://github.com/zfifteen/prime-gap-structure/blob/codex/solution-01d-grok-gwr-locked-chamber/benchmarks/python/predictor/simple_pgs_solution_01d_gwr_locked_chamber_probe.py)
- [summary JSON](https://github.com/zfifteen/prime-gap-structure/blob/codex/solution-01d-grok-gwr-locked-chamber/output/simple_pgs_solution_01d_gwr_locked_chamber_probe/summary.json)
- [summary CSV](https://github.com/zfifteen/prime-gap-structure/blob/codex/solution-01d-grok-gwr-locked-chamber/output/simple_pgs_solution_01d_gwr_locked_chamber_probe/summary.csv)

Result:

The weak executable reading selected too early. The strict locked readings had
no next-prime signal.

| Scale | Selector | Correct | No selection | Audit failures if promoted | Projected PGS |
|---|---|---:|---:|---:|---:|
| $10^{12}$ | weak visible closure with lock | 60/102 | 0 | 42 | 83.40% |
| $10^{15}$ | weak visible closure with lock | 76/141 | 0 | 65 | 73.90% |
| $10^{18}$ | weak visible closure with lock | 69/145 | 0 | 76 | 69.60% |
| all scales | strict GWR lock | 0 | all rows | 0 | unchanged |
| all scales | NLSC missing margin | 0 | all rows | 0 | unchanged |

Strength:

The lock expresses a real constraint: `q0` should remain the placed interior
selected integer rather than allowing later candidates to become new selected integers.

Weakness:

The lock is not a terminal selector. It does not identify which later candidate
is the endpoint.

Limitation:

The missing variable is still the endpoint margin. Locking the selected integer does not
derive that margin.

## Solution 1d Integration: Locked-State Margin Probe

Branch:
[`codex/solution-01d-gwr-locked-integration`](https://github.com/zfifteen/prime-gap-structure/tree/codex/solution-01d-gwr-locked-integration)

Commit: `e81d287`

Proposed integration:

Give the locked-chamber idea a fairer test by computing visible locked-state
features outside the generator, then mining whether any state key determines
the missing terminal margin.

The probe computes:

- visible-open candidates after `q0`;
- visible delta vectors;
- visible gap vectors;
- square-ceiling observables;
- seed residues;
- probe-only integer class from existing measurement rows;
- terminal margin as audit-only label.

Test performed:

The branch added leave-one-out replay. A key must select the held-out row
without using its own audit label.

Artifacts:

- [probe script](https://github.com/zfifteen/prime-gap-structure/blob/codex/solution-01d-gwr-locked-integration/benchmarks/python/predictor/simple_pgs_solution_01d_locked_state_integration_probe.py)
- [summary JSON](https://github.com/zfifteen/prime-gap-structure/blob/codex/solution-01d-gwr-locked-integration/output/simple_pgs_solution_01d_locked_state_integration_probe/summary.json)
- [locked-state key report](https://github.com/zfifteen/prime-gap-structure/blob/codex/solution-01d-gwr-locked-integration/output/simple_pgs_solution_01d_locked_state_integration_probe/locked_state_key_report.csv)
- [locked-state replay summary](https://github.com/zfifteen/prime-gap-structure/blob/codex/solution-01d-gwr-locked-integration/output/simple_pgs_solution_01d_locked_state_integration_probe/locked_state_replay_summary.csv)

Result:

No visible locked-state key promoted.

Best replay signal:

| Scale | Key | Correct | No selection | Audit failures | Projected PGS |
|---|---|---:|---:|---:|---:|
| $10^{15}$ | `K_visible_prefix_2` | 29/141 | 91 | 21 | 55.02% |
| $10^{18}$ | `K_visible_prefix_2` | 13/145 | 100 | 32 | 47.20% |

Some richer keys were zero-collision in-sample only because they were
effectively row-unique:

| Key | Rows | Key count | Repeated keys | Collision keys |
|---|---:|---:|---:|---:|
| `K_visible_prefix_8` | 388 | 388 | 0 | 0 |
| `K_square_delta_bucket` | 388 | 388 | 0 | 0 |
| `K_locked_full_visible` | 388 | 388 | 0 | 0 |

Strength:

This is the fairest current integration of the GWR-locked idea. It supplies
additional probe-side state without changing the generator or emitted record
contract.

Weakness:

The tested visible keys either do not replay or replay with audit failures.
Row-unique keys describe individual chambers but do not generalize into a
next-prime-margin law.

Limitation:

The probe only tests the current visible-state key families. It does not prove
that no deeper GWR/DNI state can determine the margin.

## Solution 2: Residual Symmetry Termination

Branch:
[`codex/solution-02-gemini-rst-law`](https://github.com/zfifteen/prime-gap-structure/tree/codex/solution-02-gemini-rst-law)

Commit: `4994dc2`

Proposed solution:

Compute a pre-shadow closure-state vector and slide it across the right side of
the shadow seed. Select the candidate whose right-side vector minimizes the
Hamming distance from the pre-shadow vector:

```text
CSR(x) = Hamming(A, B(x))
q = first argmin_x CSR(x)
```

Test performed:

The branch regenerated closure-state vectors from current PGS-visible logic
using `closure_reason(...)`. It tested:

- the literal fixed `128`-integer pre-shadow vector;
- a chamber-native prefix vector from `p` into `q0`;
- all integer candidates;
- visible-open candidate domains only.

Artifacts:

- [probe script](https://github.com/zfifteen/prime-gap-structure/blob/codex/solution-02-gemini-rst-law/benchmarks/python/predictor/simple_pgs_solution_02_rst_probe.py)
- [summary JSON](https://github.com/zfifteen/prime-gap-structure/blob/codex/solution-02-gemini-rst-law/output/simple_pgs_solution_02_rst_probe/summary.json)
- [RST summary CSV](https://github.com/zfifteen/prime-gap-structure/blob/codex/solution-02-gemini-rst-law/output/simple_pgs_solution_02_rst_probe/rst_summary.csv)
- [RST selection rows](https://github.com/zfifteen/prime-gap-structure/blob/codex/solution-02-gemini-rst-law/output/simple_pgs_solution_02_rst_probe/rst_selection_rows.csv)

Result:

No RST variant promoted. The visible-open domains produced some correct picks
and would raise projected PGS over `50%`, but only with many wrong selections.

Best legal-domain results:

| Scale | Vector | Domain | Correct | Audit failures | Projected PGS |
|---|---|---|---:|---:|---:|
| $10^{15}$ | anchor prefix | visible-open anchor bound | 52/141 | 89 | 64.26% |
| $10^{18}$ | anchor prefix | visible-open anchor bound | 47/145 | 98 | 60.80% |
| $10^{15}$ | fixed 128 | visible-open anchor bound | 41/141 | 100 | 59.84% |
| $10^{18}$ | fixed 128 | visible-open anchor bound | 27/145 | 118 | 52.80% |

The all-integer domains selected too early almost everywhere.

Strength:

The proposal required no generator change. Both vectors could be regenerated
from current deterministic closure logic, so the falsification surface was
clean and cheap after caching.

Weakness:

The Hamming-minimum criterion is not a next-prime selector. It frequently picks
another right-side impostor or overshoots the true next prime.

Limitation:

This branch tested binary closure-state vectors only. It does not rule out a
more structured residual using richer signed or weighted PGS states, but the
submitted CSR/Hamming law is not promotable.

## Solution 3: Shadow Seed Frontier Exhaustion

Branch:
[`codex/solution-03-meta-frontier-exhaustion`](https://github.com/zfifteen/prime-gap-structure/tree/codex/solution-03-meta-frontier-exhaustion)

Commit: `cba771c`

Proposed solution:

Treat `q0` as an interior seed and use a mark stream from chamber witnesses.
The rule selects the first unmarked candidate after a contiguous marked run
that exhausts all open residues at the seed:

```text
S_p(t) = 1 if t == p mod w for some w in W_p
q = first unmarked candidate after ResClosed(q0, tk) = Open(q0)
```

Test performed:

The branch first checked whether the submitted materialized inputs exist, then
tested artifact-native proxy rules using current candidate rows:

- visible-closure marked run over all materialized candidates;
- visible-closure marked run over odd candidates;
- witness-congruence marked run over odd candidates;
- witness-congruence marked run with residue-exhaustion gating.

Artifacts:

- [probe script](https://github.com/zfifteen/prime-gap-structure/blob/codex/solution-03-meta-frontier-exhaustion/benchmarks/python/predictor/simple_pgs_solution_03_frontier_exhaustion_probe.py)
- [summary JSON](https://github.com/zfifteen/prime-gap-structure/blob/codex/solution-03-meta-frontier-exhaustion/output/simple_pgs_solution_03_frontier_exhaustion_probe/summary.json)
- [materialized contract](https://github.com/zfifteen/prime-gap-structure/blob/codex/solution-03-meta-frontier-exhaustion/output/simple_pgs_solution_03_frontier_exhaustion_probe/materialized_contract.csv)
- [materialized coverage](https://github.com/zfifteen/prime-gap-structure/blob/codex/solution-03-meta-frontier-exhaustion/output/simple_pgs_solution_03_frontier_exhaustion_probe/materialized_coverage.csv)
- [frontier summary](https://github.com/zfifteen/prime-gap-structure/blob/codex/solution-03-meta-frontier-exhaustion/output/simple_pgs_solution_03_frontier_exhaustion_probe/frontier_summary.csv)

Materialization result:

The exact submitted inputs are not present in current artifacts.

| Required object | Present |
|---|---|
| `W_p` | false |
| `Open(q0)` | false |
| `S_p(t)` | false |

The current candidate rows also cover only the $10^{15}$ and $10^{18}$ shadow
groups:

| Scale | Expected shadow rows | Materialized candidate groups | Coverage |
|---|---:|---:|---:|
| $10^{12}$ | 102 | 0 | 0.0% |
| $10^{15}$ | 141 | 141 | 100.0% |
| $10^{18}$ | 145 | 145 | 100.0% |

Proxy-rule result:

No executable proxy promoted.

| Scale | Rule | Correct | No selection | Audit failures | Projected PGS |
|---|---|---:|---:|---:|---:|
| $10^{15}$ | visible run, all candidates | 76/141 | 0 | 65 | 73.90% |
| $10^{18}$ | visible run, all candidates | 69/145 | 0 | 76 | 69.60% |
| $10^{15}$ | visible run, odd candidates | 71/141 | 11 | 59 | 71.89% |
| $10^{18}$ | visible run, odd candidates | 63/145 | 15 | 67 | 67.20% |
| $10^{15}$ | witness congruence, odd | 0/141 | 141 | 0 | 43.37% |
| $10^{18}$ | witness congruence, odd | 0/145 | 145 | 0 | 42.00% |

Strength:

The proposal gives a crisp process-level object: a mark frontier and residue
exhaustion test, rather than another candidate-local tag.

Weakness:

The exact mark stream inputs are not materialized. The visible-run proxy
repeats the known too-early failure; the witness-congruence proxy abstains on
all tested rows.

Limitation:

This branch does not falsify a future implementation that explicitly
materializes `W_p`, `Open(q0)`, and `S_p(t)`. It rejects the submitted test
against current artifacts and the tested artifact-native approximations.

## Solution 4: Square-Grid `openQ`

Branch:
[`codex/solution-04-deepseek-square-grid-openq`](https://github.com/zfifteen/prime-gap-structure/tree/codex/solution-04-deepseek-square-grid-openq)

Commit: `343616d`

Proposed solution:

Generate the square-ceiling grid rooted at `p` and `q0`:

$$q_k = ceil((floor(sqrt(p q0)) + k)^2 / p)$$

Then select the first `q_k > q0` that remains open under the same active wall
set `W` used by chamber closure:

```text
openQ(x) = true if x mod w != 0 for every w in W
```

Test performed:

The exact submitted state is not materialized in current artifacts, so the
branch tested the square-grid claim directly and evaluated two artifact-native
`openQ` interpretations:

- materialized visible witnesses from existing candidate rows;
- all integer walls through `visible_divisor_bound = 10000`.

Both variants were tested with and without a wheel-open filter, under both
`p + candidate_bound` and `q0 + candidate_bound` windows.

Artifacts:

- [probe script](https://github.com/zfifteen/prime-gap-structure/blob/codex/solution-04-deepseek-square-grid-openq/benchmarks/python/predictor/simple_pgs_solution_04_square_grid_openq_probe.py)
- [summary JSON](https://github.com/zfifteen/prime-gap-structure/blob/codex/solution-04-deepseek-square-grid-openq/output/simple_pgs_solution_04_square_grid_openq_probe/summary.json)
- [square-grid summary CSV](https://github.com/zfifteen/prime-gap-structure/blob/codex/solution-04-deepseek-square-grid-openq/output/simple_pgs_solution_04_square_grid_openq_probe/square_grid_summary.csv)
- [selection rows](https://github.com/zfifteen/prime-gap-structure/blob/codex/solution-04-deepseek-square-grid-openq/output/simple_pgs_solution_04_square_grid_openq_probe/square_grid_selection_rows.csv)
- [materialized contract](https://github.com/zfifteen/prime-gap-structure/blob/codex/solution-04-deepseek-square-grid-openq/output/simple_pgs_solution_04_square_grid_openq_probe/materialized_contract.csv)

Result:

No rule promoted. The decisive failure is earlier than `openQ`: the audited
endpoint is not present in the proposed square-grid sequence for any tested
shadow row.

| Scale | Shadow rows | True endpoint not in square grid | Correct selections | No selections |
|---|---:|---:|---:|---:|
| $10^{12}$ | 102 | 102 | 0 | 102 |
| $10^{15}$ | 141 | 141 | 0 | 141 |
| $10^{18}$ | 145 | 145 | 0 | 145 |

Materialization result:

The exact submitted inputs are not present in current artifacts.

| Required object | Present |
|---|---|
| active wall prime set `W` | false |
| `closed[1..q0]` chamber vector | false |
| square-grid `q_k` sequence | computable from `p` and `q0` |

Candidate-row materialization is also incomplete for the lower high-scale
surface:

| Scale | Expected shadow rows | Materialized candidate groups | Coverage |
|---|---:|---:|---:|
| $10^{12}$ | 102 | 0 | 0.0% |
| $10^{15}$ | 141 | 141 | 100.0% |
| $10^{18}$ | 145 | 145 | 100.0% |

Strength:

The proposal is compact and falsifiable. It names a specific candidate stream
and a specific chamber-openness predicate.

Weakness:

The central claim that the true next prime lies in the square-grid candidate
stream fails on the current 388 shadow rows. With the target absent from the
candidate stream, no `openQ` predicate can recover it.

Limitation:

This branch rejects the submitted square-grid law at `candidate_bound = 128`.
It does not rule out a different square-derived coordinate that enumerates the
ordinary rightward candidate stream rather than the submitted `q_k` sequence.

## Solution 5: Shadow Seed Endpoint Recovery Law

Branch:
[`codex/solution-05-claude-ssbrl-residue-advance`](https://github.com/zfifteen/prime-gap-structure/tree/codex/solution-05-claude-ssbrl-residue-advance)

Commit: `bfdab74`

Proposed solution:

Use the shadow seed's blocking witness `r` and the chamber residue state at
`q0`:

```text
dominant case: q = q0 + r
general case: advance residues from q0 and select the first unblocked position
```

The submitted law treats `r`, the active wall primes, and the residue vector at
`q0` as current chamber-state objects.

Test performed:

The branch tested:

- the audit-only `q0 + r` claim, where `r` is the seed's least factor;
- the audit-only least-factor progression `q0 + k r`;
- residue advance using visible prime walls through `10000`;
- residue advance using all integer walls through `10000`;
- residue advance using materialized visible witnesses from candidate rows.

Artifacts:

- [probe script](https://github.com/zfifteen/prime-gap-structure/blob/codex/solution-05-claude-ssbrl-residue-advance/benchmarks/python/predictor/simple_pgs_solution_05_ssbrl_probe.py)
- [summary JSON](https://github.com/zfifteen/prime-gap-structure/blob/codex/solution-05-claude-ssbrl-residue-advance/output/simple_pgs_solution_05_ssbrl_probe/summary.json)
- [SSBRL summary CSV](https://github.com/zfifteen/prime-gap-structure/blob/codex/solution-05-claude-ssbrl-residue-advance/output/simple_pgs_solution_05_ssbrl_probe/ssbrl_summary.csv)
- [selection rows](https://github.com/zfifteen/prime-gap-structure/blob/codex/solution-05-claude-ssbrl-residue-advance/output/simple_pgs_solution_05_ssbrl_probe/ssbrl_selection_rows.csv)
- [materialized contract](https://github.com/zfifteen/prime-gap-structure/blob/codex/solution-05-claude-ssbrl-residue-advance/output/simple_pgs_solution_05_ssbrl_probe/materialized_contract.csv)

Result:

No rule promoted.

The direct `q0 + r` claim is false on the tested surface. The seed least factor
is always larger than the next-prime distance from the seed:

| Scale | Shadow rows | median `r` | median `q - q0` | `r = q - q0` |
|---|---:|---:|---:|---:|
| $10^{12}$ | 102 | 77,377 | 22 | 0 |
| $10^{15}$ | 141 | 171,629 | 24 | 0 |
| $10^{18}$ | 145 | 1,023,047 | 28 | 0 |

Residue advance over visible walls has signal, but it is unsafe:

| Scale | Rule family | Correct | Too early | Projected PGS |
|---|---|---:|---:|---:|
| $10^{12}$ | visible wall residue advance | 60/102 | 42 | 83.40% |
| $10^{15}$ | visible wall residue advance | 76/141 | 65 | 73.90% |
| $10^{18}$ | visible wall residue advance | 69/145 | 76 | 69.60% |

Materialization result:

The exact submitted state is not present in current artifacts.

| Required object | Present |
|---|---|
| seed blocking witness `r` in chamber state | false |
| active wall prime set / `sieve_primes` | false |
| residue vector at `q0` | false |

Strength:

The proposal is close to a real process model: it treats recovery as a
rightward continuation of chamber state rather than a flat tag on one
candidate.

Weakness:

The proposed witness step points in the wrong direction. The least factor of
the seed is far outside the actual seed-to-next-prime distance, so `q0 + r` and
`q0 + k r` cannot select the endpoint under the current chamber window.
Residue advance without the least-factor step reproduces the known unsafe
first-visible-open behavior.

Limitation:

This branch rejects the submitted SSBRL against current artifacts. It does not
rule out a future chamber-state object that records a different blocking phase
than the seed's least factor.

## Solution 6: Windowed Flux/Pressure Stabilization

Branch:
[`codex/solution-06-copilot-windowed-stabilization`](https://github.com/zfifteen/prime-gap-structure/tree/codex/solution-06-copilot-windowed-stabilization)

Commit: `fb1f18a`

Proposed solution:

Select the terminal next prime as the first rightward index after `q0` where a
PGS-visible recovery state stabilizes. The proposed recovery state uses:

- visible candidate flux;
- chamber-closure pressure;
- a window width `W = max(128, floor(log(p)^2))`;
- a stability gap `G = ceil(W / 8)`.

Test performed:

The submitted per-index flux and pressure series are not materialized in the
current sidecars. The branch synthesized them from the current PGS-visible
closure predicate over a local rightward window and tested:

- literal flux/pressure stabilization;
- a next-prime-open stabilization variant where the selected `r` must be
  visible-open;
- the first-visible-open selector as a baseline comparator.

Artifacts:

- [probe script](https://github.com/zfifteen/prime-gap-structure/blob/codex/solution-06-copilot-windowed-stabilization/benchmarks/python/predictor/simple_pgs_solution_06_windowed_stabilization_probe.py)
- [summary JSON](https://github.com/zfifteen/prime-gap-structure/blob/codex/solution-06-copilot-windowed-stabilization/output/simple_pgs_solution_06_windowed_stabilization_probe/summary.json)
- [stabilization summary CSV](https://github.com/zfifteen/prime-gap-structure/blob/codex/solution-06-copilot-windowed-stabilization/output/simple_pgs_solution_06_windowed_stabilization_probe/stabilization_summary.csv)
- [selection rows](https://github.com/zfifteen/prime-gap-structure/blob/codex/solution-06-copilot-windowed-stabilization/output/simple_pgs_solution_06_windowed_stabilization_probe/stabilization_selection_rows.csv)
- [materialized contract](https://github.com/zfifteen/prime-gap-structure/blob/codex/solution-06-copilot-windowed-stabilization/output/simple_pgs_solution_06_windowed_stabilization_probe/materialized_contract.csv)

Result:

No rule promoted. Both stabilization rules abstained on every
`shadow_seed_recovery` and unresolved row. The first-visible-open baseline
again shows high projected PGS only by accepting many too-early endpoints.

| Scale | Source | Stabilization correct | Stabilization no selection | First-visible correct | First-visible too early |
|---|---|---:|---:|---:|---:|
| $10^{12}$ | shadow seed | 0/102 | 102 | 60/102 | 42 |
| $10^{15}$ | shadow seed | 0/141 | 141 | 76/141 | 65 |
| $10^{18}$ | shadow seed | 0/145 | 145 | 69/145 | 76 |

Unresolved rows were also not recovered by stabilization:

| Scale | Unresolved rows | Stabilization selections | First-visible too early |
|---|---:|---:|---:|
| $10^{12}$ | 3 | 0 | 3 |
| $10^{15}$ | 7 | 0 | 7 |
| $10^{18}$ | 6 | 0 | 6 |

Materialization result:

The exact submitted state is not present in current artifacts.

| Required object | Present |
|---|---|
| per-index emitted / confirmed counts | false |
| per-index visible candidate flux | false |
| per-index chamber pressure | false |

Strength:

The proposal correctly avoids a flat candidate tag and tries to use a process
state over a rightward window.

Weakness:

The concrete stabilization criteria are too strict to select any tested
endpoint. When relaxed to the first visible-open comparator, the rule
collapses into the known unsafe early-selection pattern.

Limitation:

This branch rejects the submitted flux/pressure law as instantiated from the
current closure predicate. It does not rule out a different pressure definition
that is independently materialized as a PGS state rather than synthesized from
closed-position density.

## Solution 7: Seed-Erasure Next-Prime Law

Branch:
[`codex/solution-07-seed-erasure-endpoint`](https://github.com/zfifteen/prime-gap-structure/tree/codex/solution-07-seed-erasure-boundary)

Commit: `973b3e3`

Proposed solution:

Treat the true next prime as the first visible-open candidate after `q0` where
the rightward chamber trace no longer depends on the placed shadow seed.

```text
seed_erasure_defect(c) =
  disagreement count between the right trace with q0 present
  and the right trace with q0 erased
```

The selector chooses the first visible-open `c > q0` where the defect is zero,
or the first stable minimum if zero is too strict.

Test performed:

The current chamber does not materialize a placed-seed influence term. The
branch therefore tested three concrete interpretations:

- literal re-anchor identity, where no explicit seed influence exists;
- seed-offset phase wall, using the visible offset `q0 - p`;
- candidate-margin phase wall, using the visible margin `c - q0`.

Each interpretation was tested with trace windows `128` and `64`.

Artifacts:

- [probe script](https://github.com/zfifteen/prime-gap-structure/blob/codex/solution-07-seed-erasure-boundary/benchmarks/python/predictor/simple_pgs_solution_07_seed_erasure_probe.py)
- [window 128 summary JSON](https://github.com/zfifteen/prime-gap-structure/blob/codex/solution-07-seed-erasure-boundary/output/simple_pgs_solution_07_seed_erasure_probe/summary.json)
- [window 128 summary CSV](https://github.com/zfifteen/prime-gap-structure/blob/codex/solution-07-seed-erasure-boundary/output/simple_pgs_solution_07_seed_erasure_probe/seed_erasure_summary.csv)
- [window 64 summary JSON](https://github.com/zfifteen/prime-gap-structure/blob/codex/solution-07-seed-erasure-boundary/output/simple_pgs_solution_07_seed_erasure_probe_w64/summary.json)
- [window 64 summary CSV](https://github.com/zfifteen/prime-gap-structure/blob/codex/solution-07-seed-erasure-boundary/output/simple_pgs_solution_07_seed_erasure_probe_w64/seed_erasure_summary.csv)

Result:

No rule promoted. The literal interpretation collapses to the known
first-visible-open selector. The explicit seed-phase integrations select many
wrong endpoints.

Window `128`:

| Scale | Rule | Correct | Too early | Too late | Projected PGS |
|---|---|---:|---:|---:|---:|
| $10^{12}$ | literal identity | 60/102 | 42 | 0 | 83.40% |
| $10^{12}$ | seed-offset phase | 35/102 | 23 | 44 | 73.52% |
| $10^{12}$ | candidate-margin phase | 30/102 | 19 | 53 | 71.54% |
| $10^{15}$ | literal identity | 76/141 | 65 | 0 | 73.90% |
| $10^{15}$ | seed-offset phase | 55/141 | 38 | 48 | 65.46% |
| $10^{15}$ | candidate-margin phase | 36/141 | 36 | 69 | 57.83% |
| $10^{18}$ | literal identity | 69/145 | 76 | 0 | 69.60% |
| $10^{18}$ | seed-offset phase | 45/145 | 48 | 52 | 60.00% |
| $10^{18}$ | candidate-margin phase | 31/145 | 49 | 65 | 54.40% |

Window `64`:

| Scale | Rule | Correct | Too early | Too late | Projected PGS |
|---|---|---:|---:|---:|---:|
| $10^{12}$ | literal identity | 60/102 | 42 | 0 | 83.40% |
| $10^{12}$ | seed-offset phase | 36/102 | 28 | 38 | 73.91% |
| $10^{12}$ | candidate-margin phase | 37/102 | 28 | 37 | 74.31% |
| $10^{15}$ | literal identity | 76/141 | 65 | 0 | 73.90% |
| $10^{15}$ | seed-offset phase | 40/141 | 40 | 61 | 59.44% |
| $10^{15}$ | candidate-margin phase | 42/141 | 46 | 53 | 60.24% |
| $10^{18}$ | literal identity | 69/145 | 76 | 0 | 69.60% |
| $10^{18}$ | seed-offset phase | 51/145 | 46 | 48 | 62.40% |
| $10^{18}$ | candidate-margin phase | 46/145 | 59 | 40 | 60.40% |

Materialization result:

The required seed-erasure object is not present in current artifacts.

| Required object | Present |
|---|---|
| literal seed-erasure trace in current chamber state | false |
| placed-seed influence term | false |

Strength:

The test showed exactly where the proposed mechanism would need to live: in a
real, materialized seed influence term. Without that term, erasure is
mathematically invisible.

Weakness:

The tested seed-phase integrations are not safe selectors. They either reduce
to the first-visible-open failure or produce mixed early and late errors.

Limitation:

This branch rejects the current explicit seed-erasure integrations. It does
not rule out a future chamber model where `q0` contributes a real stateful
influence that can be erased and compared.

## Solution 8: Bidirectional Chamber Closure

Branch:
`codex/solution-08-seed-pressure-gap`

Commit: `uncommitted`

Proposed solution:

Treat each visible-open candidate after `q0` as a proposed right endpoint, not
only as a point in the anchor-framed rightward scan. Earlier visible-open
impostors that are open from `p` should close from the proposed endpoint side
if the candidate is the real terminal next prime.

The tested selector computes a right-phase defect:

```text
right_phase_defect(c) =
  count of earlier anchor-visible-open nodes n
  whose distance c - n is also right-phase open
```

The branch tests whether the true next prime is the first visible-open candidate
with zero defect, the leftmost minimum-defect candidate, or the first candidate
whose full left-open interior is closed by the right endpoint phase.

Test performed:

The probe tested right-endpoint phase closure under mod `30` and mod `210` on
the current high-scale shadow rows:

- `B0_first_visible_open_baseline`;
- `B1_first_prior_right_closed_mod30`;
- `B2_min_right_defect_mod30`;
- `B3_first_two_sided_closed_mod30`;
- `B4_first_prior_right_closed_mod210`;
- `B5_min_right_defect_mod210`;
- `B6_first_two_sided_closed_mod210`.

Artifacts:

- [probe script](../../../benchmarks/python/predictor/simple_pgs_solution_08_bidirectional_chamber_probe.py)
- [summary JSON](../../../output/simple_pgs_solution_08_bidirectional_chamber_probe/summary.json)
- [rule report CSV](../../../output/simple_pgs_solution_08_bidirectional_chamber_probe/bidirectional_rule_report.csv)
- [candidate rows CSV](../../../output/simple_pgs_solution_08_bidirectional_chamber_probe/bidirectional_candidate_rows.csv)

Result:

No rule promoted. The right-phase closure signal is real and measurable, but
it does not identify the terminal margin. It often chooses a later candidate
past the true next prime, while still choosing too early on many rows.

| Scale | Rule family | Correct | Too early | Too late | No selection | Projected PGS |
|---|---|---:|---:|---:|---:|---:|
| $10^{12}$ | first visible baseline | 60/102 | 42 | 0 | 0 | 83.40% |
| $10^{12}$ | bidirectional right phase | 24/102 | 18 | 60 | 0 | 69.17% |
| $10^{15}$ | first visible baseline | 76/141 | 65 | 0 | 0 | 73.90% |
| $10^{15}$ | bidirectional right phase | 32/141 | 33 | 76 | 0 | 56.22% |
| $10^{18}$ | first visible baseline | 69/145 | 76 | 0 | 0 | 69.60% |
| $10^{18}$ | bidirectional right phase | 29/145 | 47 | 68 | 1 | 53.60% |

Strength:

The probe tests a genuinely different chamber interpretation. It asks whether
the endpoint is the first point that closes its own left shadow, rather than
the first point that remains open from the anchor.

Weakness:

The current right-phase definition has no integer memory. It can describe a
balanced interior phase after the real next prime as easily as a terminal
endpoint, which creates many too-late selections.

Limitation:

This branch rejects mod-`30` and mod-`210` right-phase closure as currently
materialized. It does not rule out a right-endpoint state that carries the
placed seed or GWR-selected integer as an active term.

## Solution 9: Seed-Distance Closure

Branch:
`codex/solution-09-seed-distance-closure`

Commit: `uncommitted`

Proposed solution:

Treat each anchor-visible-open candidate after `q0` as a proposed right
endpoint. Require that every prior anchor-visible-open point (including the
seed itself) is *visibly closed* by the distance to the candidate, using the
same PGS-visible `closure_reason(0, delta)` predicate (wheel + bounded divisor
witnesses).

The tested selector is:

```text
Pick the first anchor-visible-open candidate c after q0
such that for every prior visible-open node n <= c,
closure_reason(0, c - n) is not None.
```

Test performed:

The probe tested the distance-closure gate on the current high-scale shadow
rows:

- baseline `B0_first_visible_open_baseline`;
- distance gate `D1_first_seed_distance_closes_all_prior`.

Artifacts:

- [probe script](../../../benchmarks/python/predictor/simple_pgs_solution_09_seed_distance_closure_probe.py)
- [summary JSON](../../../output/simple_pgs_solution_09_seed_distance_closure_probe/summary.json)
- [rule report CSV](../../../output/simple_pgs_solution_09_seed_distance_closure_probe/seed_distance_rule_report.csv)
- [candidate rows CSV](../../../output/simple_pgs_solution_09_seed_distance_closure_probe/seed_distance_candidate_rows.csv)

Result:

No rule promoted. The distance-closure gate does not separate true next primes
from visible-open impostors: it is satisfied by the first visible-open
candidate on every target row, so it collapses to the known first-visible-open
baseline.

| Scale | Rule family | Correct | Too early | Too late | No selection | Projected PGS |
|---|---|---:|---:|---:|---:|---:|
| $10^{12}$ | first visible baseline | 60/102 | 42 | 0 | 0 | 83.40% |
| $10^{12}$ | seed-distance closure | 60/102 | 42 | 0 | 0 | 83.40% |
| $10^{15}$ | first visible baseline | 76/141 | 65 | 0 | 0 | 73.90% |
| $10^{15}$ | seed-distance closure | 76/141 | 65 | 0 | 0 | 73.90% |
| $10^{18}$ | first visible baseline | 69/145 | 76 | 0 | 0 | 69.60% |
| $10^{18}$ | seed-distance closure | 69/145 | 76 | 0 | 0 | 69.60% |

Strength:

This probe adds one explicit seed-carried predicate without adding new emitted
fields or invoking forbidden labels. It tests a concrete two-sided closure
operator that is stronger than mod-only residue closure.

Weakness:

The closure operator is too weakly correlated with the hidden large-factor
structure. Empirically, the seed-to-first-visible-open distance is always
visibly closed (wheel-closed or small-witness-closed), so the gate never
filters the baseline impostor.

Limitation:

This branch rejects seed-distance closure as materialized by
`closure_reason(0, delta)` with the current visible divisor bound. It does not
rule out a integer-aware state transition that distinguishes the seed from the
first visible-open candidate.

## Solution 10: Continued-Chamber Ladder

Branch:
`codex/solution-10-continued-chamber-ladder`

Commit: `uncommitted`

Proposed solution:

Use the Lambert continued-fraction ladder `2, 6, 10, 14, ...` as a post-seed
correction structure. Materialize the ladder as a deterministic congruence on
seed-to-candidate distance:

```text
lambert_step(distance) := distance >= 2 and (distance - 2) mod 4 == 0
```

The probe tests whether the true next prime tends to lie on this distance ladder
or on a related ladder in the seed-framed closure prefix count, and whether
either ladder yields an audit-clean selector on shadow-seed rows.

Test performed:

The probe tested four selectors on the current 388 high-scale shadow rows:

- `first_visible_open` baseline;
- `first_distance_on_4m_plus_2`;
- `first_closed_prefix_on_4m_plus_2`;
- `first_both_ladders`.

Artifacts:

- [probe script](../../../benchmarks/python/predictor/simple_pgs_continued_chamber_probe.py)
- [summary JSON](../../../output/simple_pgs_continued_chamber_probe/summary.json)
- [rule report CSV](../../../output/simple_pgs_continued_chamber_probe/rule_report.csv)
- [q ladder report CSV](../../../output/simple_pgs_continued_chamber_probe/q_ladder_report.csv)
- [candidate rows CSV](../../../output/simple_pgs_continued_chamber_probe/candidate_rows.csv)

Result:

No rule promoted. Every tested selector that produces nonzero hits also creates
audit failures. The best-performing continued-chamber rule has substantial
recall but is unsafe.

Per-scale selector summary:

| Scale | Rule | Correct | Failures | Selected |
|---|---|---:|---:|---:|
| $10^{12}$ | `first_distance_on_4m_plus_2` | 41/102 | 32 | 73 |
| $10^{15}$ | `first_distance_on_4m_plus_2` | 55/141 | 48 | 103 |
| $10^{18}$ | `first_distance_on_4m_plus_2` | 50/145 | 55 | 105 |

Aggregate across all scales:

| Rule | Correct | Failures |
|---|---:|---:|
| `first_distance_on_4m_plus_2` | 146 | 135 |
| `first_closed_prefix_on_4m_plus_2` | 54 | 53 |
| `first_both_ladders` | 16 | 10 |

Observed true-next-prime membership on the distance ladder:

| Scale | q on 4m+2 distance ladder |
|---|---:|
| $10^{12}$ | 59/102 |
| $10^{15}$ | 78/141 |
| $10^{18}$ | 76/145 |

Strength:

The ladder property is real and measurable. The true next prime is more likely
than not to satisfy the `4m+2` distance predicate from the seed on these
surfaces.

Weakness:

The property is not selective enough to identify the terminal next prime. Many
visible-open impostors also lie on the ladder, so selecting on ladder
membership produces audit failures.

Limitation:

This branch rejects the literal Lambert ladder materialization as a endpoint
selector. It does not rule out a seed-carried transition state that uses the
ladder only as a prior inside a stricter integer-preservation or reset
discriminator.

## Solution 11: Integer Threat Transition Gate

Branch:
`codex/solution-11-carrier-threat-margin`

Commit: `uncommitted`

Proposed solution:

Treat the first post-seed wheel-open closure with a small divisor witness as a
PGS-visible integer-transition event:

- threat = first `n > q0` with `closure_reason(p, n - p)` of the form
  `divisor_witness:w` with `w <= 97`;
- select `q_hat` = last anchor-visible-open candidate strictly before the
  threat.

Test performed:

The probe evaluated the integer-threat gate on the 388 high-scale shadow rows
with:

- `candidate_bound=128`
- `visible_divisor_bound=10_000`
- `threat_witness_bound=97`

Artifacts:

- [probe script](../../../benchmarks/python/predictor/simple_pgs_solution_11_carrier_threat_margin_probe.py)
- [summary JSON](../../../output/simple_pgs_solution_11_carrier_threat_margin_probe/summary.json)
- [rule report CSV](../../../output/simple_pgs_solution_11_carrier_threat_margin_probe/carrier_threat_rule_report.csv)
- [event rows CSV](../../../output/simple_pgs_solution_11_carrier_threat_margin_probe/carrier_threat_event_rows.csv)

Result:

No rule promoted. A low-witness post-seed threat exists on every shadow row,
but it typically occurs before any post-seed visible-open candidate, so the
gate abstains frequently. When the gate does select, it produces audit
failures via both early and late mis-selections.

| Scale | Selected | Correct | Audit failures if promoted | No selection | Projected PGS |
|---|---:|---:|---:|---:|---:|
| $10^{12}$ | 29/102 | 14/102 | 15 | 73 | 65.22% |
| $10^{15}$ | 38/141 | 18/141 | 20 | 103 | 50.60% |
| $10^{18}$ | 48/145 | 18/145 | 30 | 97 | 49.20% |

Strength:

The integer-threat observable is genuinely PGS-visible and does not use audit
labels or any exact divisor-field classification. It is a concrete attempt to
turn a post-seed closure witness event into a next-prime-margin marker.

Weakness:

The threat is too local and too common. It appears immediately after `q0` on
all rows, so it does not separate the terminal next prime from visible-open
impostors and it often leaves no selectable visible-open candidate before the
threat.

Limitation:

This branch rejects the specific low-witness threat-as-transition
materialization. It does not rule out a integer-preservation or reset
observable that depends on a different post-seed invariant than the first
small divisor witness.

## Current Lesson

The strongest common finding across these branches is:

`q0` is useful as a placed interior seed, but neither visible chamber restart,
GWR later-side dominance, nor a locked selected integer condition currently determines
the next-prime offset.

The missing object remains:

```text
endpoint margin = q - q0
```

or equivalently:

```text
next-prime offset = q - p
```

The next useful proposal should identify that margin from PGS-visible state, or
name one new narrow observable that can be computed in a probe and tested under
leave-one-out replay.
