# Current Class-Only Spoiler Bound Leaves An Infinite Family

This note records the exact result of the first executed class-only test for
the spoiler inequality used in the repo's former finite-reduction proof route,
now retained only as historical context in
[`what_counts_as_gwr_proof.md`](./what_counts_as_gwr_proof.md).

The question is narrow:

starting from the current earlier-spoiler reduction,

$$
a^{(D-\delta)} < 2^{(\delta-2)},
$$

can one derive a finite bound from this inequality alone at the level of
divisor classes?

The answer at the class-only level is **no**.

## Exact Witness Family

For every integer $m \ge 4$, define

$$
\delta = 2m - 1,
\qquad
D = 2m,
\qquad
a = 3 \cdot 2^{m-1}.
$$

Then $a$ is composite and

$$
d(a) = d\!\left(2^{m-1} \cdot 3\right) = m \cdot 2 = 2m = D.
$$

So this gives an exact divisor-class witness for the pair $(\delta, D)$.

Under the current spoiler reduction, elimination would require

$$
a^{D-\delta} \ge 2^{\delta-2}.
$$

But here $D - \delta = 1$, so the elimination condition is just

$$
a \ge 2^{\delta-2} = 2^{2m-3}.
$$

The constructed earlier value is

$$
a = 3 \cdot 2^{m-1}.
$$

For every $m \ge 4$,

$$
3 \cdot 2^{m-1} < 2^{2m-3},
$$

because this is equivalent to

$$
3 < 2^{m-2},
$$

which holds for all $m \ge 4$.

So the current class-only inequality leaves this whole family unresolved.

## Effect

The unresolved witness values are

$$
a_m = 3 \cdot 2^{m-1},
$$

and these grow without bound as $m$ grows.

That means this inequality by itself does **not** produce a finite class-level
bound.

This is weaker than a failure of the whole former finite-reduction route.

The script does **not** build an actual prime gap or an actual later selected integer
value $w$.

So it does **not** prove that the whole finite-reduction route is impossible.

It says something narrower:

the current spoiler inequality, by itself, does not force a finite class-level
remainder.

## Executed Artifact

The executed proof-pursuit script is
[`finite_remainder_attempt.py`](../experiments/proof/finite_remainder_attempt.py).

It emits a deterministic JSON artifact containing the obstruction family and
the status of that narrow class-only route.
