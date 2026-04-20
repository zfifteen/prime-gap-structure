# GWR Gap-Type Hybrid Scheduler Findings

## Observable Facts

The local scheduler result was real, but it did not close the stationary walk.

On the aligned pooled `256`-window surface, the earlier scheduler probe had
already reduced concentration L1 error from `0.1390` to `0.0201`. But on the
full `1,000,000`-step stationary walk, the best three-step concentration was
still only `0.4900`.

So the immediate question was whether the missing engine layer was:

- a hybrid of lag-2 memory and a small global cycle;
- an explicit reset trigger;
- or both together.

The hybrid probe tests exactly that finite family.

## Hybrid Models Tested

The new probe keeps the same persistent `14`-state core and compares six
deterministic models:

1. `second_order_rotor`
2. `lag2_state_scheduler`
3. `mod_cycle_scheduler`
4. `hybrid_lag2_mod8_scheduler`
5. `hybrid_lag2_mod8_reset_hdiv_scheduler`
6. `hybrid_lag2_mod8_reset_nontriad_scheduler`

Here:

- `mod8` means the scheduler carries an explicit `8`-phase counter;
- `reset_hdiv` resets that phase when a higher-divisor state arrives;
- `reset_nontriad` resets it whenever the walk leaves the Semiprime Wheel
  Attractor.

The exact artifacts are:

- [../../output/gwr_dni_gap_type_hybrid_scheduler_probe_summary.json](../../output/gwr_dni_gap_type_hybrid_scheduler_probe_summary.json)
- ![Hybrid scheduler probe overview](../../output/gwr_dni_gap_type_hybrid_scheduler_probe_overview.png)

## Main Result

The strongest supported result is:

The hybrid engine improves the pooled-window fit again, but it still does not
close the stationary million-step walk.

The best pooled-window model is
`hybrid_lag2_mod8_reset_nontriad_scheduler`.

Its pooled `256`-window concentrations are:

- one-step: `0.3269`
- two-step: `0.5057`
- three-step: `0.7692`

against the real pooled target:

- one-step: `0.3284`
- two-step: `0.5059`
- three-step: `0.7594`

So the pooled concentration L1 error drops to `0.0116`.

That is another clear gain over the earlier best `lag2_state_scheduler`
surface at `0.0201`.

## What The Stationary Walk Still Says

The stationary walk remains the blocker.

The best full-walk three-step concentration is delivered by
`hybrid_lag2_mod8_scheduler`, not by the reset variants:

- `second_order_rotor`: `0.3478`
- `lag2_state_scheduler`: `0.4900`
- `mod_cycle_scheduler`: `0.3957`
- `hybrid_lag2_mod8_scheduler`: `0.4966`
- `hybrid_lag2_mod8_reset_hdiv_scheduler`: `0.4929`
- `hybrid_lag2_mod8_reset_nontriad_scheduler`: `0.4907`

So none of the tested finite hybrids crosses the requested `0.60` threshold on
the full stationary walk.

That matters because it tells us exactly what the current engine completion
claim can and cannot be.

Supported:

- a finite hybrid scheduler closes the local-window surface to about `1.2%`
  concentration L1;
- a hybrid lag-2 plus modulo controller improves the stationary walk relative
  to the plain lag-2 scheduler.

Not yet supported:

- that the current finite hybrid also reproduces the long-horizon stationary
  re-entry law.

## The 8-Phase Question

The `8`-phase controller is good, but the current reduced-state surface does
not isolate it as uniquely privileged.

Two cycle sweeps matter here.

For the plain modulo scheduler, the best pooled-window cycle in the tested
range `2..12` is actually `11`, with:

- pooled concentration L1: `0.0202`
- full-walk three-step: `0.4149`

For the hybrid lag-2 plus higher-divisor-reset family, the best pooled-window
cycle in the same range is `2`, with:

- pooled concentration L1: `0.0091`
- full-walk three-step: `0.4917`

So the current evidence does support a **small periodic controller**, but it
does not yet support a unique arithmetic lock-in to an `8`-phase controller.

That is an important narrowing:

- the periodic layer looks real;
- the special status of `8` is not yet established on this reduced surface.

## Reset Interpretation

The two reset laws separate cleanly.

`reset_nontriad` is the best local-window fitter. It says the right reset event
for local concentration is leaving the Semiprime Wheel Attractor.

`reset_hdiv` is more arithmetic in flavor, but on the tested surface it is not
the best local-window model and it does not improve the stationary walk beyond
the no-reset hybrid.

So the present reading is:

- leaving the attractor is the stronger empirical reset marker;
- higher-divisor arrival is still meaningful, but not yet the dominant reset
  law.

## Record-Gap Reset Signature

The record-gap readout does not support the strongest reset-story version.

On the `387` records in the local `10^12..10^18` extract:

- previous higher-divisor share: `0.2119`
- previous nontriad share: `0.3282`
- current higher-divisor share: `0.0000`
- current nontriad share: `0.1421`

For the `24` maximal records:

- previous higher-divisor share: `0.2917`
- previous nontriad share: `0.3750`
- current higher-divisor share: `0.0000`
- current nontriad share: `0.0833`

So maximal gaps are somewhat more likely to be **preceded** by higher-divisor
or nontriad states than the record pool as a whole, but they are not
themselves higher-divisor reset states.

That is the clean arithmetic reading:

- reset-adjacent context may help prepare a maximal gap;
- the maximal gap itself is not simply “the higher-divisor phase.”

## Current Claim

The current supported claim is:

Prime-gap type generation is best modeled, on the present reduced surface, by a
hierarchical finite engine with three visible pieces:

1. a persistent `14`-state core grammar;
2. a lag-2 local scheduler;
3. a small periodic gate with explicit reset behavior.

That engine now fits the observed pooled `256`-window concentration surface to
L1 error `0.0116`.

The remaining missing piece is narrower than before:

the long-horizon re-entry law that decides how local windows are chained into a
single stationary walk.
