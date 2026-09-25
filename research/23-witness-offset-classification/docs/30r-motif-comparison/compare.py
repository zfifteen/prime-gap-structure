"""Retrospective comparison of exact divisor fields at a fixed finite range."""
import csv
import json
import math
from pathlib import Path
import subprocess
import sys
import types
from collections import Counter

HERE = Path(__file__).resolve().parent
COMMIT = '362d95e688872786aaab2afe5f9c7edf1977fa8f'
CHAPTER = 'research/23-witness-offset-classification'
LIMIT = 100_000_000
source = subprocess.check_output(['git', 'show', f'{COMMIT}:{CHAPTER}/scripts/classify_offsets.py'], text=True)
module = types.ModuleType('pinned_classifier')
sys.modules[module.__name__] = module
exec(compile(source, 'pinned_classifier', 'exec'), module.__dict__)
_, tau = module.build_compact_divisor_tables(LIMIT)
print('Divisor field built', flush=True)
counts = {'winner': 0, 'loser': 0}
by_position = {group: [[0, 0, 0] for _ in range(7)] for group in counts}
undercut_histogram = Counter()
sole_examples = {}
winners = []
with (HERE / 'matched_chambers.csv').open('w', newline='') as stream:
    writer = csv.writer(stream, lineterminator='\n')
    writer.writerow(['p', 'q', 'selected_offset', 'undercut_count'] + [f'tau_p_plus_{i}' for i in range(1, 8)])
    for p in range(29, LIMIT - 8, 30):
        if tau[p] != 2 or tau[p + 8] != 2 or tau[p + 1] != 16:
            continue
        values = list(tau[p + 1:p + 8])
        if min(values) == 2:
            continue
        undercuts = [i + 1 for i, value in enumerate(values) if value < 16]
        offset = values.index(min(values)) + 1
        group = 'winner' if offset == 1 else 'loser'
        counts[group] += 1
        undercut_histogram[len(undercuts)] += 1
        for i, value in enumerate(values):
            by_position[group][i][0 if value < 16 else 1 if value == 16 else 2] += 1
        writer.writerow([p, p + 8, offset, len(undercuts), *values])
        record = dict(p=p, q=p+8, counts=values, selected_offset=offset)
        if group == 'winner':
            winners.append(record)
        if len(undercuts) == 1 and undercuts[0] not in sole_examples:
            sole_examples[undercuts[0]] = record

previous = json.loads((HERE.parent / '30r-review/audit.json').read_text())['chambers']
assert [(r['p'], r['counts']) for r in winners] == [(r['p'], r['tau_including_endpoints'][1:-1]) for r in previous]
for record in sole_examples.values():
    actual = [sum(1 + (d*d != n) for d in range(1, math.isqrt(n)+1) if n % d == 0)
              for n in range(record['p'], record['q'] + 1)]
    assert actual == [2, *record['counts'], 2]
    assert min(actual[1:-1]) > 2
for group in counts:
    assert all(sum(row) == counts[group] for row in by_position[group])
assert sum(undercut_histogram.values()) == sum(counts.values())
result = dict(status='measured below 10^8; retrospective matched comparison',
              source_commit=COMMIT, limit=LIMIT, counts=counts,
              position_columns=['below_16', 'equal_16', 'above_16'],
              by_position=by_position, undercut_histogram=dict(sorted(undercut_histogram.items())),
              least_p_sole_undercut_examples=sole_examples,
              winners_match_prior_audit=True, independent_examples_audit=True,
              high_scale_surface_executed=False)
(HERE / 'summary.json').write_text(json.dumps(result, indent=2) + '\n')
print(json.dumps(result, indent=2))
