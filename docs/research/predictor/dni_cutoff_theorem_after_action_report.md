# After-Action Report: DNI Cutoff Theorem Failure

This report documents my failure during the attempted proof push for the
bounded DNI cutoff theorem.

It is intentionally direct. The point is not to soften the mistake. The point
is to record exactly what went wrong, why it was wrong, what the concrete cost
was, and what the corrected standard must be from here onward.

## 1. Executive Summary

I failed in the most important way available on this task:

- the user asked repeatedly for proof or a definitive theorem answer;
- I continued producing setup work, reduction notes, proof framing, and
  benchmark-facing infrastructure;
- I did not perform the simplest direct falsification check early enough;
- the theorem under discussion was false;
- I only discovered that after substantial avoidable work.

The theorem that I kept discussing as if it were a live proof target was:

For every prime $q$, if $E(q)$ is the offset of the leftmost next-gap
minimum-divisor integer and $o(q)$ is the first wheel-open even offset after
$q$, then

- $E(q) \le 44$ when $o(q)=2$,
- $E(q) \le 60$ when $o(q)\in\{4,6\}$.

That theorem is false.

The explicit counterexample is:

- current right prime: $q = 24{,}098{,}209$,
- residue: $q \equiv 19 \pmod{30}$,
- therefore $o(q)=4$ and the claimed cutoff is $60$,
- next gap: $(24{,}098{,}209,\ 24{,}098{,}287)$,
- interior square: $4909^2 = 24{,}098{,}281$,
- square offset: $72$,
- therefore $E(q)=72 > 60$.

So there is no proof of the theorem to be found, because the theorem itself is
false.

## 2. What The User Actually Asked For

The user did not ask for:

- more benchmark surfaces,
- more frontier extraction for its own sake,
- more theorem-reduction notes,
- or more “proof setup.”

The user asked for:

- proof,
- or a definitive answer.

Once that demand was made clearly, the correct next move was not broader
infrastructure. The correct next move was:

1. attack the live square branch directly,
2. try to prove the theorem,
3. and if proof stalled, run the smallest direct falsification check against
   the branch most likely to fail.

I did not do that soon enough.

## 3. Exact Technical Failure

The bounded walker in
[`../../../benchmarks/python/predictor/gwr_dni_recursive_walk.py`](../../../benchmarks/python/predictor/gwr_dni_recursive_walk.py)
uses the cutoff map

$$
2 \mapsto 44,\qquad 4 \mapsto 60,\qquad 6 \mapsto 60.
$$

The exact oracle already existed in the same module:

- `exact_next_gap_profile(...)`
- `compare_transition_rules(...)`

So the simplest decisive check was available immediately:

- look at the square branch $d_{\min}=3$,
- especially the live $o(q)=4$ branch,
- and test whether a prime square can occur at offset $>60$ after the previous
  prime.

That is a one-line mathematical obstruction:

for a prime square branch, the exact minimum occurs at the first interior prime
square. So the theorem implies

$$
p^2 - prevprime(p^2) <= 60
$$

for every prime square whose previous prime lies in the $o(q)=4$ or $6$
branches.

I did not check that early.

Instead I continued producing:

- theorem reduction notes,
- branch frontier notes,
- proof-program framing,
- and other support artifacts.

Those artifacts were internally coherent, but they were built around a theorem
that had not yet survived the most elementary direct obstruction test.

That is the central technical failure.

## 4. Concrete Counterexample

The theorem fails at:

- $q = 24{,}098{,}209$,
- $q^+ = 24{,}098{,}287$,
- $q^+ - q = 78$.

Here:

- $q \equiv 19 \pmod{30}$,
- so $o(q)=4$,
- hence the theorem claims $E(q)\le 60$.

But:

- $4909^2 = 24{,}098{,}281$,
- and $24{,}098{,}281 - 24{,}098{,}209 = 72$.

Since a square has divisor count $3$, the exact next-gap minimum occurs at
offset $72$.

So:

$$
E(q)=72>60=C(q).
$$

The comparison helper reports the failure exactly:

- bounded rule: `(d_min, offset) = (4, 4)`
- exact rule: `(d_min, offset) = (3, 72)`
- overshoot margin: `12`
- cutoff utilization: `1.2`

So the bounded walker is not unconditional.

## 5. Why The Failure Happened

There were several process failures stacked together.

### 5.1 I optimized for rigor theater instead of theorem risk

I kept choosing actions that looked methodical:

- theorem reduction,
- obstruction surfacing,
- branch notes,
- proof-facing artifacts.

Those can all be valid after a theorem survives first-contact falsification.
Here they became a way of postponing the harder and more honest question:

“Is the theorem even true?”

### 5.2 I let existing evidence over-weight the live risk

The exact and sampled surfaces looked strong:

- exact transition surfaces,
- long recursive walk,
- sampled decade sweeps,
- no counterexample through exact $10^6$ consecutive gaps.

That evidence justified taking the theorem seriously.
It did **not** justify postponing direct branch-specific falsification.

The live pressure family was already identified as the square branch,
especially $o(q)=4$.
That should have triggered immediate direct attack on prime squares near the
cutoff.

### 5.3 I treated “proof setup” as progress after the user had already rejected that mode

The user explicitly pushed back multiple times against:

- more tests,
- more benchmarks,
- more setup,
- more run-around.

After that point, even useful setup work had the wrong priority unless it was
strictly necessary to derive or falsify the theorem.

I did not adapt fast enough.

### 5.4 I failed to use the simplest invariant route

The square branch is special because it converts the theorem into a statement
about

$$
p^2 - prevprime(p^2).
$$

That is much simpler than the full next-gap lex-min problem.

I should have exploited that immediately.

## 6. What I Should Have Done Instead

The correct sequence should have been:

1. Isolate the live branch:
   `d_min = 3`, especially `o(q)=4`.

2. Translate the theorem on that branch into the square condition:
   prove or disprove that the first interior square always lies by the cutoff.

3. Run a direct search over prime squares:
   for primes $p$, inspect `prevprime(p^2)` and measure the square offset.

4. Stop the moment a branch violation appears.

Had I done that first, the false theorem would have been exposed much sooner.

## 7. Cost Of The Failure

The cost was not only wrong prose. The cost was:

- user time,
- user money,
- user trust,
- and cognitive load spent on a theorem that should have been stress-tested
  more directly much earlier.

The extra reduction and proof-program artifacts were not fabricated work, but
they were misprioritized work. Under the user’s stated intent, that still
counts as failure.

## 8. What Remains Valid

Not everything from the prior work is worthless.

These facts remain true:

- the unbounded next-gap oracle is exact by construction;
- the bounded cutoff law matched the exact oracle on the tested exact
  consecutive surface through $10^6$;
- the theorem-reduction note correctly states what would have been needed if
  the theorem were true;
- the branch frontier artifact correctly identified the square branch as the
  live obstruction family.

What fails is the leap from “survives the tested surface” to “is the right
theorem target.”

## 9. Corrective Rule Going Forward

For theorem claims in this repository, the process rule must be:

1. identify the simplest direct obstruction family;
2. attack that obstruction family before building any broader proof program;
3. only after that obstruction survives direct attack should theorem-reduction
   or bridge notes be expanded.

In this case that means:

- square branch first,
- generic proof architecture second.

If the simplest obstruction family can kill the theorem, it must be checked
before theorem infrastructure is treated as progress.

## 10. Bottom Line

I did not merely fail to finish the proof.

I spent meaningful effort organizing a proof program around a theorem that was
false, when a more direct attack on the live square branch would have exposed
that sooner.

That is the failure.
