"""One frozen positional rule, tested in one fresh retrospective band."""
import csv
import hashlib
import json
import math
from pathlib import Path
import subprocess
import sys
import types
from collections import Counter
HERE=Path(__file__).resolve().parent
LOW,HIGH=100_000_000,110_000_000
COMMIT='362d95e688872786aaab2afe5f9c7edf1977fa8f'
rule_hash=hashlib.sha256((HERE/'FROZEN_RULE.txt').read_bytes()).hexdigest()
source=subprocess.check_output(['git','show',f'{COMMIT}:research/23-witness-offset-classification/scripts/classify_offsets.py'],text=True)
module=types.ModuleType('pinned_classifier')
sys.modules[module.__name__]=module
exec(compile(source,'pinned_classifier','exec'),module.__dict__)
_,tau=module.build_compact_divisor_tables(HIGH+8)
print('Fresh-band divisor field built',flush=True)
records=[]; violations=[]; winners=[]; branch_examples={}; branches=Counter()
for p in range(LOW+((29-LOW)%30),HIGH,30):
    if tau[p]!=2 or tau[p+8]!=2 or tau[p+1]!=16: continue
    values=list(tau[p+1:p+8])
    if min(values)==2: continue
    r=(p+1)//30
    assert r%2==1
    branch=r%4
    forced=7 if branch==1 else 3
    minimum=min(values)
    offset=values.index(minimum)+1
    record=dict(p=p,q=p+8,r_mod4=branch,forced_position=forced,selected_offset=offset,counts=values)
    records.append(record); branches[branch]+=1
    branch_examples.setdefault(branch,record)
    bad=((p+forced)%8!=4 or values[forced-1]%3!=0 or values[forced-1]==16
         or values[2]==values[6]==16 or (offset==1 and values[forced-1]<18))
    if bad: violations.append(record)
    if offset==1: winners.append(record)
assert records
with (HERE/'holdout_chambers.csv').open('w',newline='') as stream:
    writer=csv.writer(stream,lineterminator='\n')
    writer.writerow(['p','q','r_mod4','forced_position','selected_offset']+[f'tau_p_plus_{i}' for i in range(1,8)])
    for row in records: writer.writerow([row[k] for k in ['p','q','r_mod4','forced_position','selected_offset']]+row['counts'])
audit_rows={row['p']:row for row in list(branch_examples.values())+winners}
for row in audit_rows.values():
    actual=[sum(1+(d*d!=n) for d in range(1,math.isqrt(n)+1) if n%d==0) for n in range(row['p'],row['q']+1)]
    assert actual==[2,*row['counts'],2]
result=dict(status='measured on fresh band [10^8,1.1*10^8); arithmetic rule checked on that band',
            frozen_rule_sha256=rule_hash,source_commit=COMMIT,range=[LOW,HIGH],matched_count=len(records),
            branches=dict(branches),violation_count=len(violations),violations=violations,
            winners=winners,winner_count=len(winners),
            winners_with_final_tie=sum(row['counts'][6]==16 for row in winners),
            winners_with_unique_minimum=sum(row['counts'].count(16)==1 for row in winners),
            independently_audited=sorted(audit_rows),high_scale_surface_executed=False)
(HERE/'holdout_summary.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result,indent=2))
