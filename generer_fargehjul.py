#!/usr/bin/env python3
"""Generate fargehjul.svg - chemistry complementary colour wheel for Kjemi-heftet."""
import math

# Redusert totalbredde og høyde for mindre dødt rom
VW, VH = 880, 460
cx, cy = 210, 230  
outerR, innerR = 150, 80
# Ny radius for tekst, plassert midt i kakestykket
label_r = (outerR + innerR) / 2

BLUE = "#1F4E79"
SUBTLE = "#5A5A5A"
BORDER = "#C4D2E4"
FONT = "Calibri, sans-serif"

# 12 segments, clockwise from top. (name, hex, wheel-label)
segments = [
    ("gronn",      "#34A853", "~530"),
    ("gulgronn",   "#8FBC1A", "~570"),
    ("gul",        "#F2C40D", "~580"),
    ("oransje",    "#F39200", "~600"),
    ("rodoransje", "#E8511D", "~630"),
    ("rod",        "#D52E2E", "~670"),
    ("purpur",     "#B02A6F", "purpur*"),
    ("fiolett",    "#7C3F98", "~415"),
    ("blafiolett", "#5141A0", "~440"),
    ("bla",        "#2466C6", "~465"),
    ("blagronn",   "#1597A6", "~485"),
    ("gronnbla",   "#169A6E", "~500"),
]

# complementary-pair table
rows = [
    ("400-430", "fiolett",    "#7C3F98", "gulgronn",  "#8FBC1A"),
    ("430-465", "blafiolett", "#5141A0", "gul",       "#F2C40D"),
    ("465-490", "bla",        "#2466C6", "oransje",   "#F39200"),
    ("490-500", "blagronn",   "#1597A6", "rod",       "#D52E2E"),
    ("500-560", "gronn",      "#34A853", "purpur",    "#B02A6F"),
    ("560-580", "gulgronn",   "#8FBC1A", "fiolett",   "#7C3F98"),
    ("580-620", "oransje",    "#F39200", "bla",       "#2466C6"),
    ("620-700", "rod",        "#D52E2E", "blagronn",  "#1597A6"),
]

# Norwegian display names
disp = {
    "gronn": "gr\u00f8nn", "gulgronn": "gulgr\u00f8nn", "gul": "gul",
    "oransje": "oransje", "rodoransje": "r\u00f8doransje", "rod": "r\u00f8d",
    "purpur": "purpur", "fiolett": "fiolett", "blafiolett": "bl\u00e5fiolett",
    "bla": "bl\u00e5", "blagronn": "bl\u00e5gr\u00f8nn", "gronnbla": "gr\u00f8nnbl\u00e5",
}

def pt(r, deg):
    a = math.radians(deg)
    return (cx + r * math.sin(a), cy - r * math.cos(a))

def seg_path(k):
    a0, a1 = k * 30, (k + 1) * 30
    ox0, oy0 = pt(outerR, a0)
    ox1, oy1 = pt(outerR, a1)
    ix1, iy1 = pt(innerR, a1)
    ix0, iy0 = pt(innerR, a0)
    return (f"M {ox0:.2f} {oy0:.2f} "
            f"A {outerR} {outerR} 0 0 1 {ox1:.2f} {oy1:.2f} "
            f"L {ix1:.2f} {iy1:.2f} "
            f"A {innerR} {innerR} 0 0 0 {ix0:.2f} {iy0:.2f} Z")

parts = []
parts.append(
    f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {VW} {VH}" '
    f'width="{VW}" height="{VH}" font-family="{FONT}">')
parts.append(f'<rect x="0" y="0" width="{VW}" height="{VH}" fill="#FFFFFF"/>')

# --- wheel segments ---
for k, (name, hexc, lbl) in enumerate(segments):
    parts.append(f'<path d="{seg_path(k)}" fill="{hexc}" stroke="#FFFFFF" stroke-width="1.6"/>')

# outline circles
parts.append(f'<circle cx="{cx}" cy="{cy}" r="{outerR}" fill="none" stroke="{BORDER}" stroke-width="1"/>')
parts.append(f'<circle cx="{cx}" cy="{cy}" r="{innerR}" fill="none" stroke="{BORDER}" stroke-width="1"/>')

# centre text
parts.append(f'<text x="{cx}" y="{cy-4}" font-size="14" fill="#8A8A8A" text-anchor="middle">synlig lys</text>')
parts.append(f'<text x="{cx}" y="{cy+16}" font-size="14" fill="#8A8A8A" text-anchor="middle">\u2248 400\u2013700 nm</text>')

# wavelength labels inside segments
for k, (name, hexc, lbl) in enumerate(segments):
    ang = k * 30 + 15
    lx, ly = pt(label_r, ang)
    
    # Bestem tekstfarge basert på bakgrunnsfargen for best lesbarhet
    t_color = "#000000" if name in ["gul", "gulgronn", "oransje"] else "#FFFFFF"
    
    if lbl == "purpur":
        parts.append(f'<text x="{lx:.1f}" y="{ly+5:.1f}" font-size="14" font-weight="bold" fill="{t_color}" text-anchor="middle">{lbl}</text>')
    else:
        # Deler opp tallet og "nm" på to linjer for at de skal få plass i "kakestykket"
        parts.append(f'<text x="{lx:.1f}" y="{ly-2:.1f}" font-size="14" font-weight="bold" fill="{t_color}" text-anchor="middle">{lbl}</text>')
        parts.append(f'<text x="{lx:.1f}" y="{ly+12:.1f}" font-size="11" font-weight="bold" fill="{t_color}" text-anchor="middle">nm</text>')

# --- table ---
tx = 410 
col1, col2, col3 = 130, 160, 160 
tw = col1 + col2 + col3
hdr_y = 65 
hdr_h = 38 
row_h = 36 

# Bakgrunnsfarger for rader
for i in range(len(rows)):
    ry = hdr_y + hdr_h + i * row_h
    bg = "#FFFFFF" if i % 2 == 0 else "#F2F4F7"
    parts.append(f'<rect x="{tx}" y="{ry}" width="{tw}" height="{row_h}" fill="{bg}"/>')

# Overskriftsrad bakgrunn
parts.append(f'<rect x="{tx}" y="{hdr_y}" width="{tw}" height="{hdr_h}" fill="#DDEBF7"/>')

# Rutenett (Grid lines)
for i in range(len(rows) + 2):
    y = hdr_y + i * row_h + (hdr_h - row_h if i > 0 else 0)
    parts.append(f'<line x1="{tx}" y1="{y}" x2="{tx+tw}" y2="{y}" stroke="#A6A6A6" stroke-width="1"/>')

xs = [tx, tx+col1, tx+col1+col2, tx+tw]
bottom_y = hdr_y + hdr_h + len(rows) * row_h
for x in xs:
    parts.append(f'<line x1="{x}" y1="{hdr_y}" x2="{x}" y2="{bottom_y}" stroke="#A6A6A6" stroke-width="1"/>')

def center_text(x, y, text, weight="normal", size="14"):
    return f'<text x="{x}" y="{y+5:.0f}" font-family="{FONT}" font-size="{size}" font-weight="{weight}" fill="#000000" text-anchor="middle">{text}</text>'

# Header tekst 
parts.append(center_text(tx + col1/2, hdr_y + hdr_h/2, "\u03bb absorbert (nm)", weight="bold", size="15"))
parts.append(center_text(tx + col1 + col2/2, hdr_y + hdr_h/2, "Absorbert farge", weight="bold", size="15"))
parts.append(center_text(tx + col1 + col2 + col3/2, hdr_y + hdr_h/2, "Observert farge", weight="bold", size="15"))

# Datarader 
for i, (rng, an, ah, on, oh) in enumerate(rows):
    midy = hdr_y + hdr_h + i * row_h + row_h / 2
    
    # Kolonne 1: Bølgelengde
    parts.append(center_text(tx + col1/2, midy, rng, size="14"))

    sw = 16 
    
    # Kolonne 2: Absorbert farge
    cx2 = tx + col1 + col2/2
    parts.append(f'<rect x="{cx2 - 45}" y="{midy - sw/2:.0f}" width="{sw}" height="{sw}" rx="3" fill="{ah}" stroke="#888888" stroke-width="0.5"/>')
    parts.append(f'<text x="{cx2 - 20}" y="{midy+5:.0f}" font-family="{FONT}" font-size="14" fill="#000000">{disp[an]}</text>')

    # Kolonne 3: Observert farge
    cx3 = tx + col1 + col2 + col3/2
    parts.append(f'<rect x="{cx3 - 45}" y="{midy - sw/2:.0f}" width="{sw}" height="{sw}" rx="3" fill="{oh}" stroke="#888888" stroke-width="0.5"/>')
    parts.append(f'<text x="{cx3 - 20}" y="{midy+5:.0f}" font-family="{FONT}" font-size="14" fill="#000000">{disp[on]}</text>')

parts.append('</svg>')

svg = "\n".join(parts)

with open("fargehjul.svg", "w", encoding="utf-8") as f:
    f.write(svg)
print("wrote fargehjul.svg", len(svg), "bytes")