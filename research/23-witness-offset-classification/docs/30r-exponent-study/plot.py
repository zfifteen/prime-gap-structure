"""Display the frozen positional exclusion and its fresh-band counts."""
import json
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
h=Path(__file__).resolve().parent
s=json.loads((h/'holdout_summary.json').read_text())
fig,ax=plt.subplots(figsize=(10,4.5),layout='constrained')
fig.patch.set_facecolor('#fafbfc'); ax.set_axis_off(); ax.set_xlim(0,10); ax.set_ylim(0,4.5)
ax.text(5,4.2,'Two positions cannot both have sixteen divisors',ha='center',fontsize=16,weight='bold')
ax.text(5,3.82,'p = 30r − 1, with r odd: the residue of r decides the restricted position',ha='center',fontsize=11)
ax.text(4.5,3.35,'p + 3',ha='center',fontsize=13); ax.text(8,3.35,'p + 7',ha='center',fontsize=13)
for y,branch,forced in [(2.25,1,7),(1.05,3,3)]:
 ax.text(.15,y+.2,f'r ≡ {branch} (mod 4)',fontsize=12)
 ax.text(.15,y-.1,f"{s['branches'].get(str(branch),0)} fresh chambers",fontsize=10,color='#586571')
 for x,seat in [(3,3),(6.5,7)]:
  restricted=seat==forced
  ax.add_patch(Rectangle((x,y-.35),3,1,facecolor='#c4ded5' if restricted else '#e8edf1',edgecolor='white'))
  ax.text(x+1.5,y+.27,'Exactly two factors of 2' if restricted else 'At least three factors of 2',ha='center',fontsize=10)
  ax.text(x+1.5,y-.05,'Divisor count is a multiple of 3' if restricted else 'This rule permits count 16',ha='center',fontsize=10)
ax.text(5,.25,f"Fresh band [10⁸, 1.1×10⁸): {s['matched_count']:,} matched chambers, {s['violation_count']} rule violations",ha='center',fontsize=12,weight='bold')
fig.savefig(h/'positional_rule.png',dpi=170,bbox_inches='tight')
