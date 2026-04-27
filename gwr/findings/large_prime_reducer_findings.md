# Large-Prime Reducer Findings

This note records the executed status of the repo's former finite-reduction
route:

1. exact earlier-competing-integer exhaustion on the full small-prime surface, and
2. a fixed-factor large-prime reducer above an explicit threshold.

## Executed Reducer

The script is
[`large_prime_reducer.py`](../experiments/proof/large_prime_reducer.py).

It does two things:

1. exhaustively scans every prime gap below a fixed large-prime threshold
   $P_0$ using exact integer-power score comparison against all earlier
   interior candidates;
2. above that threshold, applies the fixed-factor bound
   $$
   \frac{q}{p} < 1 + \frac{1}{25 \log^2 P_0}
   $$
   and tests the resulting worst-case divisor-class threshold against the
   minimal integer with each earlier divisor count $D$.

For fixed $D$, the worst remaining class threshold occurs at the adjacent class
$\delta = D - 1$, so the large-prime test reduces to
$$
a < c_0^{D-3},
\qquad
c_0 = 1 + \frac{1}{25 \log^2 P_0},
$$
where $a$ is the minimal integer with exactly $D$ divisors.

## Executed Surface

The main executed artifact uses
$$
P_0 = 396739,
\qquad
c_0 \approx 1.000240704655167.
$$

Artifact:

- [`large_prime_reducer_396739_32768.json`](../../output/gwr_proof/large_prime_reducer_396739_32768.json)

The executed result is:

- exact small-prime surface scanned through $396739$,
- `29830` prime gaps with composite interior,
- `0` exact earlier competing integers,
- `0` unresolved earlier candidates,
- and `0` unresolved divisor-class rows through earlier divisor count
  $D = 32768$.

This means the current fixed-factor large-prime reducer stays fully closed on
the tested divisor-class table through $32768$.

## What This Does And Does Not Settle

This is a real proof advance.

It replaces the earlier loose factor-2 reduction with an explicit large-prime
route that is exact below $P_0$ and fully closed through a very large
divisor-class surface above $P_0$.

What remains open is the universal tail above the tested divisor-class table.

So this artifact is a strong reducer result inside that route, not a mandatory
gate for theorem language.

It does show that the remaining gap has become much narrower:

- no earlier-competing-integer counterexample exists on the full exact surface below
  $396739$,
- and no unresolved large-prime divisor class appears through $D = 32768$
  under the current fixed-factor reducer.
