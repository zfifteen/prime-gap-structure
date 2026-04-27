# Prime-Endpoint Placement Finding

This note records a stronger reading of what `Gap Winner Rule` (`GWR`) says
about prime gaps.

The usual surface statement is:

- which interior composite wins the implemented raw-`Z` score.

That statement is correct, but it is not the whole structural content.

If `GWR` holds on a prime gap, then the maximizer rule is also a local constraint
on where the consecutive primes at the endpoints are allowed to sit.

In the dominant `d=4` regime, that endpoint reading becomes especially
concrete:

- the selected integer starts a square-phase clock,
- and the next prime must arrive before the next prime square after the
  selected integer.

So the right endpoint prime is not free to drift arbitrarily once the selected integer is
fixed. It is bounded above by a later low-divisor threat horizon determined by
the composite interior itself.

## Strongest Supported Claim

The strongest supported claim is:

`GWR`, as a proved prime-selected interior integer law on the current proof surface, is not
only a statement about which
composite wins inside a gap. It is also a local endpoint-placement constraint
on where the consecutive primes bounding that gap are allowed to occur.

The dominant `d=4` specialization sharpens that into a concrete prime-placement
bound:

$$q \le S_{+}(w),$$

where:

- $w$ is the implemented score maximizer,
- $q$ is the right endpoint prime of the gap,
- $S_{+}(w)$ is the next prime square after $w$.

So the dominant interior selected integer acts as a clock whose next `d=3` tick gives an
upper bound on where the following prime can land.

This is a stronger reading than "the selected integer is the first low-divisor carrier."
It says the composite interior imposes an admissible stopping region for the
next prime.

## The Exact Conditional Structure

The note
[`prime_gap_exclusion_consequences.md`](./prime_gap_exclusion_consequences.md)
already records the exact divisor-profile consequence of `GWR`.

If the selected integer is $m = p + r$ with divisor count $\delta = d(m)$, then the
interior must have the form

$$>\delta,\ >\delta,\ \ldots,\ >\delta,\ \delta,\ \ge \delta,\ \ge \delta,\ \ldots,\ \ge \delta.$$

In words:

- every earlier interior integer must avoid divisor classes $\le \delta$,
- every later interior integer must avoid divisor classes $< \delta$ until the
  right endpoint prime arrives.

That means the gap endpoints are not free to enclose an arbitrary interior.
The consecutive primes must bound an interval whose interior divisor profile is
compatible with the maximizer rule.

This is already a genuine statement about prime placement, because prime gaps
are defined by consecutive primes.

## Why This Is More Than A Composite-Selected integer Note

The usual phrasing starts from the composites:

- given the interior of the gap, which composite wins?

The endpoint-placement reading starts from the same law and turns it around:

- given that the selected integer sits at offset $r$ with divisor class $\delta$, which
  interior profiles are consecutive primes allowed to bound at all?

That inversion matters.

The selected integer does not merely summarize the interior after the fact. If `GWR`
holds, the selected integer also certifies a set of forbidden lower-divisor events that
the left prefix and right suffix were not allowed to realize before the gap
opened and before it closed.

So the gap endpoints are constrained by the admissibility of the interior
divisor profile, not only by abstract gap length.

## The Dominant `d=4` Square-Phase Clock

The note
[`dominant_d4_arrival_reduction_findings.md`](./dominant_d4_arrival_reduction_findings.md)
records the dominant reduction:

- if the selected integer has `d(w)=4`, then the gap contains no interior prime square,
- and the selected integer is the first interior carrier with `d(n)=4`.

The note
[`closure_constraint_findings.md`](./closure_constraint_findings.md)
then records the measured closure consequence:

$$q \le T_{<}(w).$$

For `d(w)=4`, the first strictly simpler later threat is exactly the next
prime square, so

$$T_{<}(w) = S_{+}(w),$$

and therefore

$$q \le S_{+}(w).$$

This is the cleanest prime-placement version of the dominant case.

The interior composite selected integer determines a concrete later threat horizon, and
the right endpoint prime must occur before that horizon is crossed.

That is why the right phrase here is not merely "closure consequence." It is
also:

- a local upper bound on right-endpoint prime placement,
- driven by the low-divisor threat geometry of the composite interior.

## A Measurable Endpoint Observable

The existing closure notes track:

- threat distance:
  $$S_{+}(w) - w,$$
- prime-arrival margin:
  $$S_{+}(w) - q.$$

Those two quantities immediately give a third observable:

$$U_{\square}(w, q) = \frac{q - w}{S_{+}(w) - w}.$$

This is the **square-phase utilization** of the right endpoint.

Interpretation:

- `U_square = 1` means the next prime arrives exactly at the square-threat
  horizon,
- `U_square < 1` means the prime arrives before the next prime-square threat,
- very small `U_square` means the prime uses only a tiny fraction of the
  available square-phase budget.

Under the dominant `d=4` specialization of that closure consequence,

$$U_{\square}(w, q) \le 1.$$

So this ratio turns the closure law into a endpoint-placement coordinate.

## What The Current Surface Shows

The note
[`closure_constraint_findings.md`](./closure_constraint_findings.md)
already records the needed means:

- mean threat distance $S_{+}(w) - w$,
- mean prime-arrival margin $S_{+}(w) - q$,
- zero observed closure violations on the documented surface.

Subtracting those two committed means gives the mean selected integer-to-prime distance
$q - w$, and therefore the mean square-phase utilization.

On the documented surface, the dominant `d=4` regime gives:

| Regime | Mean threat distance | Mean selected integer-to-prime distance | Mean square-phase utilization |
|---|---:|---:|---:|
| exact $10^6$ | `5869.60` | `12.07` | `2.06e-3` |
| even $10^8$ | `89705.62` | `14.97` | `1.67e-4` |
| even $10^{10}$ | `522402.96` | `16.44` | `3.15e-5` |
| even $10^{12}$ | `2371908.08` | `17.64` | `7.44e-6` |
| even $10^{14}$ | `117070590.73` | `18.57` | `1.59e-7` |
| even $10^{16}$ | `393506966.29` | `19.37` | `4.92e-8` |
| even $10^{18}$ | `3595291803.67` | `20.12` | `5.60e-9` |

The same closure note also records minimum prime-arrival margin `2` on every
listed deterministic regime.

So the current tested dominant surface shows a striking split:

- the mean selected integer-to-next-prime step stays only about `12` to `20`,
- while the mean selected integer-to-next-prime-square threat distance grows from the
  thousands into the billions,
- and the resulting mean endpoint utilization drops from about `2e-3` at the
  exact $10^6$ surface to about `6e-9` at the even-band $10^{18}$ surface.

That does **not** state a separate pointwise asymptotic law. It does show that, on the
current documented surface, the following prime is arriving extremely early
relative to the available square-threat horizon.

## What This Changes In The Reading Of GWR

This finding changes the natural language of the project in three ways.

### 1. `GWR` is not only a maximizer rule

It is also a endpoint-placement law.

The maximizer rule identifies:

- what lower-divisor events the left prefix failed to realize before the
  selected integer,
- and what later lower-divisor threat the right suffix failed to realize
  before the next prime arrived.

That makes the endpoint primes part of the theorem content, not just the
background scenery.

### 2. The dominant `d=4` regime has a literal clock variable

In the dominant case, the next prime square after the selected integer is not just an
auxiliary construction.

It is the first later strictly simpler threat.

So the quantity

$$S_{+}(w) - w$$

is a literal countdown variable for the earliest `d=3` intrusion, and the next
prime must arrive before that countdown reaches zero.

### 3. Prime-gap interior structure can be read as a stopping rule

The dominant closure law can be read as:

- the selected integer appears,
- the later simpler threat horizon is determined,
- the right endpoint prime must stop the gap before that threat enters.

This does not mean the repo has proved a literal dynamical process on the
integers.

It does mean that the interior composite structure defines a stopping endpoint
for admissible prime-gap termination.

## Relation To The Admissibility-Censorship Finding

This note is narrower than
[`prime_gap_admissibility_censorship_finding.md`](./prime_gap_admissibility_censorship_finding.md).

That earlier finding says:

- actual prime gaps appear to realize only a thin subset of the divisor-class
  spoiler patterns that class-only algebra leaves unresolved.

The present note says something more specific:

- once the selected integer is fixed, the same interior structure yields direct
  constraints on where the endpoint primes are allowed to sit,
- and in the dominant `d=4` regime those constraints are naturally measured by
  a square-phase utilization ratio.

So the admissibility note is about which interior patterns are realizable at
all.
This endpoint note is about how the realized interior pattern constrains the
prime endpoints once it occurs.

## Scope Limits

This finding does **not** claim:

- that `GWR` is already proved universally,
- that the right endpoint is uniquely forced among all hypothetical prime
  placements,
- that the mean square-phase utilization controls every individual gap,
- or that the observed tiny utilization values already constitute a theorem.

The exact supported statement is narrower:

- if `GWR` holds, then the interior maximizer rule implies local constraints on
  prime-gap endpoint placement,
- and on the current documented dominant `d=4` surface, the right endpoint
  prime uses only a tiny mean fraction of the available square-threat budget.

## Safe Summary

The safest strong statement is:

`GWR`, if true as a prime-gap law, does not merely rank composites inside a
gap. It constrains where the consecutive endpoint primes are allowed to occur.

In the dominant `d=4` regime, the selected integer starts a square-phase clock, and the
next prime must appear before the next prime square after that selected integer. On the
current documented surface, the next prime uses only a tiny mean fraction of
that available square-phase budget.
