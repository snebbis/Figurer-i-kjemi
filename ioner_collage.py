from rdkit import Chem
from rdkit.Chem import Draw
from rdkit.Chem.Draw import rdMolDraw2D
import math
import re

# Valenselektroner (hovedgruppe). Overgangsmetaller står ikke her -> får ikke
# tegnet ledige par (Lewis-formalismen gjelder ikke pent for Mn/Cr).
VALENS_ELEKTRONER = {
    'H': 1, 'B': 3, 'C': 4, 'N': 5, 'O': 6, 'P': 5, 'S': 6,
    'F': 7, 'Cl': 7, 'Br': 7, 'I': 7,
}

# 1. Utvalgte ioner (samme liste som før)
ion_data = [
    {"Navn": "Ammonium", "SMILES": "[NH4+]"},
    {"Navn": "Oksonium", "SMILES": "[OH3+]"},
    {"Navn": "Hydroksid", "SMILES": "[OH-]"},
    {"Navn": "Nitrat", "SMILES": "[O-][N+](=O)[O-]"},
    {"Navn": "Nitritt", "SMILES": "[O-]N=O"},
    {"Navn": "Cyanid", "SMILES": "[C-]#N"},
    {"Navn": "Sulfat", "SMILES": "[O-]S(=O)(=O)[O-]"},
    {"Navn": "Sulfitt", "SMILES": "[O-]S(=O)[O-]"},
    {"Navn": "Hydrogensulfat", "SMILES": "OS(=O)(=O)[O-]"},
    {"Navn": "Tiosulfat", "SMILES": "[O-]S(=O)(=S)[O-]"},
    {"Navn": "Karbonat", "SMILES": "[O-]C([O-])=O"},
    {"Navn": "Hydrogenkarbonat", "SMILES": "OC(=O)[O-]"},
    {"Navn": "Fosfat", "SMILES": "[O-]P(=O)([O-])[O-]"},
    {"Navn": "Hydrogenfosfat", "SMILES": "OP(=O)([O-])[O-]"},
    {"Navn": "Dihydrogenfosfat", "SMILES": "OP(=O)(O)[O-]"},
    {"Navn": "Oksalat", "SMILES": "[O-]C(=O)C(=O)[O-]"},
    {"Navn": "Acetat", "SMILES": "CC(=O)[O-]"},
    {"Navn": "Permanganat", "SMILES": "[O-][Mn](=O)(=O)=O"},
    {"Navn": "Kromat", "SMILES": "[O-][Cr](=O)(=O)[O-]"},
    {"Navn": "Dikromat", "SMILES": "[O-][Cr](=O)(=O)O[Cr](=O)(=O)[O-]"},
    {"Navn": "Hypokloritt", "SMILES": "[O-]Cl"},
    {"Navn": "Kloritt", "SMILES": "[O-]Cl=O"},
    {"Navn": "Klorat", "SMILES": "[O-]Cl(=O)=O"},
    {"Navn": "Perklorat", "SMILES": "[O-]Cl(=O)(=O)=O"}
]


def les_smiles(smiles):
    """Parser SMILES uten RDKits 'cleanup'-steg. Det steget skriver om
    hypervalente klor-oksyanioner (klorat, perklorat ...) til en
    ladningsseparert form. Vi vil beholde strukturen slik den er skrevet
    (dobbeltbindinger), så alle oksyanionene tegnes konsekvent."""
    mol = Chem.MolFromSmiles(smiles, sanitize=False)
    if mol is None:
        return None
    flags = (Chem.SanitizeFlags.SANITIZE_ALL
             ^ Chem.SanitizeFlags.SANITIZE_CLEANUP
             ^ Chem.SanitizeFlags.SANITIZE_PROPERTIES)
    Chem.SanitizeMol(mol, sanitizeOps=flags)
    mol.UpdatePropertyCache(strict=False)
    return mol


def beregn_ledige_par(atom):
    """Antall ledige elektronpar fra Lewis-formalismen:
    ikke-bindende elektroner = gruppeelektroner - formell ladning - sum bindingsordener."""
    sym = atom.GetSymbol()
    if sym not in VALENS_ELEKTRONER:
        return 0
    gruppe = VALENS_ELEKTRONER[sym]
    fc = atom.GetFormalCharge()
    bindingssum = sum(b.GetBondTypeAsDouble() for b in atom.GetBonds())
    bindingssum += atom.GetTotalNumHs()
    ikke_bindende = gruppe - fc - bindingssum
    if ikke_bindende < 0:
        return 0
    return int(round(ikke_bindende)) // 2


def storste_gap(vinkler):
    """Returnerer retningen (radianer) midt i det største åpne mellomrommet
    mellom de oppgitte vinklene. Med én vinkel blir det rett motsatt."""
    if not vinkler:
        return -math.pi / 2.0
    s = sorted(v % (2 * math.pi) for v in vinkler)
    n = len(s)
    beste_gap, beste_midt = -1.0, 0.0
    for i in range(n):
        a1 = s[i]
        a2 = s[(i + 1) % n]
        if i + 1 == n:
            a2 += 2 * math.pi
        gap = a2 - a1
        if gap > beste_gap:
            beste_gap = gap
            beste_midt = (a1 + a2) / 2.0
    return beste_midt % (2 * math.pi)


def implisitt_h_retning(bindingsvinkler):
    """Retningen RDKit tegner en implisitt H-etikett i."""
    if not bindingsvinkler:
        return 0.0
    return storste_gap(bindingsvinkler)


def sett_ladningsfri_label(mol):
    """RDKit tegner ladningen klistret inntil atomet. Vi overstyrer etiketten
    så RDKit kun tegner grunnsymbolet - selve ladningstegnet tegner vi selv.
    Vi skjuler også 'H' for nøytrale OH-grupper, slik at vi kan tegne H manuelt."""
    for atom in mol.GetAtoms():
        sym = atom.GetSymbol()
        nh = atom.GetTotalNumHs()
        fc = atom.GetFormalCharge()

        # Isoler O med H i fler-atomige ioner (f.eks dihydrogenfosfat) for manuell tegning
        if mol.GetNumAtoms() > 1 and sym == 'O' and nh > 0:
            atom.SetProp('atomLabel', sym)
            atom.SetProp('DrawManualH', str(nh))
        elif fc != 0:
            if nh == 0:
                lab = sym
            elif nh == 1:
                lab = sym + 'H'
            else:
                lab = f'{sym}H{nh}'
            atom.SetProp('atomLabel', lab)


def ekstra_svg(mol, d2d):
    """Bygger SVG-elementer for ledige elektronpar (prikkpar), ladninger
    og manuelt posisjonerte H-atomer. Ladningen plasseres på motsatt side av
    bindingen; de ledige parene fordeles i de resterende åpne sektorene."""
    ut = []
    for atom in mol.GetAtoms():
        i = atom.GetIdx()
        p = d2d.GetDrawCoords(i)
        px, py = p.x, p.y

        # Retninger ut mot tunge naboer
        bindingsvinkler = []
        for nb in atom.GetNeighbors():
            q = d2d.GetDrawCoords(nb.GetIdx())
            bindingsvinkler.append(math.atan2(q.y - py, q.x - px))

        nh = atom.GetTotalNumHs()
        sym_lengde = len(atom.GetSymbol())

        # --- Ladning (plasseres først, motsatt bindingen / i største gap) ---
        fc = atom.GetFormalCharge()
        ladnings_vinkel = None
        if fc != 0:
            ladnings_vinkel = storste_gap(bindingsvinkler)
            r = 16 + 6 * max(0, sym_lengde - 1) + (5 if nh else 0)
            lx = px + r * math.cos(ladnings_vinkel)
            ly = py + r * math.sin(ladnings_vinkel)
            if abs(fc) == 1:
                tegn = '+' if fc > 0 else '\u2212'
            else:
                tegn = f"{abs(fc)}{'+' if fc > 0 else '\u2212'}"
            ut.append(
                f'<text x="{lx:.1f}" y="{ly:.1f}" text-anchor="middle" '
                f'dominant-baseline="central" font-family="Arial, sans-serif" '
                f'font-size="17" font-weight="bold" fill="#000">{tegn}</text>'
            )
            
        # --- Manuell H (Ned og til høyre relativt til O) ---
        manuell_h_vinkel = None
        if atom.HasProp('DrawManualH'):
            dx, dy = 18.0, 16.0  # Justert vinkel ned/høyre for H-atomet
            hx = px + dx
            hy = py + dy
            manuell_h_vinkel = math.atan2(dy, dx)

            nh_val = int(atom.GetProp('DrawManualH'))
            h_tekst = 'H' if nh_val == 1 else f'H<tspan baseline-shift="sub" font-size="0.75em">{nh_val}</tspan>'

            ut.append(
                f'<text x="{hx:.1f}" y="{hy:.1f}" text-anchor="middle" '
                f'dominant-baseline="central" font-family="sans-serif" '
                f'font-size="24" fill="#FF0000">{h_tekst}</text>'
            )

        # --- Ledige elektronpar ---
        n_par = beregn_ledige_par(atom)
        if n_par:
            opptatt = list(bindingsvinkler)
            if manuell_h_vinkel is not None:
                opptatt.append(manuell_h_vinkel) # Hindre kollisjon med vår manuelle H
            elif nh: 
                opptatt.append(implisitt_h_retning(bindingsvinkler))
                
            if ladnings_vinkel is not None:
                opptatt.append(ladnings_vinkel)
                
            r = 13 + 4 * max(0, sym_lengde - 1) + (3 if nh else 0)
            for _ in range(n_par):
                th = storste_gap(opptatt)
                opptatt.append(th)
                cx = px + r * math.cos(th)
                cy = py + r * math.sin(th)
                ux, uy = -math.sin(th), math.cos(th)  # vinkelrett på radien
                sep = 2.9
                for sgn in (-1, 1):
                    ut.append(
                        f'<circle cx="{cx + ux * sep * sgn:.1f}" '
                        f'cy="{cy + uy * sep * sgn:.1f}" r="1.8" fill="#000"/>'
                    )
    return '\n'.join(ut)


def path_bbokser(svg):
    """Rammeboks for hver enkelt <path> i SVG-en, i tegnerekkefølge. For et
    énatoms-ion er path-ene glyfene i den kondenserte etiketten fra venstre
    mot høyre, så path[0] er selve det tunge atomet (O i 'OH3', N i 'NH4')."""
    bokser = []
    for d in re.findall(r" d='([^']*)'", svg):
        tall = [float(t) for t in re.findall(r'-?\d*\.?\d+', d)]
        xs, ys = tall[0::2], tall[1::2]
        if xs:
            bokser.append((min(xs), min(ys), max(xs), max(ys)))
    return bokser


def par_prikker(cx, cy, radial_vinkel):
    """To prikker som utgjør ett ledig par, stilt vinkelrett på radien."""
    ux, uy = -math.sin(radial_vinkel), math.cos(radial_vinkel)
    sep = 2.9
    return ''.join(
        f'<circle cx="{cx + ux * sep * s:.1f}" cy="{cy + uy * sep * s:.1f}" '
        f'r="1.8" fill="#000"/>'
        for s in (-1, 1)
    )


def ekstra_svg_enkelt(mol, bokser):
    """Ladning og ledige par for et frittstående énatoms-ion (ammonium,
    oksonium, hydroksid). Hele den kondenserte etiketten er ett objekt:
    ladningen settes over etiketten, mens de ledige parene festes til selve
    det tunge atom-glyfen (path[0]) - aldri på H-ene - på de sidene som er
    ledige (RDKit tegner alltid H-ene mot høyre, så venstre/topp/bunn er fri)."""
    atom = mol.GetAtomWithIdx(0)
    ut = []

    # Ladning over siste glyf (øvre høyre) - konvensjonell ioneskrivemåte,
    # og holder seg unna de ledige parene som sitter på det tunge atomet til venstre
    fc = atom.GetFormalCharge()
    if fc != 0:
        if abs(fc) == 1:
            tegn = '+' if fc > 0 else '\u2212'
        else:
            tegn = f"{abs(fc)}{'+' if fc > 0 else '\u2212'}"
        sx0, sy0, sx1, sy1 = bokser[-1]
        ut.append(
            f'<text x="{(sx0 + sx1) / 2:.1f}" y="{sy0 - 11:.1f}" '
            f'text-anchor="middle" dominant-baseline="central" '
            f'font-family="Arial, sans-serif" font-size="17" '
            f'font-weight="bold" fill="#000">{tegn}</text>'
        )

    # Ledige par på det tunge atom-glyfen: venstre, topp, bunn
    ax0, ay0, ax1, ay1 = bokser[0]
    acx, acy = (ax0 + ax1) / 2.0, (ay0 + ay1) / 2.0
    m = 7.0
    ankre = [
        (ax0 - m, acy, math.pi),         # venstre
        (acx, ay0 - m, -math.pi / 2),    # topp
        (acx, ay1 + m, math.pi / 2),     # bunn
    ]
    for k in range(min(beregn_ledige_par(atom), len(ankre))):
        ax, ay, vinkel = ankre[k]
        ut.append(par_prikker(ax, ay, vinkel))

    return '\n'.join(ut)


def tegn_ion(smiles, bredde, hoyde):
    """Tegner ionet uten RDKit-legend, men med ledige par og flyttet ladning."""
    mol = les_smiles(smiles)
    if not mol:
        return ''
    mol = Draw.PrepareMolForDrawing(mol)
    sett_ladningsfri_label(mol)

    d2d = rdMolDraw2D.MolDraw2DSVG(bredde, hoyde)
    opts = d2d.drawOptions()
    opts.bondLineWidth = 3
    opts.fixedFontSize = 24
    opts.minFontSize = 24
    opts.padding = 0.19  # mindre marg -> større molekyl -> mer plass mellom atomer
    opts.clearBackground = False

    d2d.DrawMolecule(mol)

    if mol.GetNumAtoms() == 1:
        # Frittstående énatoms-ion: etiketten er ett objekt. Hent glyf-boksene
        # fra SVG-en og plasser pyntingen rundt selve det tunge atomet.
        d2d.FinishDrawing()
        svg_tekst = d2d.GetDrawingText()
        bokser = path_bbokser(svg_tekst)
        ekstra = ekstra_svg_enkelt(mol, bokser) if bokser else ''
    else:
        ekstra = ekstra_svg(mol, d2d)   # GetDrawCoords må kalles før FinishDrawing
        d2d.FinishDrawing()
        svg_tekst = d2d.GetDrawingText()

    content = svg_tekst.split('?>')[-1].split('<svg')[1].split('>', 1)[1].rsplit('</svg>', 1)[0]
    return content + '\n' + ekstra


def generer_perfekt_kollasje(data, filnavn="ioner_kjemi_v6.svg"):
    mols_per_rad = 6
    cell_w, cell_h = 270, 270

    n_rader = (len(data) + mols_per_rad - 1) // mols_per_rad
    total_w = mols_per_rad * cell_w
    total_h = n_rader * cell_h

    hoved_svg = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{total_w}" height="{total_h}" viewBox="0 0 {total_w} {total_h}">',
        '<rect width="100%" height="100%" fill="white"/>'
    ]

    for i, item in enumerate(data):
        rad = i // mols_per_rad
        kol = i % mols_per_rad
        x = kol * cell_w
        y = rad * cell_h

        ion_content = tegn_ion(item["SMILES"], cell_w, cell_h - 60)

        hoved_svg.append(f'<g transform="translate({x}, {y})">')
        hoved_svg.append(ion_content)
        hoved_svg.append(
            f'<text x="{cell_w / 2}" y="{cell_h - 15}" '
            f'text-anchor="middle" '
            f'font-family="Arial, sans-serif" '
            f'font-size="22" '
            f'font-weight="bold" '
            f'fill="black">{item["Navn"]}</text>'
        )
        hoved_svg.append('</g>')

    hoved_svg.append('</svg>')

    with open(filnavn, "w", encoding="utf-8") as f:
        f.write("\n".join(hoved_svg))

    print(f"Suksess! Nå med ledige elektronpar og flyttet ladning. Lagret som {filnavn}")


if __name__ == "__main__":
    generer_perfekt_kollasje(ion_data)