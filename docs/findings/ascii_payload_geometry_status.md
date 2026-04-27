# ASCII Payload Geometry Status

This note records the current state of the SHA-side reordering work on the
contract stream used by the prime prefilter.

## Finding

Process progress is real. Breakthrough progress is not yet validated.

The carry-reset and decimal-rollover ranking ideas were retired by direct
contract-stream probes. The sharper replacement is ASCII payload geometry:
rank candidates by the leftmost changed character in the full payload
`namespace:bit_length:index:counter`, plus changed-digit count,
trailing-zero depth, and length-increase status.

On the first official steady-state run now committed in this repository, that
geometry ranking did not improve early prefilter arrival.

Across `512,000` tested `2048`-bit indices at production namespace
`cdl-prime-z-band`, the dominant geometry orderings
`combined`, `leftmost_first`, `changed_digits_first`, and
`trailing_zero_first` all produced the same result:

- baseline first-three prefilter remaining candidate mean position `21.5013`
- reordered first-three prefilter remaining candidate mean position `22.2600`
- position gain `-0.7587`
- relative change `-3.53%`

The same steady-state run showed only a tiny Miller-Rabin improvement:

- baseline first Miller-Rabin remaining candidate mean position `562.136`
- reordered first Miller-Rabin remaining candidate mean position `561.452`
- position gain `0.684`
- relative change `0.12%`
- Miller-Rabin advantage batch share `11.4%`

That is not a production-grade lift. The strongest supported reading so far is
that the current geometry ranking family has not yet delivered a useful
reordering lever on the steady-state contract stream.

## Real Progress

The work still produced real forward motion:

- the weak carry-reset idea is now closed by data rather than intuition,
- the repo now contains a contract-faithful geometry probe and a canonical
  two-run driver,
- the official steady-state benchmark surface is now committed as a reusable
  artifact rather than a one-off terminal experiment.

This is strong process progress and strong hypothesis elimination.

It is not yet the desired performance or theory breakthrough.

## Tested Surface

Earlier actual-stream probes already showed that simple decimal-window
groupings did not help:

- on a `2048`-bit `10,000`-index probe, baseline prefilter survival was
  `8.51%`,
- the first decile after each `10`-window survived at `7.8%`,
- the first decile after each `100`-window survived at `6.8%`,
- the first decile after each `1000`-window survived at `8.6%`,
- indices ending in `0` survived at `7.81%`,
- indices ending in `00` survived at `6.06%`.

The first official geometry run extended that negative picture at larger scale:

- steady-state regime: `512,000` indices, start index `100000`,
  batch size `1024`,
- baseline prefilter pass-through rate `8.9475%`,
- baseline Miller-Rabin pass-through rate `0.1363%`,
- no tested ordering produced useful prefilter advancement.

The committed feature table still shows a real local effect in rare regimes:

- the dominant class with `leftmost_delta_pos = 27`,
  `changed_digits = 1`, `trailing_zero_depth = 0` carries `90%` of the stream
  and survives the prefilter at `8.9616%`,
- the rarer class with `leftmost_delta_pos = 24`,
  `changed_digits = 4`, `trailing_zero_depth = 3` survives the prefilter at
  `11.0869%` and Miller-Rabin at `0.4348%`,
- but that rarer class appears only `460` times in `512,000` indices, so the
  current ordering does not convert that local enrichment into global arrival
  gain.

## Current Status

The canonical two-run helper was launched with timestamp `20260405T032424Z`.

- the steady-state artifact is complete and committed,
- the rollover companion run is still in progress at the time of this note,
- no claim is made yet about length-increase or rollover-dominated geometry.

## Decision Gate

The active gate stays simple:

- if the rollover regime produces a clear lift, integrate the winning ordering
  as an optional lightweight mode and re-run end-to-end benchmarks,
- if the rollover regime is also flat or negative, retire the full ranking
  family and pivot to the algorithmering path: a Rust or SIMD hot-path port of
  candidate generation, prefilter, and Miller-Rabin.

## Artifacts

- [ascii_delta_geometry_probe.py](../../benchmarks/python/sha_nonce/ascii_delta_geometry_probe.py)
- [run_ascii_delta_geometry_experiments.sh](../../benchmarks/python/sha_nonce/run_ascii_delta_geometry_experiments.sh)
- [steady-state official JSON](../../benchmarks/output/python/sha_nonce/ascii_delta_geometry_probe_run1_steady_20260405T032424Z/ascii_delta_geometry_probe.json)
