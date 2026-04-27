# Gap Anatomy Decomposition of GWR

This note records one cleaner reading of the current `Gap Winner Rule` surface.

The strongest supported finding is:

`GWR` currently looks less like a full gap-wide score optimization and more
like a layered first-arrival law.

On one exact session probe through $10^6$, every observed selected divisor-count class matched
the first carrier of the smallest divisor class present in the gap interior.
On two deterministic exploratory windows of width $2 \times 10^6$ near
$10^{12}$, the dominant `d=4` first-arrival offsets stayed small while the
`No-Later-Simpler-Composite` slack varied mainly with position relative to the
next prime square.

That does not replace the current validated surface in the repo notes. It does
give a better decomposition of what the current selected integer and closure laws may be
measuring.

## Scope

This note combines two kinds of evidence.

### Existing validated surface

The repo already documents:

- the canonical `GWR` statement in
  [`gap_winner_rule.md`](./gap_winner_rule.md),
- the closure surface in
  [`closure_constraint_findings.md`](./closure_constraint_findings.md),
- the dominant `d=4` reduction in
  [`dominant_d4_arrival_reduction_findings.md`](./dominant_d4_arrival_reduction_findings.md),
- and the current claim structure in
  [`claim_hierarchy.md`](./claim_hierarchy.md).

### New session probe surface

This note also records one small deterministic probe surface computed directly
from the same exact divisor-count and score definitions used elsewhere in the
repo:

- one exact full scan on `[2, 10^6]`,
- one deterministic window on
  `[10^{12} + 2,\ 10^{12} + 2{,}000{,}002)`,
- one matched deterministic window of the same width ending exactly at the
  prime square $1000003^2 = 1000006000009$.

These new windows are exploratory session probes, not a new committed
validation ladder.

## Setting

Let $(p, q)$ be one prime gap with interior integers

$$p + 1,\ p + 2,\ \ldots,\ q - 1.$$

Write the smallest divisor class present in the interior as

$$\delta_{\min}(p, q) = \min_{p < n < q} d(n).$$

For each divisor class $\delta$ present in the gap, write its first-arrival
offset as

$$A_{\delta}(p, q) = \min \{r \ge 1 : d(p + r) = \delta\}.$$

The implemented score maximizer is

$$w = \arg\max_{p < n < q} L(n), \quad L(n) = \left(1 - \frac{d(n)}{2}\right)\ln(n).$$

The point of this note is that the current data are better read through
$\delta_{\min}$ and $A_{\delta}$ than through a generic score-optimization
story.

## Hierarchical First-Arrival Law

The cleanest current reading is:

1. identify the smallest divisor class that actually appears in the gap,
2. then take the first carrier of that class from the left.

In symbols, the layered reading is

$$w = p + A_{\delta_{\min}(p, q)}(p, q).$$

This says the competition is hierarchical by divisor layer:

- if a `d=3` carrier appears, it should beat every `d \ge 4` carrier,
- if no `d=3` appears but some `d=4` does, then `d=4` should beat every
  `d \ge 6` carrier,
- if no `d=3,4` appear but `d=6` does, then `d=6` should win,
- and so on.

That is a different reading from
"evaluate one continuous score across the whole interior and see which point
wins."

### Exact $10^6$ Session Probe

On the exact probe through $10^6$, the observed selected divisor-count classes were:

- `d=3`: `167`
- `d=4`: `58,303`
- `d=6`: `2,983`
- `d=8`: `7,392`
- `d=9`: `6`
- `d=10`: `118`
- `d=12`: `820`
- `d=14`: `15`
- `d=15`: `1`
- `d=16`: `485`
- `d=18`: `4`
- `d=20`: `12`
- `d=24`: `16`
- `d=32`: `5`

On that exact surface, every observed selected integer matched the first carrier of the
smallest divisor class present:

- `167 / 167` first-`d=3` matches,
- `58,303 / 58,303` first-`d=4` matches,
- `2,983 / 2,983` first-`d=6` matches,
- `7,392 / 7,392` first-`d=8` matches,
- and the same exact match for every rarer observed class above.

So the hierarchical reading is not only a `d=4` story on that probe. It held
class by class across the whole observed selected integer surface.

## Early-Arrival Law

The dominant regime is still `d=4`, so the most useful arrival observable is

$$A_4(p, q) = \min \{r \ge 1 : d(p + r) = 4\},$$

when a `d=4` carrier is present.

The current probes suggest that once the `d=3` layer is absent, the decisive
`d=4` layer appears very early.

### Exact $10^6$ Probe, `d=4` Selected integer Gaps

Among the `58,303` gaps whose selected integer had `d(w)=4`:

- median first-`d=4` offset: `3`,
- `90`th percentile: `6`,
- `99`th percentile: `10`,
- maximum observed first-`d=4` offset: `22`.

### Exploratory Window Near $10^{12}$

On the deterministic window
`[10^12 + 2, 10^12 + 2,000,002)`, among `56,732` `d=4` selected integer gaps:

- median first-`d=4` offset: `6`,
- `90`th percentile: `12`,
- `99`th percentile: `22`,
- maximum observed first-`d=4` offset: `50`.

On the matched window of the same width ending at the prime square
$1000003^2 = 1000006000009$, among `56,792` `d=4` selected integer gaps:

- median first-`d=4` offset: `6`,
- `90`th percentile: `12`,
- `99`th percentile: `22`,
- maximum observed first-`d=4` offset: `51`.

The key point is not the exact constants. It is that the decisive `d=4` layer
still appears very near the left prime even when the scale jumps by six orders
of magnitude.

That is why the current surface looks less like "a long global score contest"
and more like "an early low-divisor arrival that usually never gets overturned."

## Square Phase

In the dominant `d=4` regime, the first strictly simpler class is `d=3`, and
that class occurs exactly at prime squares.

So the next later threat to a `d=4` selected integer is the next prime square after the
selected integer. Write that quantity as $\Sigma_{+}(w)$.

This introduces one hidden variable:

the gap's position relative to that next prime-square endpoint.

It is useful to separate two quantities:

$$\Phi_{\square}(w) = \Sigma_{+}(w) - w,$$

the selected integer's remaining distance to the next prime square, and

$$M_{\square}(w, q) = \Sigma_{+}(w) - q,$$

the closure margin left after the right prime arrives.

The current session probes show that this square phase changes the closure
slack dramatically even when the overall scale and the first-`d=4` arrival
pattern barely change.

### Same Scale, Different Square Phase

At scale about $10^{12}$:

- on the window
  `[10^12 + 2, 10^12 + 2,000,002)`,
  the minimum observed `d=4` closure margin was `4,000,098`;
- on the matched window ending at $1000003^2$,
  the minimum observed `d=4` closure margin dropped to `66`.

The first-`d=4` offset distribution barely moved between those two windows.
The sharp change was in how close the whole window sat to the next prime square.

That is what "square phase" means here.

It is not scale.
It is not the general density of `d=4` carriers.
It is the gap's location inside the current prime-square chamber.

## NLCT as a Quantified Consequence of Square Exclusion

The dominant reduction already says:

- if the selected divisor-count class is `d=4`, then the gap contains no interior prime square;
- once no interior prime square is present, the selected integer is the first interior
  `d=4` carrier.

In that regime, `No-Later-Simpler-Composite` becomes

$$q < \Sigma_{+}(w).$$

So the dominant `d=4` version of `NLCT` can be read as:

square exclusion with a ruler attached.

The qualitative form is:

- no later prime square enters before the gap closes.

The quantitative form is:

- the gap closes with margin
  $M_{\square}(w, q) = \Sigma_{+}(w) - q$ still remaining.

### Exact $10^6$ Margin Snapshot

Among the `58,303` exact `d=4` selected integer gaps through $10^6$:

- minimum observed closure margin: `2`,
- median observed closure margin: `4,118`,
- `90`th percentile: `13,562`,
- only about `0.45%` of these gaps had margin `<= 20`.

So on that exact probe, most `d=4` gaps were not close to failure. They closed
with substantial square-phase slack.

### Exploratory Pre-Square Window Near $10^{12}$

On the matched window ending at $1000003^2$:

- minimum observed closure margin: `66`,
- median observed closure margin: `1,001,190`,
- only `28 / 56,792` `d=4` selected integer gaps had margin `<= 1000`,
- only about `1.76 \times 10^{-5}` had margin `<= 100`.

So even in a deliberately dangerous square-phase placement, the genuinely tight
`d=4` cases remained very thin.

This is why the dominant `d=4` version of `NLCT` currently looks more like a
quantified consequence of square exclusion plus early `d=4` arrival than like
an independent global mechanism.

## What This Changes

This decomposition suggests a cleaner internal anatomy for the current selected integer
surface.

### 1. `GWR` may be layered rather than globally optimized

The natural local objects are:

- the smallest divisor class present,
- the first-arrival offset of that class,
- and the later strictly simpler threat horizon.

That is a sharper basis for local consequence notes than the raw score alone.

### 2. The dominant `d=4` regime may mostly reduce to three local objects

Those objects are:

- absence of the `d=3` layer,
- early arrival of the `d=4` layer,
- remaining square-phase slack at closure.

That is a much narrower mechanism than "the whole score field must be searched
globally."

### 3. The real hard cases may live in a thin square-adjacent tail

Most windows look extremely slack.
The delicate cases appear when the gap lies very near the next prime square.

That points the stress-test program toward square-adjacent families rather than
toward generic high-scale windows.

## Why This Could Add Information Beyond the RH Bridge

The current `DNI`-to-`RH` bridge in
[`docs/dni_rh_bridge.md`](../../docs/dni_rh_bridge.md)
is exact, but it reconstructs the classical detector
$-\zeta'(s)/\zeta(s)$.

The gap-anatomy quantities in this note are different in kind:

- $\delta_{\min}(p, q)$,
- first-arrival offsets $A_{\delta}(p, q)$,
- square phase $\Phi_{\square}(w)$,
- and closure margin $M_{\square}(w, q)$.

These are local admissibility variables for prime-gap interiors.
If they eventually yield theorem-level bounds, the added information would not
come from repeating the bridge identity. It would come from constraining which
interior composite patterns consecutive primes are allowed to enclose.

That is still not a direct result about zeta zeros.
It is the kind of local prime-gap information that could matter beside the
bridge rather than inside it.

## Safe Summary

The current `GWR` surface is better read as a gap-anatomy decomposition than
as one undifferentiated score law.

The leading picture is:

- the selected integer is the first carrier of the smallest divisor class present,
- the dominant `d=4` regime is driven by early `d=4` arrival once the `d=3`
  layer is absent,
- and the dominant `NLCT` margin is controlled mainly by square phase.

That is not a separate prime-distribution theorem on its own.
It does identify a cleaner set of local observables and a narrower mechanism
than the repo had before.
