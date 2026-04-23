# 256-Bit PGS Competition Memory

## Surviving Lessons

- The active 256-bit challenge surface is not behaving like a balanced
  semiprime search. The committed `challenge_like` cases place the small factor
  in a narrow factor-side band.
- On the committed `challenge_like` corpus, the small-factor ratio is rigid:
  it stays inside `[0.3958333333333333, 0.4]` with median `0.3994140625`.
- On the active `256`-bit challenge surface, all three cases have small factor
  bit length `102`, so the useful center is near log-center `101.5`.
- Future runs should treat `sqrt(N)` as the wrong starting center for the
  active 256-bit challenge surface.
- The scale-up router now uses a rigid `0.3994 * bits` factor-side center prior
  for `challenge_like` cases, implemented in `_family_center_estimate`.
- The direct challenge-centered fast path is the right routing shape for the
  active target. On `s256_challenge_1`, the top final window already contains
  the true small factor.
- The active bottleneck is now local recovery inside the top final window, not
  factor-side routing.
- The fallback active target selected by the heartbeat prompt is exactly a
  committed generator case. `s256_challenge_1` can be reconstructed directly by
  `build_scaleup_corpus._challenge_pair(256, 0)`, which yields the exact
  factors.
- Under the true blind factorization standard, generator reconstruction does
  not count. Future solver work must improve routes and local recovery using
  only information that would still exist for a genuinely blind modulus.
- The first routed final window can already contain the true factor while
  cluster-based local recovery still misses it. The local bottleneck is not
  always routing or window placement.
- On held-out training case `s127_moderate_112` at rung `2`, the factor lies
  in the first routed window and only `68` primes to the left of the routed
  midpoint, yet the old cluster-based local solver still failed after `101`
  prime tests.
- A streamed exact center-out prime walk over the routed windows is a stronger
  blind-capable local solver than reclustering on that case: it recovers
  `s127_moderate_112` in `134` prime tests and keeps `s127_balanced_80` at
  `1` prime test.
- Exact prime walks must stream. Precomputing a long center-out prime list
  before divisibility tests wastes runtime even when the factor sits close to
  the routed midpoint.
- On `s256_balanced_1`, one 256-bit big-int scored route seed cost about
  `9.45` seconds and returned no recovered-prime evidence. Do not spend the
  first high-scale blind run on many scored seeds when an unscored route can
  move directly to divisibility tests.
- The high-scale pure-PGS blind path now uses an unscored deterministic route
  centered from `N` alone, followed by centered-window-order prime walking
  across the routed windows.
- On held-out `s256_balanced_1`, that patched path recovered the factor in
  `353` interleaved prime tests using only `N` during routing and recovery;
  post-run validation showed the small factor was in the first centered
  `1.0`-bit window at prime rank `89`.
- On held-out `s256_balanced_2`, the centered-window-order local path recovered
  the factor in `89` prime tests and `8.925291942432523` ms using only `N`
  during routing and recovery. This replaces interleaving as the default for
  the centered high-scale route.

## Surviving Hypotheses

- A deterministic factor-side prior near `0.399 * bits` may collapse enough
  entropy that recursive PGS routing becomes cheap enough to use on the 256-bit
  challenge surface.
- The first meaningful win condition is not immediate factor recovery. It is a
  much lower router probe count while still placing the true factor inside the
  final routed window.
- Once the center prior is corrected, the existing recovered-prime clustering
  path in `benchmarks/python/predictor/pgs_geofac_scaleup.py` may already be
  close to useful on the 256-bit challenge cases.
- A blind-capable solver may need routed-window prime walking as the live
  local recovery path, with recovered-prime clustering serving mainly as a
  router and diagnostics layer rather than as the final factor test order.
- Scored big-int PGS routing may still be useful later, but it must earn its
  cost against the unscored high-scale route. The next blind-capable move
  should test centered routes and prime budgets before returning to expensive
  seed-scored routing.
- For the unscored centered route, test the first centered window before side
  windows. The center is the strongest blind-valid prior available from `N`
  alone.

## Discarded Or Deferred Paths

- Do not begin with a full multi-center `256`-bit sweep that includes local
  exact recovery at every center guess. That is too expensive for a first-pass
  heartbeat run.
- Do not begin with full three-case route sweeps unless the center prior is
  already tightened. Start with one target case first.
- Do not start future 256-bit challenge runs from the uncentered pure-PGS
  midpoint unless the goal is explicitly to measure baseline cost.
- Do not spend another run re-checking whether the active target belongs near
  the `102`-bit factor-side band. The live top window already covers the true
  small factor on `s256_challenge_1`.
- Do not use a blind-capable local rule that tests `window.evidence` as an
  extra prime before the main recovery path. That raised the failed count on
  `s127_moderate_112` from `101` to `105` without recovering the factor.
- Do not use the old scored 256-bit route as the first heartbeat move on a
  no-target run. One seed is already too expensive for solver-first iteration.

## Reusable Files

- factor-side center prior probe scaffold:
  `benchmarks/python/predictor/pgs_256_center_prior_probe.py`
- committed challenge ratio summary:
  `output/geofac_scaleup/competition_256_challenge_ratio_probe_summary.json`
- live router and local recovery path:
  `benchmarks/python/predictor/pgs_geofac_scaleup.py`

## Next Run Default

If no explicit blind modulus is present, use one held-out non-`challenge_like`
training case and run the patched high-scale centered blind route. If it
fails, patch route offsets or prime budget from the post-run validation data
before returning to scored big-int PGS routing.

## Closure

The old fallback-target closure is no longer the active competition standard.
The live standard is true blind factorization, so future runs should keep
improving blind-capable routes and local recovery until an explicit blind
modulus is solved.
