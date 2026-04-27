# No-Later-Simpler-Composite As A Direct Prime-Gap Theorem

The strongest supported claim at present is this:

The No-Later-Simpler-Composite condition has zero observed violations on the
repository's deterministic validation ladder through $10^{18}$, but its status
as a theorem independent of `GWR` is still open.

That is the exact independence question:

Can the right-flank closure law be proved directly as a prime-gap theorem,
without first proving the full maximizer rule?

## 1. Exact Statement

Let $(p, q)$ be a prime gap and let

$$w = \arg\max_{p < n < q} L(n)$$

be the implemented raw-$Z$ log-score maximizer on the interior composites, where

$$L(n) = \left(1 - \frac{d(n)}{2}\right)\ln(n).$$

Define the later simpler threat horizon by

$$T_{<}(w) = \min \{n > w : d(n) < d(w)\}.$$

The direct theorem candidate is:

$$q \le T_{<}(w).$$

In ordinary language:

once the score maximizer appears, the next prime closes the gap before any later
strictly simpler composite can appear.

## 2. What Is Already Closed

On the current repo proof surface, this statement is already an exact
corollary of `GWR`.

If `GWR` holds on the gap, then the selected integer is the leftmost integer of the
minimal divisor class present in the gap. A later interior composite with
strictly smaller divisor count would contradict that selected integer description
immediately.

So the logical status is:

- proved as a consequence of `GWR`,
- empirically validated as a standalone law on the documented tested surface,
- not yet proved as an independent theorem.

References:

- [../../../gwr/findings/claim_hierarchy.md](../../../gwr/findings/claim_hierarchy.md)
- [../../../gwr/findings/closure_constraint_findings.md](../../../gwr/findings/closure_constraint_findings.md)
- [../../../gwr/archive/standalone-candidates/no_later_simpler_composite_theorem.md](../../../gwr/archive/standalone-candidates/no_later_simpler_composite_theorem.md)

## 3. Why Independence Is Not Automatic

The direct theorem is weaker than full `GWR`, but it does not already follow
from the left-to-right divisor ordering theorem alone.

The proved lexicographic raw-$Z$ dominance law controls comparisons of the
form

$$a < b \quad \text{and} \quad d(a) \le d(b).$$

That settles the case where an earlier composite is at least as simple as a
later one. The direct `NLSC` theorem asks for the opposite threat geometry:

- the threatening composite is later than $w$,
- and it is strictly simpler than $w$.

That is exactly the regime not discharged by the earlier-side dominance law.

So the independence problem is real. It is not just a restatement of the
already-closed left-flank theorem.

## 4. The Right Object

The direct theorem should be read as a prime-placement law, not as a selected integer
ranking law.

The quantity that matters is the closure margin

$$M_{\mathrm{close}}(p, q, w) = T_{<}(w) - q.$$

Positive margin means the gap closed before the first later simpler threat
arrived.

This is the direct invariant for the independent theorem program. The target is
not to recover the whole interior ordering of the gap. The target is only to
show that prime closure occurs before the first later strictly simpler divisor
class can enter.

## 5. Dominant Reduction

On the measured surface, the dominant selected divisor-count class is $d(w)=4$.

In that regime, the next strictly smaller divisor class is $d=3$, and among
composites that means prime squares exactly. So the threat horizon becomes

$$T_{<}(w) = S_{+}(w),$$

where $S_{+}(w)$ is the next prime square after $w$.

Then the direct theorem specializes to

$$q \le S_{+}(w).$$

This is the cleanest first target because it converts the abstract closure
question into a literal race between:

- prime-gap termination at $q$,
- and the next prime-square arrival after $w$.

That is also the regime that carries most of the recursive walk surface.

## 6. What A Direct Proof Would Need

A true independent proof has to establish right-flank closure without using the
full statement that $w$ is the leftmost minimum-divisor integer of the gap.

The narrow program is:

1. Fix the score maximizer $w$ directly from the implemented score.
2. Control the first later lower-divisor arrival $T_{<}(w)$.
3. Show that the prime endpoint $q$ must occur before that threat horizon.

For the dominant $d=4$ branch, step 2 is explicit because the threat is the
next prime square. So the first serious direct theorem target is:

$$q \le S_{+}(w) \quad \text{for every gap whose score maximizer has } d(w)=4.$$

If that branch closes independently, the remaining work becomes a sparse
low-class residual problem rather than the whole theorem at once.

## 7. What Would Count As Closure

The independence question is answered only by one of these outcomes:

1. a direct proof of $q \le T_{<}(w)$ without routing through `GWR`;
2. a direct disproof by explicit counterexample;
3. a reduction that shows the direct theorem is equivalent to some narrower
   unresolved branch such as the dominant square-threat case.

At present, the repo has strong validation and a clean theorem candidate, but
not yet item `1`, `2`, or a finished version of `3`.

## 8. Bottom Line

`NLSC` is currently strongest as a right-flank closure law with theorem-sized
content of its own.

It already holds exactly as a corollary of `GWR`. What remains open is whether
prime gaps force that same closure law directly, without first proving the full
interior maximizer theorem.

That is the clean hierarchical gap still left in the current prime-gap
structure program.
