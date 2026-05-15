import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import norm
# --- Styling ---
plt.rcParams.update({
    'font.family': 'sans-serif',
    'font.size': 14,
    'axes.spines.top': False,
    'axes.spines.right': False,
    'axes.spines.left': False,
    'axes.linewidth': 1.0,
})
TRUE_MEAN = 50
TRUE_STD = 2
x = np.linspace(38, 62, 500)
true_curve = norm.pdf(x, TRUE_MEAN, TRUE_STD)
fig, axes = plt.subplots(2, 2, figsize=(10, 7), dpi=200)
fig.subplots_adjust(hspace=0.65, wspace=0.3)
titles = [
    '(a) Forstyrrende variabler',
    '(b) Systematiske feil',
    '(c) Tilfeldige feil',
    '(d) Måleusikkerhet',
]
colors = ['#E05252', '#E88C30', '#4A90D9', '#6BB86B']
# --- Helper to style each subplot ---
def style_ax(ax, title):
    ax.set_title(title, fontsize=16, fontweight='bold', pad=12)
    ax.set_yticks([])
    ax.set_xlabel('Måleverdi', fontsize=14)
    ax.vlines(TRUE_MEAN, 0, 0.22, color='#555555', linestyle=':', linewidth=1.0, alpha=0.6)
    ax.set_xlim(38, 62)
    ax.set_ylim(0, 0.25)
# (a) Forstyrrende variabler
ax = axes[0, 0]
style_ax(ax, titles[0])
ax.fill_between(x, true_curve, alpha=0.15, color='black')
ax.plot(x, true_curve, color='black', linewidth=2)
confound_curve = norm.pdf(x, TRUE_MEAN + 3.5, TRUE_STD * 1.8)
ax.fill_between(x, confound_curve, alpha=0.2, color=colors[0])
ax.plot(x, confound_curve, color=colors[0], linewidth=2)
ax.annotate('', xy=(53.5, 0.17), xytext=(50, 0.20),
            arrowprops=dict(arrowstyle='->', color=colors[0], lw=2))
# (b) Systematiske feil
ax = axes[0, 1]
style_ax(ax, titles[1])
ax.fill_between(x, true_curve, alpha=0.15, color='black')
ax.plot(x, true_curve, color='black', linewidth=2)
sys_curve = norm.pdf(x, TRUE_MEAN + 4, TRUE_STD)
ax.fill_between(x, sys_curve, alpha=0.2, color=colors[1])
ax.plot(x, sys_curve, color=colors[1], linewidth=2)
ax.annotate('', xy=(54, 0.195), xytext=(50, 0.195),
            arrowprops=dict(arrowstyle='->', color=colors[1], lw=2))
# (c) Tilfeldige feil
ax = axes[1, 0]
style_ax(ax, titles[2])
ax.fill_between(x, true_curve, alpha=0.15, color='black')
ax.plot(x, true_curve, color='black', linewidth=2)
rand_curve = norm.pdf(x, TRUE_MEAN, TRUE_STD * 2.2)
ax.fill_between(x, rand_curve, alpha=0.2, color=colors[2])
ax.plot(x, rand_curve, color=colors[2], linewidth=2)
ax.annotate('', xy=(55.5, 0.06), xytext=(53, 0.06),
            arrowprops=dict(arrowstyle='->', color=colors[2], lw=2))
ax.annotate('', xy=(44.5, 0.06), xytext=(47, 0.06),
            arrowprops=dict(arrowstyle='->', color=colors[2], lw=2))
# (d) Måleusikkerhet
ax = axes[1, 1]
style_ax(ax, titles[3])
ax.fill_between(x, true_curve, alpha=0.15, color='black')
ax.plot(x, true_curve, color='black', linewidth=2)
meas_curve = norm.pdf(x, TRUE_MEAN, TRUE_STD * 1.5)
ax.fill_between(x, meas_curve, alpha=0.2, color=colors[3])
ax.plot(x, meas_curve, color=colors[3], linewidth=2)
ax.annotate('', xy=(54, 0.10), xytext=(52.5, 0.10),
            arrowprops=dict(arrowstyle='->', color=colors[3], lw=2))
ax.annotate('', xy=(46, 0.10), xytext=(47.5, 0.10),
            arrowprops=dict(arrowstyle='->', color=colors[3], lw=2))
plt.savefig('/home/claude/figur_0_2_feilkilder.png', dpi=200, bbox_inches='tight',
            facecolor='white', edgecolor='none')
plt.close()
print("Figur lagret: figur_0_2_feilkilder.png")