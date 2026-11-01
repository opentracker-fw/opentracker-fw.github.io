"""Original inline SVG illustrations for the image flavours (drawn in code, no external art).

Every function returns an <svg> string. Ids inside an SVG are prefixed with the flavour
name, so several illustrations can sit on one page. All of them are decorative
(aria-hidden); the text next to them says what they are.
"""

import math
import random


def _svg(w, h, body, extra=""):
    return (f'<svg class="art" viewBox="0 0 {w} {h}" preserveAspectRatio="xMidYMid slice" '
            f'aria-hidden="true" focusable="false" xmlns="http://www.w3.org/2000/svg"{extra}>'
            + body + "</svg>")


def classic(w=480, h=240):
    """A vintage synth: wooden end cheeks with grain, a cream panel with knobs, a keyboard."""
    rnd = random.Random(7)
    p = []
    p.append('''<defs>
<radialGradient id="cl-room" cx="50%" cy="20%" r="85%"><stop offset="0" stop-color="#7a4a1c"/><stop offset=".55" stop-color="#3b2310"/><stop offset="1" stop-color="#1e1208"/></radialGradient>
<linearGradient id="cl-wood" x1="0" x2="1"><stop offset="0" stop-color="#5e3216"/><stop offset=".35" stop-color="#a0602b"/><stop offset=".7" stop-color="#8a4f22"/><stop offset="1" stop-color="#4f2a12"/></linearGradient>
<linearGradient id="cl-panel" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#f6ecd4"/><stop offset="1" stop-color="#e6d5b0"/></linearGradient>
<radialGradient id="cl-cap" cx="40%" cy="35%" r="70%"><stop offset="0" stop-color="#5a4838"/><stop offset="1" stop-color="#17110c"/></radialGradient>
<radialGradient id="cl-amb" cx="40%" cy="35%" r="70%"><stop offset="0" stop-color="#ffd28a"/><stop offset="1" stop-color="#c9781f"/></radialGradient>
<radialGradient id="cl-glow"><stop offset="0" stop-color="#ffb347" stop-opacity=".9"/><stop offset="1" stop-color="#ffb347" stop-opacity="0"/></radialGradient>
<linearGradient id="cl-white" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#fffaf0"/><stop offset="1" stop-color="#e9dfc9"/></linearGradient>
</defs>''')
    p.append(f'<rect width="{w}" height="{h}" fill="url(#cl-room)"/>')
    p.append('<ellipse cx="240" cy="226" rx="230" ry="16" fill="#000" opacity=".35"/>')
    # body
    x0, x1, y0, y1 = 34, 446, 44, 214
    cheek = 34
    for cx in (x0, x1 - cheek):
        p.append(f'<rect x="{cx}" y="{y0 - 6}" width="{cheek}" height="{y1 - y0 + 10}" rx="7" fill="url(#cl-wood)"/>')
        # grain: wavy lines and a knot
        for i in range(7):
            gx = cx + 4 + i * 4.3 + rnd.uniform(-1, 1)
            d = f"M{gx:.1f} {y0 - 4} "
            for k in range(1, 6):
                yy = y0 - 4 + k * (y1 - y0 + 8) / 5
                d += f"S{gx + rnd.uniform(-3, 3):.1f} {yy - 14:.1f} {gx + rnd.uniform(-1.5, 1.5):.1f} {yy:.1f} "
            p.append(f'<path d="{d}" fill="none" stroke="#3f200c" stroke-width="{rnd.choice([0.8, 1.1, 1.5])}" opacity=".55"/>')
        ky = rnd.uniform(y0 + 40, y1 - 40)
        p.append(f'<ellipse cx="{cx + cheek / 2:.1f}" cy="{ky:.1f}" rx="5" ry="9" fill="none" stroke="#3f200c" stroke-width="1.2" opacity=".6"/>')
        p.append(f'<rect x="{cx}" y="{y0 - 6}" width="{cheek}" height="{y1 - y0 + 10}" rx="7" fill="none" stroke="#2a150a" stroke-width="1.5"/>')
    px0, px1 = x0 + cheek, x1 - cheek
    p.append(f'<rect x="{px0}" y="{y0}" width="{px1 - px0}" height="104" fill="url(#cl-panel)"/>')
    p.append(f'<rect x="{px0}" y="{y0}" width="{px1 - px0}" height="5" fill="#2b1a0c" opacity=".85"/>')
    # section lines and printed label bars
    for sx in (150, 246, 330):
        p.append(f'<line x1="{sx}" y1="{y0 + 12}" x2="{sx}" y2="{y0 + 96}" stroke="#b49a6a" stroke-width="1.2"/>')
    for sx, sw in ((78, 50), (166, 60), (262, 50), (346, 46)):
        p.append(f'<rect x="{sx}" y="{y0 + 10}" width="{sw}" height="4" rx="2" fill="#c9762a" opacity=".85"/>')
    # knobs
    rows = [(y0 + 38, [86, 118, 168, 200, 232, 266, 298, 352, 384]),
            (y0 + 76, [86, 118, 168, 200, 266, 298, 352, 384])]
    for ky, xs in rows:
        for kx in xs:
            amber = rnd.random() < 0.28
            r = 11.5
            p.append(f'<circle cx="{kx}" cy="{ky + 2}" r="{r + 1}" fill="#000" opacity=".25"/>')
            p.append(f'<circle cx="{kx}" cy="{ky}" r="{r}" fill="url(#{"cl-amb" if amber else "cl-cap"})" stroke="#1a120b" stroke-width="1"/>')
            for t in range(11):  # scale ticks
                a = math.radians(135 + t * 27)
                p.append(f'<line x1="{kx + math.cos(a) * (r + 3):.1f}" y1="{ky + math.sin(a) * (r + 3):.1f}" '
                         f'x2="{kx + math.cos(a) * (r + 5.5):.1f}" y2="{ky + math.sin(a) * (r + 5.5):.1f}" stroke="#6b5434" stroke-width=".9"/>')
            a = math.radians(rnd.uniform(140, 400))
            col = "#2b1a0c" if amber else "#f6ecd4"
            p.append(f'<line x1="{kx}" y1="{ky}" x2="{kx + math.cos(a) * (r - 2):.1f}" y2="{ky + math.sin(a) * (r - 2):.1f}" '
                     f'stroke="{col}" stroke-width="2.2" stroke-linecap="round"/>')
    # rocker switches and LED
    for sx in (240, 252):
        p.append(f'<rect x="{sx - 4}" y="{y0 + 66}" width="8" height="18" rx="2" fill="#2b1a0c"/>'
                 f'<rect x="{sx - 3}" y="{y0 + 67}" width="6" height="8" rx="1.5" fill="#d4422b"/>')
    p.append(f'<circle cx="420" cy="{y0 + 22}" r="14" fill="url(#cl-glow)"/>'
             f'<circle cx="420" cy="{y0 + 22}" r="3.6" fill="#ffcf6b"/>')
    # wheels
    for wx in (px0 + 8, px0 + 24):
        p.append(f'<rect x="{wx}" y="{y0 + 112}" width="10" height="46" rx="3" fill="#1b130d"/>')
        for k in range(6):
            p.append(f'<line x1="{wx + 1}" y1="{y0 + 118 + k * 7}" x2="{wx + 9}" y2="{y0 + 118 + k * 7}" stroke="#4a3a2a" stroke-width="1"/>')
    # keyboard
    kx0, kx1, ky0, ky1 = px0 + 44, px1 - 6, y0 + 108, y1 - 4
    p.append(f'<rect x="{px0}" y="{y0 + 104}" width="{px1 - px0}" height="{y1 - y0 - 104}" fill="#24170d"/>')
    nwhite = 17
    kw = (kx1 - kx0) / nwhite
    for i in range(nwhite):
        p.append(f'<rect x="{kx0 + i * kw:.2f}" y="{ky0}" width="{kw - 1.2:.2f}" height="{ky1 - ky0}" rx="2" fill="url(#cl-white)"/>')
    for i in range(nwhite - 1):
        if i % 7 in (0, 1, 3, 4, 5):
            bx = kx0 + (i + 1) * kw - kw * 0.32
            p.append(f'<rect x="{bx:.2f}" y="{ky0}" width="{kw * 0.62:.2f}" height="{(ky1 - ky0) * 0.6:.1f}" rx="1.5" fill="#15100b"/>'
                     f'<rect x="{bx + 1.5:.2f}" y="{ky0}" width="{kw * 0.62 - 3:.2f}" height="3" fill="#3b2d22"/>')
    p.append(f'<rect x="{px0}" y="{y1}" width="{px1 - px0}" height="5" fill="#2b1a0c"/>')
    return _svg(w, h, "".join(p))


def techno(w=480, h=240):
    """Concrete warehouse at night: a city skyline with a TV tower, red lasers, a strobe."""
    rnd = random.Random(23)
    p = []
    p.append('''<defs>
<linearGradient id="te-sky" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#050505"/><stop offset=".62" stop-color="#2a0606"/><stop offset=".8" stop-color="#5a0b0b"/></linearGradient>
<radialGradient id="te-strobe"><stop offset="0" stop-color="#fff" stop-opacity="1"/><stop offset=".12" stop-color="#fff" stop-opacity=".85"/><stop offset="1" stop-color="#fff" stop-opacity="0"/></radialGradient>
<filter id="te-concrete" x="0" y="0" width="100%" height="100%"><feTurbulence type="fractalNoise" baseFrequency=".85" numOctaves="3" seed="4"/><feColorMatrix values="0 0 0 0 .55  0 0 0 0 .55  0 0 0 0 .55  0 0 0 .55 0"/><feComposite in2="SourceGraphic" operator="in"/></filter>
<filter id="te-glow" x="-20%" y="-20%" width="140%" height="140%"><feGaussianBlur stdDeviation="2.2"/></filter>
<pattern id="te-hazard" width="16" height="16" patternUnits="userSpaceOnUse" patternTransform="rotate(45)"><rect width="8" height="16" fill="#f2f2f2"/><rect x="8" width="8" height="16" fill="#0a0a0a"/></pattern>
</defs>''')
    p.append(f'<rect width="{w}" height="{h}" fill="url(#te-sky)"/>')
    # strobe burst
    p.append('<circle cx="392" cy="36" r="120" fill="url(#te-strobe)" opacity=".55"/>')
    for k in range(10):
        a = math.radians(k * 36 + 8)
        p.append(f'<line x1="392" y1="36" x2="{392 + math.cos(a) * 150:.1f}" y2="{36 + math.sin(a) * 150:.1f}" stroke="#fff" stroke-width=".8" opacity=".25"/>')
    # lasers from two heads
    beams = []
    for ox, oy, n in ((46, 18, 9), (250, 6, 7)):
        for k in range(n):
            tx = rnd.uniform(0, w)
            ty = rnd.uniform(130, 175)
            beams.append(f'M{ox} {oy} L{tx:.1f} {ty:.1f}')
    d = " ".join(beams)
    p.append(f'<path d="{d}" stroke="#ff1f1f" stroke-width="4" opacity=".45" filter="url(#te-glow)" fill="none"/>')
    p.append(f'<path d="{d}" stroke="#ff4a4a" stroke-width="1.1" opacity=".9" fill="none"/>')
    # skyline
    base = 168
    sky = [f"M0 {base}"]
    x = 0
    while x < w:
        bw = rnd.choice([14, 18, 22, 26, 34])
        bh = rnd.choice([18, 26, 34, 44, 52, 30, 62])
        if 270 < x < 330:
            bh = min(bh, 24)
        sky.append(f"L{x} {base - bh} L{x + bw} {base - bh}")
        x += bw
    sky.append(f"L{w} {base} Z")
    p.append(f'<path d="{" ".join(sky)}" fill="#000"/>')
    # lit windows
    for _ in range(40):
        wx, wy = rnd.uniform(0, w), rnd.uniform(base - 50, base - 6)
        p.append(f'<rect x="{wx:.1f}" y="{wy:.1f}" width="2.4" height="3" fill="{rnd.choice(["#f2f2f2", "#ff3b3b", "#9a9a9a"])}" opacity="{rnd.uniform(.35, .9):.2f}"/>')
    # TV tower
    tx = 300
    p.append(f'<polygon points="{tx - 7},{base} {tx + 7},{base} {tx + 3.2},70 {tx - 3.2},70" fill="#000"/>')
    p.append(f'<circle cx="{tx}" cy="62" r="15" fill="#000"/>')
    p.append(f'<rect x="{tx - 9}" y="74" width="18" height="5" rx="2" fill="#000"/>')
    p.append(f'<rect x="{tx - 2.2}" y="16" width="4.4" height="34" fill="#000"/>')
    p.append(f'<rect x="{tx - 1.1}" y="4" width="2.2" height="14" fill="#000"/>')
    p.append(f'<circle cx="{tx}" cy="4" r="2.6" fill="#ff2a2a"/><circle cx="{tx}" cy="4" r="7" fill="#ff2a2a" opacity=".35"/>')
    p.append(f'<ellipse cx="{tx - 5}" cy="57" rx="5" ry="3" fill="#fff" opacity=".18"/>')
    # concrete floor
    p.append(f'<rect x="0" y="{base}" width="{w}" height="{h - base}" fill="#3c3c3c"/>')
    p.append(f'<rect x="0" y="{base}" width="{w}" height="{h - base}" fill="#888" filter="url(#te-concrete)" opacity=".7"/>')
    for jx in range(0, w, 96):
        p.append(f'<line x1="{jx}" y1="{base}" x2="{jx}" y2="{h}" stroke="#1d1d1d" stroke-width="1.5"/>')
    p.append(f'<rect x="0" y="{base + 9}" width="{w}" height="7" fill="#e10600"/>')
    p.append(f'<rect x="372" y="{base + 30}" width="108" height="20" fill="url(#te-hazard)"/>')
    # floor laser reflections
    p.append(f'<path d="M40 {base + 40} L200 {base + 34} M150 {base + 60} L330 {base + 52}" stroke="#ff3030" stroke-width="1" opacity=".5"/>')
    return _svg(w, h, "".join(p))


def idm(w=480, h=240):
    """A glitchy grid: scattered pixels, a clean and a crushed waveform, cyan and magenta."""
    rnd = random.Random(42)
    p = []
    p.append('''<defs>
<linearGradient id="id-bg" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#060a1e"/><stop offset=".6" stop-color="#0d0a2a"/><stop offset="1" stop-color="#1a0624"/></linearGradient>
<pattern id="id-grid" width="16" height="16" patternUnits="userSpaceOnUse"><path d="M16 0H0V16" fill="none" stroke="#20e3ff" stroke-width=".6" opacity=".22"/></pattern>
<filter id="id-glow" x="-10%" y="-30%" width="120%" height="160%"><feGaussianBlur stdDeviation="2.5"/></filter>
</defs>''')
    p.append(f'<rect width="{w}" height="{h}" fill="url(#id-bg)"/><rect width="{w}" height="{h}" fill="url(#id-grid)"/>')
    # pixels
    for _ in range(120):
        s = rnd.choice([4, 4, 8, 8, 12, 16])
        x = rnd.randrange(0, w // 4) * 4
        y = rnd.randrange(0, h // 4) * 4
        c = rnd.choice(["#20e3ff", "#ff2bd6", "#ff2bd6", "#20e3ff", "#ffffff", "#7c5cff"])
        p.append(f'<rect x="{x}" y="{y}" width="{s}" height="{s}" fill="{c}" opacity="{rnd.uniform(.12, .75):.2f}"/>')
    # clean sine and a stepped (crushed) wave
    mid = 120
    sine = " ".join(f"{'M' if i == 0 else 'L'}{x} {mid + 46 * math.sin(x / 38) * math.exp(-((x - 240) / 260) ** 2):.1f}" for i, x in enumerate(range(0, w + 1, 4)))
    p.append(f'<path d="{sine}" fill="none" stroke="#20e3ff" stroke-width="6" opacity=".35" filter="url(#id-glow)"/>')
    p.append(f'<path d="{sine}" fill="none" stroke="#ff2bd6" stroke-width="2" transform="translate(4 0)" opacity=".8"/>')
    p.append(f'<path d="{sine}" fill="none" stroke="#bff7ff" stroke-width="2"/>')
    step = []
    for i, x in enumerate(range(0, w + 1, 12)):
        y = 186 + round(18 * math.sin(x / 17) + 10 * math.sin(x / 5.3)) // 8 * 8
        step.append(f"M{x} {y}" if i == 0 else f"H{x} V{y}")
    p.append(f'<path d="{" ".join(step)}" fill="none" stroke="#ff2bd6" stroke-width="2.2"/>')
    # noise burst
    nz = " ".join(f"{'M' if i == 0 else 'L'}{x} {52 + rnd.uniform(-14, 14) * (1 if 120 < x < 260 else .25):.1f}" for i, x in enumerate(range(60, 360, 3)))
    p.append(f'<path d="{nz}" fill="none" stroke="#20e3ff" stroke-width="1.2" opacity=".85"/>')
    # glitch slices: displaced bands
    for _ in range(9):
        y = rnd.randrange(10, h - 10)
        hh = rnd.choice([2, 3, 4, 6, 9])
        x = rnd.randrange(-40, w - 80)
        ww = rnd.randrange(60, 220)
        c = rnd.choice(["#20e3ff", "#ff2bd6", "#ffffff"])
        p.append(f'<rect x="{x}" y="{y}" width="{ww}" height="{hh}" fill="{c}" opacity="{rnd.uniform(.25, .7):.2f}"/>')
    # scan lines
    p.append(f'<rect width="{w}" height="{h}" fill="none"/>')
    for y in range(0, h, 3):
        p.append(f'<line x1="0" y1="{y}.5" x2="{w}" y2="{y}.5" stroke="#000" stroke-width="1" opacity=".18"/>')
    return _svg(w, h, "".join(p))


ART = {"classic": classic, "techno": techno, "idm": idm}
