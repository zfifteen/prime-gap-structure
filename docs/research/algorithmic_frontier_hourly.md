## 2026-04-11 03:47 run
Claim:
On a deterministic 200-step consecutive surface starting at the first prime at or above 10^13, the current bounded GWR/DNI walker is not computationally superior to direct `sympy.nextprime` for immediate next-prime recovery.
Method:
Timed 200 consecutive recoveries from q = 10000000000037 with `benchmarks/python/predictor/gwr_dni_recursive_walk.py:bounded_next_gap_profile`, then timed 200 consecutive `sympy.nextprime(q)` recoveries on the same chain and compared the final primes.
Result:
The bounded walker took 0.9152082090149634 s. The `sympy.nextprime` baseline took 0.002706792001845315 s. The walker was slower by 338.11545489680543x. Both runs ended at 10000000005521, so the walker matched the same 200-step chain on this surface.
Verdict:
supported
Artifacts:
docs/research/algorithmic_frontier_hourly.md

## 2026-04-11 03:55 run
Mechanism:
Wheel-open first-`d=4` witness handoff: detect the first wheel-open composite with `d(n)=4` after known prime `q`, then start classical next-prime search from that witness instead of from `q`.
Why it could help:
It removes full primality tests on every wheel-open candidate at or before the witness, and the GWR/DNI near-edge `d=4` structure says that witness often appears very early.
Method:
Ran one exact deterministic consecutive-gap sweep through right prime `<= 10^7`, and counted wheel-open candidate-primality tests for baseline wheel search versus a hybrid that hands off at the first in-gap wheel-open `d=4` witness and otherwise falls back to baseline.
What was built or tested:
An in-shell Python prototype used `src/python/z_band_prime_composite_field/field.py:divisor_counts_segment` to compute exact gap interiors, locate the first in-gap wheel-open `d=4` witness offset, and total the baseline and hybrid wheel-candidate test counts.
Result:
On `664,575` consecutive gaps, the witness existed in `425,526` gaps (`64.03%`). Mean wheel-candidate primality tests fell from `4.0126` to `3.0758`, a reduction of `0.9368` tests per gap or `23.35%` overall. In applicable gaps the mean reduction was `1.4630` tests, and `78.59%` of applicable gaps exposed the handoff by offsets `2/4/6`.
Status:
ADVANCE
Artifacts:
`docs/research/algorithmic_frontier_hourly.md`; in-shell Python experiment output with `applicable_share = 0.6402979347703419`, `overall_reduction_fraction = 0.23345507100072263`, and top witness offsets `(6, 120434)`, `(4, 107183)`, `(2, 106819)`.
Next step:
Replace the exact `d(n)=4` oracle in this same handoff with a deterministic low-cost wheel-open semiprime witness detector and re-measure the same candidate-test reduction surface.

## 2026-04-11 04:08 run
Mechanism:
Short-table certified opening-prefix pruning: skip the longest initial wheel-open prefix whose members each have a fixed small-prime divisor certificate, then start classical prime testing at the first uncertified candidate.
Why it could help:
It replaces full candidate primality tests on a guaranteed-composite opening prefix with a short fixed set of modulus checks and avoids full interval divisor-count construction.
Method:
Ran one deterministic consecutive-gap sweep through current right prime `< 10^7`, swept fixed certificate tables from `{7}` through primes `<= 47`, and counted baseline wheel-candidate prime tests versus a safe hybrid that prunes only individually certified opening-prefix candidates.
What was built or tested:
An in-shell Python prototype enumerated wheel-open candidates in each exact gap, certified each opening-prefix candidate by divisibility against the fixed table, stopped at the first uncertified candidate, and tallied the remaining full candidate primality tests.
Result:
On `664,575` consecutive gaps, the best tested short table was primes `<= 47`, which certified a nonempty opening prefix in `338,906` gaps (`51.00%`). Full wheel-candidate prime tests fell from `2,666,669` to `2,053,701`, a reduction of `612,968` tests or `22.99%` overall; mean tests per gap fell from `4.0126` to `3.0902`, with `1.8087` tests saved on applicable gaps. The certified prefix reached lengths `1/2/3/4` in `178,158 / 91,784 / 41,456 / 16,486` gaps, and the sweep improved monotonically from `{7}` (`4.15%`) up to primes `<= 47` (`22.99%`).
Status:
ADVANCE
Artifacts:
`docs/research/algorithmic_frontier_hourly.md`; in-shell Python experiment output with the short-table sweep over `{7}` through primes `<= 47` and exact best-table counts `applicable_gaps = 338906`, `saved_tests = 612968`, `overall_reduction_fraction = 0.22986279887005098`.
Next step:
Compress the primes-`<= 47` certificate rule into a residue lookup and test the same safe prefix-pruning yield on a higher-scale surface.

## 2026-04-11 05:04 run
Mechanism:
Fixed small-prime opening-prefix pruning at higher scale: certify the initial wheel-open prefix by divisibility against primes `<= 47`, then start full prime testing at the first uncertified candidate.
Why it could help:
It swaps expensive full primality tests for a short deterministic divisibility screen on the composite-dense opening prefix that GWR/DNI places near the left endpoint.
Method:
Ran one deterministic 100,000-gap consecutive sweep starting at the first prime `>= 10^12`, used `sympy.nextprime` only to obtain the true next-prime endpoint, counted baseline wheel-open candidate tests, and subtracted only the contiguous opening prefix individually certified composite by primes `<= 47`.
What was built or tested:
An in-shell Python prototype walked 100,000 consecutive gaps from `q = 1000000000039`, computed the certified opening-prefix length for each gap with the fixed table `(7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47)`, and tallied the remaining full candidate tests.
Result:
On this `10^12` surface, baseline wheel-open candidate tests totaled `736,450` and the fixed-table hybrid totaled `644,121`, so the mechanism removed `92,329` full candidate tests or `12.54%` overall. A nonempty certified opening prefix appeared in `50,766` gaps (`50.77%`), the mean full-test count fell from `7.3645` to `6.44121`, the mean saving stayed at `0.92329` tests per gap, and the longest certified prefix observed was `11` wheel-open candidates.
Status:
ADVANCE
Artifacts:
`docs/research/algorithmic_frontier_hourly.md`; in-shell Python experiment output with `start_prime = 1000000000039`, `saved_total = 92329`, `overall_reduction_fraction = 0.12537035779754227`, `applicable_share = 0.50766`, and prefix histogram head `[(1, 26487), (2, 13747), (3, 6351), (4, 2518), (5, 1054)]`.
Next step:
Encode the same primes-`<= 47` opening-prefix rule as a straight-line pretest in the repo’s prime-search path and count the resulting Miller-Rabin call reduction on the existing candidate corpora.

## 2026-04-11 06:04 run
Mechanism:
Residue-mask opening-prefix lookup for primes `<= 47`: precompute, from `q mod 30` and `q mod p`, which of the first wheel-open candidates after `q` are individually certified composite, then hand classical next-prime search to the first uncertified candidate.
Why it could help:
It keeps the same GWR/DNI-guided opening-prefix pruning while replacing candidate-by-candidate small-prime divisibility checks with `12` table lookups, bitwise OR, and a leading-ones scan.
Method:
Ran one deterministic `100,000`-gap consecutive sweep starting at the first prime `>= 10^12`, built `64`-bit masks for each `(q mod 30, q mod p)` state with primes `(7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47)`, and compared the lookup-predicted certified opening prefix against the direct divisibility-certified prefix on every gap.
What was built or tested:
An in-shell Python prototype precomputed `2,544` state entries, one mask table per prime, OR-ed the `12` masks selected by the current right-prime residues, and recovered the contiguous certified opening prefix by scanning the low bits of the combined mask.
Result:
On the same `10^12` surface from `q = 1000000000039`, the residue-mask lookup matched the direct primes-`<= 47` certificate prefix on all `100,000` gaps with `0` mismatches. It therefore reproduced the same hybrid gain exactly: baseline wheel-open candidate tests `736,450`, hybrid tests `644,121`, saved tests `92,329`, overall reduction `12.54%`, and applicable-gap share `50.77%`. The longest certified opening prefix observed was `11`, so the `64`-bit mask left wide headroom on this surface, and the full lookup surface fits in `20,352` bytes at one `uint64` per state.
Status:
ADVANCE
Artifacts:
`docs/research/algorithmic_frontier_hourly.md`; in-shell Python output with `mismatch_count = 0`, `saved_tests = 92329`, `overall_reduction_fraction = 0.12537035779754227`, `state_entries = 2544`, and `u64_table_bytes = 20352`.
Next step:
Thread this same residue-mask lookup into one straight-line next-prime search prototype and count the full candidate-primality tests it removes on the same `10^12` surface.

## 2026-04-11 07:17 run
Mechanism:
Residue-mask opening-prefix front gate for next-prime search: use `q mod 30` plus `q mod p` for primes `<= 47` to skip the initial wheel-open candidates that are individually certified composite, then begin full primality testing at the first uncertified candidate.
Why it could help:
It replaces a nontrivial share of full `isprime` calls near the left edge of each gap with `12` table lookups, one bitwise OR reduction, and a leading-ones scan.
Method:
Ran one deterministic `100,000`-gap consecutive sweep starting at the first prime `>= 10^13`, comparing a baseline wheel-open next-prime loop against the same loop with the residue-mask-certified opening prefix skipped before any `isprime` call.
What was built or tested:
An in-shell Python prototype precomputed the `2,544` lookup states for primes `(7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47)`, used the masks to recover the certified opening-prefix length at each current right prime, and then ran the straight-line hybrid search loop to the same next prime.
Result:
On the `10^13` surface from `q = 10000000000037`, the hybrid found the same `100,000`-prime chain with `0` mismatches while cutting full `isprime` calls from `797,327` to `704,873`. That removed `92,454` expensive calls, a reduction of `11.60%` overall. A nonempty certified opening prefix appeared in `50,914` gaps (`50.91%`), the mean full-test count fell from `7.97327` to `7.04873`, the mean saving was `0.92454` calls per gap, and the longest certified prefix observed was `12` wheel-open candidates.
Status:
ADVANCE
Artifacts:
`docs/research/algorithmic_frontier_hourly.md`; in-shell Python output with `start_prime = 10000000000037`, `saved_isprime_calls = 92454`, `saved_call_fraction = 0.11595493442464636`, `applicable_gap_share = 0.50914`, `max_prefix = 12`, `state_entries = 2544`, and `u64_table_bytes = 20352`.
Next step:
Run this same residue-mask front gate against a Miller-Rabin-backed next-prime loop so the saved expensive calls are counted in the probable-prime regime rather than only in `sympy.isprime`.

## 2026-04-11 08:07 run
Mechanism:
Residue-mask opening-prefix front gate for exact next-prime search: use `q mod 30` plus `q mod p` for primes `<= 47` to skip the initial wheel-open candidates that are individually certified composite before fixed-base Miller-Rabin and final exact confirmation.
Why it could help:
It can remove left-edge Miller-Rabin work by turning the GWR/DNI composite-heavy opening prefix into a constant-size lookup.
Method:
Ran one deterministic `100,000`-gap consecutive sweep starting at the first prime `>= 10^13`, comparing a baseline exact wheel-open search (`miller_rabin_fixed_bases` plus final `sympy.isprime`) against the same search with the residue-mask-certified opening prefix skipped first.
What was built or tested:
An in-shell Python prototype precomputed the same `2,544` lookup states (`20,352` bytes as `uint64` masks), executed both exact search loops over the same prime chain, and counted Miller-Rabin calls, candidates that reached modular exponentiation, modular-exponentiation `pow` calls, and elapsed time.
Result:
On the `10^13` surface from `q = 10000000000037`, both paths recovered the same `100,000`-prime chain. The hybrid cut Miller-Rabin entry calls from `797,327` to `704,873`, saving `92,454` calls (`11.60%`). But the repo’s Miller-Rabin path already rejects divisibility by primes `<= 37` before modular exponentiation, so only `7,175` skipped candidates would have reached the exponentiation path. Total `pow` calls fell only from `2,013,551` to `1,999,209`, a reduction of `14,342` (`0.712%`), and total wall time worsened slightly from `5.9585 s` to `6.0804 s` (`0.980x`).
Status:
FAILED
Artifacts:
`docs/research/algorithmic_frontier_hourly.md`; in-shell Python output with `saved_mr_calls = 92454`, `saved_pow_calls = 14342`, `saved_pow_fraction = 0.0071227398759703625`, `saved_pow_candidates = 7175`, `baseline_elapsed_s = 5.958472915983293`, `hybrid_elapsed_s = 6.080358917010017`, `state_entries = 2544`, and `u64_table_bytes = 20352`.
Next step:
Fold the same residue-mask lookup into the pre-Miller-Rabin small-prime stage itself so the lookup replaces existing divisibility work instead of duplicating it.

## 2026-04-11 09:07 run
Mechanism:
Propagated endpoint-state 64-open residue mask: carry `q mod p` for primes `<= 37` and replace the candidate-by-candidate small-prime gate on the first `64` wheel-open candidates with one combined certification mask.
Why it could help:
The GWR/DNI edge structure says the useful composite information is endpoint-local, so one small residue state can certify most of the early search window without per-candidate divisor checks.
Method:
Ran one deterministic `100,000`-gap consecutive sweep starting at the first prime `>= 10^13`, comparing a baseline exact wheel-open next-prime loop against a hybrid that propagated the endpoint residue state across gaps, OR-ed nine precomputed masks, and sent only uncertified positions to bare Miller-Rabin plus final exact confirmation.
What was built or tested:
An in-shell Python prototype precomputed `1,496` `uint64` state entries for primes `(7, 11, 13, 17, 19, 23, 29, 31, 37)`, covering the first `64` wheel-open offsets for each `(q mod 30, q mod p)` state, then ran both exact search loops on the same `100,000`-prime chain while updating the residue state by the realized gap offset after each step.
Result:
On the `10^13` surface from `q = 10000000000037`, the hybrid matched all `100,000` next primes with `0` mismatches and resolved `99,989` gaps (`99.989%`) entirely inside the masked `64`-open window. Candidate-side small-prime modulus checks fell from `5,145,085` to `794`, plus `9` initial residue mods to seed the state, a `99.984%` reduction in that stage. Miller-Rabin calls and modular-exponentiation `pow` calls stayed identical at `444,678` and `2,013,551`, while wall time improved from `5.7923 s` to `5.6795 s` (`1.0199x`).
Status:
ADVANCE
Artifacts:
`docs/research/algorithmic_frontier_hourly.md`; in-shell Python output with `mask_width = 64`, `state_entries = 1496`, `u64_table_bytes = 11968`, `saved_small_prime_mods = 5144282`, `saved_small_prime_mod_fraction = 0.9998439287203224`, `resolved_in_window_fraction = 0.99989`, `baseline_elapsed_s = 5.7923303749994375`, and `hybrid_elapsed_s = 5.6794587500044145`.
Next step:
Replace the in-shell prototype with the same propagated `64`-open mask inside one repo next-prime search path and remeasure on the same `10^13` consecutive surface.

## 2026-04-11 10:06 run
Mechanism:
Propagated endpoint-state `64`-open residue mask for exact next-prime search: carry `q mod p` for primes `<= 37` and replace the first `64` wheel-open candidate-side small-prime checks with one combined certification mask.
Why it could help:
It collapses the composite-heavy left edge of each next-prime search into `9` carried residues plus one mask OR, removing most repeated small-prime modulus work before Miller-Rabin.
Method:
Moved the mechanism out of an in-shell prototype into one repo benchmark script, then ran one deterministic `100,000`-gap consecutive sweep from `q = 10000000000037` comparing the exact baseline wheel-open loop against the exact endpoint-mask loop.
What was built or tested:
Added `benchmarks/python/predictor/gwr_dni_boundary_state_mask_search.py`, which precomputes `1,496` `uint64` certification states, propagates the nine carried residues by the realized gap offset, and verifies exact chain parity against the baseline path on every step.
Result:
On the same `10^13` surface, the new repo prototype matched all `100,000` next primes with `0` mismatches and resolved `99,989` gaps (`99.989%`) inside the masked `64`-open window. Candidate-side small-prime modulus checks fell from `5,145,085` to `794`, plus `9` initial residue mods, a `99.9846%` reduction in that stage. Miller-Rabin, `pow`, and final `isprime` call counts stayed identical at `444,678`, `2,013,551`, and `100,000`, while wall time improved from `5.9371 s` to `5.6934 s` (`1.0428x`).
Status:
ADVANCE
Artifacts:
`benchmarks/python/predictor/gwr_dni_boundary_state_mask_search.py`; `docs/research/algorithmic_frontier_hourly.md`; script output with `state_entries = 1496`, `u64_table_bytes = 11968`, `saved_small_prime_mods = 5144291`, `resolved_in_window_fraction = 0.99989`, and `elapsed_speedup = 1.0428044811527897`.
Next step:
Extend the same propagated endpoint-state mask just far enough to absorb the remaining `11` fallback gaps and rerun the same exact search loop.

## 2026-04-11 11:03 run
Mechanism:
Propagated endpoint-state `96`-open residue mask for exact next-prime search: carry `q mod p` for primes `<= 37` and certify the first `96` wheel-open candidates from one endpoint mask before bare Miller-Rabin.
Why it could help:
It widens the same endpoint-local compressed state just enough to absorb the remaining fallback gaps, so the candidate-by-candidate small-prime gate can disappear entirely after the initial residue seed.
Method:
Derived the exact required search depth on the existing `10^13` chain by measuring the realized wheel-open index of the true next prime on each of `100,000` consecutive gaps, then reran the exact endpoint-mask hybrid once at `96` opens on that same chain.
What was built or tested:
An in-shell Python prototype found that only `11` gaps exceeded the current `64`-open window and that the deepest required wheel-open position was `93`, then rebuilt the carried-residue mask at width `96` and reran the repo's exact baseline and hybrid loops from `q = 10000000000037`.
Result:
On the same `100,000`-gap `10^13` surface, the `96`-open mask matched the exact chain with `0` mismatches and resolved all `100,000` gaps inside the mask (`100%`). Candidate-side small-prime modulus checks fell from `5,145,085` to `0`, plus `9` initial seed-residue mods, so the recurring small-prime gate was eliminated entirely on this surface. Miller-Rabin, `pow`, and final `isprime` counts stayed identical at `444,678`, `2,013,551`, and `100,000`, while wall time still improved from `5.9298 s` to `5.7318 s` (`1.0345x`).
Status:
ADVANCE
Artifacts:
`docs/research/algorithmic_frontier_hourly.md`; in-shell Python output with `max_open_index = 93`, `count_gt_64 = 11`, `mask_width = 96`, `resolved_in_window_fraction = 1.0`, `saved_small_prime_mod_fraction = 1.0`, `estimated_u64_table_bytes = 23936`, and `elapsed_speedup = 1.034540059922176`.
Next step:
Rerun this same full-coverage endpoint-state mask at the exact observed ceiling of `93` wheel-open positions to see whether the no-fallback gain survives with no extra mask slack.

## 2026-04-11 12:00 run
Mechanism:
Current-gap DNI transition lookup: use `(q mod 30, current gap width, current dmin, current peak offset)` to jump directly to the next prime by exact next-gap-width lookup.
Why it could help:
If exact, it would replace the unbounded exact DNI interior scan with one lookup and remove nearly all next-gap divisor work on supported states.
Method:
Deterministic experiment.
What was built or tested:
An in-shell Python experiment built the lookup from exact transition rows with current right prime `<= 10^5` via `benchmarks/python/predictor/gwr_dni_transition_probe.py:transition_rows`, kept only signatures with one observed next gap width, and tested that frozen map on `1,000` consecutive exact next-gap steps starting at `q = 10000000000037` using `benchmarks/python/predictor/gwr_dni_recursive_walk.py:exact_next_gap_profile`.
Result:
The mechanism failed under scale transfer. The training surface produced only `234` unique supported states. On the `1,000`-gap `10^13` chain, the lookup applied to `85` gaps (`8.5%`) and was exact on only `4` of them (`4.71%` of applicable, `0.4%` overall). Even counting only those `4` exact direct jumps, it would remove just `30` scanned offsets out of `29,844` total (`0.10%`).
Status:
FAILED
Artifacts:
`docs/research/algorithmic_frontier_hourly.md`; in-shell Python output with `train_rows = 9591`, `train_unique_states = 234`, `applicable = 85`, `exact = 4`, `baseline_offsets = 29844`, `saved_offsets_if_jump_on_exact_supported_states = 30`, and `saved_offset_fraction_total = 0.0010052271813429834`.
Next step:
Test the same transition law again only with a fixed next-gap DNI prefix if it can gain cross-scale exact support without collapsing into a near-one-state-per-gap table.

## 2026-04-12 daily run
Mechanism:
Winner-location prediction from the locked 12-offset prefix: after the fixed prefix scan yields `delta <= 3`, no later composite can undercut that divisor class, so the lex-min state `(delta, omega)` already identifies an interior witness `W = q + omega`, and `nextprime(W - 1)` recovers the exact endpoint.
Why it could help:
It replaces the remaining divisor-count walk to the endpoint with one fast next-prime recovery call once the prefix lock holds.
Method:
Compared the live bounded walker against the pre-shortcut bounded scan reproduced verbatim from the earlier prefix-plus-extended-loop logic on two verified lock-triggering primes.
What was built or tested:
Verified the live `benchmarks/python/predictor/gwr_dni_recursive_walk.py:bounded_next_gap_profile` on `q = 229433` and `q = 1026167`, tracked its `divisor_counts_segment` calls, and compared the returned endpoint against the reconstructed old bounded loop that kept counting divisors until the prime endpoint.
Result:
For `q = 229433`, the locked prefix gives `delta = 3` at `omega = 8`. The live lock path used exactly `12` divisor-count calls plus one `nextprime` recovery and returned `229459`, while the old bounded loop used `26` divisor-count calls to reach the same endpoint, eliminating `14` divisor-count operations (`53.85%`). For `q = 1026167`, the locked prefix gives `delta = 3` at `omega = 2`. The live lock path again used `12` divisor-count calls plus one `nextprime` recovery and returned `1026197`, while the old bounded loop used `30` divisor-count calls, eliminating `18` divisor-count operations (`60%`). In both cases the recovered endpoint was identical.
Status:
ADVANCE
Artifacts:
`benchmarks/python/predictor/gwr_dni_recursive_walk.py`; `tests/python/predictor/test_gwr_dni_recursive_walk.py`; `docs/research/algorithmic_frontier_hourly.md`; in-shell verification output with old bounded call counts `26` and `30`, live prefix-path divisor-count calls `12` and `12`, and exact recovered endpoints `229459` and `1026197`.
Next step:
Derive an exact `delta = 4` sub-condition from the Z-band invariants that certifies when the same winner-location prediction can fire without any extended scan.

## 2026-04-12 20:17 run
Mechanism:
Winner-anchored tail scan: once the DNI/GWR lex-min localizer has identified the leftmost minimum-divisor carrier at offset `omega`, recover the next-prime endpoint by scanning only from `q + omega + 1` forward instead of from `q + 1`.
Why it could help:
It removes the left prefix `[q + 1, q + omega]` from the exact divisor-field endpoint search. Because the lex-min carrier stays near the left edge on the tested surface, that cuts pure DNI/GWR search width before any classical machinery enters.
Method:
Deterministic experiment.
What was built or tested:
An in-shell Python experiment used `benchmarks/python/predictor/gwr_dni_recursive_walk.py:exact_next_gap_profile` to collect `5,000` consecutive exact next-gap profiles starting at `q = 10000000000037`, then timed the same exact divisor-field endpoint scan twice on that chain: once from `q + 1`, and once from the exact winner anchor `q + omega + 1`.
Result:
The winner-anchored scan matched the same `5,000` next primes with `0` mismatches. Mean exact gap width was `29.6308`, mean winner offset was `5.9066`, and the exact search width after the winner was `23.7242`, so the DNI/GWR anchor removed `19.93%` of the pure endpoint-search width. In the current `64`-wide block implementation that reduced divisor-field reads from `356,736` to `347,264` (`2.66%`) and improved endpoint-scan wall time from `11.0483 s` to `10.7264 s` (`1.0300x`).
Status:
ADVANCE
Artifacts:
`docs/research/algorithmic_frontier_hourly.md`; in-shell Python output with `steps = 5000`, `search_width_saved_fraction_exact = 0.19933987607489503`, `baseline_integers_read = 356736`, `anchor_integers_read = 347264`, and `elapsed_speedup = 1.0300109322761077`.
Next step:
Inline the same winner-anchored tail scan into the exact recursive walker after lex-min localization and re-measure the end-to-end pure DNI/GWR step gain.

## 2026-04-12 21:10 run
Mechanism:
Current-lex-min clipped divisor classification: in a pure DNI/GWR exact next-prime walk, evaluate each new interior candidate only up to the current winning divisor class `delta - 1`, and stop the factor work as soon as the candidate is forced above that threshold.
Why it could help:
Once the walk has already seen a candidate with divisor class `delta`, no later value with `d(n) >= delta` can change the lex-min state. That means most later composites do not need full divisor evaluation.
Method:
Deterministic experiment.
What was built or tested:
An in-shell Python sandbox built two candidate-by-candidate pure DNI/GWR exact walkers on the same `1,000`-gap chain starting at `q = 100000007`: a baseline that computed each interior `d(n)` exactly, and a clipped walker that used the live lex-min threshold `stop_at = delta - 1` to abort factor work as soon as a candidate could no longer improve the state.
Result:
The clipped walker recovered the same `1,000` consecutive next primes with `0` mismatches and reached the same final prime `100018627`. Wall time fell from `0.10189116699621081 s` to `0.05691070796456188 s` (`1.7903689945248638x` speedup). On the same chain it reduced prime-factor trial steps from `718,602` to `317,108` (`55.87%`), factor divisions from `48,725` to `32,592` (`33.11%`), residual primality checks from `18,652` to `4,248` (`77.22%`), and residual square checks from `6,758` to `1,501` (`77.79%`). The exact next-gap minimum was `d = 4` on `749` of the `1,000` gaps, so the live threshold usually collapsed quickly to the `3`-class test.
Status:
ADVANCE
Artifacts:
`docs/research/algorithmic_frontier_hourly.md`; in-shell Python experiment output with `start_q = 100000007`, `steps = 1000`, `speedup = 1.7903689945248638`, `prime_trial_reduction_fraction = 0.55871539461343`, and `residual_prime_check_reduction_fraction = 0.7722496247051255`.
Next step:
Move the same clipped-divisor rule into a repo-side predictor prototype and re-measure it against the current vectorized exact walk.

## 2026-04-12 22:05 run
Mechanism:
Current-lex-min clipped divisor classification: after the exact DNI/GWR prefix scan fixes the live minimum divisor class `delta`, classify each later interior candidate only up to `delta - 1` instead of recomputing its full divisor count.
Why it could help:
Once a candidate with divisor class `delta` is already known, any later value with `d(n) >= delta` cannot change the lex-min state. That can cut exact divisor work inside the pure DNI/GWR next-prime walk itself.
Method:
Deterministic experiment.
What was built or tested:
An in-shell Python repo-side prototype kept the current `12`-offset `divisor_counts_segment` prefix from `benchmarks/python/predictor/gwr_dni_recursive_walk.py:exact_next_gap_profile`, then replaced the tail's full `64`-wide block divisor-count scan with candidate-by-candidate clipped classification that stopped factor work at `delta - 1` after each lex-min update.
Result:
On `1,000` consecutive exact next-gap steps starting at `q = 1000000000039`, the clipped prototype matched the current `exact_next_gap_profile` with `0` mismatches and reached the same final prime `1000000027591`. Wall time fell from `1.4655225839815103 s` to `1.1192784579470754 s` (`1.3093458321975557x`). On the same chain, the current exact walk read `69,248` block slots while the clipped prototype inspected only the `27,552` actual candidates up to the true next primes, removing `41,696` slot evaluations (`60.21256931608133%`).
Status:
ADVANCE
Artifacts:
`docs/research/algorithmic_frontier_hourly.md`; in-shell Python output with `start_q = 1000000000039`, `steps = 1000`, `speedup = 1.3093458321975557`, `segment_slots_read_by_current_exact_walk = 69248`, `candidate_visits_exact_gap_width = 27552`, and `saved_fraction = 0.6021256931608133`.
Next step:
Inline the same clipped-divisor tail into the exact recursive walker and re-measure the repo path on the same `10^12` chain.

## 2026-04-12 23:06 run
Mechanism:
Current-lex-min clipped divisor classification in the exact DNI/GWR recursive walk: after the fixed 12-offset prefix sets the live minimum divisor class `delta`, classify each later candidate only up to `delta - 1` instead of reading full divisor-count blocks through the endpoint.
Why it could help:
Once a candidate with divisor class `delta` is already known, no later value with `d(n) >= delta` can change the lex-min state. That removes unnecessary exact divisor-field work from the pure DNI/GWR next-prime walk itself.
Method:
sandbox prototype.
What was built or tested:
Patched `benchmarks/python/predictor/gwr_dni_recursive_walk.py` so the live unbounded runtime path uses `_exact_next_gap_profile_clipped(...)`, which keeps the existing 12-offset prefix scan and then switches to capped single-candidate classification; measured that path against the old `exact_next_gap_profile(...)` block scan on `1,000` consecutive steps starting at `q = 1000000000039`.
Result:
The patched unbounded walk matched the old exact oracle on all `1,000` steps and reached the same final prime `1000000027591`. Wall time fell from `1.5411759580019861 s` to `1.134829582995735 s` for a `1.3580681902330864x` speedup. Exact divisor-field segment reads fell from `69,248` slots to `12,000`, removing `57,248` slots or `82.67097966728281%`, and the live path made only the prefix segment read on the known long-gap anchor `q = 24098209`.
Status:
ADVANCE
Artifacts:
`benchmarks/python/predictor/gwr_dni_recursive_walk.py`; `tests/python/predictor/test_gwr_dni_recursive_walk.py`; `docs/research/algorithmic_frontier_hourly.md`; measured output with `baseline_elapsed = 1.5411759580019861`, `fast_elapsed = 1.134829582995735`, `speedup = 1.3580681902330864`, `baseline_segment_slots = 69248`, `fast_prefix_segment_slots = 12000`, and `saved_segment_fraction = 0.8267097966728281`.
Next step:
Thread the same clipped divisor classifier into the standalone exact endpoint walk and measure the same `10^12` chain.
