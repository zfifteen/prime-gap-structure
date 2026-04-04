# Bouncy Castle Direct-Core RSA Keygen Baseline

Date: 2026-04-04

This report records the canonical source-built baseline for direct Bouncy Castle
RSA key generation from vendored source tag `r1rv83`.

## Headline Performance Numbers

- The direct core path generated `100` `4096`-bit RSA keypairs in `169032.092789` ms total (`169.032093` s total).
- Mean time per keypair was `1690.320928` ms.
- Median time per keypair was `1498.037208` ms.
- Minimum observed time was `269.134083` ms and maximum observed time was `4782.356125` ms.
- Measured throughput was `0.591604` keypairs per second.

| Metric | Value |
|---|---:|
| Key size (bits) | 4096 |
| Timed iterations | 100 |
| Total wall time (ms) | 169032.092789 |
| Total wall time (s) | 169.032093 |
| Throughput (keypairs/s) | 0.591604 |
| Mean time per keypair (ms) | 1690.320928 |
| Median time per keypair (ms) | 1498.037208 |
| Minimum time per keypair (ms) | 269.134083 |
| Maximum time per keypair (ms) | 4782.356125 |

## Test Setup

| Setting | Value |
|---|---|
| Artifact origin | source-build |
| Bouncy Castle source tag | `r1rv83` |
| Bouncy Castle source commit | `d4cc9614fc849e840ffdc7941f4a2941131d0c9c` |
| Built artifact | `bcprov-jdk18on-1.83.jar` |
| Built jar SHA-256 | `0f7de9775ca37908dfb77d33964075e8b9ce9a92eab5e2695fbb194715ec709e` |
| Generator path | `org.bouncycastle.crypto.generators.RSAKeyPairGenerator` |
| Public exponent | `65537` |
| Certainty | `144` |
| Warmup iterations | `0` |
| SecureRandom algorithm | `SHA1PRNG` |
| Seed bytes | `[42]` |
| Build JDK | `openjdk version "25.0.2" 2026-01-20` |
| Runtime JDK | `openjdk version "21.0.10" 2026-01-20` |
| Runtime vendor | `Homebrew` |
| OS | `Mac OS X` |
| Architecture | `aarch64` |
| Started at UTC | `2026-04-04T17:43:12.635055Z` |
| Completed at UTC | `2026-04-04T17:46:01.667700Z` |

## Artifact Paths

- Canonical source-built result:
  [`bcprov-jdk18on-1.83-source-r1rv83-rsa4096-direct-core-seed-byte-42-runs-100.json`](./bcprov-jdk18on-1.83-source-r1rv83-rsa4096-direct-core-seed-byte-42-runs-100.json)
- Historical Maven-jar result:
  [`bcprov-jdk18on-1.83-rsa4096-direct-core-seed-byte-42-runs-100.json`](./bcprov-jdk18on-1.83-rsa4096-direct-core-seed-byte-42-runs-100.json)

## Reproduction

Run the baseline again with:

```bash
./tests/performance-comparisons/bouncycastle-keygen-baseline/run_baseline.sh
```
