# Phase-Budget Hidden-State Probe Findings

The strongest supported claim on the retained `10^12..10^18` catalog window surface is:

the current parity-plus-previous-state hidden model is missing one endpoint-budget bit.

On this pooled surface, the three-value label

- `non_d4`,
- `d4_low`,
- `d4_high`,

beats current selected integer parity as a next-triad predictor, and it still adds pooled signal after parity and previous reduced state are already present.

## Phase-Budget Definition

For current `d = 4` rows, compute square-phase utilization

$$U_{\square}(w, q) = \frac{q - w}{S_{+}(w) - w}.$$

Then, inside each current local-geometry cell

- carrier family,
- selected-integer offset,
- first-open offset,

split rows at the exact pooled median of $U_{\square}(w, q)$.

Rows below that median are labeled `d4_low`. Rows at or above it are labeled `d4_high`. All non-`d = 4` rows are labeled `non_d4`.

## Pooled Readout

- baseline log loss: `0.599308`
- parity gain: `0.014128`
- phase-budget gain: `0.027771`
- parity + previous-state gain: `0.108789`
- previous-state + phase-budget gain: `0.120587`
- parity + previous-state + phase-budget gain: `0.131856`

So the phase-budget label does two distinct things on the retained surface:

- by itself it beats parity by `0.013642` pooled log-loss gain;
- when appended to the current parity-plus-previous-state model, it adds `0.023067` more pooled gain.

## Label Shares

- `d4_low`: support `691`, next-triad share `0.712012`
- `d4_high`: support `730`, next-triad share `0.654795`
- `non_d4`: support `357`, next-triad share `0.663866`

So on the retained pooled surface, the low-budget and high-budget `d = 4` halves are separated by a next-triad gap of
 `0.057217`.

## Inside The Existing Hidden-State Cells

Restrict to populated `d = 4` strata keyed only by:

- current selected integer parity,
- previous reduced state.

Inside those already-existing hidden-state cells:

- used strata: `16`
- positive low-minus-high lifts: `11`
- negative low-minus-high lifts: `5`
- balanced weighted lift: `0.045082`

That is the direct reason this looks like new state rather than a restatement of parity:
the budget split keeps working inside the parity-plus-previous-state cells themselves.

## Reading

The existing hidden-state story says the next gap remembers where it came from and whether the current selected integer is even or odd.

The new readout says that is still incomplete. The current row also carries a one-bit record of how much of its local square budget it used before closure. That budget bit is pooled, measurable, and predictive on top of the current hidden-state candidate.

This is a bounded pooled-window claim, not yet a theorem and not yet a per-power monotonic law.

## Decision Rule

On retained high-scale windows, do not treat two rows with the same current selected integer parity and the same previous reduced state as equivalent when one is `d4_low` and the other is `d4_high`.

Score the `d4_low` row as more likely to return the next gap to the odd-semiprime triad.

## Artifacts

- [phase-budget hidden-state probe](../../benchmarks/python/predictor/gwr_phase_budget_hidden_state_probe.py)
- [summary JSON](../../output/gwr_phase_budget_hidden_state_probe_summary.json)
- [strata CSV](../../output/gwr_phase_budget_hidden_state_probe_strata.csv)
