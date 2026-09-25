# Protocol: Carrier Information Hold-Out 1 (CIH-1)

## 1. Question
On non-near-square balanced semiprimes, does the Gap Winner Rule (GWR) selected `carrier_w` land closer to the true factors {p,q} than a uniform random control drawn from the same public certificate search band?

## 2. Non-goals
This experiment does not claim factorization breakthroughs, does not evaluate RSA oracle capability, and does not test exact product closure (which is known to leave a non-zero remainder under V3). It solely tests for residual information content (distance-to-factor) in the GWR carrier object versus a null uniform baseline.

## 3. Population and exclusion
- **Population**: Balanced semiprimes (N = p * q) generated randomly by Meta AI.
- **Exclusion (Contamination Gate)**: Any case where `min(|p - sqrt(N)|, |q - sqrt(N)|) < 100000` OR `|p - sqrt(N)| / sqrt(N) < 0.01` is strictly EXCLUDED from the primary analysis to prevent near-square Fermat-step leakage.
- **Other Exclusions**: Cases missing a valid lower certificate chamber.

## 4. Carrier definition (what object is scored)
The scored object is `lower.carrier_w`, defined strictly as the integer selected by the Gap Winner Rule (leftmost minimum-divisor maximizer) from the ordered divisor-count field within the immediate public chamber preceding `isqrt(N)`.

## 5. Search band definition
The search band is defined as the closed interval `[lower_anchor, upper_anchor]`, where `lower_anchor` is the start of the lower chamber and `upper_anchor` is the end of the lower chamber containing `carrier_w`.

## 6. Control definition
The control is `uniform_band_control`, consisting of `U` integers drawn uniformly at random from the identical search band `[lower_anchor, upper_anchor]` for each case. Sample size per case: 1000 control integers.

## 7. Primary metric
Let `D_c = min(|carrier_w - p|, |carrier_w - q|)`.
Let `D_u = min(|u - p|, |u - q|)` for `u` in the control set.
Let `Delta = median(D_u) - D_c` for a single case.
The **primary metric** is the **median of Delta** across all non-excluded cases in the corpus.
Direction: Higher is better (a positive median indicates the carrier is closer than the median control).

## 8. Secondary metrics (non-decisional)
- Mean of `Delta` across cases.
- Win-rate: Proportion of cases where `D_c < median(D_u)`.
- Tail severity: Distribution of `r_tail` classifications.

## 9. Statistical tests and decision rules
- **Test**: One-sided Wilcoxon signed-rank test on paired differences (`median(D_u) - D_c`).
- **Alpha**: 0.05.
- **Minimum Cases**: 30 non-excluded cases.
- **Decision Rule**: Reject the null hypothesis if p < 0.05 AND Median of Delta > 0. If rejected, conclude `carrier_better`.

## 10. Multiple-testing / peeking policy
No peeking allowed. The RA must run the corpus in a single blind pass, emit the score records, and compute the final statistic exactly once. No hyperparameter grid search over `boundD` or first-tail window is permitted.

## 11. PGS purity boundary
- **Forbidden in inference**: `gcd`, `N % x` factor selection, `isprime`, Miller-Rabin (`MR`), factor APIs, and exact product closure checks used as inference gates. Bidirectional floor holds are not allowed as sole success criteria. Historical false class blacklists are explicitly forbidden.
- **Audit only (scoring phase)**: `p`, `q`, primality checks on factors, and product check `p * q == N`.

## 12. Abort conditions
The experiment immediately aborts without decision if:
- Purity boundaries are violated in the log trace.
- The number of non-excluded cases drops below 30.
- First-tail window is altered from `[-12, 6]`.
- `boundD` formula is not exactly `max(20, (6 * (g_lo + g_up)) // 5)`.

## 13. Reporting language allowed after run
- "measured on hold-out corpus C with N cases"
- "hypothesis"
- "no verified/validated language"
- "no factorization claim"

## 14. Open parameters still allowed (must be empty or justified)
- Bit length of the moduli (controlled by Meta AI corpus builder, likely 128-bit, 256-bit). Justification: Test should be scale-invariant over the tested range.

