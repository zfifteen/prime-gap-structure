# Baseline Interpretation Card for CIH-1

This checklist governs how the baseline outputs constrain the CIH-1 primary experiment.

| Metric | Threshold | RA Action if Threshold Violated |
|--------|-----------|---------------------------------|
| `near_square_rate` | Must be explicitly logged. | Near-square cases MUST be excluded from the primary `median_delta_distance` calculation. |
| `floor_pass_rate_median`| Expected > 0.95 near √N. | Confirm bidirectional floor alone is not used as a success rule in CIH-1 (per freeze). |
| `audit_integrity_failures` | Must be 0. | Abort CIH-1 scoring; Meta corpus is malformed (e.g., p*q != N). |
| `official_replay_ok` | Must be true. | Abort if standard 40/50/64-bit fixture tests fail (ensures isqrt/math libraries did not silently overflow). |
