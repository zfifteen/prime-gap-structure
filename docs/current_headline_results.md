# Current Headline Results

- **GWR is proved and closed on the repository's current proof surface.** The
  live theorem statement is
  [../gwr/findings/gwr_hierarchical_local_dominator_theorem.md](../gwr/findings/gwr_hierarchical_local_dominator_theorem.md),
  and the live proof summary is [../GWR_PROOF.md](../GWR_PROOF.md).
- **The later side is closed exactly.** The ordered backbone is
  [../gwr/findings/lexicographic_raw_z_dominance_theorem.md](../gwr/findings/lexicographic_raw_z_dominance_theorem.md):
  if `a < b` and `d(a) <= d(b)`, then `L(a) > L(b)`.
- **The earlier side is closed by the local admissibility route plus the
  residual-class closure artifacts.** The local admissibility note is
  [../gwr/findings/prime_gap_admissibility_theorem.md](../gwr/findings/prime_gap_admissibility_theorem.md).
  The closing residual artifacts are
  [../output/gwr_proof/residual_class_closure_20260413_0008.json](../output/gwr_proof/residual_class_closure_20260413_0008.json)
  and
  [../output/gwr_proof/residual_class_closure_20260413_1104.json](../output/gwr_proof/residual_class_closure_20260413_1104.json),
  with latest retained summary `all_requested_classes_closed = true`.
- **The exact no-early-spoiler audit now carries the proof surface through
  `p < 5 x 10^9`.** The aggregate artifact
  [../output/gwr_proof/parallel_no_early_spoiler_5e9.json](../output/gwr_proof/parallel_no_early_spoiler_5e9.json)
  reports `172,913,029` gaps, `660,287,089` earlier candidates before the
  true `GWR` carrier, `0` exact earlier spoilers, and `0` bridge failures.
- **The square-adjacent stress surface at `10^12` remains clean.** The matched
  artifact
  [../output/gwr_proof/earlier_spoiler_local_dominator_scan_square_adjacent_1e12.json](../output/gwr_proof/earlier_spoiler_local_dominator_scan_square_adjacent_1e12.json)
  reports `137,771` gaps, `649,769` earlier candidates, and `0` unresolved.
- **The exact DNI/GWR next-prime oracle remains exact by construction.** Given
  a known prime `q`, the unbounded walker recovers the next prime from the
  ordered divisor structure of the next-gap interior. See
  [./research/predictor/gwr_dni_exact_recursive_prime_walk_note.md](./research/predictor/gwr_dni_exact_recursive_prime_walk_note.md).
- **The recursive walk surface remains exact on the committed tested ladder.**
  The DNI transition rule is exact on `743,075 / 743,075` rows from the
  combined `10^6 + 10^7` next-gap surface, and the recursive walk records
  `664,578 / 664,578` exact consecutive next-prime recoveries from prime `11`
  through prime `10,000,121` with `0` skipped gaps.
- **The old fixed cutoff theorem is false and stays archived as false.** The
  fixed map `{2:44, 4:60, 6:60}` fails at `q = 24,098,209`.
- **The live bounded walker is certified on the committed exact surface
  through `q <= 10^7`.** The bounded rule is the empirical compression
  `C(q) = max(64, ceil(0.5 * log(q)^2))`, and the live honesty gate is the
  exact compare scan in
  [../benchmarks/python/predictor/gwr_dni_cutoff_counterexample_scan.py](../benchmarks/python/predictor/gwr_dni_cutoff_counterexample_scan.py).
  The committed `10^7` scan reports `664,575` tested gaps, `0`
  counterexamples, maximum exact peak offset `60`, and maximum cutoff
  utilization `0.6153846153846154`.
- **Deterministic prefilter performance remains the practical payoff.** The
  current production Python path rejects about `91%` of tested odd candidates
  before Miller-Rabin and produced `2.09x` and `2.82x` end-to-end deterministic
  RSA key-generation speedups on the curated `2048`-bit and `4096`-bit corpora.
  See [./prefilter/benchmarks.md](./prefilter/benchmarks.md).
- **Pre-proof notes are now archived.** Historical proof-progress material
  lives under
  [./archive/pre-proof-gwr/README.md](./archive/pre-proof-gwr/README.md)
  and
  [../gwr/archive/pre-proof/README.md](../gwr/archive/pre-proof/README.md).
