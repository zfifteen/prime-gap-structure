# Rule X Consistency-Collapse Algorithm

## Executive Summary

The Rule X algorithm is a finite candidate-elimination model for next-prime
next-prime inference from an input prime `p`.

It does not score candidate primes. It does not search until the next prime. It
builds candidate next-prime hypotheses and eliminates the hypotheses whose
proposed intervals contradict available PGS evidence.

On the current high-scale search-interval-reset surface:

```text
decade windows: 10^8 through 10^18
input primes per decade: 256
candidate bound: 1024
input primes tested: 2816
```

the current rule stack produced:

```text
exact next-prime matches: 2816 / 2816
coverage: 100.000000%
unresolved input primes: 0
false outputs: 0
candidate-bound misses: 0
```

The result is significant because the algorithm now distinguishes current-search interval
endpoint evidence from later-search interval tail evidence. Once the first resolved
remaining candidate appears, later unresolved candidates are assigned to later search intervals
and no longer block output for the original input prime.

The earlier semiprime-shadow landmark hold remains necessary. It prevents
two-factor witness-horizon landmarks from being promoted into false endpoints.
The search-interval-reset rule then closes the remaining coverage gap by classifying
later unresolved tails as post-endpoint search interval material.

## Core Object

For an input prime `p`, define a finite set of candidate right
endpoints:

$$C(p, H) = \{p + h : 1 \leq h \leq H,\ p + h \in W_{30}\}.$$

Here `W_30` is the set of integers whose residue modulo `30` is wheel-open.
The experiment uses `H = 128` and wheel-open residues modulo `30`:

```text
1, 7, 11, 13, 17, 19, 23, 29
```

Each candidate `c = p + h` defines a proposed interval:

$$I(p, c) = \{p+1, p+2, \dots, c-1\}.$$

The algorithm asks one question:

```text
If c were the next prime endpoint, can the proposed interval remain consistent
with the current PGS evidence?
```

The endpoint is inferred by consistency collapse followed by search-interval reset:

```text
all impossible proposed intervals are removed;
the first resolved candidate appears;
that candidate closes the current search interval;
later unresolved candidates are assigned to later search intervals;
the first resolved candidate is output as q_hat.
```

## Rule Vocabulary

### Candidate Endpoint Hypothesis

A candidate next-prime hypothesis is one proposed statement:

```text
q_hat = p + h
```

It is not assumed prime. It is a node in the algorithm.

### Positive Composite Witness

A positive composite witness is a deterministic factor `r <= B` such that:

$$r \mid n.$$

If a candidate next prime has a positive composite witness, that candidate is
rejected.

If an interior wheel-open position has no positive witness, that interior
position remains unresolved. Absence of a witness is not primality evidence.

### Resolved Remaining Candidate

A candidate is a resolved candidate when:

1. the candidate itself has no positive composite witness;
2. all wheel-open interior positions in its proposed interval are closed by
   positive composite evidence;
3. the proposed interval contains a integer available to the rule stack;
4. no active rule rejects the candidate.

Resolved remaining candidate does not mean "proved prime" in the mathematical sense. It
means "not eliminated by the label-free finite rule stack."

### Unresolved Hold

An unresolved hold is an abstention state before search-interval reset. A candidate
with unresolved interior positions remains active until a resolved candidate
closes the current search interval.

Before search-interval reset, unresolved alternatives block output. After the first
resolved candidate, later unresolved alternatives belong to a later search interval and
do not compete with the current input prime's endpoint.

### Semiprime-Shadow Landmark

A semiprime-shadow landmark is a wheel-open candidate or interior position that
has no positive witness within the current witness horizon but is large enough
to hide a two-factor composite whose factors both exceed that horizon.

Let `B` be the witness bound and let `s` be the first prime greater than `B`.
The first possible two-factor composite with both factors beyond `B` is:

$$s^2.$$

Therefore, a no-witness candidate `n` satisfying

$$n \geq s^2$$

is held open as a semiprime-shadow landmark.

This is not a rejection. The semiprime-shadow landmark is load-bearing PGS
evidence. The model does not promote it to a resolved next prime remaining candidate until
it is cleared by additional evidence.

### Integer Lock

Each proposed interval has a GWR-style integer: the leftmost known composite in
the proposed interior with minimum divisor count among known composites.

The integer is not locked merely because it appears. The algorithm locks a integer
only after a resolved candidate exists.

In logic-puzzle language:

```text
the search-interval account cannot become binding until the proposed endpoint has earned
resolved-candidate status.
```

### Lower-Divisor Threat

After a integer `w` is locked, the first later known composite `t` with lower
divisor count is a lower-divisor threat:

$$t > w,\ d(t) < d(w).$$

Under GWR/NLSC, a locked integer cannot be followed inside the same prime gap
by a strictly simpler composite. Therefore, once the integer is legitimately
locked, the first certified lower-divisor threat becomes a right-endpoint
ceiling.

The algorithm rejects later candidate next primes that extend beyond this threat.

### Search-Interval Reset

A search-interval reset occurs at the first resolved candidate `r` after input prime `p`.

The observable state is:

```text
p ... r ... u
```

where `r` is the first resolved candidate and `u` is a later unresolved
candidate.

The reset rule is:

```text
once r is resolved, r closes the p search interval;
later unresolved candidates u are post-reset search-interval material;
u is not a competing endpoint for input prime p.
```

This rule does not promote arbitrary candidates. It activates only after the
existing Rule X stack has produced a resolved candidate. The reset classifies
the later tail. It does not create the first remaining candidate.

## Rule Stack

The current Rule X search-interval-reset stack is:

```text
1. Build wheel-open candidate next-prime hypotheses.
2. Reject candidate composites with positive composite witnesses.
3. Hold proposed intervals with unresolved wheel-open interiors.
4. Hold semiprime-shadow landmarks open instead of treating them as resolved q.
5. Lock the selected integer only after a resolved candidate exists.
6. Find the first certified lower-divisor threat after the locked selected integer.
7. Reject candidate next primes beyond that threat.
8. Identify the first resolved candidate r.
9. Reset the search interval at r.
10. Exclude later unresolved candidates as post-reset search-interval material.
11. Output r as q_hat.
12. Audit classically after generation.
```

The decisive safety rule is step `4`. Before this rule, semiprime-shadow
landmarks were incorrectly promoted to resolved next prime remaining candidates. That caused
premature integer locks and true-next-prime rejection. After the hold-open rule,
the tested `11..100000` surface has zero true-next-prime rejections for witness
bounds `97` and `127`.

The decisive coverage rule is step `9`. Before this rule, the algorithm found the
true next prime as the first resolved candidate but refused to output when later
unresolved tail candidates remained. After search-interval reset, those tail candidates
are assigned to later search intervals and no longer block the current endpoint.

## Why GWR/NLSC Alone Did Not Collapse Candidates

GWR and NLSC are interior consistency laws. If each proposed interval is allowed
to choose its own integer from scratch, every proposed interval can often remain
internally coherent.

The initial structural-only run showed:

```text
structural_rejection_count = 0
structural_unique_anchor_count = 0
```

This does not weaken GWR/NLSC. It identifies the missing operational condition:

```text
candidate extensions must not be allowed to freely rewrite the selected integer story
after a selected integer has legitimately locked.
```

The algorithm supplies that missing operational condition.

## Why The Naive Integer Lock Failed

The naive rule was:

```text
lock the first selected integer immediately
```

On `11..100000`, `candidate_bound = 128`, this was unsafe:

```text
rule_x_rejection_count = 297753
rule_x_unique_anchor_count = 4162
rule_x_true_boundary_rejected_count = 7297
```

The rule locked too early. Many input primes begin with a small composite near
`p + 1`, but the true gap later introduces the actual integer before the prime
endpoint. Locking the first integer converts real reset structure into a false
contradiction.

## Why The Semiprime-Shadow Landmark Hold Is Necessary

The failed label-free runs revealed a single obstruction family. At
`witness_bound = 97`, the true-next-prime rejections were caused by candidates
with no witness at or below `97` that were actually:

```text
492 distinct semiprimes
15 prime squares
```

Examples:

```text
10609 = 103^2
11413 = 101 * 113
11449 = 107^2
11639 = 103 * 113
13231 = 101 * 131
```

These are semiprime-shadow landmarks. They mark the two-factor layer just
beyond the current witness horizon. The error was not their existence. The
error was treating them as resolved prime-endpoint candidates.

The hold-open rule fixes this by preserving the landmark state:

```text
no witness <= B and n >= next_prime(B)^2
=> SEMIPRIME_SHADOW_LANDMARK_HOLD
```

The candidate remains active but unresolved. It cannot lock the integer and it
cannot be outputted.

## Measured Surface

### Search Interval-Reset Decade Ladder

The search-interval-reset rule was rerun on the same high-scale decade ladder used for
the previous Rule X and classical comparisons:

```text
decades: 10^8 through 10^18
input primes per decade: 256
candidate bound: 1024
input primes tested: 2816
```

The aggregate result:

```text
exact matches: 2816
coverage: 100.000000%
unresolved input primes: 0
false outputs: 0
candidate-bound misses: 0
tail cases converted by reset: 2303
tail candidates excluded by reset: 77457
total runtime: 36.951566 seconds
```

Per-decade result:

| Decade | Input primes | Exact matches | Unresolved | False outputs | Bound misses |
|---:|---:|---:|---:|---:|---:|
| `10^8` | `256` | `256` | `0` | `0` | `0` |
| `10^9` | `256` | `256` | `0` | `0` | `0` |
| `10^10` | `256` | `256` | `0` | `0` | `0` |
| `10^11` | `256` | `256` | `0` | `0` | `0` |
| `10^12` | `256` | `256` | `0` | `0` | `0` |
| `10^13` | `256` | `256` | `0` | `0` | `0` |
| `10^14` | `256` | `256` | `0` | `0` | `0` |
| `10^15` | `256` | `256` | `0` | `0` | `0` |
| `10^16` | `256` | `256` | `0` | `0` | `0` |
| `10^17` | `256` | `256` | `0` | `0` | `0` |
| `10^18` | `256` | `256` | `0` | `0` | `0` |

This is a decade-window result, not exhaustive coverage of every prime through
`10^18`.

### Tested Runs

| Run | Input primes | Candidate bound | Witness bound | Unique matches | True rejected |
|---|---:|---:|---:|---:|---:|
| label-free lock before landmark hold | `11..100000` | `128` | `97` | `2107` | `507` |
| label-free lock before landmark hold | `11..100000` | `128` | `127` | `2144` | `331` |
| label-free lock before landmark hold | `11..100000` | `128` | `317` | `2231` | `0` |
| Rule X with semiprime-shadow landmark hold | `11..100000` | `128` | `97` | `311` | `0` |
| Rule X with semiprime-shadow landmark hold | `11..100000` | `128` | `127` | `488` | `0` |

The `317` run is a finite full-witness control for this surface because
`317 > sqrt(100128)`. It shows the selected-integer-lock pressure rule is safe when
false endpoint promotion is removed by complete small-scale witness coverage.

The semiprime-shadow landmark hold gives the same zero true-rejection safety
without full witness coverage, at the cost of holding more proposed intervals
unresolved.

### Current Best Guarded Runs

At `witness_bound = 97`:

```text
label_lock_rejection_count = 189148
label_lock_unique_resolved_anchor_count = 311
label_lock_unique_resolved_match_count = 311
label_lock_true_boundary_rejected_count = 0
```

At `witness_bound = 127`:

```text
label_lock_rejection_count = 201033
label_lock_unique_resolved_anchor_count = 488
label_lock_unique_resolved_match_count = 488
label_lock_true_boundary_rejected_count = 0
```

## Output Contract

The search-interval-reset algorithm may output when all of these hold:

```text
first_resolved_survivor exists
semiprime-shadow landmarks before that candidate are not promoted
positive composite witnesses reject closed candidate next primes
selected-integer lock and lower-divisor threat rules do not reject the candidate
true-next-prime labels have not been consulted
```

Later unresolved candidates do not block output after search-interval reset:

```text
p ... first_resolved_survivor ... later_unresolved_tail
      ^ output this endpoint       ^ classify as later search-interval material
```

The outputted experimental record should remain minimal if promoted into a
generator-style path:

```json
{"p": 11, "q": 13}
```

All rule status, integer lock, landmark, threat, and audit fields belong in
sidecar records.

## Audit Endpoint

Classical labels are downstream audit only. The rule implementation must not use:

- `nextprime`;
- `isprime`;
- Miller-Rabin;
- prime-marker masking;
- actual gap width;
- scan-to-first-prime behavior.

The current experiment script includes exact labels for measurement and
development comparison, but the Rule X decision layer is the label-free
candidate-elimination path described above.

## Relation To Existing Artifacts

This artifact supersedes the loose "Rule X" brainstorming label with a precise
candidate-elimination and search-interval-reset rule stack.

It is related to these earlier lines of work:

- `positive_composite_witness_rejection`;
- selected-integer-locked pressure ceilings;
- candidate-constraint graph solving;
- semiprime-shadow recovery;
- unresolved candidate holds.

The first new contribution is the semiprime-shadow landmark hold before integer
lock. It prevents unresolved two-factor landmarks from being promoted to
endpoint candidates.

The second new contribution is search-interval reset at the first resolved candidate.
It converts the later unresolved tail from apparent endpoint competition into
post-endpoint search interval structure.

## Current Status

Rule X with semiprime-shadow landmark hold is a safe finite inference algorithm on
the documented `11..100000`, `candidate_bound = 128` surface for
`witness_bound = 97` and `127`:

```text
true_boundary_rejected_count = 0
```

Before search-interval reset, it did not resolve every input prime:

```text
witness_bound = 97:  311 / 9588 exact unique matches
witness_bound = 127: 488 / 9588 exact unique matches
```

Rule X with search-interval reset resolved the full decade-window ladder:

```text
10^8 through 10^18
2816 / 2816 exact matches
0 unresolved
0 false outputs
0 candidate-bound misses
```

The search-interval-reset rule is now the production selection rule. The production generator
uses exact divisor-count GWR/NLSC search-interval-reset state instead of the earlier
first-uneliminated-candidate shortcut.

Current production generator check:

```text
surface: 11..100000
candidate_bound: 128
input primes tested: 9588
PGS outputs: 9588
failed outputs: 0
```

High-scale production check:

```text
surface: 256 consecutive input primes per decade, 10^8 through 10^18
candidate_bound: 1024
input primes tested: 2816
PGS outputs: 2816
failed outputs: 0
```

The current `v1.1` production generator removes the displaced fallback and
trial-division paths entirely. The generator is PGS-only: unresolved selection rule
states raise explicitly instead of invoking another prime-search method.

## Artifact Links

- Experiment script:
  [../../../experiments/rule_x_logic_engine/run_logic_model.py](../../../experiments/rule_x_logic_engine/run_logic_engine.py)
- Guarded `witness_bound = 97` summary:
  [../../../experiments/rule_x_logic_engine/results_11_100000_b128_label_w97_shadow_guard/summary.json](../../../experiments/rule_x_logic_engine/results_11_100000_b128_label_w97_shadow_guard/summary.json)
- Guarded `witness_bound = 127` summary:
  [../../../experiments/rule_x_logic_engine/results_11_100000_b128_label_w127_shadow_guard/summary.json](../../../experiments/rule_x_logic_engine/results_11_100000_b128_label_w127_shadow_guard/summary.json)
- Guarded findings:
  [../../../experiments/rule_x_logic_engine/results_11_100000_b128_label_w127_shadow_guard/findings.md](../../../experiments/rule_x_logic_engine/results_11_100000_b128_label_w127_shadow_guard/findings.md)
- Search-interval-reset probe script:
  [../../../experiments/rule_x_logic_engine/run_chamber_reset_probe.py](../../../experiments/rule_x_logic_engine/run_chamber_reset_probe.py)
- Search-interval-reset decade ladder summary:
  [../../../experiments/rule_x_logic_engine/chamber_reset_decade_ladder_1e8_1e18_a256_b1024/summary.json](../../../experiments/rule_x_logic_engine/chamber_reset_decade_ladder_1e8_1e18_a256_b1024/summary.json)
- Search-interval-reset probe report:
  [../../../experiments/rule_x_logic_engine/chamber_reset_probe_1e8_1e18_a256_b1024/report.md](../../../experiments/rule_x_logic_engine/chamber_reset_probe_1e8_1e18_a256_b1024/report.md)
