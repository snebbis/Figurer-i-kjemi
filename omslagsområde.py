"""
pH-skala med vektet indikatorblanding og titreringssammenligning.
Genererer to figurer:
  1) Kontinuerlig pH-skala med fire indikatorer (metylrødt, lakmus, bromtymolblått, fenolftalein)
  2) Bromtymolblått ved titrering av HCl med NaOH

Krav: matplotlib, numpy
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
from matplotlib.lines import Line2D

# Sett globale font-innstillinger for hele scriptet
plt.rcParams.update({
    'font.family': 'sans-serif',
    'font.sans-serif': ['Arial', 'Helvetica', 'DejaVu Sans', 'sans-serif'],
    'font.size': 14
})

# ---------------------------------------------------------------------------
# Felles fargekonstanter (RGB 0-1)
# ---------------------------------------------------------------------------
MR_RED    = np.array([211, 47, 47]) / 255
MR_ORANGE = np.array([239, 108, 0]) / 255
MR_YELLOW = np.array([253, 216, 53]) / 255

LK_RED    = np.array([198, 40, 40]) / 255
LK_PURPLE = np.array([106, 27, 154]) / 255
LK_BLUE   = np.array([21, 101, 192]) / 255

BT_YELLOW = np.array([253, 216, 53]) / 255
BT_GREEN  = np.array([67, 160, 71]) / 255
BT_BLUE   = np.array([25, 118, 210]) / 255

PF_PINK   = np.array([233, 30, 99]) / 255

OUTSIDE_WEIGHT = 0.2
PF_WEIGHT_MAX  = 1.5


def lerp(a, b, t):
    return a * (1 - t) + b * t


def _indicator_color_weight(pH, lo, hi, c_start, c_mid, c_end):
    """Returner (farge, vekt) for en indikator med tre-punkts omslag."""
    if pH < lo:
        return c_start, OUTSIDE_WEIGHT
    if pH > hi:
        return c_end, OUTSIDE_WEIGHT
    t = (pH - lo) / (hi - lo)
    if t < 0.5:
        color = lerp(c_start, c_mid, t * 2)
    else:
        color = lerp(c_mid, c_end, (t - 0.5) * 2)
    return color, 1.0


def mr(pH):
    return _indicator_color_weight(pH, 4.4, 6.2, MR_RED, MR_ORANGE, MR_YELLOW)


def lk(pH):
    return _indicator_color_weight(pH, 4.5, 8.3, LK_RED, LK_PURPLE, LK_BLUE)


def bt(pH):
    return _indicator_color_weight(pH, 6.0, 7.6, BT_YELLOW, BT_GREEN, BT_BLUE)


def pf(pH):
    if pH < 8.2:
        return PF_PINK, 0.0
    if pH >= 10.0:
        return PF_PINK, PF_WEIGHT_MAX
    return PF_PINK, PF_WEIGHT_MAX * (pH - 8.2) / 1.8


def blended_color(pH):
    """Vektet RGB-gjennomsnitt av alle fire indikatorer ved gitt pH."""
    items = [mr(pH), lk(pH), bt(pH)]
    pf_c, pf_w = pf(pH)
    if pf_w > 0:
        items.append((pf_c, pf_w))
    total_w = sum(w for _, w in items)
    color = sum(c * w for c, w in items) / total_w
    return np.clip(color, 0, 1)


def make_gradient_image(pH_range, color_func, height=1):
    """Lag et (height, N, 3) bilde av farger langs pH."""
    colors = np.array([color_func(p) for p in pH_range])
    return np.tile(colors[np.newaxis, :, :], (height, 1, 1))


def single_indicator_color(pH, lo, hi, c_start, c_mid, c_end):
    """Farge for enkeltstående indikatorbånd (uten blanding)."""
    if pH < lo or pH > hi:
        return np.array([0.88, 0.87, 0.86])  # nøytral grå
    t = (pH - lo) / (hi - lo)
    if t < 0.5:
        return lerp(c_start, c_mid, t * 2)
    return lerp(c_mid, c_end, (t - 0.5) * 2)


# ═══════════════════════════════════════════════════════════════════════════
# FIGUR 1: pH-skala med fire indikatorer + samlet vektet gradient
# ═══════════════════════════════════════════════════════════════════════════

def figur1_ph_skala(save_path="ph_skala_indikatorer.png"):
    pH = np.linspace(0, 14, 1400)

    # Indikatordefinisjoner: (navn, lo, hi, c_start, c_mid, c_end)
    indicators = [
        ("Metylrødt\npH 4,4–6,2",       4.4, 6.2, MR_RED, MR_ORANGE, MR_YELLOW),
        ("Lakmus\npH 4,5–8,3",           4.5, 8.3, LK_RED, LK_PURPLE, LK_BLUE),
        ("Bromtymolblått\npH 6,0–7,6",   6.0, 7.6, BT_YELLOW, BT_GREEN, BT_BLUE),
    ]

    fig, axes = plt.subplots(
        6, 1, figsize=(14, 8),
        gridspec_kw={"height_ratios": [1, 1, 1, 1, 0.3, 2], "hspace": 0.15},
    )
    fig.patch.set_facecolor("white")

    # --- Indikator 1-3 ---
    for i, (label, lo, hi, cs, cm, ce) in enumerate(indicators):
        ax = axes[i]
        img = make_gradient_image(
            pH, lambda p, lo=lo, hi=hi, cs=cs, cm=cm, ce=ce:
                single_indicator_color(p, lo, hi, cs, cm, ce),
            height=20,
        )
        ax.imshow(img, aspect="auto", extent=[0, 14, 0, 1])
        ax.set_xlim(0, 14)
        ax.set_yticks([])
        ax.set_xticks([])
        ax.set_ylabel(label, fontsize=14, rotation=0, ha="right", va="center",
                       labelpad=110)
        # Rammer rundt omslagsområdet
        ax.axvline(lo, color="black", lw=1.0, ls="--", alpha=0.5)
        ax.axvline(hi, color="black", lw=1.0, ls="--", alpha=0.5)

    # --- Fenolftalein (spesialbehandlet: fargeløs → rosa) ---
    ax_pf = axes[3]
    pf_img_colors = []
    for p in pH:
        if p < 8.2:
            pf_img_colors.append(np.array([0.88, 0.87, 0.86]))
        elif p > 10.0:
            pf_img_colors.append(PF_PINK)
        else:
            t = (p - 8.2) / 1.8
            pf_img_colors.append(lerp(np.array([0.96, 0.94, 0.94]), PF_PINK, t))
    pf_img = np.tile(np.array(pf_img_colors)[np.newaxis, :, :], (20, 1, 1))
    ax_pf.imshow(pf_img, aspect="auto", extent=[0, 14, 0, 1])
    ax_pf.set_xlim(0, 14)
    ax_pf.set_yticks([])
    ax_pf.set_xticks([])
    ax_pf.set_ylabel("Fenolftalein\npH 8,2–10,0", fontsize=14, rotation=0,
                      ha="right", va="center", labelpad=110)
    ax_pf.axvline(8.2, color="black", lw=1.0, ls="--", alpha=0.5)
    ax_pf.axvline(10.0, color="black", lw=1.0, ls="--", alpha=0.5)

    # --- Mellomrom ---
    axes[4].set_visible(False)

    # --- Samlet vektet gradient ---
    ax_main = axes[5]
    main_img = make_gradient_image(pH, blended_color, height=40)
    ax_main.imshow(main_img, aspect="auto", extent=[0, 14, 0, 1])
    ax_main.set_xlim(0, 14)
    ax_main.set_yticks([])
    ax_main.set_xticks(range(15))
    ax_main.tick_params(axis="x", labelsize=16)
    ax_main.set_xlabel("pH", fontsize=18, fontweight="bold")
    ax_main.set_ylabel("Vektet\nblanding", fontsize=14, rotation=0,
                        ha="right", va="center", labelpad=110, fontweight="bold")

    # pH 7 markør
    for ax in axes[:4]:
        ax.axvline(7, color="white", lw=1.5, ls=":", alpha=0.8)
    ax_main.axvline(7, color="white", lw=2.5, ls="--", alpha=0.9)
    ax_main.text(7, 1.15, "pH 7\nnøytral", ha="center", va="bottom",
                 fontsize=14, color="#444", transform=ax_main.get_xaxis_transform(), fontweight="bold")

    fig.suptitle("pH-skala med vektet indikatorblanding", fontsize=22,
                 fontweight="bold", y=0.98)

    plt.savefig(save_path, dpi=200, bbox_inches="tight", facecolor="white")
    plt.close()
    print(f"Figur 1 lagret: {save_path}")


# ═══════════════════════════════════════════════════════════════════════════
# FIGUR 2: Indikatorvalg (titrering HCl + NaOH) - Kun Bromtymolblått
# ═══════════════════════════════════════════════════════════════════════════

def figur2_titrering(save_path="titrering_indikatorvalg.png"):
    pH = np.linspace(0, 14, 1400)

    fig = plt.figure(figsize=(12, 6), facecolor="white")

    # Manuell plassering av den ene gjenværende aksen: [left, bottom, width, height]
    ax = fig.add_axes([0.08, 0.35, 0.88, 0.35])

    fig.text(
        0.5, 0.92,
        "0,07 M HCl titreres med 0,1 M NaOH",
        ha="center", fontsize=22, fontweight="bold",
    )
    fig.text(
        0.5, 0.84,
        "Sterk syre + sterk base → ekvivalenspunkt ved pH 7",
        ha="center", fontsize=18, color="#444",
    )

    eq_pH = 7.0
    eq_color = "#d32f2f"
    tp_color = "#00695c"
    
    lo, hi = 6.0, 7.6
    tp_pH = 7.1

    img = make_gradient_image(
        pH, lambda p: single_indicator_color(p, lo, hi, BT_YELLOW, BT_GREEN, BT_BLUE),
        height=30,
    )
    ax.imshow(img, aspect="auto", extent=[0, 14, 0, 1])
    ax.set_xlim(0, 14)
    ax.set_ylim(0, 1)
    ax.set_yticks([])
    ax.set_xticks(range(15))
    ax.tick_params(axis="x", labelsize=16)
    ax.set_xlabel("pH", fontsize=18, fontweight="bold")

    # Omslagsområde-bue over panelet
    ax.annotate(
        "", xy=(lo, 1.08), xytext=(hi, 1.08),
        xycoords=("data", "axes fraction"),
        textcoords=("data", "axes fraction"),
        arrowprops=dict(arrowstyle="<->", color="#888", lw=1.5),
        annotation_clip=False,
    )
    range_label = f"Omsl. pH {lo:.1f}–{hi:.1f}".replace(".", ",")
    ax.text(
        (lo + hi) / 2, 1.15, range_label,
        transform=ax.get_xaxis_transform(),
        ha="center", va="bottom", fontsize=14, color="#666", fontweight="bold"
    )

    # Ekvivalenspunkt (rød stiplet)
    ax.axvline(eq_pH, color=eq_color, lw=3, ls="--", zorder=5)

    # Titreringspunkt (teal hel)
    ax.axvline(tp_pH, color=tp_color, lw=3, ls="-", zorder=5)

    # Etiketter: én til venstre, én til høyre
    ax.annotate(
        "Ekvivalenspunkt\npH 7", xy=(eq_pH, 0),
        xycoords=("data", "axes fraction"),
        xytext=(eq_pH - 2.0, -0.35),
        textcoords=("data", "axes fraction"),
        ha="center", va="top", fontsize=14,
        color=eq_color, fontweight="bold",
        arrowprops=dict(arrowstyle="-", color=eq_color, lw=1.5),
    )
    ax.annotate(
        "Titreringspunkt\npH ≈ 7,1", xy=(tp_pH, 0),
        xycoords=("data", "axes fraction"),
        xytext=(tp_pH + 2.0, -0.35),
        textcoords=("data", "axes fraction"),
        ha="center", va="top", fontsize=14,
        color=tp_color, fontweight="bold",
        arrowprops=dict(arrowstyle="-", color=tp_color, lw=1.5),
    )

    # Legende
    legend_elements = [
        Line2D([0], [0], color=eq_color, lw=3, ls="--",
               label="Ekvivalenspunkt (kjemisk)"),
        Line2D([0], [0], color=tp_color, lw=3, ls="-",
               label="Titreringspunkt (visuelt)"),
    ]
    fig.legend(
        handles=legend_elements, loc="lower center", ncol=2,
        fontsize=14, frameon=True, edgecolor="#ccc", fancybox=True,
        bbox_to_anchor=(0.5, 0.02),
    )

    plt.savefig(save_path, dpi=200, bbox_inches="tight", facecolor="white")
    plt.close()
    print(f"Figur 2 lagret: {save_path}")


# ═══════════════════════════════════════════════════════════════════════════
if __name__ == "__main__":
    figur1_ph_skala("ph_skala_indikatorer.png")
    figur2_titrering("titrering_indikatorvalg.png")
    print("Ferdig.")