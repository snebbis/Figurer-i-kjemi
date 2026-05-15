"""Generate a periodic table SVG showing electronegativity values."""

def generate_svg() -> str:
    # ---------- Geometry ----------
    CELL = 70
    PAD = 40
    LEGEND_GAP = 30
    LEGEND_BOX = 25
    BOTTOM_PAD = 40

    # ---------- Palette ----------
    # Distinkte pastellfarger basert på rød, oransje, gul, grønn, rosa
    COLORS = {
        "en_4":   "#FCA5A5", # Pastellrød
        "en_3":   "#FDBA74", # Pastelloransje
        "en_2":   "#FEF08A", # Pastellgul
        "en_1":   "#A7F3D0", # Pastellgrønn
        "en_0":   "#F9A8D4", # Pastellrosa
        "noble":  "#F3F4F6", # Lys grå for edelgasser
    }

    NOBLE_GASES = {"He", "Ne", "Ar", "Kr", "Xe", "Rn"}
    FONT = "Arial, Helvetica, sans-serif"

    # ---------- Data: (symbol, value, grid_x, grid_y, color) ----------
    elements = [
        # Top hydrogen row (H er hevet til y = -1.2)
        ("H",  "2,2",  2.5, -1.2, "en_2"),
        ("He", "",     7,   -1, "noble"),
        # Row 0
        ("Li", "1,0",  0, 0, "en_1"),
        ("Be", "1,6",  1, 0, "en_1"),
        ("B",  "2,0",  2, 0, "en_2"),
        ("C",  "2,55",  3, 0, "en_2"),
        ("N",  "3,0",  4, 0, "en_3"),
        ("O",  "3,4",  5, 0, "en_3"),
        ("F",  "4,0",  6, 0, "en_4"),
        ("Ne", "",     7, 0, "noble"),
        # Row 1
        ("Na", "0,93", 0, 1, "en_0"),
        ("Mg", "1,3",  1, 1, "en_1"),
        ("Al", "1,6",  2, 1, "en_1"),
        ("Si", "1,9",  3, 1, "en_1"),
        ("P",  "2,2",  4, 1, "en_2"),
        ("S",  "2,6",  5, 1, "en_2"),
        ("Cl", "3,2",  6, 1, "en_3"),
        ("Ar", "",     7, 1, "noble"),
        # Row 2
        ("K",  "0,82", 0, 2, "en_0"),
        ("Ca", "1,3",  1, 2, "en_1"),
        ("Ga", "1,6",  2, 2, "en_1"),
        ("Ge", "2,0",  3, 2, "en_2"),
        ("As", "2,2",  4, 2, "en_2"),
        ("Se", "2,6",  5, 2, "en_2"),
        ("Br", "3,0",  6, 2, "en_3"),
        ("Kr", "",     7, 2, "noble"),
        # Row 3
        ("Rb", "0,82", 0, 3, "en_0"),
        ("Sr", "0,95", 1, 3, "en_0"),
        ("In", "1,8",  2, 3, "en_1"),
        ("Sn", "2,0",  3, 3, "en_2"),
        ("Sb", "2,1",  4, 3, "en_2"),
        ("Te", "2,1",  5, 3, "en_2"),
        ("I",  "2,7",  6, 3, "en_2"),
        ("Xe", "",     7, 3, "noble"),
        # Row 4
        ("Cs", "0,79", 0, 4, "en_0"),
        ("Ba", "0,89", 1, 4, "en_0"),
        ("Tl", "2,0",  2, 4, "en_2"),
        ("Pb", "2,3",  3, 4, "en_2"),
        ("Bi", "2,0",  4, 4, "en_2"),
        ("Po", "2,0",  5, 4, "en_2"),
        ("At", "2,2",  6, 4, "en_2"),
        ("Rn", "",     7, 4, "noble"),
        # Row 5
        ("Fr", "0,70", 0, 5, "en_0"),
        ("Ra", "0,89", 1, 5, "en_0"),
    ]

    # ---------- Canvas ----------
    # Grid columns: 0..7 (8 wide). Grid rows: -1..5 (7 tall).
    n_cols, n_rows = 8, 7
    grid_w = n_cols * CELL              # 560
    grid_h = n_rows * CELL              # 490

    # Høyden er justert ned siden overskriften er borte
    width = grid_w + 2 * PAD            # 640
    height = PAD + grid_h + LEGEND_GAP + LEGEND_BOX + BOTTOM_PAD

    # Helper: grid coords -> pixel top-left of cell
    def to_px(gx: float, gy: float) -> tuple[float, float]:
        return PAD + gx * CELL, PAD + (gy + 1) * CELL  # +1 shifts y=-1 to top

    parts: list[str] = []
    parts.append(
        f'<svg xmlns="http://www.w3.org/2000/svg" '
        f'width="{width}" height="{height}" '
        f'viewBox="0 0 {width} {height}">'
    )

    # White background
    parts.append(f'<rect width="{width}" height="{height}" fill="white"/>')

    # H -> He connector line
    hx, hy = to_px(2.5, -1.2)
    hex_, hey = to_px(7, -1)
    line_y = hy + CELL / 2
    parts.append(
        f'<line x1="{hx + CELL}" y1="{line_y}" '
        f'x2="{hex_}" y2="{line_y}" '
        f'stroke="black" stroke-width="2"/>'
    )

    # Cells
    for sym, val, gx, gy, color in elements:
        px, py = to_px(gx, gy)
        fill = COLORS[color]
        parts.append(
            f'<rect x="{px}" y="{py}" width="{CELL}" height="{CELL}" '
            f'fill="{fill}" stroke="black" stroke-width="1"/>'
        )
        cx = px + CELL / 2
        if sym in NOBLE_GASES:
            cy = py + CELL / 2
            parts.append(
                f'<text x="{cx}" y="{cy}" font-family="{FONT}" '
                f'font-size="22" text-anchor="middle" '
                f'dominant-baseline="central">{sym}</text>'
            )
        else:
            # Sentrerer tekstblokken i hver boks
            sy = py + CELL / 2 - 10
            vy = py + CELL / 2 + 12
            parts.append(
                f'<text x="{cx}" y="{sy}" font-family="{FONT}" '
                f'font-size="22" text-anchor="middle" '
                f'dominant-baseline="central">{sym}</text>'
            )
            parts.append(
                f'<text x="{cx}" y="{vy}" font-family="{FONT}" '
                f'font-size="16" text-anchor="middle" '
                f'dominant-baseline="central">{val}</text>'
            )

    # Legend
    legend_items = [
        ("en_4", "4,0"),
        ("en_3", "3,0-3,9"),
        ("en_2", "2,0-2,9"),
        ("en_1", "1,0-1,9"),
        ("en_0", "0-0,99"),
    ]
    legend_y = PAD + grid_h + LEGEND_GAP
    slot_w = grid_w / len(legend_items)

    for i, (color_key, label) in enumerate(legend_items):
        slot_left = PAD + i * slot_w
        box_x = slot_left + 12
        box_y = legend_y
        parts.append(
            f'<rect x="{box_x}" y="{box_y}" '
            f'width="{LEGEND_BOX}" height="{LEGEND_BOX}" '
            f'fill="{COLORS[color_key]}" stroke="black" stroke-width="1"/>'
        )
        text_x = box_x + LEGEND_BOX + 8
        text_y = box_y + LEGEND_BOX / 2
        parts.append(
            f'<text x="{text_x}" y="{text_y}" font-family="{FONT}" '
            f'font-size="16" dominant-baseline="central">{label}</text>'
        )

    parts.append("</svg>")
    return "\n".join(parts)


if __name__ == "__main__":
    svg_content = generate_svg()
    out_path = "elektronegativitet.svg"
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(svg_content)
    print(f"Successfully generated {out_path}")