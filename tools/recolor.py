#!/usr/bin/env python3
"""GenoTheme recolour script.

Builds the GenoTheme KDE Plasma 6 theme set from Daemon 2.0 (MathisP75/daemon-kde-mk2,
GPL-3.0) by swapping Daemon's cyberpunk cyan/red/maroon palette for the GenoCorp palette.

usage: tools/recolor.py <path-to-daemon-kde-mk2 checkout> <output dir (e.g. themes/)>

Pinned upstream commit used for the first build: 01bf4df4666e9021ac8013bc2c4eaabc8d312d68
Hand-written pieces (colour scheme, Konsole scheme, look-and-feel defaults) live in
tools/static/ and are copied verbatim.
"""
import gzip, os, re, shutil, sys
from pathlib import Path

# ---- GenoCorp palette ---------------------------------------------------
BG, BG2, BG3 = "#020205", "#05061a", "#080a24"
BLUE, PURE_BLUE, PERI = "#4d6bff", "#0000ff", "#9fb3ff"
TEXT, MUTED, RED = "#d9def5", "#6a7095", "#ff0000"

# Daemon colour -> GenoCorp colour (case-insensitive, 6-digit hex)
MAP = {
    # cyans / blues -> electric blue / periwinkle
    "#5df4fe": BLUE, "#00ffff": BLUE, "#3daee9": BLUE, "#3daee6": BLUE,
    "#1e92ff": BLUE, "#2eb8e6": BLUE, "#0099e5": BLUE, "#1d99f3": BLUE,
    "#5beedc": PERI, "#5aeedc": PERI, "#93cee9": PERI,
    # reds / yellows / pinks -> GenoCorp red, accents
    "#ff5048": RED, "#fb3048": RED, "#ff2a2a": RED, "#fdf500": RED,
    "#da4453": RED, "#ed333b": RED,
    "#e455ae": PERI, "#28c775": PERI, "#cb1dcd": PURE_BLUE,
    "#710100": "#4a0010",
    # dark maroon/grey backgrounds -> navy blacks
    "#331319": BG3, "#14101f": BG2, "#130f1e": BG2, "#210e15": BG,
    "#040a10": BG, "#070d1a": BG2, "#272932": "#0d1030",
    "#d1c5c0": TEXT,
}
# extra mapping for the GTK (Breeze-derived) CSS: greys -> navy
GTK_MAP = dict(MAP, **{
    "#31363b": "#0a0c26", "#2a2e32": "#080a20", "#1b1e20": BG, "#262a2d": "#07091e",
    "#191b1d": BG, "#232629": "#05061a", "#fcfcfc": TEXT, "#eff0f1": TEXT,
    "#7c8288": MUTED, "#a1a9b1": MUTED, "#54575a": "#2a2f5a",
})
RGBA_MAP = {  # rgba() triplets in GTK CSS
    (37, 164, 230): (77, 107, 255), (61, 174, 233): (77, 107, 255),
    (214, 46, 63): (255, 0, 0), (45, 49, 54): (10, 12, 38), (76, 79, 82): (42, 47, 90),
    (144, 154, 163): (106, 112, 149),
}

HEX = re.compile(r"#[0-9a-fA-F]{6}(?![0-9a-fA-F])")

def recolor_text(t, mapping=MAP):
    def sub(m):
        s = m.group(0); r = mapping.get(s.lower())
        if r is None: return s
        return r.upper() if s[1:].isupper() and any(c.isalpha() for c in s[1:]) else r
    t = HEX.sub(sub, t)
    return t

def recolor_rgba(t):
    def sub(m):
        rgb = tuple(int(x) for x in m.group(1, 2, 3)); r = RGBA_MAP.get(rgb)
        if not r: return m.group(0)
        return "rgba(%d, %d, %d, %s)" % (*r, m.group(4))
    return re.sub(r"rgba\((\d+),\s*(\d+),\s*(\d+),\s*([0-9.]+)\)", sub, t)

def recolor_file(p, mapping=MAP, extra=None):
    if p.is_symlink(): return
    b = p.read_bytes(); gz = p.suffix == ".svgz"
    if gz: b = gzip.decompress(b)
    t = b.decode("utf-8", "surrogateescape")
    n = recolor_text(t, mapping)
    if extra: n = extra(n)
    if n != t:
        b = n.encode("utf-8", "surrogateescape")
        p.write_bytes(gzip.compress(b, mtime=0) if gz else b)

def tree(src, dst):
    if dst.exists(): shutil.rmtree(dst)
    shutil.copytree(src, dst, symlinks=True)
    return dst

def walk(d, exts):
    for p in sorted(d.rglob("*")):
        if p.is_file() and not p.is_symlink() and p.suffix in exts: yield p

def main(up, out):
    up, out = Path(up), Path(out); out.mkdir(parents=True, exist_ok=True)
    static = Path(__file__).resolve().parent / "static"

    # 1. Plasma style
    d = tree(up / "Plasma Style/Daemon-2.0", out / "plasma/desktoptheme/GenoTheme")
    # panel frame uses electric blue (like the wallpaper lines) instead of Daemon's red
    panel = dict(MAP, **{"#ff5048": BLUE, "#fb3048": BLUE})
    for p in walk(d, {".svg", ".svgz"}):
        recolor_file(p, panel if p.name.startswith("panel-background") else MAP)
    (d / "metadata.json").write_text("""{
    "KPlugin": {
        "Authors": [{"Name": "Mathis Paquet (Daemon 2.0)"}, {"Name": "GenoCorp (GenoTheme recolour)"}],
        "Category": "",
        "Description": "GenoCorp recolour of Daemon 2.0",
        "EnabledByDefault": true,
        "Id": "GenoTheme",
        "License": "GPL-3.0-or-later",
        "Name": "GenoTheme",
        "Version": "1.0",
        "Website": "https://github.com/MathisP75/daemon-kde-mk2"
    },
    "X-Plasma-API": "5.0"
}
""")

    # 2. Aurorae window decoration (active title bar becomes electric blue, close = red)
    d = tree(up / "Window Decorations/daemon-2.0", out / "aurorae/themes/GenoTheme")
    os.rename(d / "daemon-2.0rc", d / "GenoThemerc")
    amap = dict(MAP, **{"#fb3048": BLUE, "#ff5048": PERI})
    for p in walk(d, {".svg"}):
        recolor_file(p, dict(amap, **({"#fb3048": BLUE} if p.name != "close.svg" else {"#fb3048": RED, "#ff5048": RED})))
    rc = (d / "GenoThemerc").read_text()
    rc = rc.replace("ActiveTextColor=7,13,25", "ActiveTextColor=2,2,5").replace("InactiveTextColor=7,13,25", "InactiveTextColor=106,112,149")
    (d / "GenoThemerc").write_text(rc)
    md = (d / "metadata.desktop").read_text()
    md = md.replace("Name=Daemon-2.0", "Name=GenoTheme").replace("X-KDE-PluginInfo-Name=Daemon-2.0", "X-KDE-PluginInfo-Name=GenoTheme")
    (d / "metadata.desktop").write_text(md)

    # 3. Kvantum
    d = tree(up / "Kvantum/daemon-2.0", out / "kvantum/GenoTheme")
    os.rename(d / "daemon-2.0.kvconfig", d / "GenoTheme.kvconfig")
    os.rename(d / "daemon-2.0.svg", d / "GenoTheme.svg")
    recolor_file(d / "GenoTheme.svg")
    kv = (d / "GenoTheme.kvconfig").read_text()
    general = {"window.color": BG2, "base.color": BG, "alt.base.color": BG2, "button.color": BG3,
               "light.color": RED, "mid.light.color": RED, "dark.color": BG, "mid.color": RED,
               "highlight.color": BLUE, "inactive.highlight.color": "#2a3a8f",
               "text.color": TEXT, "window.text.color": TEXT, "button.text.color": PERI,
               "disabled.text.color": MUTED, "tooltip.text.color": TEXT,
               "highlight.text.color": "#ffffff", "link.color": BLUE, "link.visited.color": PERI}
    def kvline(line):
        k = line.split("=", 1)[0].strip()
        if k in general and "[GeneralColors]" in state: return "%s=%s" % (k, general[k].upper())
        if k.startswith("text.") and "=" in line:
            v = line.split("=", 1)[1].strip().lower()
            if v == "#5df4fe": return "%s=%s" % (k, PERI.upper())
            if v == "#d1c5c0": return "%s=%s" % (k, TEXT.upper())
        return line
    out_lines, state = [], ""
    for line in kv.splitlines():
        if line.startswith("["): state = line.strip()
        out_lines.append(kvline(line))
    (d / "GenoTheme.kvconfig").write_text(recolor_text("\n".join(out_lines) + "\n"))

    # 4. Icons
    d = tree(up / "Icon Theme/Daemon-Icons", out / "icons/GenoTheme-Icons")
    for p in walk(d, {".svg"}): recolor_file(p)
    it = (d / "index.theme").read_text()
    it = re.sub(r"(?m)^Name=.*$", "Name=GenoTheme-Icons", it, count=1)
    it = re.sub(r"(?m)^Comment=.*$", "Comment=GenoCorp recolour of Daemon-Icons (Simply Circles)", it, count=1)
    (d / "index.theme").write_text(it)
    for sc in d.rglob("svg-color-change.sh"):
        if not sc.is_symlink(): sc.write_text(re.sub("(?i)#5DF4FE", BLUE.upper(), sc.read_text()))

    # 5. GTK (Breeze-Dark derived CSS; PNG assets left as-is)
    src = up / "GTK Theme/Breeze-Dark"
    if src.exists():
        d = tree(src, out / "gtk/GenoTheme-GTK")
        for p in walk(d, {".css", ".svg", ".ini", ".rc", ""}):
            recolor_file(p, GTK_MAP, recolor_rgba)
        for p in d.rglob("index.theme"):
            p.write_text(re.sub(r"(?m)^Name=.*$", "Name=GenoTheme-GTK", p.read_text()))

    # 6. Static hand-written files
    for p in static.rglob("*"):
        if p.is_file():
            t = out / p.relative_to(static); t.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(p, t)
    print("GenoTheme built in", out)

if __name__ == "__main__":
    if len(sys.argv) != 3: sys.exit(__doc__)
    main(sys.argv[1], sys.argv[2])
