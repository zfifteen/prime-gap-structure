# Bouncy Castle RSA Upper-Band V1 Experiment

Date: 2026-04-04

This report records the first modified Bouncy Castle experiment built from the vendored `r1rv83` source snapshot with one narrow RSA-specific change: generate RSA prime candidates only from the exact band that already satisfies BC's square-bound rule.

## Headline Result

The upper-band build materially improved direct-core `4096`-bit RSA key generation on the fixed `100`-run benchmark surface.

- Baseline total wall time was `169032.092789` ms (`169.032093` s).
- Upper-band `v1` total wall time was `102305.073667` ms (`102.305074` s).
- Measured speedup was `1.652236x`.
- Wall time fell by `39.475947%`.
- Throughput rose from `0.591604` to `0.977469` keypairs per second.

This confirms that the earlier measured `~42%` square-bound loss was wall-clock significant on the benchmark surface used here.

## Performance Comparison

| Metric | Baseline | RSA upper-band v1 | Change |
|---|---:|---:|---:|
| Total wall time (ms) | `169032.092789` | `102305.073667` | `-66727.019122` |
| Total wall time (s) | `169.032093` | `102.305074` | `-66.727019` |
| Mean time per keypair (ms) | `1690.320928` | `1023.050737` | `-667.270191` |
| Median time per keypair (ms) | `1498.037208` | `954.640542` | `-543.396666` |
| Minimum time per keypair (ms) | `269.134083` | `251.150958` | `-17.983125` |
| Maximum time per keypair (ms) | `4782.356125` | `2647.297750` | `-2135.058375` |
| Throughput (keypairs/s) | `0.591604` | `0.977469` | `+65.223568%` |

## Patch Summary

The experiment keeps the baseline BC source tree untouched and uses a sibling modified tree:

- Baseline tree:
  [`../vendor/bc-java-r1rv83/`](../vendor/bc-java-r1rv83/)
- Modified tree:
  [`../vendor/bc-java-r1rv83-rsa-upper-band-v1/`](../vendor/bc-java-r1rv83-rsa-upper-band-v1/)

Only one source file differs between those trees:

- [`../vendor/bc-java-r1rv83-rsa-upper-band-v1/core/src/main/java/org/bouncycastle/crypto/generators/RSAKeyPairGenerator.java`](../vendor/bc-java-r1rv83-rsa-upper-band-v1/core/src/main/java/org/bouncycastle/crypto/generators/RSAKeyPairGenerator.java)

The change is narrow:

- `chooseRandomPrime()` now computes the exact lower bound implied by BC's existing square-bound rule.
- A new RSA-local helper generates candidates only from that accepted band before the existing later checks run.
- The later square-bound line remains in place as an invariant check and did not fail during the `100`-run benchmark.
- `BigIntegers.java`, `Primes.java`, and the baseline vendored source tree were not modified.

## Test Setup

| Setting | Value |
|---|---|
| Artifact origin | `source-build-experiment` |
| Base Bouncy Castle source tag | `r1rv83` |
| Base Bouncy Castle source commit | `d4cc9614fc849e840ffdc7941f4a2941131d0c9c` |
| Experiment id | `rsa-upper-band-v1` |
| Built artifact | `bcprov-jdk18on-1.83.jar` |
| Built jar SHA-256 | `4f00588e9cd6088fcc7d9c7f7d0a36201834142bec3a09ae158a3dddf9932055` |
| Generator path | `org.bouncycastle.crypto.generators.RSAKeyPairGenerator` |
| Key size (bits) | `4096` |
| Timed iterations | `100` |
| Warmup iterations | `0` |
| Public exponent | `65537` |
| Certainty | `144` |
| SecureRandom algorithm | `SHA1PRNG` |
| Seed bytes | `[42]` |
| Build JDK | `openjdk version "25.0.2" 2026-01-20` |
| Runtime JDK | `openjdk version "21.0.10" 2026-01-20` |
| Runtime vendor | `Homebrew` |
| OS | `Mac OS X` |
| Architecture | `aarch64` |
| Started at UTC | `2026-04-04T19:14:29.199274Z` |
| Completed at UTC | `2026-04-04T19:16:11.498583Z` |

## Artifacts

- Canonical baseline result:
  [`bcprov-jdk18on-1.83-source-r1rv83-rsa4096-direct-core-seed-byte-42-runs-100.json`](./bcprov-jdk18on-1.83-source-r1rv83-rsa4096-direct-core-seed-byte-42-runs-100.json)
- Modified `v1` result:
  [`bcprov-jdk18on-1.83-source-r1rv83-rsa-upper-band-v1-rsa4096-direct-core-seed-byte-42-runs-100.json`](./bcprov-jdk18on-1.83-source-r1rv83-rsa-upper-band-v1-rsa4096-direct-core-seed-byte-42-runs-100.json)
- Strategy memo that motivated this patch:
  [`../BC_STRATEGY_DEEP_DIVE.md`](../BC_STRATEGY_DEEP_DIVE.md)

## Reproduction

Run the experiment again with:

```bash
./tests/performance-comparisons/bouncycastle-keygen-baseline/run_upper_band_v1.sh
```
