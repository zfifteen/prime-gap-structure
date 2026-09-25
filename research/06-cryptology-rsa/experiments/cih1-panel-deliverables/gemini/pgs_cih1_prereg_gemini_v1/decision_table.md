# Decision Table

| Outcome | Condition | Allowed claim sentence |
|---------|-----------|------------------------|
| `carrier_better` | Analyzed cases >= 30, p < 0.05, Median Delta > 0 | "Hypothesis: GWR carrier information distance is significantly lower than uniform band sampling, measured on hold-out corpus with N cases (no verified/validated language, no factorization claim)." |
| `no_difference` | Analyzed cases >= 30, p >= 0.05 OR Median Delta <= 0 | "Hypothesis: GWR carrier information shows no statistically significant advantage over uniform band sampling, measured on hold-out corpus with N cases." |
| `control_better` | Analyzed cases >= 30, p < 0.05 in opposite direction | "Hypothesis: Uniform band sampling significantly outperforms GWR carrier distance, measured on hold-out corpus with N cases." |
| `aborted` | Purity violation, invalid parameters, or crash | "Experiment CIH-1 aborted due to protocol violation. No conclusions drawn." |
| `contaminated` | Analyzed cases < 30 after near-square exclusions | "Experiment CIH-1 contaminated by insufficient non-near-square cases. No conclusions drawn." |

