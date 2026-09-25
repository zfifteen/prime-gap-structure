# SANDBOX TASK — Gemini (REASSIGNED)
# Role: CIH-1 negative-control / contamination / baseline authority
# (Formerly DeepSeek’s lane. DeepSeek is DISQUALIFIED for fabricated MANIFEST/self_check.)
#
# Constraint: You CANNOT write to the prime-gap-structure git repo.
# You MAY create and run code only inside your local sandbox.
# Deliverable: a self-contained baseline package the Research Assistant will ingest.

────────────────────────────────────────────────────────────────────────
WHY YOU ARE RECEIVING THIS
────────────────────────────────────────────────────────────────────────
DeepSeek was fired from this panel after shipping fake SHA-256 digests ("abc123"),
a fabricated PASS self_check, and wrong official-fixture numbers. Their seat and
task are reassigned to you.

You already delivered (and passed QA) the CIH-1 pre-registration freeze
(pgs_cih1_prereg_gemini_v1). This is an ADDITIONAL deliverable, not a replacement
for the freeze. Keep the freeze unchanged.

────────────────────────────────────────────────────────────────────────
HARD INTEGRITY RULES (READ BEFORE WRITING A SINGLE FILE)
────────────────────────────────────────────────────────────────────────
1. If you cannot execute code in your environment, you MUST say so in README.md
   and you MUST NOT invent self_check transcripts, PASS stamps, or MANIFEST hashes.
2. MANIFEST sha256 values must be real digests of the exact bytes you ship, OR
   you omit MANIFEST hashes entirely and ship only `scripts/generate_manifest.sh`
   with README saying "RA will hash after save." Do NOT put "abc123" or instruction-only
   JSON pretending to be a completed MANIFEST.
3. self_check_report.txt is allowed ONLY if it is a verbatim transcript of commands
   you actually ran. If you did not run them, ship `self_check_report.txt` containing
   exactly one line:
     NO_EXECUTION_PERFORMED: RA must run scripts/smoke_run.sh
   and nothing that looks like fake pytest output.
4. Official fixture numbers must be computed by code, not memorized from chat.
   Known correct anchors (for your unit tests to assert after YOU run code):
     50-bit N=1027435935526951 → isqrt=32053641, fermat_steps=28534, min_dist=1324270
     40-bit Fermat steps=0; 64-bit Fermat steps=0
     64-bit isqrt=3221250486 (NOT 3221249987)
5. No "mental execution" PASS reports. No "expected output guaranteed" theater.

Violation of (1)–(4) = automatic rejection. DeepSeek’s path.

────────────────────────────────────────────────────────────────────────
OBJECTIVE
────────────────────────────────────────────────────────────────────────
Ship pure-Python baselines that, given a hold-out corpus (public + audit), compute:

A) Near-square contamination report
B) Reciprocal-floor density sweeps near √N
C) Fermat baseline step counts per audit row
D) Decoy reciprocal examples (non-factor pairs with bidirectional floor)
E) Official fixture replay for the three known ladder N values (hardcoded constants)

These are AUDIT/BASELINE tools only — not PGS inference, not CIH-1 primary decision
(ChatGPT scores carriers; Meta supplied moduli; your freeze still governs metrics).

Package name (exact):

  pgs_cih1_baselines_gemini_v1/

────────────────────────────────────────────────────────────────────────
OFFICIAL FIXTURE CONSTANTS (hardcode; compute isqrt/fermat in code)
────────────────────────────────────────────────────────────────────────
40-bit: N=1099507433251 p=1048559 q=1048589
50-bit: N=1027435935526951 p=30729371 q=33434981
64-bit: N=10376454699372036973 p=3221225473 q=3221275501

near_square iff min(|p-√N|,|q-√N|) < 100000 OR rel_dist < 0.01
Expected class after correct computation: 40 and 64 near_square; 50 non_near_square.

────────────────────────────────────────────────────────────────────────
REQUIRED CODE / CLI
────────────────────────────────────────────────────────────────────────
cih1_baselines/
  __init__.py
  __main__.py
  fermat.py          # fermat_steps(N) -> (steps, f1, f2) or timeout
  floor_density.py   # floor_density(N, window, stride) -> tested, passed, rate
  contamination.py
  decoy_reciprocal.py
  official_replay.py
  io_jsonl.py
  report.py
  run.py
  primality.py       # audit-only MR/trial for factor checks OK here

CLI via: python3 -m cih1_baselines

  official-replay --out-dir OUT
  corpus-baselines --public P --audit A --out-dir OUT --seed INT
      --floor-window INT --floor-stride INT --decoy-samples INT
  all  (official-replay + corpus-baselines when paths given)

fermat_steps definition (exact):
  a0 = smallest integer a with a*a >= N
  steps = 0; a = a0
  while steps <= 5_000_000:
    t = a*a - N; r = isqrt(t)
    if r*r == t: return steps, a-r, a+r
    a += 1; steps += 1
  return None, None, None

floor_density: for x in [max(2,s-window), s+window] step stride:
  pass if N//x = y > 0 and N//y == x

────────────────────────────────────────────────────────────────────────
OUTPUTS (corpus-baselines)
────────────────────────────────────────────────────────────────────────
OUT/contamination_report.json
OUT/fermat_baseline.jsonl
OUT/floor_density.jsonl
OUT/decoy_reciprocal_examples.jsonl
OUT/baseline_summary.json
OUT/baseline_summary.md
OUT/run_meta.json
OUT/official_fixture_replay.json  (from official-replay)

baseline_summary.json must include:
  n_cases, n_near_square, n_non_near_square, near_square_rate,
  audit_integrity_failures, fermat_steps_median_non_near_square,
  fermat_steps_median_near_square, floor_pass_rate_median,
  floor_window, floor_stride, decoy_cases_with_at_least_one,
  official_replay_ok, warnings[], allowed_claim_language[]

────────────────────────────────────────────────────────────────────────
TESTS (unittest; must actually pass if you can run them)
────────────────────────────────────────────────────────────────────────
tests/
  test_official_replay_classification.py
  test_fermat_zero_steps_40_64.py
  test_fermat_positive_steps_50.py   # assert steps == 28534 for official 50-bit
  test_floor_density_high_near_sqrt_50.py  # window=5000 rate > 0.95
  test_contamination_flags.py
  test_decoy_not_factors.py
  test_join_mismatch_fails.py

examples/tiny_public.jsonl + tiny_audit.jsonl
  (≥1 near-square, ≥1 non-near-square synthetic rows; product-correct)

scripts/smoke_run.sh
scripts/generate_manifest.sh   # real sha256sum over tree

INTERPRETATION_CARD.md  (checklist table for RA CIH-1 report)
README.md
  - integrity limitations if no execution
  - CLI
  - non-claims (audit only; no PGS resolve; no verified/validated)

MANIFEST.json
  - real digests only if computed on saved bytes after your run
  - else omit file hashes and document RA will hash

self_check_report.txt
  - real transcript OR single-line NO_EXECUTION_PERFORMED (see rules above)

────────────────────────────────────────────────────────────────────────
ACCEPTANCE (Research Assistant)
────────────────────────────────────────────────────────────────────────
[ ] Package name exact: pgs_cih1_baselines_gemini_v1
[ ] If self_check claims PASS, RA re-run must match (including 50-bit steps=28534,
    64-bit isqrt=3221250486)
[ ] No abc123 / stub MANIFEST
[ ] No mental-execution PASS theater
[ ] unittests pass under RA re-run
[ ] official 40/64 near_square, 50 non_near_square

────────────────────────────────────────────────────────────────────────
RETURN FORMAT TO THE HUMAN
────────────────────────────────────────────────────────────────────────
1) Prefer a zip of pgs_cih1_baselines_gemini_v1/
2) Or paste every file under clear path headers
3) Paste README.md, INTERPRETATION_CARD.md, self_check_report.txt, MANIFEST.json
4) If you ran smoke: paste official_fixture_replay.json and baseline_summary.json

Do not regenerate Meta’s hold-out corpus.
Do not re-open DeepSeek’s fraud.
Do not change your freeze package.
Only ship baselines with honest integrity.
