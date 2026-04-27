# BC Strategy Deep Dive

The no-patch probe answered the first transfer question directly. On the true Bouncy Castle post-`createRandomPrime()` surface, repo-style chunked-GCD tables through `300,007` and `1,000,003` rejected `0` additional candidates out of the `2,376` candidates that reached the BC probable-prime stage on the fixed `4,096`-candidate corpus. Both tables only added cost.

Measured post-`createRandomPrime()` totals from [the canonical probe result](./results/bcprov-jdk18on-1.83-source-r1rv83-rsa4096-strategy-probe-seed-byte-42.json):

| Variant | Added-table rejects | MR calls | Added-table time (s) | Total post-`createRandomPrime()` time (s) | Relative to current BC |
|---|---:|---:|---:|---:|---:|
| Current BC | `0` | `2,376` | `0.000` | `85.805` | `1.000x` |
| BC + chunked GCD to `300,007` | `0` | `2,376` | `22.897` | `108.788` | `0.789x` |
| BC + chunked GCD to `1,000,003` | `0` | `2,376` | `71.326` | `157.400` | `0.545x` |

The theoretical raw headroom from BC's current `<= 743` screen to these deeper limits was still large on paper: `47.2537%` to `300,007` and `51.8499%` to `1,000,003`. The probe shows that this headroom does not survive onto BC's actual post-`createRandomPrime()` stream.

The full probe wall time was `36.17` minutes. That is much larger than the modeled totals in the table because the modeled surface starts after `createRandomPrime()`, while the real run still had to spend most of its time generating the fixed `4,096`-candidate corpus through BC's existing `createRandomPrime()` path.

## 1. Grounded Repo Findings That Transfer To BC

The strongest validated repo result is still the deterministic factor-gated win on a less-conditioned candidate stream.

- The production Python path rejects composites only when it finds a concrete factor in gated prime tables, keeps survivors on the fixed-point convention `proxy_z = 1.0`, then runs fixed-base Miller-Rabin and final confirmation.
- The validated repo benchmark surface in [benchmarks.md](../../../docs/prefilter/benchmarks.md) reports about `91%` candidate rejection before Miller-Rabin and end-to-end deterministic RSA speedups of `2.09x` at `2048` bits and `2.82x` at `4096` bits.
- The repo's table-depth sweep in [RSA_TABLE_DEPTH_SWEEP_REPORT.md](../../../benchmarks/output/python/prefilter/rsa_table_depth_sweep/RSA_TABLE_DEPTH_SWEEP_REPORT.md) shows that deeper is not automatically better. On the tested Python RSA surface, `1,000,003` beat both `300,007` and `3,000,000`.
- The repo's broader structural findings remain real but separate from the production prefilter. In [raw_composite_z_gap_edge.md](../../../docs/gap_ridge/raw_composite_z_gap_edge.md), the exact raw composite field forms a near-edge low-divisor ridge, with edge-distance-`2` enrichment `1.965x` and `d(n) = 4` carrier enrichment `4.116x`. The leftmost minimizer rule also matched all tested gaps on the committed surface.

The transfer lesson is narrow. The repo gives BC one proven mechanism first: deterministic concrete-factor discovery before expensive probable-prime work. The probe says the question is not whether that mechanism matters in principle. The question is where BC still has access to a stream that has not already been conditioned past that opportunity.

## 2. Grounded BC Call-Path Analysis

The relevant BC call path is straightforward in the vendored `r1rv83` source.

- In [RSAKeyPairGenerator.java](./vendor/bc-java-r1rv83/core/src/main/java/org/bouncycastle/crypto/generators/RSAKeyPairGenerator.java), `generateKeyPair()` calls `chooseRandomPrime()` for both `p` and `q`.
- `chooseRandomPrime()` calls `BigIntegers.createRandomPrime(bitlength, 1, random)` first, then applies `p.mod(e)`, the `p * p >= sqrdBound` check, `isProbablePrime(p)`, and finally `gcd(e, p - 1)`.
- In [BigIntegers.java](./vendor/bc-java-r1rv83/core/src/main/java/org/bouncycastle/util/BigIntegers.java), `createRandomPrime()` already filters with the product of odd primes from `3` through `743`, then loops until `rv.isProbablePrime(1)` succeeds.
- In [Primes.java](./vendor/bc-java-r1rv83/core/src/main/java/org/bouncycastle/math/Primes.java), `hasAnySmallFactors()` still checks up to `211`, and `isMRProbablePrime()` then runs randomized Miller-Rabin.

The probe result says this conditioning is already decisive on the measured surface.

- `4,096` candidates were generated with `BigIntegers.createRandomPrime(2048, 1, random)`.
- `1,720` candidates, or `41.9922%`, were rejected only by the `p * p >= 2^4095` bound.
- `2,376` candidates, or `58.0078%`, reached the BC probable-prime stage.
- Of those `2,376`, current BC rejected `0` by `Primes.hasAnySmallFactors()`, `0` by `12` randomized MR rounds, and `0` by `gcd(e, p - 1)`.
- The pass share `58.0078%` is close to the exact uniform upper-band expectation $2 - \sqrt{2} = 58.5786\%$ for the square-bound cut. The post-`createRandomPrime()` stream therefore looks much more like an upper/lower range split than like a factor-rich composite stream.

That is the main BC-specific result from this round. On this surface, the only measured rejector after `createRandomPrime()` was the square-bound cut, not factor discovery.

## 3. Ranked Hypothesis Ladder

`H1` Evidence-backed, narrowed:
Deeper deterministic factor tables are still the primary artifact-adjacent transfer mechanism from this repo to BC, but the probe shows that mechanism has no remaining headroom after `createRandomPrime()` on the measured BC surface. If this repo improves BC, the factor-gated part has to move earlier.

`H2` Evidence-backed on the repo surface, not supported on this BC insertion point:
The repo's own RSA sweep favored about `1,000,003` rather than simply pushing deeper. On BC's post-`createRandomPrime()` surface, neither `300,007` nor `1,000,003` rejects anything, and `1,000,003` is only more expensive. The depth choice matters only if we first recover an earlier, less-conditioned candidate stream.

`H3` Medium-confidence, strengthened by the probe:
The best BC insertion point is earlier than randomized MR and likely earlier than `chooseRandomPrime()`'s current post-`createRandomPrime()` checks. The evidence is direct: the measured post-`createRandomPrime()` stream has zero factor-table headroom and zero MR headroom in this corpus.

`H4` Medium-confidence:
A fixed-base deterministic MR front-end is worth testing only after we move earlier in the candidate path, likely inside or immediately around `createRandomPrime()`. Testing it after `createRandomPrime()` but before BC's randomized MR is still possible, but this probe suggests the certainty=`1` `BigInteger.isProbablePrime()` screen has already done most of that work.

`H5` Speculative:
The gap-ridge, lexicographic, and residue-modulated findings may still help BC candidate ordering, especially if we open the candidate loop before the certainty=`1` probable-prime screen. Those findings are about structure inside a broader candidate field, not about the already-conditioned post-`createRandomPrime()` stream measured here.

## 4. Next BC Patch Candidates

The first BC code experiment should not be a late-stage table gate in `RSAKeyPairGenerator.isProbablePrime()`. The probe falsified that as a first move on the measured surface.

Ordered patch candidates:

1. Patch [BigIntegers.java](./vendor/bc-java-r1rv83/core/src/main/java/org/bouncycastle/util/BigIntegers.java) first, not [RSAKeyPairGenerator.java](./vendor/bc-java-r1rv83/core/src/main/java/org/bouncycastle/crypto/generators/RSAKeyPairGenerator.java).
   Add any repo-derived deterministic factor gating before `rv.isProbablePrime(1)` inside `createRandomPrime()`, where BC still has access to the raw odd-increment search path after the existing `<= 743` screen.

2. Treat the square-bound loss as a first-class BC opportunity.
   The probe measured `41.9922%` rejection at `p * p >= 2^4095`, and the observed pass share is close to the exact uniform upper-band expectation. That makes upper-band candidate bias inside `createRandomPrime()` a serious BC-specific strategy, because it attacks the only measured rejector on this surface.

3. If a pure factor-table patch inside `createRandomPrime()` is still weak, test a tighter early composite screen there.
   The next no-patch idea to lift into code would be repo-style factor tables plus a fixed-base deterministic MR front-end before BC reaches the later randomized MR path.

4. Deprioritize the later `gcd(e, p - 1)` path.
   For `e = 65537`, BC already checks `p.mod(e)` earlier. The probe measured `0` rejections at both stages, and the later gcd path is not the first place to look for keygen speed.

5. Keep the gap-ridge line as a second phase.
   If we later open the earlier candidate loop, the repo's lexicographic and residue findings may help candidate ordering or candidate bias. They should not be the first BC patch while the earlier deterministic screens remain untested.

This round therefore narrows the strategy sharply. The repo's measured win does not port to BC by adding a deeper factor table after `createRandomPrime()`. The next serious BC work should move earlier than that stage or change the distribution of candidates entering it.
