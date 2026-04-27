# Lexicographic Raw-Z Dominance Theorem

## Theorem

Let

$$
Z(n) = \left(1 - \frac{d(n)}{2}\right)\ln(n)
$$

for every composite integer $n$, where $d(n)$ is the divisor count of $n$.

Let $a$ and $b$ be composite integers with $a < b$. If

$$
d(a) \le d(b),
$$

then

$$
Z(a) > Z(b).
$$

Equivalently, along increasing composite integers, raw-$Z$ is strictly ordered
by the partial order

- smaller divisor count first,
- and, for equal divisor count, smaller integer first.

## Proof

For a composite integer $n$, one has $d(n) \ge 3$. Define

$$
\alpha(n) = \frac{d(n)}{2} - 1.
$$

Then $\alpha(n) \ge 1/2 > 0$, and the score may be rewritten as

$$
Z(n) = -\left(\frac{d(n)}{2} - 1\right)\ln(n) = -\alpha(n)\ln(n).
$$

Now let $a$ and $b$ be composite integers with $a < b$ and $d(a) \le d(b)$.

Set

$$
A = \alpha(a), \qquad B = \alpha(b).
$$

Since $d(a) \le d(b)$, one has $A \le B$. Since $a < b$ and $\ln(x)$ is strictly
increasing on $(0, \infty)$, one has $\ln(a) < \ln(b)$.

Because $A > 0$, it follows that

$$
A\ln(a) < A\ln(b).
$$

Because $A \le B$ and $\ln(b) > 0$, it follows that

$$
A\ln(b) \le B\ln(b).
$$

Combining the two inequalities gives

$$
A\ln(a) < B\ln(b).
$$

Multiplying by `-1` reverses the inequality:

$$
-A\ln(a) > -B\ln(b).
$$

Substituting back $Z(a) = -A\ln(a)$ and $Z(b) = -B\ln(b)$ yields

$$
Z(a) > Z(b).
$$

This proves the claim.

## Corollary

Let $S = \{n_1 < n_2 < \cdots < n_k\}$ be a finite nonempty increasing list of
composite integers such that, whenever `i < j`, one has

$$
d(n_i) \le d(n_j)
$$

for the selected integer $n_i$ against every later candidate $n_j$.

Then $n_i$ is the unique maximizer of $Z$ on $S$.

In particular, if the interior composites of a prime gap satisfy this ordered
divisor condition relative to the leftmost minimizer, then the raw-$Z$
selected integer is exactly the Gap Winner Rule selected integer.

## Remark

The stress-test surface rules out a stronger unrestricted global claim. It is
not true in general that

$$
d(a) < d(b) \Rightarrow Z(a) > Z(b)
$$

for arbitrary unordered composite pairs.

One explicit counterexample is

- $a = 49$, $d(a) = 3$, $Z(a) = -1.945910149\ldots$
- $b = 6$, $d(b) = 4$, $Z(b) = -1.791759469\ldots$

Here $d(a) < d(b)$ but $Z(a) < Z(b)$.

So the exact theorem supported by the current algebra and stress tests is a
lexicographic dominance theorem in the ordered direction: lower-or-equal
divisor count wins only when it also occurs at the earlier integer.

This keeps the theorem narrow and correct. The separate prime-gap question is
whether the interior divisor profile of a prime gap always places the
leftmost minimizer in precisely that ordered-dominance regime.
