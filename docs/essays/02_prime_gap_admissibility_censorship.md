# Essay 2: Why Actual Prime Gaps Look Much More Restricted Than Divisor Counts Alone

This essay starts from one simple contrast.

If we look only at divisor counts, the current comparison argument still leaves
infinitely many unresolved patterns.

But if we look at actual gaps between consecutive primes, the checked cases in
this repository look much stricter.

That contrast may be telling us something important.

The missing step may not be only a better inequality.
It may also be a theorem about which divisor-count patterns can actually occur
inside a real prime gap.

## The Basic Contrast

The project now has two kinds of evidence.

The first kind asks what is still unresolved if we reason only from divisor
counts.

The second kind asks what actually happens inside checked gaps between
consecutive primes.

If those two views told the same story, we would expect the unresolved patterns
from divisor-count algebra to show up often in the checked gaps.

That is not what the repository reports.

On paper, many patterns still look possible.
In actual checked gaps, the hard cases look much rarer and much more local.

That is the main point of this essay.

## Divisor Counts Alone Still Leave Infinite Unresolved Families

The
[note on the infinite unresolved divisor-count family](../../gwr/findings/current_spoiler_bound_no_finite_remainder.md)
shows that the current divisor-count comparison does not reduce the problem to
a finite list of leftover cases.

It gives an explicit infinite family:

$$\delta = 2m - 1,\qquad D = 2m,\qquad a = 3 \cdot 2^{m-1},\qquad m \ge 4.$$

So if we work only with divisor counts, unresolved patterns continue forever.

The repo also contains a stronger large-prime reduction in the
[note on the large-prime reduction](../../gwr/findings/large_prime_reducer_findings.md).
That note is a real proof advance.
But it does not erase the basic point made above:

divisor counts alone still leave a genuine infinite remainder.

## Actual Checked Prime Gaps Look Much Stricter

Now compare that abstract picture with what the repository finds in actual
prime gaps.

The
[note on exact earlier-candidate collapse](../../gwr/findings/earlier_spoiler_local_dominator_findings.md)
reports:

- `169021` earlier interior candidates on the exact run through `10^6`,
- `3349874` earlier interior candidates on the exact run through `2 × 10^7`,
- `0` unresolved earlier candidates on both exact runs.

So every actual earlier interior candidate in those checked ranges is already
beaten by some later interior number.

That same note also shows that this gets easier, not harder, as divisor count
goes up.

On the exact run through `2 × 10^7`:

- divisor counts such as `64`, `72`, and `96` have maximum first-beating offset
  `2`,
- divisor counts `120` and above already collapse to maximum offset `1`,
- the larger offsets are concentrated in low divisor counts such as `4`, `6`,
  `8`, `12`, and `16`.

So the hard cases are not spreading outward into a long high-divisor tail.
They are being squeezed into a small low-divisor part of the problem.

## The Exact Earlier-Candidate Check Is Not Barely True. It Has Room To Spare

The
[note on exact earlier-versus-winner margins](../../gwr/findings/no_early_spoiler_margin_findings.md)
and the matching output file
[exact earlier-versus-winner scan through 2 × 10^7](../../output/gwr_proof/no_early_spoiler_margin_scan_2e7.json)
compare every earlier interior candidate with the actual winner on the full
exact range through `2 × 10^7`.

That record reports:

- `1163198` prime gaps with composite interior,
- `3349874` earlier interior candidates before the true winner,
- `0` earlier interior candidates beating that winner.

The hardest cases are still safely on the winning side.

The same note reports:

- smallest direct score gap
  $L(w) - L(k) \approx 0.9808292530$
  at the gap `(7, 11)`,
- smallest ratio margin about `0.0714285168`
  at the gap `(2486509, 2486513)` with winner divisor count `30`
  and earlier divisor count `32`.

So the exact checked range is not only free of counterexamples.
Its hardest cases still stay a positive distance from failure.

## One Normalized Ratio Makes The Same Point

The
[note on the normalized failure ratio](../../gwr/findings/asymptotic_bridge_load_findings.md)
rewrites the remaining comparison problem into one dimensionless ratio:

$$B(k, w) = \frac{\frac{\ln w}{\ln k} - 1}{\frac{\delta}{d_{\min} - 2}}.$$

Failure would require:

$$B(k, w) \ge 1.$$

On the full exact range through `2 × 10^7`, the repository reports:

- `3349874` earlier candidates,
- `0` failures of this ratio test,
- largest observed value
  $B_{\max} \approx 0.0566416671$.

That means the hardest exact case currently uses only about `5.66%` of the
amount needed to fail.

That is a striking result.

If the unresolved divisor-count patterns were appearing often inside real prime
gaps, we would expect this ratio to pile up near `1`, or at least to show many
cases much closer to `1` than `0.0566`.

The checked exact file does not look like that.

## The Hardest Cases Are Small Local Patterns, Not The Largest Gaps

Two more notes sharpen the same point.

The
[note on the tightest exact ratio cases](../../gwr/findings/no_early_spoiler_ratio_frontier_findings.md)
shows that the tightest exact cases are led by nearby divisor-count pairs such
as:

- `(30, 32)`,
- `(15, 16)`,
- `(22, 24)`,
- `(18, 20)`.

The
[note on large-gap margins](../../gwr/findings/large_gap_margin_findings.md)
then shows that the largest actual gaps are not the hardest part of the
problem.

This matters.

Many problems get harder because some scale variable keeps growing and slowly
overwhelms the local mechanism.

That is not how this checked data behave.

The hardest cases are small local patterns, especially gap-`4`, gap-`6`, and
nearby configurations.

That suggests the remaining difficulty is local, not a broad large-scale
collapse.

## The Later Side Also Stays Clean At Large Scale

The
[note on later-side checks](../../gwr/findings/closure_constraint_findings.md)
reports zero observed later-side failures on:

- the exact full run to `10^6`,
- deterministic even-band windows at every decade from `10^8` through `10^18`.

The strongest public output file there is
[later-side checks through `10^18`](../../output/gwr_closure_constraint_even_bands_through_1e18.json).

In the common case where the winner has four divisors, that note reports:

- positive margin against the next prime-square threat on every checked range,
- minimum margin `2` on every listed deterministic range,
- and very large growth in the mean distance to the next prime square.

The
[note on the local bound for the next prime](../../gwr/findings/prime_boundary_placement_finding.md)
pushes that one step further.

On the documented four-divisor ranges:

- the mean distance from the winner to the next prime stays only about `12.07`
  at exact `10^6` and about `20.12` near `10^18`,
- the mean distance from the winner to the next prime square grows from about
  `5869.6` to about `3595291803.7`,
- so the share of the available room that gets used falls from about
  `2.06e-3` to about `5.60e-9`.

So even this later-side condition is not merely positive in the checked runs.
It stays far away from failure.

## What This Contrast Suggests

This is the point where the object of study changes.

A simple first reading of the project would be:

- there is a winner claim,
- there is a hard comparison inequality behind it,
- and the task is to find a stronger inequality.

The contrast described above suggests something deeper.

It suggests:

- divisor counts alone allow many patterns that still look unresolved,
- but actual gaps between consecutive primes seem to allow only a small part of
  that larger paper picture,
- so the missing theorem may need to explain not only who wins, but which
  divisor-count patterns can actually appear inside a real prime gap.

That is the main idea.

Many patterns look possible on paper.
Far fewer seem to survive the extra requirement that they occur between two
actual consecutive primes.

## Why This Changes The Search

This is not just a new way to describe the project.
It changes where effort should go.

If the real problem were a broad large-scale tail, then the obvious strategy
would be:

- go much farther out,
- scan larger and larger ranges,
- and keep waiting for the hardest cases to move outward with scale.

The current repository evidence does not point there first.

It points toward:

- gap-`4` and gap-`6` patterns,
- nearby low divisor-count pairs,
- cases close to prime squares,
- and gaps where the first appearance of the minimum divisor count is delayed.

That is a much narrower search space.

It is also a more hopeful one.

A broad large-scale failure pattern is hard to imagine turning into a sharp
local theorem.

A thin family of small local patterns is exactly where a sharp local theorem
might live.

## Why This Also Fits The Prime-Boundary View

This reading also fits the newer work on where the next prime can occur.

If the main claim were only a statement about which composite wins after the
fact, then it would not naturally tell us much about where the boundary primes
can sit.

But once we read the gap interior as a restricted local pattern, the boundary
statement becomes natural.

The
[note on the local bound for the next prime](../../gwr/findings/prime_boundary_placement_finding.md)
states the sharpest version.

If the main claim holds, then the winning interior number also defines a later
point that the next prime must beat.

In the common case where the winner has four divisors:

$$q \le S_{+}(w).$$

So the same picture has two sides:

- only a small part of the paper possibilities seem to occur inside real prime
  gaps,
- and once the actual interior winner is fixed, the next prime also has a
  local bound.

## What This Essay Does Not Claim

This essay does not claim:

- that the main claim is already proved for all prime gaps,
- that every unresolved divisor-count family is impossible in actual prime
  gaps,
- that finite checked ranges settle the whole problem by themselves,
- or that the current evidence already gives a complete theorem about which
  patterns can occur.

The claim is narrower.

It is that the committed repository evidence supports one clear explanation for
why the checked cases look the way they do.

That explanation is:

actual gaps between consecutive primes appear to obey stricter local rules than
the current divisor-count inequalities alone can express.

That is already a serious research claim.

It is also a testable one.

If future exact or deterministic runs begin to show:

- many cases with the normalized ratio near `1`,
- hardest cases dominated by generic large gaps,
- or repeated appearance of the current unresolved divisor-count families as
  actual gap interiors,

then this reading will weaken sharply.

At the moment, the repository reports the opposite.

## Why I Think This Matters

Many projects find one strong pattern.

This repository may have found something bigger:

the gap between paper possibilities and actual arithmetic behavior may itself
be a mathematical clue.

That changes the central question.

The question may not be only:

- which interior composite wins?

The deeper question may be:

- which divisor-count patterns can real prime gaps contain at all?

If that is the right question, then the project may already be much closer to
its real target than it first appeared.

## Sources

The finding that prompted this essay is recorded in:

- [finding on the gap between paper possibilities and actual prime gaps](../../gwr/findings/prime_gap_admissibility_censorship_finding.md)

The closest supporting notes and output files are:

- [note on the infinite unresolved divisor-count family](../../gwr/findings/current_spoiler_bound_no_finite_remainder.md)
- [note on the large-prime reduction](../../gwr/findings/large_prime_reducer_findings.md)
- [note on exact earlier-candidate collapse](../../gwr/findings/earlier_spoiler_local_dominator_findings.md)
- [note on exact earlier-versus-winner margins](../../gwr/findings/no_early_spoiler_margin_findings.md)
- [note on the tightest exact ratio cases](../../gwr/findings/no_early_spoiler_ratio_frontier_findings.md)
- [note on large-gap margins](../../gwr/findings/large_gap_margin_findings.md)
- [note on the normalized failure ratio](../../gwr/findings/asymptotic_bridge_load_findings.md)
- [note on later-side checks](../../gwr/findings/closure_constraint_findings.md)
- [note on the local bound for the next prime](../../gwr/findings/prime_boundary_placement_finding.md)
- [exact earlier-versus-winner scan through 2 × 10^7](../../output/gwr_proof/no_early_spoiler_margin_scan_2e7.json)
- [normalized-ratio scan through 2 × 10^7](../../output/gwr_proof/asymptotic_bridge_load_scan_2e7.json)
- [exact earlier-candidate scan through 2 × 10^7](../../output/gwr_proof/earlier_spoiler_local_dominator_scan_2e7.json)
- [later-side checks through `10^18`](../../output/gwr_closure_constraint_even_bands_through_1e18.json)
