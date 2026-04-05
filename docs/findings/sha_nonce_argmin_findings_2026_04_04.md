# SHA Nonce Argmin Findings (2026-04-04)

This note records what the current SHA-256 nonce-line work actually supports, what remains open, and what experiment is next. It separates findings from mechanism stories.

## What Has Been Established

Three findings are supported by the current artifacts.

### 1. The argmin-position channel is distinct from the output-value channel

The reset-centered argmin experiment shows that the position of the minimum hash within a nonce window carries structure that is not captured by output-value probes.

The strongest control result is that the half-shifted arm removes the original raw alignment effect while the reset-centered profiles collapse onto a shared shape. In the current artifact:

- raw profile correlation is `-0.149`
- reset-centered profile correlation is `0.683`
- raw total variation distance is `0.0552`
- reset-centered total variation distance is `0.0285`

Those numbers show that the aligned and half-shifted conditions are reading the same underlying reset-centered positional structure from different phase origins.

### 2. The `k = 7` component matches a direct `ROTR7` model

The `k = 7` component of the observed mean reset-centered profile matches the direct `ROTR7` nonce-word model closely.

In the phase probe artifact:

- observed `k = 7` crest is `27.31`
- `ROTR7` model crest is `26.93`
- phase difference is `0.066` radians
- correlation between observed and modeled `k = 7` components is `0.9978`

The full `sigma0 = ROTR7 ^ ROTR18 ^ SHR3` model does not match that same component:

- `sigma0` crest is `17.79`
- phase difference is `1.637` radians
- correlation is `-0.0661`

So the supported conclusion is narrow and exact: the observed `k = 7` component aligns with direct `ROTR7`, not with full `sigma0`.

### 3. The aligned spectrum contains a strong 14-anchored family

The dominant harmonic in the observed mean reset-centered profile is `k = 27`, but the aligned spectrum also contains a strong anchor at `k = 14` and several other high-power terms near a `14n - 1` line.

For the aligned reset-centered profile, the strongest harmonics are:

```text
 1  k=27  amp=0.3032
 2  k=55  amp=0.2721
 3  k=14  amp=0.2416
 4  k=41  amp=0.2283
 5  k=75  amp=0.2148
 6  k=90  amp=0.2140
 7  k=71  amp=0.2133
 8  k=97  amp=0.2118
 9  k=86  amp=0.2113
10  k=15  amp=0.2102
```

The currently interesting 14-family candidates are:

```text
k    nearest 14n   delta
14      14          0
27      28         -1
41      42         -1
55      56         -1
71      70         +1
86      84         +2
97      98         -1
```

That is enough to say the 14-anchor is real and that a candidate `14n - 1` family exists. It is not enough to call it a closed law, because `71` and `86` are genuine departures.

## Where Mechanism Attribution Ran Ahead of the Data

The mechanism story for `k = 27` changed multiple times while being fitted against the same dataset. Those revisions were driven by re-analysis, not by new data.

That means the following are still hypotheses, not findings:

- `sigma1` / lag-7 beat attribution for `k = 27`
- 4-hop lag-7 chain attribution
- 2-hop lag-7 plus nonce-ramp cross-term attribution

The correct current statement is simpler:

- `k = 7` has a supported direct `ROTR7` explanation
- `k = 14` is a real aligned-spectrum anchor
- `k = 27` is the dominant observed harmonic
- the schedule-path mechanism for `k = 14`, `k = 27`, and the surrounding family is still open

## Why The Next Probe Is Different

The next planned experiment is not another reinterpretation of the existing `32,768`-window dataset. It is a new data-generating probe.

The planned probe is a nonce word-position sweep:

- move the nonce injection across selected second-block word positions
- rerun the reset-centered carry-window protocol
- extract crest offsets and amplitudes for the tracked harmonics

The minimum tracked set is:

- `k = 7`
- `k = 14`
- `k = 27`
- `k = 55`
- `k = 71`
- `k = 86`

The sweep matters because it can answer a question the current dataset cannot:

- do `k = 7` and the 14-anchored family move together under word-position changes, or do they travel through different schedule paths?

That is the first planned experiment that can materially discriminate between the current mechanism candidates.

## Honest State

The honest state of the project at this point is:

- one confirmed positional leakage channel: the reset-centered argmin-position channel
- one confirmed subcomponent identification: `k = 7` aligns with direct `ROTR7`
- one strong structural observation: a 14-anchored family exists in the aligned spectrum
- one dominant unexplained harmonic: `k = 27`
- one pre-registered next probe that can separate findings from mechanism stories

The progress is real, but not complete. The strongest unsupported move at this stage would be to describe the `k = 27` mechanism as settled before the word-position sweep runs.

## Source Artifacts

- [reset_centered_argmin_probe.json](../../benchmarks/output/python/sha_nonce/reset_centered_argmin_probe/reset_centered_argmin_probe.json)
- [reset_centered_argmin_probe.svg](../../benchmarks/output/python/sha_nonce/reset_centered_argmin_probe/reset_centered_argmin_probe.svg)
- [rotr7_phase_probe.json](../../benchmarks/output/python/sha_nonce/rotr7_phase_probe/rotr7_phase_probe.json)
- [rotr7_phase_probe.svg](../../benchmarks/output/python/sha_nonce/rotr7_phase_probe/rotr7_phase_probe.svg)
- [reset_centered_argmin_probe.py](../../benchmarks/python/sha_nonce/reset_centered_argmin_probe.py)
- [rotr7_phase_probe.py](../../benchmarks/python/sha_nonce/rotr7_phase_probe.py)
