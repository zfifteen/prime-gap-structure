# Next-Prime Law 005B Failure Autopsy: Anchor 3137

## Status

Next-Prime Law 005B is quarantined as an absorption rule.

The failure is reproduced at anchor $p = 3137$. The previous-to-current carrier shift lock authorizes a false resolved survivor at offset 12, and that false absorber removes the audited true next prime at offset 26.

Pure generator emission remains forbidden.

## Observed Failure

Before 005B absorption, the strongest safe eliminator has:

- anchor: 3137
- previous anchor: 3121
- actual next prime offset: 26
- actual next prime integer: 3163
- resolved survivor offsets: 2, 12
- unresolved candidate offsets: 26, 30, 32, 44, 50, 54

After 005B-only absorption:

- false absorber offset: 12
- false absorber integer: 3149
- absorbed offsets: 26, 30, 32, 44, 50, 54
- true next prime status: rejected

The hard gate fails because the true next prime candidate at offset 26 is removed.

## Why 005B Fired

The previous chamber is $3121 \to 3137$, with gap width 16.

Its first legal carrier is:

- offset: 4
- integer: 3125
- divisor class: 6
- family: known_basis_prime_power

For the false absorber candidate $3137 + 12 = 3149$, the current carrier is:

- offset: 2
- integer: 3139
- divisor class: 4
- family: known_basis_semiprime

The 005B predicate sees a previous-to-current carrier shift:

`previous=4,6,known_basis_prime_power|current=2,4,known_basis_semiprime`

That is enough for the quarantined integration rule to absorb later unresolved candidates.

## What Distinguishes Offset 12 From Offset 26

Offset 12 is not a lawful endpoint on the audited label surface because:

- $3149 = 47 \cdot 67$
- the current extended witness bound is 97
- therefore offset 12 has a positive composite witness under the same witness basis used for single-hole closure

Offset 26 has no positive witness under the same bound:

- $3163$ has no extended positive witness through 97 in this probe
- the audited label says the next prime is offset 26

The false absorber also depends on single-hole positive witness closure:

- offset 12 became resolved by closing interior offset 2
- the closure witness was factor 43

The true next prime candidate at offset 26 remained unresolved before absorption because its interior had two unresolved wheel-open offsets:

- 2
- 12

Those offsets are exactly the composite structure that the one-hole closure rule cannot complete.

## What The Hardening Probe Missed

The hardening probe only evaluated the previous-to-current carrier shift lock inside rows where the audited true next prime was already a resolved survivor before absorption.

At anchor 3137:

- previous row available: true
- previous chamber signal present: true
- later unresolved alternatives after the true next prime: true
- higher-divisor pressure lock absent at the true next prime: true
- actual next prime resolved before absorption: false

So this anchor was outside the hardening population. The hardening result was zero-wrong as a selector in its target population, but direct integration broadened the operational domain and allowed a false resolved survivor to absorb an unresolved true next prime.

## Quarantine Conditions

Two label-free conditions would make 005B abstain at anchor 3137:

1. Abstain when the proposed absorber endpoint has a positive composite witness under the current witness bound.
2. Abstain when the proposed absorber depends on single-hole positive witness closure.

Both are structural and label-free at this anchor. Neither is approved as a patch. Each must be tested broadly before 005B can return as an integration candidate.

## Decision

005B remains useful as forensic evidence that previous-chamber memory matters. It is not sufficient to authorize absorption.

The live status is:

- 005A higher-divisor pressure lock: preserved as narrow candidate-grade
- 005B previous-to-current carrier shift lock: quarantined as absorption logic
- combined 005A/005B modes: rejected
- pure generation: fail-closed
