# Next-Prime Law 005A Evidence Stack

## Status

Next-Prime Law 005A is the sole live Next-Prime Law 005 candidate.

Current project status:

- PGS Prime Generator: not complete
- Milestone 0: accepted
- Milestone 1 positive emission: blocked
- pure prime emission: forbidden
- Next-Prime Law 005A: candidate-grade, action-population audit passed, safe so far, narrow
- Next-Prime Law 005B: quarantined
- PGS-inferred prime emission: not approved

This note is offline theorem discovery. It consolidates evidence for 005A. It does not approve pure generation, prime emission, or theorem status.

## Candidate Statement

A proposed right endpoint has a resolved chamber certificate. Later candidate chambers remain unresolved because they extend past that resolved candidate.

Next-Prime Law 005A adds one lock condition:

```text
resolved chamber
+ higher-divisor pressure lock
=> later unresolved extension candidates may be absorbed in the offline eliminator
```

Operationally, 005A says:

```text
If a resolved survivor has legal higher-divisor pressure between itself and its later unresolved alternatives, then that resolved survivor may absorb those later unresolved alternatives in the offline composite-exclusion eliminator.
```

The rule remains candidate-grade. It is not a proof that the resolved survivor is prime.

## Allowed Inputs

005A may use only evidence available from the label-free eliminator state:

- resolved chamber status from composite exclusion
- later unresolved candidate offsets
- bounded positive composite witnesses
- bounded legal divisor-class certificates
- the first legal integer of the proposed chamber
- divisor class of that integer
- higher-divisor pressure after the resolved candidate and before later unresolved alternatives
- selected-integer-locked pressure ceiling state already computed without labels
- single-hole positive witness closure state already computed without labels

Classical labels may be attached only after the rule acts, for audit.

## Forbidden Inputs

005A must not use:

- `isprime`
- `nextprime`
- Miller-Rabin
- prime marker identity
- scan-to-first-prime logic
- actual future next-prime offset inside the rule
- future gap width
- old recursive walker output
- full forbidden divisor ladders
- hidden primality-by-absence logic

The rule must abstain when the legal higher-divisor pressure lock is absent.

## Hardening Surface

005A hardening used:

- candidate bound: 64
- witness bound: 97
- single-hole positive witness closure: enabled
- selected-integer-locked pressure ceiling: enabled
- selected-integer-lock predicate: unresolved_alternatives_before_threat

Staged hardening results:

| surface | true resolved candidates | false resolved candidates | true selected | false selected | wrong |
|---|---:|---:|---:|---:|---:|
| 11..10000 | 1173 | 282 | 31 | 0 | 0 |
| 11..100000 | 7431 | 4354 | 31 | 0 | 0 |
| 11..1000000 | 49019 | 46286 | 31 | 0 | 0 |

The selector safety gate passed through input primes 11..1000000:

```text
higher_divisor_pressure_lock_false_selected: 0
higher_divisor_pressure_lock_wrong_count: 0
```

## Integration Surface

005A flagged integration used the same base eliminator configuration:

- candidate bound: 64
- witness bound: 97
- single-hole positive witness closure: enabled
- selected-integer-locked pressure ceiling: enabled
- selected-integer-lock predicate: unresolved_alternatives_before_threat
- higher-divisor locked absorption: enabled only in offline integration

Integration results:

| surface | unique resolved survivors | true next prime rejected | absorption correct | absorption wrong | false survivor absorbed |
|---|---:|---:|---:|---:|---:|
| 11..100000 | 25 | 0 | 31 | 0 | 0 |
| 11..1000000 | 25 | 0 | 31 | 0 | 0 |

The integration safety gate passed:

```text
true_boundary_rejected_count: 0
absorption_wrong_count: 0
false_resolved_survivor_absorbed_count: 0
```

## Action-Population Audit

005B failed because its hardening population did not cover every candidate it could act on during integration.

005A passed that audit.

Action-population audit results:

| lock | hardening candidates | integration actions | missed actions | wrong absorptions | true next prime rejected |
|---|---:|---:|---:|---:|---:|
| 005A higher_divisor_pressure_lock | 114222 | 31 | 0 | 0 | 0 |

Surface detail:

| surface | hardening candidates | integration actions | missed actions | wrong absorptions | true next prime rejected |
|---|---:|---:|---:|---:|---:|
| 11..1000000 | 95305 | 31 | 0 | 0 | 0 |
| 100000..200000 | 10163 | 0 | 0 | 0 | 0 |
| 1000000..1100000 | 8754 | 0 | 0 | 0 | 0 |

The audit invariant passed:

Let $M$ be the missed action candidate count.

$$M = 0$$

This removes the specific population-mismatch risk that killed 005B. It does not approve generator emission.

## Shifted-Window Result

005A was tested on shifted windows:

| surface | unique resolved survivors | true next prime rejected | applied | wrong |
|---|---:|---:|---:|---:|
| 100000..200000 | 0 | 0 | 0 | 0 |
| 1000000..1100000 | 0 | 0 | 0 | 0 |

The shifted windows safely abstained. That is acceptable for candidate safety, but it shows the lock is sparse and not a general next-prime-forcing theorem.

## Coverage Limitation

005A has narrow coverage.

Across the origin surface through input primes 11..1000000:

- selected true resolved candidates: 31
- unique resolved survivors produced by integration: 25
- shifted-window activations: 0

The candidate is valuable because it has not been wrong where it fires. It is not broad enough to complete Milestone 1.

## Falsification Conditions

Immediately quarantine 005A if any future run shows:

```text
higher_divisor_pressure_lock_false_selected > 0
absorption_wrong_count > 0
false_resolved_survivor_absorbed_count > 0
true_boundary_rejected_count > 0
missed_action_candidate_count > 0
```

Also quarantine it if a dependency audit finds any forbidden input in the rule computation.

One wrong case kills generator eligibility for 005A.

## Why Pure Emission Remains Forbidden

005A remains offline and candidate-grade because:

- it has not been proven as a theorem
- it has narrow coverage
- shifted windows abstain
- classical labels are still used after action for audit
- the pure generator has no approved emission contract
- no emitted value has been certified as a PGS-inferred prime
- the candidate has not yet passed a controlled expansion stress test

The pure generator must continue to fail closed.

## Next Gate Before Milestone 1

The next gate is a controlled single-axis stress test.

Recommended first expansion:

```text
candidate_bound: 128
witness_bound: 97
surface: input primes 11..1000000
```

This changes the candidate horizon while preserving the witness basis.

Alternative expansion:

```text
candidate_bound: 64
witness_bound: 127
surface: input primes 11..1000000
```

This changes the witness basis while preserving the candidate horizon.

Only one axis should change at a time. The same gates must pass:

```text
selector false selections: 0
integration wrong absorptions: 0
true next prime rejections: 0
missed action candidates: 0
```

If 005A passes one controlled expansion, the next artifact should be an expanded 005A stress-test note. If it fails any gate, 005A must be quarantined or re-hardened before any further candidate-law work.
