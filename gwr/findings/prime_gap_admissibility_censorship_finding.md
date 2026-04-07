# Finding: Actual Prime Gaps Use Only A Small Part Of The Divisor-Count Patterns That Look Possible On Paper

This note records one cross-file conclusion from the current repository.

The key point is not only that the main winner claim keeps surviving checked
runs.

The stronger point is this:

divisor counts alone still leave infinitely many unresolved patterns, but the
actual prime gaps checked in this repository show only a much smaller and much
more restricted set of hard cases.

That suggests the missing theorem may need to explain not only which interior
number wins, but which divisor-count patterns can actually occur between
consecutive primes.

## Strongest Supported Claim

The strongest supported reading is:

actual gaps between consecutive primes appear to realize only a small part of
the divisor-count patterns that look possible when we reason on paper from
divisor counts alone.

In ordinary language:

- divisor counts alone leave many unresolved patterns,
- actual prime gaps seem to block most of those patterns from appearing,
- so the remaining burden behind the winner claim is likely a theorem about
  which interior divisor-count patterns real prime gaps can contain.

That is stronger than saying only that no counterexample has been found.

## Facts Already Recorded In The Repository

### 1. Divisor counts alone still leave infinitely many unresolved families

The
[note on the infinite unresolved divisor-count family](./current_spoiler_bound_no_finite_remainder.md)
records an explicit infinite unresolved family:

$$\delta = 2m - 1,\qquad D = 2m,\qquad a = 3 \cdot 2^{m-1},\qquad m \ge 4.$$

So the current divisor-count comparison does not close the problem by itself.

The repo also records a stronger large-prime reduction in the
[note on the large-prime reduction](./large_prime_reducer_findings.md).
That reduction is a real step forward, but it does not change the basic fact
above:

at the level of divisor counts alone, unresolved families remain.

### 2. Actual earlier interior candidates collapse in exact checked gaps

The exact prime-gap files show a very different picture.

The
[note on exact earlier-candidate collapse](./earlier_spoiler_local_dominator_findings.md)
reports:

- `169021` earlier interior candidates on the exact run through `10^6`,
- `3349874` earlier interior candidates on the exact run through `2 × 10^7`,
- `0` unresolved earlier candidates on both exact ranges.

So every actual earlier interior candidate in those checked ranges is already
beaten by some later interior number.

That same note also shows that this becomes easier as divisor count goes up.
On the exact run through `2 × 10^7`:

- divisor counts such as `64`, `72`, and `96` have maximum first-beating
  offset `2`,
- divisor counts `120` and above already collapse to maximum offset `1`,
- the larger offsets stay concentrated in low divisor counts such as `4`, `6`,
  `8`, `12`, and `16`.

So the hard cases are not drifting into a long high-divisor tail.
They are being squeezed into a small low-divisor part of the problem.

### 3. The exact earlier-versus-winner check stays safely away from failure

The
[note on exact earlier-versus-winner margins](./no_early_spoiler_margin_findings.md)
records the exact comparison that matters most for the winner claim:

- `1163198` prime gaps with composite interior,
- `3349874` earlier interior candidates before the true winner,
- `0` earlier interior candidates beating that winner.

The same note records:

- smallest direct score gap
  $L(w) - L(k) \approx 0.9808292530$
  at the gap `(7, 11)`,
- smallest ratio margin about `0.0714285168`
  at the gap `(2486509, 2486513)` with winner divisor count `30`
  and earlier divisor count `32`.

So the exact checked range is not merely free of counterexamples.
Its hardest cases still stay positively separated from failure.

### 4. One normalized ratio stays very small on the exact checked range

The
[note on the normalized failure ratio](./asymptotic_bridge_load_findings.md)
rewrites the remaining comparison problem into one dimensionless ratio:

$$B(k, w) = \frac{\frac{\ln w}{\ln k} - 1}{\frac{\delta}{d_{\min} - 2}}.$$

Failure would require:

$$B(k, w) \ge 1.$$

On the full exact run through `2 × 10^7`, the repository records:

- `3349874` earlier candidates,
- `0` failures,
- largest observed value
  $B_{\max} \approx 0.0566416671$.

That largest value occurs at the tiny gap `(7, 11)`, with earlier candidate
`8` and winner `9`.

So the hardest exact checked case currently uses only about `5.66%` of what
would be needed to fail.

### 5. The hardest checked cases are tiny local patterns, not the largest gaps

The
[note on the tightest exact ratio cases](./no_early_spoiler_ratio_frontier_findings.md)
shows that the tightest ratio cases are led by nearby divisor-count pairs such
as:

- `(30, 32)`,
- `(15, 16)`,
- `(22, 24)`,
- `(18, 20)`.

The
[note on large-gap margins](./large_gap_margin_findings.md)
then shows that the largest actual gaps are not where the exact condition
tightens first.

So the current hardest checked cases are being led by tiny local patterns,
especially gap-`4` and nearby small-gap configurations.

### 6. The later side stays clean far beyond the exact base range

The
[note on later-side checks](./closure_constraint_findings.md)
records zero observed later-side failures on:

- the exact full run to `10^6`,
- deterministic even-band windows at every decade from `10^8` through
  `10^18`.

In the common case where the winner has four divisors, that same note records
positive margin against the next prime-square threat on every tested range.

So the later side does not show a scale-driven collapse on the checked ranges.

## The Contrast That Forces This Reading

Taken one by one, the notes above say:

- divisor counts alone still leave infinite unresolved families,
- actual earlier interior candidates disappear quickly in exact checked gaps,
- exact score margins stay positive,
- the normalized ratio stays tiny,
- the largest gaps are not the hardest checked cases,
- and the later side stays clean through the current high-scale checks.

Taken together, they suggest something sharper:

the hard part of the problem is probably not that actual prime gaps are full of
near-failure patterns that slowly get worse with scale.

The checked files instead support this reading:

many divisor-count patterns remain unresolved on paper, but only a small part
of them seem able to occur inside actual gaps between consecutive primes.

That is the central claim of this note.

## What This Adds Beyond Existing Notes

This note is not just a restatement of one earlier file.

It adds a different synthesis.

The contrast between unresolved paper patterns and the much thinner set of
hard cases inside actual prime gaps is itself informative.

That contrast suggests that the missing mathematical ingredient may be a rule
about which interior divisor-count patterns can actually occur between
consecutive primes.

## Consequences For The Proof Program

If this reading is right, then the main open problem should be posed less as:

"what inequality eventually defeats the infinite tail?"

and more as:

"what local divisor-count patterns can a true gap between consecutive primes
actually contain?"

That changes the research posture in several concrete ways.

### 1. The remaining hard part should be searched as a small-pattern problem

The current hardest checked cases already point toward:

- gap-`4` and gap-`6` configurations,
- nearby low divisor-count pairs,
- cases close to prime squares,
- delayed first appearance of the minimum divisor count.

That is a much more specific target than simply "very large gaps" or "very
large scale."

### 2. Large scale alone is probably the wrong main coordinate

The current large-`p` reduction note in
[the proof note on the universal large-`p` step](../experiments/proof/proof_bridge_universal_lemma.md)
already shows that the large-`p` tail reduces to explicit constants plus a
finite verification threshold.

The present finding helps explain why that shape is plausible:

the exact checked cases do not suggest a broad outward march toward failure.
They suggest a very thin family of local hard cases.

### 3. The key missing theorem may be about what can occur, not only about score comparison

The score law already has a strong ordered backbone in the
[theorem on score order when divisor count does not increase](./lexicographic_raw_z_dominance_theorem.md).

What remains open is not that score comparison is completely mysterious.

What remains open may be that actual prime-gap interiors obey stricter local
rules than divisor-count algebra alone can see.

If so, the deeper theorem would say which divisor-count patterns consecutive
primes are allowed to leave behind before the winner and before the gap ends.

## Testable Predictions

This finding is useful only if it makes risky predictions.

### Prediction 1: the hardest checked cases will stay concentrated in small local patterns

Future exact or deterministic hardest cases should continue to cluster in:

- gap-`4` and gap-`6` configurations,
- cases close to prime squares,
- nearby low divisor-count pairs,
- delayed first appearance of the minimum divisor count.

If generic large gaps with no such local structure begin to dominate the
checked hardest cases, this reading weakens sharply.

### Prediction 2: the normalized ratio should stay far below `1` outside a very thin local family

Even if future scans find new worst cases, the ratio

$$B(k, w)$$

should remain well below `1` except in a very thin family of small local hard
cases.

If broad exact or deterministic runs begin producing many cases with this
ratio close to `1`, then this finding is wrong or incomplete.

### Prediction 3: the infinite unresolved families from divisor counts alone will not show up often as actual gap patterns

The infinite unresolved families from divisor-count algebra should continue to
fail as broad sources of actual prime-gap counterexamples.

If one of those abstract families begins to appear repeatedly as actual
winner-versus-earlier geometry inside checked gaps, this reading is directly
threatened.

### Prediction 4: searches based on local structure should outperform searches based only on scale

Search programs aimed at:

- first-appearance delay,
- closeness to prime squares,
- nearby low divisor-count pairs,
- and tiny-gap patterns,

should find tighter checked cases faster than searches conditioned only on gap
length or ambient scale.

If scale-only searches consistently outperform local-structure searches in
finding the hardest cases, this reading weakens.

## Scope Limits

This note does not claim:

- a proof of the main winner claim for all prime gaps,
- a proof that every unresolved divisor-count family is impossible in actual
  prime gaps,
- a global theorem about prime counts,
- or a proof that the current zero-violation ranges persist universally.

It records a narrower finding:

the current committed files support a specific explanation for why the checked
hard cases behave the way they do.

That explanation is that actual gaps between consecutive primes obey much
stricter local rules than the current divisor-count inequalities alone can
express.

## Safe Summary

The safest strong statement is:

the repository now supports a new proof-facing reading of the winner claim:
the main missing ingredient may be a theorem about which divisor-count patterns
can actually occur inside real gaps between consecutive primes.

If that reading is right, then the deeper theorem behind the current winner
picture is not only about which composite wins. It is also about which gap
interiors are possible at all.
