import numpy as np
import matplotlib.pyplot as plt
from scipy import stats

# --- Styling ---
plt.rcParams.update({
    'font.family': 'sans-serif',
    'font.size': 12,
    'axes.spines.top': False,
    'axes.spines.right': False,
    'axes.linewidth': 1.0,
})

# --- Data ---
years = list(range(2001, 2022))
butter = [4.3, 4.4, 4.5, 4.5, 4.5, 4.7, 4.7, 5.0, 5.0, 4.9,
          5.4, 5.5, 5.5, 5.5, 5.6, 5.7, 5.7, 6.0, 6.2, 6.3, 6.5]
# Economic output in raw dollars
econ_raw = [2.6332e14, 2.793e14, 2.9692e14, 3.2231e14, 3.4736e14,
            3.6526e14, 3.8305e14, 3.9744e14, 4.05e14, 4.2605e14,
            4.3876e14, 4.4874e14, 4.558e14, 4.697e14, 4.8841e14,
            5.0836e14, 5.2526e14, 5.4759e14, 5.6738e14, 5.6426e14,
            6.075e14]
econ = [x / 1e12 for x in econ_raw]  # konverter til billioner (trillions)

butter = np.array(butter)
econ = np.array(econ)

# --- Regresjon ---
slope, intercept, r_value, p_value, std_err = stats.linregress(butter, econ)
x_fit = np.linspace(butter.min() - 0.15, butter.max() + 0.15, 100)
y_fit = slope * x_fit + intercept

# --- Plot ---
fig, ax = plt.subplots(figsize=(7, 5.5), dpi=200)

ax.scatter(butter, econ, color='#C0392B', s=60, edgecolor='white', linewidth=0.8, zorder=3)
ax.plot(x_fit, y_fit, color='#C0392B', linewidth=2, alpha=0.5, linestyle='--')

# Annotere årstall på utvalgte punkter
label_indices = [0, 4, 9, 14, 20]  # 2001, 2005, 2010, 2015, 2021
for i in label_indices:
    offset_y = 8
    offset_x = 0
    if i == 9:   # 2010 – flytt ned
        offset_y = -14
    if i == 14:  # 2015 – flytt ned
        offset_y = -14
    ax.annotate(str(years[i]), (butter[i], econ[i]),
                fontsize=8.5, color='#666666',
                textcoords='offset points', xytext=(offset_x, offset_y),
                ha='center')

ax.set_xlabel('Smørforbruk per innbygger (pounds)', fontsize=12)
ax.set_ylabel('Økonomisk produksjon,\nWashington-området (billioner USD)', fontsize=12)
ax.set_title('Falsk korrelasjon', fontsize=16, fontweight='bold', pad=10)

# Statistikk-boks
stats_text = f'r = {r_value:.3f}\nr² = {r_value**2:.3f}\np < 0,01'
ax.text(0.05, 0.95, stats_text, transform=ax.transAxes, fontsize=10,
        verticalalignment='top', color='#555555',
        bbox=dict(boxstyle='round,pad=0.4', facecolor='#F5F5F5',
                  edgecolor='#CCCCCC', linewidth=0.8))

# Kilde
ax.text(0.99, -0.14, 'Data: tylervigen.com/spurious-correlations',
        transform=ax.transAxes, fontsize=7.5, color='#AAAAAA', ha='right', style='italic')

ax.set_xlim(4.1, 6.7)
ax.set_ylim(230, 650)

plt.tight_layout()
plt.savefig('/home/claude/figur_falsk_korrelasjon.png', dpi=200, bbox_inches='tight',
            facecolor='white', edgecolor='none')
plt.close()
print("Figur lagret!")
