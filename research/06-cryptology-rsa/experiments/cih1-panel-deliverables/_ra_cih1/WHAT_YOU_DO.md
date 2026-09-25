# What you need to do to keep CIH-1 moving

RA has already run the first full pass. Your job is decision and direction, not file plumbing.

## Right now (5–10 minutes)

1. **Read** `_ra_cih1/RESULTS.md` (especially the Shape finding).
2. **Decide which decision rule is binding** for “CIH-1 success”:
   - **A (Recommended):** ChatGPT R-threshold → **`no_difference`** (substantive proximity fail; R≈1).
   - **B:** Gemini median_delta > 0 + p < 0.05 → micro-effect “carrier_better” (within-band only; easy to overclaim).
   - **C:** Redesign band/control before any success claim (see below).
3. **Say in chat** which of A/B/C you want as the official CIH-1 call.

## You do **not** need to

- Re-download panel packages
- Re-run smoke tests
- Paste code into Gemini/ChatGPT for this pass
- Touch DeepSeek (fired)

## If you pick A (`no_difference` official)

Optional next research (tell RA which):

- Close CIH-1 v1 as **measured no substantive carrier advantage under freeze band**.
- Open CIH-2 design: different control (e.g. wider public search band, not just chamber width) **without** peeking re-tuning on the same 60.
- Or pressure test on larger bit Meta-style corpus after freeze amendment.

## If you pick B (count micro-delta)

You must accept and document:

- Effect size ~10 on D_c ~ 10^6
- Band width ~28
- No factorization claim remains mandatory
- Prefer renaming the claim to “within-chamber position bias,” not “carrier information for factors”

## If you pick C (redesign)

You approve a freeze amendment **before** another scored pass:

| Open question | Your call |
|---------------|-----------|
| Search band | Chamber only (current) vs wider public interval around √N? |
| Control | Uniform in chamber vs uniform in [√N−W, √N+W]? |
| Primary metric | Keep median_delta, median_R, or both with pre-set thresholds? |
| Peeking | New hold-out seed/corpus required after redesign (yes/no) |

## Operational asks only if something breaks

- If you want a commit of `_ra_cih1/` + ChatGPT newline fix: say **“commit CIH-1 RA”**
- If you want a short executive HTML for sharing: say **“HTML summary”**
- If you want CIH-2 freeze draft: say **“draft CIH-2 freeze”**

## One sentence status

**Pipeline is complete; waiting on your A/B/C decision before the next scientific move.**
