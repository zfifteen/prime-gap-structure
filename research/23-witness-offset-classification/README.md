# Witness Offset Classification

The selected witness is the leftmost minimum-divisor integer between two consecutive primes. This chapter asks whether that offset obeys a short rule in the winner's divisor type, or in the left prime's remainder modulo 30.

Read `CONTRACT.md` for the frozen predicates, then `FINDINGS.md` for the regime results. The elevation card records the wheel claim that holds through `10^7` and fails twenty times below `10^8`.

```text
python3 -m pytest research/23-witness-offset-classification/tests/test_classify_offsets.py -q
python3 research/23-witness-offset-classification/scripts/classify_offsets.py --scan --limit 100000000
```
