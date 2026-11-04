#!/usr/bin/env python3
"""Build "UEF Pro Icons" from the UEF logo SVGs and UEF Pro letterforms.

Glyphs (Private Use Area):
  U+E000 logo (Vietnamese tagline)     mono      U+E100 same, COLRv1 colour
  U+E001 logo (English tagline)        mono      U+E101 same, COLRv1 colour
  U+E002 mark (emblem + UEF, no tagline) mono    U+E102 same, COLRv1 colour
  U+E010 badge "UEF ID"   U+E011 badge "LMS"   U+E012 badge "Workplace"

Usage (from repo root, venv with fonttools + skia-pathops):
  python icons/build_icons.py
"""
import xml.etree.ElementTree as ET
from pathlib import Path

import pathops
from fontTools.colorLib.builder import buildCOLR, buildCPAL
from fontTools.pens.cu2quPen import Cu2QuPen
from fontTools.fontBuilder import FontBuilder
from fontTools.pens.boundsPen import BoundsPen
from fontTools.pens.transformPen import TransformPen
from fontTools.pens.ttGlyphPen import TTGlyphPen
from fontTools.ttLib import TTFont
from fontTools.ttLib.tables.otTables import PaintFormat
from fontTools.svgLib.path import parse_path

ROOT = Path(__file__).resolve().parent.parent
SVG = ROOT / "icons" / "svg"
OUT = ROOT / "fonts" / "icons"
UPM = 1000
RED, BLUE = (0xED, 0x1C, 0x24), (0x00, 0x77, 0xC0)  # from the logo SVGs
NS = "{http://www.w3.org/2000/svg}"


def rect_d(x, y, w, h):
    return f"M{x},{y}h{w}v{h}h{-w}z"


def load_svg(name):
    """-> list of (class, pathops.Path) in SVG coordinates (y down)."""
    items = []
    for el in ET.parse(SVG / f"{name}.svg").iter():
        if el.tag == NS + "path":
            d = el.get("d")
        elif el.tag == NS + "rect":
            d = rect_d(*(float(el.get(k)) for k in ("x", "y", "width", "height")))
        else:
            continue
        p = pathops.Path()
        parse_path(d, p.getPen())
        items.append((el.get("class"), p))
    return items


def bounds(path):
    bp = BoundsPen(None)
    path.draw(bp)
    return bp.bounds


def union(paths):
    out = pathops.Path()
    for p in paths:
        p.draw(out.getPen())
    out.simplify(fix_winding=True)
    return out


def place(path, scale, dx, dy, flip=True):
    """Scale (and flip y for SVG), translate, return new pathops.Path."""
    out = pathops.Path()
    t = (scale, 0, 0, -scale if flip else scale, dx, dy)
    path.draw(TransformPen(out.getPen(), t))
    out.simplify(fix_winding=True)
    return out


def to_glyph(path):
    pen = TTGlyphPen(None)
    path.draw(Cu2QuPen(pen, max_err=1.0, reverse_direction=True))
    return pen.glyph()


def fit(parts, height):
    """Scale+translate groups of svg paths so they share one bbox: bottom at y=0, left at x=0."""
    all_b = [bounds(p) for ps in parts.values() for p in ps]
    x0 = min(b[0] for b in all_b)
    y0 = min(b[1] for b in all_b)
    x1 = max(b[2] for b in all_b)
    y1 = max(b[3] for b in all_b)
    s = height / (y1 - y0)
    # svg y-down: flipped y' = -s*y + s*y1  -> bottom (y1) maps to 0
    return {k: union([place(p, s, -x0 * s, y1 * s) for p in ps]) for k, ps in parts.items()}, (x1 - x0) * s


def logo_glyphs(name, height, drop_tagline):
    items = load_svg(name)
    if drop_tagline:
        items = [(c, p) for c, p in items if bounds(p)[1] < 290]
    red = [p for c, p in items if c == "d"]
    blue = [p for c, p in items if c != "d"]
    g, w = fit({"red": red, "blue": blue}, height)
    return g["red"], g["blue"], w


def badge(font, text, cap=330, pad=150, h=640, radius=130, tracking=14):
    t = pathops.Path()
    gs, cmap = font.getGlyphSet(), font.getBestCmap()
    s = cap / font["OS/2"].sCapHeight
    x = 0
    for ch in text:
        gn = cmap[ord(ch)]
        gs[gn].draw(TransformPen(t.getPen(), (s, 0, 0, s, x, 0)))
        x += gs[gn].width * s + tracking
    w = x - tracking + 2 * pad
    box = pathops.Path()
    pen = box.getPen()
    r = radius
    # rounded rect (cubic) from (0,0) to (w,h)
    k = 0.5523 * r
    pen.moveTo((r, 0)); pen.lineTo((w - r, 0))
    pen.curveTo((w - r + k, 0), (w, r - k), (w, r)); pen.lineTo((w, h - r))
    pen.curveTo((w, h - r + k), (w - r + k, h), (w - r, h)); pen.lineTo((r, h))
    pen.curveTo((r - k, h), (0, h - r + k), (0, h - r)); pen.lineTo((0, r))
    pen.curveTo((0, r - k), (r - k, 0), (r, 0)); pen.closePath()
    tb = bounds(t)
    ty = (h - cap) / 2
    txt = pathops.Path()
    t.draw(TransformPen(txt.getPen(), (1, 0, 0, 1, pad - tb[0], ty)))
    out = pathops.op(box, txt, pathops.PathOp.DIFFERENCE)
    return out, w


def main():
    src = TTFont(ROOT / "fonts" / "ttf" / "UEFPro-Bold.ttf")
    glyphs = {}  # name -> (pathops.Path, advance)
    codepoints = {}
    layers = {}

    def add(name, cp, path, adv, pad=40):
        glyphs[name] = (path, adv + 2 * pad, pad)
        codepoints[cp] = name

    for cp_m, cp_c, name, svg, drop, h in [
        (0xE000, 0xE100, "uef-logo-vi", "uef-vi-color", False, 700),
        (0xE001, 0xE101, "uef-logo-en", "uef-en-color", False, 700),
        (0xE002, 0xE102, "uef-mark", "uef-vi-color", True, 700),
    ]:
        red, blue, w = logo_glyphs(svg, h, drop)
        full = union([red, blue])
        add(name, cp_m, full, w)
        add(name + ".color", cp_c, full, w)  # fallback outline = mono
        add(name + ".red", None, red, w)
        add(name + ".blue", None, blue, w)
        layers[name + ".color"] = (name + ".red", name + ".blue")

    for cp, name, text in [(0xE010, "badge-uef-id", "UEF ID"), (0xE011, "badge-lms", "LMS"),
                           (0xE012, "badge-workplace", "Workplace")]:
        p, w = badge(src, text)
        add(name, cp, p, w, pad=60)

    order = [".notdef", "space"] + list(glyphs)
    fb = FontBuilder(UPM, isTTF=True)
    fb.setupGlyphOrder(order)
    cmap = {0x20: "space"}
    cmap.update({cp: n for cp, n in codepoints.items() if cp is not None})
    fb.setupCharacterMap(cmap)

    empty = TTGlyphPen(None).glyph()
    gl = {".notdef": empty, "space": empty}
    hm = {".notdef": (500, 0), "space": (300, 0)}
    for name, (path, adv, pad) in glyphs.items():
        moved = pathops.Path()
        path.draw(TransformPen(moved.getPen(), (1, 0, 0, 1, pad, 0)))
        gl[name] = to_glyph(moved)
        xmin = min(c[0] for c in gl[name].coordinates)
        # lsb must equal the glyph's real xMin, otherwise renderers shift each COLR layer differently
        hm[name] = (int(round(adv)), int(xmin))
    fb.setupGlyf(gl)
    fb.setupHorizontalMetrics(hm)
    fb.setupHorizontalHeader(ascent=800, descent=-200)
    fb.setupNameTable({
        "familyName": "UEF Pro Icons", "styleName": "Regular",
        "copyright": src["name"].getDebugName(0),
        "uniqueFontIdentifier": "UEFProIcons-Regular",
        "version": "Version 1.000",
        "fullName": "UEF Pro Icons Regular", "psName": "UEFProIcons-Regular",
        "licenseDescription": "SIL Open Font License 1.1 (font software). UEF logos are trademarks of UEF.",
        "licenseInfoURL": "https://openfontlicense.org",
    })
    fb.setupOS2(sTypoAscender=800, sTypoDescender=-200, sTypoLineGap=0,
                usWinAscent=800, usWinDescent=200, sCapHeight=700, sxHeight=500)
    fb.setupPost()
    fb.font["head"].fontRevision = 1.0

    palette = [(RED[0] / 255, RED[1] / 255, RED[2] / 255, 1.0), (BLUE[0] / 255, BLUE[1] / 255, BLUE[2] / 255, 1.0)]
    fb.font["CPAL"] = buildCPAL([palette])
    colr = {}
    for base, (r, b) in layers.items():
        colr[base] = {"Format": PaintFormat.PaintColrLayers, "Layers": [
            {"Format": PaintFormat.PaintGlyph, "Glyph": b,
             "Paint": {"Format": PaintFormat.PaintSolid, "PaletteIndex": 1, "Alpha": 1.0}},
            {"Format": PaintFormat.PaintGlyph, "Glyph": r,
             "Paint": {"Format": PaintFormat.PaintSolid, "PaletteIndex": 0, "Alpha": 1.0}},
        ]}
    fb.font["COLR"] = buildCOLR(colr, version=1, glyphMap=fb.font.getReverseGlyphMap())

    OUT.mkdir(parents=True, exist_ok=True)
    fb.save(OUT / "UEFProIcons-Regular.ttf")
    f = TTFont(OUT / "UEFProIcons-Regular.ttf")
    f.flavor = "woff2"
    f.save(OUT / "UEFProIcons-Regular.woff2")
    print("built", OUT)


if __name__ == "__main__":
    main()
