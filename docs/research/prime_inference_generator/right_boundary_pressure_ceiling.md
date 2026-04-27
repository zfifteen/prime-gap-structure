# Right-Endpoint Pressure Ceiling Probe

The first tested right-endpoint pressure ceiling is not safe. A later certified
lower-divisor composite can be a selected-integer reset, not a proof that the prime
endpoint occurred earlier.

Next-Prime Law 005 is not approved by this note.

## Objective

Test the squeeze architecture:

1. start from a known anchor prime $p$;
2. identify legal GWR-style selected-integer evidence to the right;
3. find a later certified lower-divisor pressure event;
4. use that event as a proposed ceiling $T$;
5. run composite exclusion only on candidate next primes below $T$;
6. attach classical labels only afterward for audit.

The intended inference shape is:

- GWR pressure says the endpoint cannot extend past $T$;
- composite exclusion eliminates non-candidate next primes before $T$;
- if exactly one candidate remains, it becomes a candidate inferred next prime.

The tested rule does not satisfy the first line.

## Instrument

Script:

- `../../../benchmarks/python/prime_inference_generator/right_boundary_pressure_ceiling_probe.py`

Artifacts:

- `right_boundary_pressure_ceiling_probe_rows.jsonl`
- `right_boundary_pressure_ceiling_probe_summary.json`

The probe uses the integrated composite-exclusion pass with:

- `single_hole_positive_witness_closure`
- `witness_bound: 97`

The ceiling logic is label-free. Labels are attached only after the ceiling and
candidate-exclusion records have been computed.

## Candidate Ceiling Rule

The probe uses only positive structure.

It certifies a selected divisor-count class when the composite is one of:

- a known-basis prime power, such as $83^2$;
- a known-basis semiprime, such as $71 \cdot 97$.

It then looks for the first later certified composite with smaller divisor
class. For the common case, this means a certified $d=4$ integer followed by a
certified $d=3$ square.

The rule is deliberately marked as a candidate pressure ceiling, not as a law.

## Surface

Run:

- anchors: `11..10_000`
- candidate bound: `64`
- witness bound: `97`

Command:

```bash
python3 benchmarks/python/prime_inference_generator/right_boundary_pressure_ceiling_probe.py --start-anchor 11 --max-anchor 10000 --candidate-bound 64 --witness-bound 97 --output-dir /tmp/pgs_right_boundary_ceiling_10000_b64_w97
```

## Result

Summary:

- `row_count: 1225`
- `candidate_pressure_ceiling_count: 139`
- `NO_LEGAL_CARRIER: 417`
- `NO_LEGAL_THREAT: 669`
- `true_boundary_rejected_count: 11`
- `true_boundary_before_T_count: 128`
- `unique_survivor_count: 17`
- `unique_survivor_match_count: 16`
- `unique_survivor_match_rate: 0.9411764705882353`
- `average_candidate_count_before_ceiling: 16.749387755102042`
- `average_candidate_count_after_ceiling: 15.739591836734695`
- `average_survivor_count_after_ceiling: 1.177142857142857`

Failure counts:

| Failure reason | Count |
|---|---:|
| `NO_LEGAL_CARRIER` | `417` |
| `NO_LEGAL_THREAT` | `669` |
| `NO_UNIQUE_BOUNDARY_BEFORE_CEILING` | `112` |
| `TRUE_BOUNDARY_NOT_BEFORE_CEILING` | `11` |
| `NONE` | `16` |

The hard safety gate fails:

- `true_boundary_rejected_count: 11`

## Concrete Failure

One failure occurs at anchor `6883`.

The candidate ceiling records:

- integer: `6887 = 71 * 97`
- selected divisor-count class: $d=4$
- threat: `6889 = 83^2`
- threat divisor class: $d=3$
- proposed ceiling offset: `T = 6`

The audited next prime is:

- actual next prime offset: `16`

So the proposed ceiling would exclude the true next prime. The later lower-divisor
event is not proof that the chamber ended before it. In this case it can act as
a selected-integer reset.

## Interpretation

The user intuition remains structurally right: if a integer is already locked,
then a later lower-divisor composite would force a right-endpoint ceiling.

The probe shows the missing condition:

- a certified lower-divisor event after the first certified composite does not
  prove that the first certified composite was the locked GWR-selected integer.

Without a selected-integer-lock predicate, lower-divisor pressure is not a safe ceiling.
It can describe a transition in the interior chamber rather than a contradiction
with the chamber.

## Status

Milestone 1 remains blocked.

Next-Prime Law 005 is not approved.

The next theorem target is a selected-integer-lock condition:

If PGS evidence establishes that a integer $w$ is the active chamber integer,
then the first later certified lower-divisor composite gives a right-endpoint
ceiling. Without that lock, the event is only pressure evidence.
