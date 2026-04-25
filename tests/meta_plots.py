import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Circle, Wedge
import matplotlib.cm as cm

# ---- your findings ----
versions = ['v0','v1','v2','v3','v4','v5']
solved = [36, 42, 130, 211, 447, 995]
total_anchors = 1225
abstain_values = [175, 3, 52] # RESOLVED_BUT_UNRESOLVED_LATER, MULTIPLE, UNRESOLVED
v5_applied, v5_solutions = 6205, 548

plt.style.use('dark_background')

# 1. Hypnotic spiral
fig1, ax1 = plt.subplots(figsize=(8,8), subplot_kw={'projection': 'polar'})
theta = np.linspace(0, 8*np.pi, 500)
r_base = np.interp(np.linspace(0, len(solved)-1, len(theta)), range(len(solved)), solved)
r = r_base * (1 + 0.1*np.sin(5*theta))
ax1.plot(theta, r, color='#00ffff', lw=2, alpha=0.8)
ax1.scatter(np.linspace(0, 8*np.pi, len(solved)), solved,
            s=[200,300,500,700,1000,1500], c=solved, cmap='plasma',
            edgecolors='white', linewidth=2)
for i,v in enumerate(versions):
    ang = i * (8*np.pi/5)
    ax1.text(ang, solved[i]+80, f'{v}\n{solved[i]}', ha='center', color='white', weight='bold')
ax1.set_rticks([]); ax1.grid(False)
ax1.set_title('Graph Solver Cascade Spiral\nv0→v5: 36 → 995 solved', color='white', pad=20)
fig1.savefig('spiral_cascade.png', dpi=200, bbox_inches='tight', facecolor='black')

# 2. Abstention mandala
fig2, ax2 = plt.subplots(figsize=(8,8)); ax2.set_aspect('equal'); ax2.set_facecolor('black')
colors = ['#ff006e', '#3a86ff', '#ffbe0b']
solved_ratio = 995/total_anchors
ax2.add_patch(Wedge((0,0), 1.0, 0, 360*solved_ratio, facecolor='#00ff88', alpha=0.3, edgecolor='white', lw=2))
start = 0
for i,val in enumerate(abstain_values):
    angle = 360*val/sum(abstain_values)
    for j in range(12):
        ax2.add_patch(Wedge((0,0), 0.7, start+j*30, start+angle+j*30, width=0.3,
                            facecolor=colors[i], alpha=0.6-j*0.04))
    start += angle
for r in np.linspace(0.2,0.9,5):
    ax2.add_patch(Circle((0,0), r, fill=False, edgecolor='white', alpha=0.2, ls='--'))
ax2.axis('off')
ax2.text(0,0,'995\nSOLVED', ha='center', va='center', color='white', fontsize=24, weight='bold')
fig2.savefig('abstention_mandala.png', dpi=200, bbox_inches='tight', facecolor='black')

# 3. Waterfall cascade
fig3, ax3 = plt.subplots(figsize=(10,6)); ax3.set_facecolor('black')
for i,h in enumerate(solved):
    for j in range(20):
        ax3.bar(i, h/20, bottom=h*j/20, width=0.6, color=cm.turbo(j/20), alpha=0.9)
    if i>0:
        ax3.annotate(f'+{h-solved[i-1]}', xy=(i,h+30), ha='center', color='#00ffff', weight='bold',
                     arrowprops=dict(arrowstyle='->', color='#00ffff', alpha=0.7))
ax3.set_xticks(range(6)); ax3.set_xticklabels(versions, color='white')
ax3.set_ylabel('Solved Boundaries', color='white'); ax3.tick_params(colors='white')
ax3.set_title('Mind-Bending Cascade: v4→v5 jump +548 with zero failures', color='white')
ax3.set_ylim(0,1100); ax3.grid(True, alpha=0.1)
ax3.text(5,500, f'v5 applied\n{v5_applied} times\n→ {v5_solutions} solves', ha='center', color='white',
         bbox=dict(boxstyle='round,pad=0.5', facecolor='#3a0ca3', alpha=0.7))
fig3.savefig('waterfall_cascade.png', dpi=200, bbox_inches='tight', facecolor='black')
