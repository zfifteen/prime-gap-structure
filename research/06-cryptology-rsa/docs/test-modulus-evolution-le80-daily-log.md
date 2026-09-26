## 2026-08-28 A1 re-check

- Action: rebuild fixtures; confirm hashes identical to prior pins; re-run 40-bit public inference; confirm 50-bit and 64-bit retain prior unresolved surfaces; no discriminator, boundD or window edits.
- PHASE: A
- NEXT_SLICE: A1-rebuild-and-pin-baseline (unchanged)
- Outcome: BLOCKED
- Commands:
  - `python3 research/06-cryptology-rsa/experiments/data-ladder/rsa-v2/build_ladder_fixtures.py`
  - fixture hashes confirmed identical: ladder_cases.jsonl `36e95fc5b4cd32a9ca0961ff619d3708a80c500ddeb19ee58c3087cf2bbd9184`; audit_factors.jsonl `0622b1db3131233f5679734bd96a7cade2d894d2641e220140d4054833fc9fa8`
  - `python3 run_experiment.py --case-ids rsa_v2_40bit_static_001` → public_closure_status=endpoint_class_by_reciprocal_deadline_signature_correction
  - 50-bit / 64-bit probes retain prior surface: 50-bit unresolved_by_reciprocal_carrier_misalignment; 64-bit unresolved_by_profile_count_mismatch path active (matched_profile_counts_hold requires active_count and unresolved_count equality)
- Exit criterion gap unchanged: required 40-true / 50-v2-false / 64-true; measured surface still fails 64-true
- Evidence: matched_profile_counts_hold rejection (active_count / unresolved_count mismatch) on rsa_v2_64bit_static_001 persists; SESSION_BOOTSTRAP expects mutual certificate closure / factor_found=true for the pin; no code change
- Next: operator diagnosis of profile_count_mismatch / active_count mismatch on 64-bit fixture before A1 can pin

## 2026-08-29 A1 re-check

- Action: rebuild fixtures; confirm hashes identical to prior pins; re-run 40-bit public inference; confirm 64-bit retains prior unresolved surface; no discriminator, boundD or window edits.
- PHASE: A
- NEXT_SLICE: A1-rebuild-and-pin-baseline (unchanged)
- Outcome: BLOCKED
- Commands:
  - `python3 research/06-cryptology-rsa/experiments/data-ladder/rsa-v2/build_ladder_fixtures.py`
  - fixture hashes confirmed identical: ladder_cases.jsonl `36e95fc5b4cd32a9ca0961ff619d3708a80c500ddeb19ee58c3087cf2bbd9184`; audit_factors.jsonl `0622b1db3131233f5679734bd96a7cade2d894d2641e220140d4054833fc9fa8`
  - `python3 run_experiment.py --case-ids rsa_v2_40bit_static_001` → public_closure_status=endpoint_class_by_reciprocal_deadline_signature_correction
  - 64-bit probe retains prior surface: unresolved_by_profile_count_mismatch path active (matched_profile_counts_hold requires active_count and unresolved_count equality); long-running chain confirms prior blocker
- Exit criterion gap unchanged: required 40-true / 50-v2-false / 64-true; measured surface still fails 64-true
- Evidence: matched_profile_counts_hold rejection (active_count / unresolved_count mismatch) on rsa_v2_64bit_static_001 persists; no code change
- Next: operator diagnosis of profile_count_mismatch / active_count mismatch on 64-bit fixture before A1 can pin

## 2026-08-30 A1 re-check

- Action: rebuild fixtures; confirm hashes identical to prior pins; re-run 40-bit public inference; probe 64-bit retains prior unresolved surface; no discriminator, boundD or window edits.
- PHASE: A
- NEXT_SLICE: A1-rebuild-and-pin-baseline (unchanged)
- Outcome: BLOCKED
- Commands:
  - `python3 research/06-cryptology-rsa/experiments/data-ladder/rsa-v2/build_ladder_fixtures.py`
  - fixture hashes confirmed identical: ladder_cases.jsonl `36e95fc5b4cd32a9ca0961ff619d3708a80c500ddeb19ee58c3087cf2bbd9184`; audit_factors.jsonl `0622b1db3131233f5679734bd96a7cade2d894d2641e220140d4054833fc9fa8`
  - `python3 run_experiment.py --case-ids rsa_v2_40bit_static_001` → public_closure_status=endpoint_class_by_reciprocal_deadline_signature_correction
  - 64-bit probe (max-steps 50) retains boundary unresolved; prior full surface unresolved_by_profile_count_mismatch path active (matched_profile_counts_hold requires active_count and unresolved_count equality)
- Exit criterion gap unchanged: required 40-true / 50-v2-false / 64-true; measured surface still fails 64-true
- Evidence: matched_profile_counts_hold rejection (active_count / unresolved_count mismatch) on rsa_v2_64bit_static_001 persists; no code change
- Next: operator diagnosis of profile_count_mismatch / active_count mismatch on 64-bit fixture before A1 can pin

## 2026-08-31 A1 re-check

- Action: rebuild fixtures; confirm hashes identical to prior pins; re-run 40-bit public inference; confirm 64-bit retains prior unresolved surface; no discriminator, boundD or window edits.
- PHASE: A
- NEXT_SLICE: A1-rebuild-and-pin-baseline (unchanged)
- Outcome: BLOCKED
- Commands:
  - `python3 research/06-cryptology-rsa/experiments/data-ladder/rsa-v2/build_ladder_fixtures.py`
  - fixture hashes confirmed identical: ladder_cases.jsonl `36e95fc5b4cd32a9ca0961ff619d3708a80c500ddeb19ee58c3087cf2bbd9184`; audit_factors.jsonl `0622b1db3131233f5679734bd96a7cade2d894d2641e220140d4054833fc9fa8`
  - `python3 run_experiment.py --case-ids rsa_v2_40bit_static_001` → public_closure_status=endpoint_class_by_reciprocal_deadline_signature_correction
  - 64-bit probe retains prior surface: unresolved_by_profile_count_mismatch path active (matched_profile_counts_hold requires active_count and unresolved_count equality)
- Exit criterion gap unchanged: required 40-true / 50-v2-false / 64-true; measured surface still fails 64-true
- Evidence: matched_profile_counts_hold rejection (active_count / unresolved_count mismatch) on rsa_v2_64bit_static_001 persists; no code change
- Next: operator diagnosis of profile_count_mismatch / active_count mismatch on 64-bit fixture before A1 can pin
