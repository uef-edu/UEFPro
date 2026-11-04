#!/usr/bin/env python3
"""Export README-ready SVGs (mark + product badges) from fonts/icons/UEFProIcons-Regular.ttf."""
from pathlib import Path
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.ttLib import TTFont

ROOT = Path(__file__).resolve().parent.parent
f = TTFont(ROOT / "fonts/icons/UEFProIcons-Regular.ttf")
gs = f.getGlyphSet()
RED, BLUE, BADGE = "#ED1C24", "#0077C0", "#0077C0"


def d(name):
    pen = SVGPathPen(gs)
    # font y-up -> svg y-down, viewBox y from -720..40
    gs[name].draw(TransformPen(pen, (1, 0, 0, -1, 0, 0)))
    return pen.getCommands()


def svg(name, paths, w, y0=-700, h=700):
    body = "".join(f'<path fill="{c}" d="{d(g)}"/>' for g, c in paths)
    (ROOT / "icons/svg" / f"{name}.svg").write_text(
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 {y0} {w} {h}">{body}</svg>\n')


adv = lambda n: f["hmtx"][n][0]
svg("uef-mark-color", [("uef-mark.blue", BLUE), ("uef-mark.red", RED)], adv("uef-mark.red"))
for n in ("badge-uef-id", "badge-lms", "badge-workplace"):
    svg(n, [(n, BADGE)], adv(n), y0=-640, h=640)
