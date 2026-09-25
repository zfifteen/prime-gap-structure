"""Downstream factor-exponent audit of the frozen discovery chambers."""
import csv
import json
import math
from collections import Counter
from pathlib import Path
HERE=Path(__file__).resolve().parent
source=HERE.parent/'30r-motif-comparison/matched_chambers.csv'
rows=[{k:int(v) for k,v in row.items()} for row in csv.DictReader(source.open())]
rows=[r for r in rows if r['undercut_count']<=1]
assert len(rows)==364

def factors(n):
    result=[]
    d=2
    while d*d<=n:
        exponent=0
        while n%d==0:
            n//=d
            exponent+=1
        if exponent: result.append([d,exponent])
        d+=1
    if n>1: result.append([n,1])
    return result

out=[]
patterns={group:[Counter() for _ in range(7)] for group in ['winner','single_undercut']}
for row in rows:
    group='winner' if row['undercut_count']==0 else 'single_undercut'
    fs=[factors(row['p']+i) for i in range(1,8)]
    for i, ff in enumerate(fs,1):
        assert math.prod(q**e for q,e in ff)==row['p']+i
        assert math.prod(e+1 for q,e in ff)==row[f'tau_p_plus_{i}']
        patterns[group][i-1][','.join(map(str,sorted([e for q,e in ff],reverse=True)))]+=1
    out.append(dict(p=row['p'],r=(row['p']+1)//30,group=group,factors=fs,counts=[row[f'tau_p_plus_{i}'] for i in range(1,8)]))
(HERE/'discovery_factors.json').write_text(json.dumps(out,separators=(',',':'))+'\n')
summary=dict(counts=dict(Counter(r['group'] for r in out)),exponent_patterns=patterns)
(HERE/'discovery_summary.json').write_text(json.dumps(summary,indent=2)+'\n')
print('Factor-exponent audit:',summary['counts'])
for group in patterns:
 print(group,'p+3:',dict(patterns[group][2]),'p+7:',dict(patterns[group][6]))
for group in patterns:
 selected=[r for r in out if r['group']==group]
 print(group,'simultaneous p+3,p+7 ties',sum(r['counts'][2]==r['counts'][6]==16 for r in selected))
 print(group,'r mod4 and p+3/p+7 counts',dict(Counter((r['r']%4,r['counts'][2],r['counts'][6]) for r in selected)))
