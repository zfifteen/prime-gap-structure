# Closing The `d=4` Square-Ceiling Branch

Update:
the previously open `r^2 - 4` obstruction is now closed by the residue split
recorded in [docs/findings/d4_square_residue_dead_zone.md](../../findings/d4_square_residue_dead_zone.md).
This note remains useful as the exact pre-closure surface report.

The strongest new fact about the current `d=4` closure program is this:

on the live earliest-`d=4` semiprime branch, the exact floor package sits at
margin `2`, and the first exact non-floor branch seen on the current exact
surface jumps directly to margin `6`.

So the live proof bottleneck is no longer a broad statement of the form

$$q \le S_{+}(w).$$

It is the narrower missing branch:

does closure at $r^2 - 4$ ever occur on the same earliest-`d=4` branch?

## 1. Branch Setup

Let $(p, q)$ be a prime gap whose implemented raw-$Z$ maximizer $w$ satisfies:

- $d(w)=4$,
- $w$ is not a prime cube,
- and $w$ is the earliest non-cube `d=4` semiprime after $p$.

Let $r$ be the smallest prime with

$$r^2 > w,$$

so the dominant square-threat ceiling is

$$S_{+}(w) = r^2.$$

The closure margin is

$$M_{\square}(p, q, w) = r^2 - q.$$

## 2. Proved Algebraic Floor

Here $r > 2$ is odd, so

$$r^2 - 1 = (r - 1)(r + 1)$$

is composite.

That gives an unconditional algebraic floor:

$$M_{\square}(p, q, w) \ge 2$$

whenever the gap closes under this square-threat ceiling.

So margin `1` is not merely unobserved. It is impossible by algebra.

## 3. Exact Measured Branch Decomposition

The current exact branch surface is now split into two deterministic regimes.

### Floor Package

The floor frontier scan in
[`../../../output/d4_square_threat_frontier_summary.json`](../../../output/d4_square_threat_frontier_summary.json)
records:

- exact full scan to $10^6$,
- deterministic even-band ladder from $10^8$ through $10^{18}$,
- global minimum margin `2`,
- top unique floor rows all at margin `2`.

That is the exact floor package:

- $r^2 - 2$ is prime,
- and closure occurs at
  $$q = r^2 - 2.$$

### First Non-Floor Branch

The exact non-floor scan in
[`../../../output/d4_square_threat_nonfloor_frontier_summary.json`](../../../output/d4_square_threat_nonfloor_frontier_summary.json)
records:

- exact scan through $10^8$,
- earliest non-cube `d=4` semiprime selected integers only,
- filter to cases where $r^2 - 2$ is composite,
- `3,570,693` such gaps on the exact scanned surface,
- zero observed margins `3`, `4`, or `5`,
- first observed non-floor margin `6`.

The compact terminal certificate from that exact scan is:

| Terminal margin | Count on exact $10^8$ non-floor surface |
|---:|---:|
| `3` | `0` |
| `4` | `0` |
| `5` | `0` |
| `6` | positive |

So the first exact non-floor branch currently visible is:

$$q = r^2 - 6.$$

This is measured fact on the exact scanned surface, not yet a theorem.

## 4. Exact `r^2 - 4` Obstruction Target

The missing obstruction is now explicit.

The companion exact obstruction scan in
[`../../../output/d4_square_threat_r2_minus_4_obstruction_summary.json`](../../../output/d4_square_threat_r2_minus_4_obstruction_summary.json)
tracks the same live branch and asks one direct question:

does any gap close at

$$q = r^2 - 4?$$

On the current exact $10^8$ surface, the scan reports:

- zero observed margin-`4` closures,
- zero cases where $r^2 - 4$ itself is prime on the live composite-`r^2-2`
  branch,
- terminal margin counts consistent with the non-floor scan,
- factor certificates for
  $r^2 - 4$,
  $r^2 - 2$,
  and
  $r^2 - 1$
  on the smallest obstruction rows.

The compact exact branch certificate from that scan is:

| Terminal mode on exact $10^8$ live branch | Count |
|---|---:|
| floor package: $q = r^2 - 2$ | `814228` |
| candidate missing branch: $q = r^2 - 4$ | `0` |
| first observed non-floor branch: $q = r^2 - 6$ | `110` |
| deeper branches: $q \le r^2 - 8$ | `3570583` |

That does not yet prove impossibility of $r^2 - 4$.
It does isolate `r^2 - 4` as the live theorem bottleneck.

## 5. Candidate Local Lemma

The candidate local admissibility lemma for this branch is:

> Let $(p, q)$ be a prime gap whose implemented score maximizer $w$ is the earliest
> non-cube `d=4` semiprime after $p$, and let $r$ be the smallest prime with
> $r^2 > w$. Then closure at $r^2 - 4$ does not occur.

Equivalently:

$$q \ne r^2 - 4.$$

Combined with the algebraic floor and the measured non-floor jump, this would
force the current branch decomposition:

- floor package:
  $$q = r^2 - 2$$
  when $r^2 - 2$ is prime;
- next live branch:
  $$q \le r^2 - 6$$
  when $r^2 - 2$ is composite.

## 6. What Is Proved, Measured, And Open

### Proved

- $r^2 - 1$ is composite for odd prime $r$.
- Therefore margin `1` is impossible.

### Exact Measured Surface

- floor package at margin `2`;
- exact non-floor jump to margin `6` through $10^8$;
- zero observed margin-`4` closures on the same exact non-floor branch.

### Open

- prove that closure at $r^2 - 4$ cannot occur on the live earliest-`d=4`
  semiprime branch;
- explain structurally why the first exact non-floor branch lands at
  $r^2 - 6$.

## 7. Bottom Line

The `d=4` square-ceiling branch has narrowed materially.

The open problem is no longer a diffuse tail-prime existence statement.
It is the much smaller local obstruction:

exclude $r^2 - 4$ on the live earliest-`d=4` branch.

If that exclusion closes, the branch decomposition becomes sharp enough to
promote the current measured jump from `2` to `6` into the next proof-facing
lemma.
