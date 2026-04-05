# No-Early-Spoiler Ratio Frontier Findings

This note records the executed pair-frontier extraction from
[`no_early_spoiler_ratio_frontier.py`](../experiments/proof/no_early_spoiler_ratio_frontier.py).

The input surface is the exact no-early-spoiler condition against the true
`GWR` carrier. The question here is narrower:

which winner/earlier divisor-class pairs come closest to violating the
ratio-form spoiler inequality?

## Executed Artifact

- [`no_early_spoiler_ratio_frontier_2e7.json`](../../output/gwr_proof/no_early_spoiler_ratio_frontier_2e7.json)

## Strongest Supported Result

On the full exact surface through $2 \cdot 10^7$, the critical-ratio frontier
is not led by the familiar low-divisor cases.

The current top ratio-form frontier pairs are:

1. winner class `30`, earlier class `32`,
2. winner class `15`, earlier class `16`,
3. winner class `22`, earlier class `24`,
4. winner class `18`, earlier class `20`,
5. winner class `32`, earlier class `36`.

So the tightest ratio-form slack is concentrated in higher winner classes where
the critical threshold

$$
\frac{d(k) - 2}{d_{\min} - 2}
$$

already sits close to $1$.

## Exact Frontier Leader

The current exact leader is the pair

$$
(d_{\min}, d(k)) = (30, 32),
$$

realized at the gap $(2486509, 2486513)$ with:

- winner $m^* = 2486512$,
- earlier candidate $k = 2486510$,
- critical-ratio margin about `0.0714285168`,
- direct log-score margin about `14.7263794181`.

So the hardest ratio-form case on the exact current surface is still not close
to zero.

## Current Reading

This frontier shifts the research picture in one clear way:

the no-early-spoiler problem is not currently tightening first in the small
winner classes.

The exact frontier is instead led by adjacent or near-adjacent higher divisor
classes where the ratio threshold is closest to $1$. That makes the next proof
target more concrete:

understand why these higher-class adjacent-pair regimes still retain a
uniformly positive gap-local margin.
