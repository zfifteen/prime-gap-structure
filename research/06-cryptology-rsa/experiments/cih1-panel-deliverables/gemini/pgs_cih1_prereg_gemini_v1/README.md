# CIH-1 Pre-registration Freeze (Gemini V1)

This package contains the frozen scientific contract for the Carrier Information Hold-Out (CIH-1) experiment. 

**Instructions for Research Assistant (RA):**
1. Ingest this freeze package strictly BEFORE generating or observing the CIH-1 moduli hold-out corpus.
2. Validate that the hold-out corpus generation respects the purity boundaries (MR/primes allowed only in the fixture builder, NEVER in the inference path).
3. Extract `carrier_w` using the frozen definitions (GWR from lower chamber).
4. Score the results using the predefined primary metric (distance-to-true-factor) against the uniform control distribution.
5. Emit results matching the JSON schemas in `schemas/`.
6. Match your conclusion text strictly to `decision_table.md`.

*Note: This package contains zero moduli and zero factors. It is exclusively the protocol freeze.*

