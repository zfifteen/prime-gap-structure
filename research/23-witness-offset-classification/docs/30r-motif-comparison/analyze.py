"""Summarize, independently audit an illustrative pair, and plot the comparison."""
import csv
import json
import math
from collections import Counter
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap

HERE = Path(__file__).resolve().parent
rows = [{k:int(v) for k,v in row.items()} for row in csv.DictReader((HERE/'matched_chambers.csv').open())]
summary = json.loads((HERE/'summary.json').read_text())
values = lambda row: [row[f'tau_p_plus_{i}'] for i in range(1,8)]
assert len(rows) == len({r['p'] for r in rows}) == sum(summary['counts'].values())
assert rows == sorted(rows,key=lambda r:r['p'])
for row in rows:
    v = values(row)
    assert row['selected_offset'] == v.index(min(v))+1
    assert row['undercut_count'] == sum(x<16 for x in v)
    assert row['q'] == row['p']+8 and row['p']%30 == 29 and v[0] == 16 and min(v)>2
for label in ['winner','loser']:
    subset = [r for r in rows if (r['undercut_count']==0) == (label=='winner')]
    observed = [[sum(values(r)[i]<16 for r in subset),sum(values(r)[i]==16 for r in subset),sum(values(r)[i]>16 for r in subset)] for i in range(7)]
    assert len(subset)==summary['counts'][label] and observed==summary['by_position'][label]
solo = Counter(row['selected_offset'] for row in rows if row['undercut_count']==1)
# Post-comparison illustration: earliest winner, then earliest loser differing at one position.
winner = next(row for row in rows if row['undercut_count']==0)
loser = next(row for row in rows if row['undercut_count']>0 and sum(a!=b for a,b in zip(values(winner),values(row)))==1)
for row in [winner,loser]:
    actual = [sum(1+(d*d!=n) for d in range(1,math.isqrt(n)+1) if n%d==0) for n in range(row['p'],row['q']+1)]
    assert actual==[2,*values(row),2]
pair = dict(status='post-comparison descriptive example; distinct actual chambers',winner=winner,loser=loser,sole_undercut_counts=dict(sorted(solo.items())),independent_pair_audit=True)
(HERE/'one_position_pair.json').write_text(json.dumps(pair,indent=2)+'\n')
fig,(top,bottom)=plt.subplots(2,1,figsize=(10,6),gridspec_kw={'height_ratios':[1,1.25]},layout='constrained')
fig.patch.set_facecolor('#fafbfc')
a=[values(winner),values(loser)]
top.imshow([[0 if n<16 else 1 if n==16 else 2 for n in v] for v in a],cmap=ListedColormap(['#f4b7b0','#b9e0d3','#eed4ad']),vmin=0,vmax=2,aspect='auto')
for i,v in enumerate(a):
 for j,n in enumerate(v):top.text(j,i,str(n),ha='center',va='center',fontsize=13)
top.set_xticks(range(7),[f'p+{i}' for i in range(1,8)])
top.set_yticks([0,1],[f"Winner\np = {winner['p']:,}",f"Loser\np = {loser['p']:,}"])
top.set_title('Six counts match exactly; the differing count identifies the losing position',fontsize=12,pad=12)
top.tick_params(length=0)
xs=list(range(2,8)); ys=[solo[x] for x in xs]
bottom.bar(xs,ys,color='#607e96',width=.65)
for x,y in zip(xs,ys):bottom.text(x,y+3,str(y),ha='center',fontsize=11)
bottom.set_xticks(xs,[f'p+{x}' for x in xs]); bottom.set_ylim(0,225)
bottom.set_ylabel('Number of chambers')
bottom.set_title('344 losing chambers have exactly one undercutting neighbor',fontsize=12)
bottom.set_xlabel('Position of the sole undercut (divisor count below 16)')
bottom.spines[['top','right']].set_visible(False)
fig.suptitle('Matched gap-8 chambers below 10⁸: 20 winners, 9,356 losers',fontsize=15,fontweight='bold')
fig.savefig(HERE/'comparison.png',dpi=170,bbox_inches='tight')
print('All 9,376 retained rows reconciled with the summary; illustrative pair independently audited.')
print('Sole undercut counts:',dict(sorted(solo.items())))
