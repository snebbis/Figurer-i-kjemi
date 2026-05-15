"""
Build an A4 SVG collage of the 20 standard amino acids.
Layout optimert for minimal avstand mellom molekyl og navn.
"""

from __future__ import annotations

import re
from pathlib import Path

import pandas as pd
from rdkit import Chem
from rdkit.Chem import AllChem
from rdkit.Chem.Draw import rdMolDraw2D

# --- Forbedret Norsk Ordbok ----------------------------------------------
_TRANSLATIONS = {
    "alanine": "Alanin",
    "arginine": "Arginin",
    "asparagine": "Asparagin",
    "aspartic acid": "Asparaginsyre",
    "aspartate": "Aspartat",
    "cysteine": "Cystein",
    "glutamic acid": "Glutaminsyre",
    "glutamate": "Glutamat",
    "glutamine": "Glutamin",
    "glycine": "Glycin",
    "histidine": "Histidin",
    "isoleucine": "Isoleucin",
    "leucine": "Leucin",
    "lysine": "Lysin",
    "methionine": "Metionin",
    "phenylalanine": "Fenylalanin",
    "proline": "Prolin",
    "serine": "Serin",
    "threonine": "Treonin",
    "tryptophan": "Tryptofan",
    "tyrosine": "Tyrosin",
    "valine": "Valin"
}

def get_norwegian_name(english_name: str) -> str:
    if not isinstance(english_name, str):
        return str(english_name)
    key = english_name.strip().lower()
    return _TRANSLATIONS.get(key, english_name)

# --- A4 canvas geometry --------------------------------------------------
PX_PER_MM = 10
A4_W_MM, A4_H_MM = 210, 297
A4_W_PX = A4_W_MM * PX_PER_MM
A4_H_PX = A4_H_MM * PX_PER_MM
MARGIN_PX = 10 * PX_PER_MM
COLS, ROWS = 4, 5

CELL_W = (A4_W_PX - 2 * MARGIN_PX) / COLS
CELL_H = (A4_H_PX - 2 * MARGIN_PX) / ROWS

# Geometri for tekst og molekyl
LABEL_FONT_PX = 40          
ATOM_FONT_PX = 38           
LABEL_BAND_PX = 15          # Minimal plass reservert til label
DRAW_W = CELL_W
DRAW_H = CELL_H - LABEL_BAND_PX

# --- SVG fragment extraction ---------------------------------------------
_SVG_OPEN_RE = re.compile(r"<svg\b[^>]*>", re.DOTALL)
_SVG_CLOSE_RE = re.compile(r"</svg>\s*$")
_BG_RECT_RE = re.compile(r"<rect[^/]*?style='[^']*fill:#FFFFFF[^']*'[^/]*/>", re.IGNORECASE)

def extract_svg_body(svg_text: str) -> str:
    body = _SVG_OPEN_RE.sub("", svg_text, count=1)
    body = _SVG_CLOSE_RE.sub("", body)
    body = _BG_RECT_RE.sub("", body)
    body = re.sub(r"<\?xml[^?]*\?>", "", body)
    body = body.replace("", "")
    return body.strip()

# --- Molecule rendering --------------------------------------------------
def render_mol_svg(smiles: str, width: int, height: int) -> str:
    mol = Chem.MolFromSmiles(smiles)
    if mol is None:
        raise ValueError(f"RDKit kunne ikke tolke SMILES: {smiles!r}")
    
    AllChem.Compute2DCoords(mol)

    drawer = rdMolDraw2D.MolDraw2DSVG(width, height)
    opts = drawer.drawOptions()
    
    opts.bondLineWidth = 2.5        
    opts.minFontSize = ATOM_FONT_PX 
    opts.maxFontSize = ATOM_FONT_PX
    opts.baseFontSize = 1.0         
    opts.clearBackground = False    
    opts.padding = 0.0              

    drawer.DrawMolecule(mol)
    drawer.FinishDrawing()
    return drawer.GetDrawingText()

# --- Page assembly -------------------------------------------------------
def build_collage(df: pd.DataFrame, out_path: Path) -> None:
    parts: list[str] = []
    parts.append(
        f'<?xml version="1.0" encoding="UTF-8" standalone="no"?>\n'
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{A4_W_MM}mm" height="{A4_H_MM}mm" '
        f'viewBox="0 0 {A4_W_PX} {A4_H_PX}">\n'
    )
    # Lagt til dominant-baseline for bedre vertikal kontroll
    parts.append(
        '  <style>\n'
        '    .aa-label { font-family: "Helvetica", "Arial", sans-serif; font-weight: bold; '
        f'font-size: {LABEL_FONT_PX}px; fill: #111; text-anchor: middle; '
        'dominant-baseline: hanging; }\n'
        '  </style>\n'
    )

    for idx, row in df.reset_index(drop=True).iterrows():
        col = idx % COLS
        rowi = idx // COLS
        x0 = MARGIN_PX + col * CELL_W
        y0 = MARGIN_PX + rowi * CELL_H

        mol_svg = render_mol_svg(row["SMILES"], int(DRAW_W), int(DRAW_H))
        body = extract_svg_body(mol_svg)

        parts.append(f'  <g transform="translate({x0:.2f},{y0:.2f})">\n')
        parts.append(body)
        parts.append("\n  </g>\n")

        norsk_navn = get_norwegian_name(row["Name"])
        
        label_x = x0 + CELL_W / 2
        # Flyttet teksten helt opp til kanten av tegningen
        label_y = y0 + DRAW_H + (LABEL_FONT_PX * 0.2)
        
        parts.append(
            f'  <text class="aa-label" x="{label_x:.2f}" '
            f'y="{label_y:.2f}">{norsk_navn}</text>\n'
        )

    parts.append("</svg>\n")
    out_path.write_text("".join(parts), encoding="utf-8")
    print(f"Ferdig! Resultatet ligger her: {out_path}")

def main() -> None:
    here = Path(__file__).parent
    try:
        df = pd.read_excel(here / "amino_acids.xlsx")
        build_collage(df, here / "amino_acids_A4_layout.svg")
    except Exception as e:
        print(f"Feil: {e}")

if __name__ == "__main__":
    main()