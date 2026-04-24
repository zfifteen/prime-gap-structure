# GPE Blocker Resolution

This note keeps the GPE requirements intact and records the exact blockers that
must be resolved for the specification in
[`tech_spec_generative_prime_engine.md`](./tech_spec_generative_prime_engine.md)
to become an implementation contract.

The milestone roadmap built from these blockers is
[`gpe_development_roadmap.md`](./gpe_development_roadmap.md).

## Strongest Current Fact

The current repository proves and validates the GWR winner surface. Given a
known left boundary prime $q$, the exact DNI/GWR oracle recovers:

- the next-gap interior winner $w$,
- the winner divisor class $d(w)$,
- and the right boundary prime $q^+$ by scanning the divisor field until
  $d(n)=2$.

That is not yet the same as a primality-free generative prime engine. The
missing object is an exact boundary selector.

## Blocker 1: Winner Is Not The Boundary

The relation $$q^+=w+1$$ is false.

The first small obstruction is:

- left boundary prime: $q=23$,
- GWR winner: $w=25$,
- right boundary prime: $q^+=29$.

So the implementation skeleton cannot emit `winner + 1`.

### Resolution Contract

Replace `winner + 1` with a deterministic boundary selector:

$$q^+=B(q,S,w,d(w)),$$

where:

- $q$ is the current prime,
- $S$ is the full GPE state,
- $w$ is the GWR winner,
- $d(w)$ is the winner divisor class,
- and $B$ returns the exact next prime without Miller-Rabin, trial division of
  the gap interior, candidate sieving lists, or Eratosthenes marking.

This is the first theorem/program target. Until $B$ exists, GPE is not an exact
prime emitter.

## Blocker 2: NLSC Gives A Ceiling, Not A Selector

The No-Later-Simpler-Composite consequence says:

$$q^+ \le T_{<}(w),$$

where $T_{<}(w)$ is the first later integer with divisor count below $d(w)$.

For the dominant $d(w)=4$ regime this specializes to:

$$q^+ \le S_{+}(w),$$

where $S_{+}(w)$ is the next prime square after $w$.

This resolves the upper boundary of the search interval, not the exact boundary
inside it. The exact selector still has to identify which admissible integer in
$(w,T_{<}(w)]$ is $q^+$.

### Resolution Contract

The boundary selector must refine the NLSC ceiling into an equality:

$$B(q,S,w,d(w)) = q^+.$$

The proof obligation is not only that $B$ terminates before $T_{<}(w)$. The
proof obligation is exact equality with the next prime.

## Blocker 3: The Reduced 14-State Rulebook Is Not Yet Deterministic Enough

The frozen v1.0 rulebook closes a reduced gap-type surface. Its laws are stated
as measured transition shares and concentration improvements, not as exact
single-successor boundary rules.

A reduced state such as `o4_d4_a1_even_semiprime`

occurs with multiple right-boundary gaps on the committed catalog surface. For
example:

| $q$ | $w$ | $q^+$ | gap |
|---:|---:|---:|---:|
| $13$ | $14$ | $17$ | $4$ |
| $73$ | $74$ | $79$ | $6$ |

Both rows have the same reduced winner type, but different boundary offsets.
Therefore the current reduced state alone cannot emit the exact prime sequence.

### Resolution Contract

The GPE state $S$ must be enlarged or sharpened only as much as needed to make
the boundary selector single-valued: $$B(q,S,w,d(w))$$ must have no collisions
on the validation surface, and the proof target must explain why the
collision-free property persists outside the tested surface.

## Blocker 4: Exact DNI Evaluation Currently Uses The Divisor Field

The current exact oracle evaluates divisor counts and detects the boundary by
the condition $d(n)=2$.

That is valid for the existing DNI/GWR oracle. It does not satisfy the GPE
requirement of zero traditional primality tests and no candidate sieving lists.

### Resolution Contract

Tier 1 must either:

- compute the winner and boundary by rulebook arithmetic without divisor-field
  scanning, or
- remain explicitly outside the zero-test GPE contract.

There is no acceptable hidden path where `find_min_L_in_window` silently
performs primality or divisor-field scanning while the surrounding engine is
described as zero-test.

## Immediate Proof Target

The next executable target is not a broader framework. It is the smallest
possible boundary-selector theorem:

Given a known prime $q$ and the exact GWR winner $w$ for the next gap, construct
a deterministic arithmetic rule $B(q,S,w,d(w))$ that returns $q^+$ exactly and
does not test candidate primality.

The first branch to attack is the dominant case: $$d(w)=4.$$

In that branch, the invariant ceiling is the next prime-square threat:
$$q^+ \le S_{+}(w).$$

The unresolved selector problem is the exact location of $q^+$ inside the
interval: $$w < q^+ \le S_{+}(w).$$

Once this branch has a collision-free rule on the committed exact surface, the
same test should be repeated for $d(w)=3$ and for higher-divisor winner classes.
