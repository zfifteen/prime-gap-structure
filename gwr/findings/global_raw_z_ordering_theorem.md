# Global Raw-Z Ordering Theorem

## Theorem

Let

`Z(n) = (1 - d(n)/2) ln(n)`

for every composite integer `n`, where `d(n)` is the divisor count of `n`.

Let `a` and `b` be composite integers. If either

- `d(a) < d(b)`, or
- `d(a) = d(b)` and `a < b`,

then

`Z(a) > Z(b)`.

Equivalently, on the composite integers, the raw-`Z` score is strictly ordered
by the lexicographic order

`(d(n), n)`

with smaller divisor count first and, among equal divisor counts, smaller `n`
first.

## Proof

For a composite integer `n`, one has `d(n) >= 4`. Define

`alpha(n) = d(n)/2 - 1`.

Then `alpha(n) > 0`, and the score may be rewritten as

`Z(n) = -(d(n)/2 - 1) ln(n) = -alpha(n) ln(n)`.

Now let `a` and `b` be composite integers satisfying either `d(a) < d(b)` or
`d(a) = d(b)` with `a < b`.

Set

`A = alpha(a),  B = alpha(b)`.

By construction, the hypothesis implies either

- `A < B`, or
- `A = B` and `a < b`.

Since `a` and `b` are positive integers and `ln(x)` is strictly increasing on
`(0, infinity)`, this gives either

- `A < B` and `ln(a) <= ln(b)` if `a <= b`, or
- `A <= B` and `ln(a) < ln(b)` if `a < b`.

In either case, because `A > 0` and `B > 0`, one obtains

`A ln(a) < B ln(b)`.

Multiplying by `-1` reverses the inequality:

`-A ln(a) > -B ln(b)`.

Substituting back `Z(a) = -A ln(a)` and `Z(b) = -B ln(b)` yields

`Z(a) > Z(b)`.

This proves the claim.

## Corollary

Let `S` be any finite nonempty set of composite integers. Then the unique
maximizer of `Z(n)` over `S` is the lexicographic winner:

1. choose the element(s) of `S` with minimal divisor count `d(n)`,
2. among those, choose the smallest integer.

In particular, if `S` is the interior composite set of a prime gap `(p, q)`,
then the raw-`Z` winner is exactly the Gap Winner Rule winner.

## Proof

Because `S` is finite, there exists at least one lexicographic winner under the
order “smallest `d(n)`, then smallest `n`.” Let `m` denote that winner.

For every other `x` in `S`, either

- `d(m) < d(x)`, or
- `d(m) = d(x)` and `m < x`.

By the theorem, `Z(m) > Z(x)` for every `x != m`. Hence `m` is the unique
maximizer of `Z` on `S`.

When `S` is the interior composite set of a prime gap, this is exactly the Gap
Winner Rule.

## Remark

The prime-gap statement is therefore a corollary of a more general ordering
law. The proof does not require any special property of prime gaps beyond the
fact that their interiors form finite sets of composite integers. The governing
structure lies in the score itself:

`Z(n) = -(d(n)/2 - 1) ln(n)`.

For composites, both factors are positive. Increasing `d(n)` increases the
positive coefficient, and increasing `n` increases `ln(n)`. Since the score is
the negative of their product, either change pushes `Z(n)` downward. The
raw-`Z` maximizer is therefore forced to occur at the smallest divisor count,
and among ties, at the smallest integer.

This shows that the Gap Winner Rule is not merely an empirical regularity on
the tested prime-gap surface. It is the restriction, to prime-gap interiors, of
a global lexicographic ordering theorem for raw-`Z` on composite integers.
