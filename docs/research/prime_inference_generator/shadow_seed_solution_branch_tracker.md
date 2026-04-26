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
| [`codex/solution-01c-grok-gwr-later-side-closure`](https://github.com/zfifteen/prime-gap-structure/tree/codex/solution-01c-grok-gwr-later-side-closure) | `56d131f` | Rejected as drop-in | Existing GWR/NLSC selectors do not select a boundary from only `p` and `q0`. |
| [`codex/solution-01d-grok-gwr-locked-chamber`](https://github.com/zfifteen/prime-gap-structure/tree/codex/solution-01d-grok-gwr-locked-chamber) | `d5d248d` | Rejected | GWR lock alone does not provide the missing boundary offset. |
| [`codex/solution-01d-gwr-locked-integration`](https://github.com/zfifteen/prime-gap-structure/tree/codex/solution-01d-gwr-locked-integration) | `e81d287` | Not promotable | Fair locked-state integration found no safe replayable boundary-margin key. |
| [`codex/solution-02-gemini-rst-law`](https://github.com/zfifteen/prime-gap-structure/tree/codex/solution-02-gemini-rst-law) | `4994dc2` | Rejected | Residual symmetry minimization selects many wrong boundaries. |

## Solution 1: Full Chamber State Contract

Branch:
[`codex/solution-01-grok-shadow-state-contract`](https://github.com/zfifteen/prime-gap-structure/tree/codex/solution-01-grok-shadow-state-contract)

Commit: `c7a0456`

Proposed solution:

Compute the boundary from a full chamber state:

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
transition system could, in principle, carry the boundary state.

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
contracts do not select a boundary from only `p` and `q0`.

| Scale | Selector | Shadow rows | Correct | No selection | Projected PGS |
|---|---|---:|---:|---:|---:|
| $10^{12}$ | boundary selector without offset | 102 | 0 | 102 | 59.68% |
| $10^{12}$ | d4 NLSC without margin | 102 | 0 | 102 | 59.68% |
| $10^{15}$ | boundary selector without offset | 141 | 0 | 141 | 43.37% |
| $10^{15}$ | d4 NLSC without margin | 141 | 0 | 141 | 43.37% |
| $10^{18}$ | boundary selector without offset | 145 | 0 | 145 | 42.00% |
| $10^{18}$ | d4 NLSC without margin | 145 | 0 | 145 | 42.00% |

Strength:

The proposal points at the correct theorem neighborhood. GWR later-side
closure and NLSC are relevant constraints after a placed winner.

Weakness:

The documented GWR later-side closure is a dominance and ceiling condition. It
does not itself return the boundary.

Limitation:

The missing variable remains the exact boundary offset or square-ceiling
margin.

## Solution 1d: GWR-Locked Chamber

Branch:
[`codex/solution-01d-grok-gwr-locked-chamber`](https://github.com/zfifteen/prime-gap-structure/tree/codex/solution-01d-grok-gwr-locked-chamber)

Commit: `d5d248d`

Proposed solution:

Add a probe-only `gwr_winner=q0` lock and resume chamber enumeration with the
shadow seed fixed as the winner:

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
no boundary signal.

| Scale | Selector | Correct | No selection | Audit failures if promoted | Projected PGS |
|---|---|---:|---:|---:|---:|
| $10^{12}$ | weak visible closure with lock | 60/102 | 0 | 42 | 83.40% |
| $10^{15}$ | weak visible closure with lock | 76/141 | 0 | 65 | 73.90% |
| $10^{18}$ | weak visible closure with lock | 69/145 | 0 | 76 | 69.60% |
| all scales | strict GWR lock | 0 | all rows | 0 | unchanged |
| all scales | NLSC missing margin | 0 | all rows | 0 | unchanged |

Strength:

The lock expresses a real constraint: `q0` should remain the placed interior
winner rather than allowing later candidates to become new winners.

Weakness:

The lock is not a terminal selector. It does not identify which later candidate
is the boundary.

Limitation:

The missing variable is still the boundary margin. Locking the winner does not
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
- probe-only carrier class from existing measurement rows;
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
boundary-margin law.

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

The Hamming-minimum criterion is not a boundary selector. It frequently picks
another right-side impostor or overshoots the true boundary.

Limitation:

This branch tested binary closure-state vectors only. It does not rule out a
more structured residual using richer signed or weighted PGS states, but the
submitted CSR/Hamming law is not promotable.

## Current Lesson

The strongest common finding across these branches is:

`q0` is useful as a placed interior seed, but neither visible chamber restart,
GWR later-side dominance, nor a locked winner condition currently determines
the boundary offset.

The missing object remains:

```text
boundary margin = q - q0
```

or equivalently:

```text
boundary offset = q - p
```

The next useful proposal should identify that margin from PGS-visible state, or
name one new narrow observable that can be computed in a probe and tested under
leave-one-out replay.
