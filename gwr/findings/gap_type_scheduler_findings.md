# GWR Gap-Type Scheduler Findings

## Observable Facts

The extreme-scale comparison surface used in the current gap-type work is not a
single stationary run. It is a pool of sampled decade windows from `10^12`
through `10^18`, and each sampled surface has exactly `256` core rows.

That matters because the headline real concentration numbers

- one-step: `0.3284`
- two-step: `0.5059`
- three-step: `0.7594`

are pooled **256-window** concentrations, not concentrations of one long
stationary sequence.

The earlier million-step stress result compared a full stationary walk against
that pooled window target. That comparison was still useful because it exposed
the missing reset logic, but it mixed two distinct regimes:

- a full synthetic walk with no window resets;
- a real reference surface built from short local windows.

The scheduler probe aligns those regimes directly.

## Finite Scheduler Candidates

The new probe tests three deterministic models on the same persistent
`14`-state core:

1. `second_order_rotor`
   The existing baseline with no explicit scheduler.
2. `mod_cycle_scheduler`
   A simple `8`-phase global counter.
3. `lag2_state_scheduler`
   A finite scheduler whose phase is the reduced state two steps back. In
   ordinary language, the core grammar keeps one more remembered core symbol.

The exact summary is in
[../../output/gwr_dni_gap_type_scheduler_probe_summary.json](../../output/gwr_dni_gap_type_scheduler_probe_summary.json)
and the overview plot is
![Scheduler probe overview](../../output/gwr_dni_gap_type_scheduler_probe_overview.png)

## Main Result

The strongest supported result is:

The missing scheduler is already visible as a finite local-memory layer, and on
the aligned `256`-window surface the `lag2_state_scheduler` nearly closes the
higher-order gap.

Its pooled `256`-window concentrations are:

- one-step: `0.3245`
- two-step: `0.4988`
- three-step: `0.7504`

against the real pooled window target:

- one-step: `0.3284`
- two-step: `0.5059`
- three-step: `0.7594`

So the pooled concentration L1 error drops to `0.0201`.

For comparison:

- `second_order_rotor`: pooled concentration L1 `0.1390`
- `mod_cycle_scheduler`: pooled concentration L1 `0.0249`
- `lag2_state_scheduler`: pooled concentration L1 `0.0201`

So the `lag2_state_scheduler` cuts the pooled concentration error by about
`85.5%` relative to the current second-order baseline, and it is the best of
the tested finite schedulers.

## Why The Modulo Scheduler Matters

The simple `8`-phase global cycle is not the best model, but it is important.

Its pooled window concentrations are:

- one-step: `0.3263`
- two-step: `0.5006`
- three-step: `0.7769`

That is already close to the real pooled target, with pooled concentration L1
`0.0249`.

So a crude global reset rhythm already recovers most of the lost structure.
That is direct evidence that the missing layer is not just a richer local
alphabet. A slow scheduler really is part of the phenomenon.

## What The Full Million-Step Walk Still Says

The full stationary walk remains the diagnostic for what is still missing.

On the full `1,000,000`-step sequences:

- `second_order_rotor` three-step concentration: `0.3478`
- `mod_cycle_scheduler` three-step concentration: `0.3957`
- `lag2_state_scheduler` three-step concentration: `0.4900`

So even the best current scheduler is still too stationary. It improves the
full-walk three-step concentration materially, but it does not yet reproduce
the local-window intensity by itself.

That is the clean reading:

- the core grammar plus a finite scheduler already explains the observed local
  window structure very well;
- the remaining gap is about how windows are entered, reset, or re-phased
  across long horizons.

## Interpretation

The scheduler is now visible in two independent ways.

First, the `lag2_state_scheduler` says that the next transition depends not
only on the current pair of core states, but also on which core state the walk
occupied two steps earlier. That is a concrete finite-memory law.

Second, the `8`-phase modulo scheduler says that a very small global rhythm can
recover most of the same pooled-window structure. That points to local epoch
control rather than an unstructured stationary process.

Together those results sharpen the working architecture:

1. a fast local grammar on the persistent `14`-state core;
2. a finite scheduler that controls local window phase;
3. a still-missing reset law that decides how one local regime hands off to
   the next over long horizons.

## Current Claim

The current supported claim is:

There exists a finite deterministic scheduler layer above the persistent
`14`-state core, and when the model is scored on the same `256`-window regime
as the real `10^12..10^18` surface, that scheduler closes most of the observed
higher-order concentration gap.

What is not yet supported is the stronger stationary claim that one unreset
million-step walk fully reproduces the same concentration surface. The new data
shows exactly where that remaining gap lives: in long-horizon re-entry and
phase-reset behavior.
