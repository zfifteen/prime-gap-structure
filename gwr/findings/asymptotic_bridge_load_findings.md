# Asymptotic Bridge-Load Findings

This note records the executed normalized bridge surface from
[`asymptotic_bridge_load_scan.py`](../experiments/proof/asymptotic_bridge_load_scan.py).

The universal proof target for the no-early-spoiler condition is

$$\frac{\ln w}{\ln k} < 1 + \frac{\delta}{d_{\min} - 2}.$$

where

- $w$ is the true `GWR` carrier,
- $k$ is an earlier interior candidate,
- $\delta = d(k) - d_{\min}$.

This artifact rewrites that target as one dimensionless load:

$$B(k,w) = \frac{\frac{\ln w}{\ln k} - 1}{\frac{\delta}{d_{\min} - 2}}.$$

So the no-early-spoiler condition is exactly

$$B(k,w) < 1.$$

## Executed Artifact

- [`asymptotic_bridge_load_scan_2e7.json`](../../output/gwr_proof/asymptotic_bridge_load_scan_2e7.json)

## Strongest Supported Result

On the exact through-$2 \cdot 10^7$ surface:

- `3349874` earlier candidates are recorded,
- every recorded earlier candidate has bridge load strictly below `1`,
- the artifact records zero bridge failures,
- and the maximum realized bridge load is about `0.0566416671`.

That maximum normalized load occurs at the gap $(7, 11)$ with:

- selected integer $w = 9$,
- earlier candidate $k = 8$,
- selected divisor-count class $d_{\min} = 3$,
- earlier class $d = 4$.

So on the current exact surface, even the hardest normalized case uses only
about `5.66 %` of the available spoiler budget.

This is the cleanest exact proof-facing surface in the repo for the asymptotic
bridge. It removes the scale of the critical excess and asks only:

how much of the available spoiler budget does the realized geometry actually
use?

## Current Reading

This normalized surface is the finite base for the bridge closure because it
isolates the universal proof target in one number.

The ratio-frontier and large-gap scans already showed:

- the hardest ratio-form cases live in tiny gap-4 configurations,
- the largest gaps are not the hard regime.

The bridge-load scan packages that same fact into the exact normalized
quantity that the analytic bridge keeps below `1`.

It also sharpens the frontier picture in one important way:

- the smallest raw critical-ratio margin comes from the higher-class pair
  `(30, 32)`,
- but the largest *normalized* bridge load still comes from the tiny
  `(d_{\min}, d) = (3, 4)` edge case at $(7, 11)$.

So the current exact surface separates two different notions of hardness:

- raw ratio slack is tightest in higher adjacent divisor classes,
- normalized budget usage is largest in the smallest low-class edge case.

The explicit certificate in
[`proof_bridge_certificate_2e7.json`](../../output/gwr_proof/proof_bridge_certificate_2e7.json)
then evaluates BHP's $\theta = 0.525$ with the recorded divisor-function
constants. For $A=1$, the bridge thresholds `102` and `3,544` both land below
the exact finite base $p < 20{,}000{,}001$, so the no-early-spoiler bridge
closes under those assumptions.
