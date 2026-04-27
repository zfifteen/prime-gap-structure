# Next-Prime Law 005 Candidate: Higher-Divisor Locked Resolved-Endpoint Absorption

Next-Prime Law 005 is a candidate law, not a theorem.

The pure generator must remain fail-closed. This note does not approve prime
emission.

## Status

Current status:

- Milestone 0: accepted.
- Milestone 1: blocked for pure generator emission.
- Next-Prime Law 005: candidate draft approved.
- Pure emission: forbidden.

The current strongest supported claim is:

```text
In offline composite-exclusion testing, the higher-divisor pressure lock
remained zero-wrong through input primes 11..1_000_000, and flagged integration
produced 25 unique resolved survivors through input primes 11..1_000_000 with zero
true-next-prime rejections and zero wrong absorptions.
```

## Problem Statement

Composite exclusion can safely reject some impossible chambers, but safe
rejection alone did not force a unique endpoint.

Resolved-chamber absorption alone also failed. It absorbed later unresolved
alternatives for true resolved endpoints, but it also absorbed later
alternatives for false resolved survivors. Therefore:

```text
resolved chamber => absorbs extensions
```

is false as a next-prime law.

The missing ingredient is a lock condition that separates true resolved
endpoints from false resolved survivors before absorption is allowed.

## Candidate Law

Candidate statement:

```text
If a proposed right endpoint has a fully resolved chamber certificate and
satisfies the higher-divisor pressure lock, then later unresolved extension
candidates may be absorbed in the offline eliminator, provided no legal reset
certificate supersedes the lock.
```

On the tested surfaces, this candidate rule selected true resolved candidates
with zero false selections and produced unique resolved survivors under flagged
integration without rejecting the true next prime.

This does not prove that the emitted candidate is prime. It only states that,
under the measured offline eliminator, a narrow PGS-native lock condition
allowed safe absorption of later unresolved alternatives.

## Allowed Evidence

The candidate law may use:

- a resolved chamber certificate already produced by the offline eliminator;
- positive composite witness evidence;
- legal divisor-class certificates from the bounded witness basis;
- higher-divisor pressure between the resolved candidate and later unresolved
  alternatives;
- selected-integer metadata computed from legal composite certificates;
- post-run classical labels for offline audit only.

## Forbidden Evidence

The candidate law must not use:

- `isprime`;
- `nextprime`;
- `prime` sequence lookup inside generation;
- prime marker identity;
- actual future next-prime offset inside the rule;
- future gap width;
- old recursive walker logic;
- full forbidden divisor ladders;
- scan-to-first-prime endpoint detection.

Offline labels are allowed only for measuring whether the candidate selected
true or false resolved candidates after the label-free records already exist.

## Operational Rule

The current offline operation is:

1. Run composite exclusion with single-hole positive witness closure enabled.
2. Run selected-integer-locked pressure ceiling with
   `unresolved_alternatives_before_threat`.
3. Identify resolved survivor candidates.
4. For each resolved candidate, inspect later unresolved alternatives.
5. If legal higher-divisor pressure exists between the resolved candidate and
   those later unresolved alternatives, treat the resolved candidate as locked.
6. Absorb later unresolved alternatives only for locked resolved candidates.
7. Fail closed unless the final candidate state contains exactly one resolved
   survivor and no unresolved alternatives.

This rule is opt-in in the offline probe:

```text
--enable-higher-divisor-pressure-locked-absorption
```

It is not enabled in the pure generator.

## Tested Surface

The candidate was tested with:

- `candidate_bound: 64`
- `witness_bound: 97`
- `single_hole_positive_witness_closure: enabled`
- `carrier_locked_pressure_ceiling: enabled`
- `carrier_lock_predicate: unresolved_alternatives_before_threat`
- `higher_divisor_pressure_locked_absorption: enabled only for integration tests`

Hardening surfaces:

- input primes `11..10_000`
- input primes `11..100_000`
- input primes `11..1_000_000`

Integration surfaces:

- input primes `11..100_000`
- input primes `11..1_000_000`
- shifted window `100_000..200_000`
- shifted window `1_000_000..1_100_000`

## Hardening Results

Higher-divisor pressure lock separator:

| Surface | Rows | True resolved | False resolved | True selected | False selected | Wrong |
|---|---:|---:|---:|---:|---:|---:|
| `11..10_000` | `1225` | `1173` | `282` | `31` | `0` | `0` |
| `11..100_000` | `9588` | `7431` | `4354` | `31` | `0` | `0` |
| `11..1_000_000` | `78494` | `49019` | `46286` | `31` | `0` | `0` |

The lock remained zero-wrong as the false-resolved candidate pool increased
from `282` to `46286`.

The selected true count stayed at `31`, so this candidate is narrow. The
important hardening result is:

```text
higher_divisor_pressure_lock_false_selected: 0
```

on every staged hardening surface.

## Integration Results

Flagged integration:

| Surface | Rows | Unique resolved survivors | True rejected | Applied | Correct | Wrong | False absorber |
|---|---:|---:|---:|---:|---:|---:|---:|
| `11..100_000` | `9588` | `25` | `0` | `31` | `31` | `0` | `0` |
| `11..1_000_000` | `78494` | `25` | `0` | `31` | `31` | `0` | `0` |

The larger integration gate passed:

```text
true_boundary_rejected_count: 0
higher_divisor_locked_absorption_wrong_count: 0
unique_resolved_survivor_count: 25
```

Shifted-window integration:

| Surface | Rows | Unique resolved survivors | True rejected | Applied | Correct | Wrong | False absorber |
|---|---:|---:|---:|---:|---:|---:|---:|
| `100_000..200_000` | `8392` | `0` | `0` | `0` | `0` | `0` | `0` |
| `1_000_000..1_100_000` | `7216` | `0` | `0` | `0` | `0` | `0` | `0` |

The shifted windows passed the safety gate but abstained. They produced no
wrong absorption and no true-next-prime rejection, but also no applications and no
unique resolved survivors.

## Why This Is Not Yet Generator Emission

This result is offline eliminator evidence.

It is not pure generator emission because:

- labels are still used after the fact to audit true and false selections;
- the rule has not been installed into the pure generation path;
- the pure generator still lacks an approved emission contract;
- the candidate has not been proven as a theorem;
- the required pure-rule dependency audit has not yet been completed;
- the shifted-window integration runs abstained.

The current result supports a candidate law, not a generator claim.

## Falsification Conditions

Immediately quarantine this candidate if any future run shows:

```text
higher_divisor_pressure_lock_false_selected > 0
higher_divisor_locked_absorption_wrong_count > 0
true_boundary_rejected_count > 0
```

One wrong case kills generator eligibility.

Also quarantine the candidate if the lock depends on any forbidden mechanism:

- prime markers;
- next-prime lookup;
- primality testing;
- actual future endpoint labels;
- hidden old-walker imports;
- full forbidden divisor ladders.

## Next Gates

Before this can touch the pure generator:

1. Complete a pure-rule dependency audit.
2. Verify the higher-divisor pressure lock can be computed without forbidden
   helpers.
3. Expand integration hardening beyond the current abstaining shifted windows.
4. Preserve abstention as the default behavior when the lock does not fire.
5. Keep pure generation fail-closed unless exactly one endpoint is inferred
   under an approved rule.

Candidate-law language may now be used for this rule. Generator language may
not.
