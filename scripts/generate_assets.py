#!/usr/bin/env python3
"""Generates self-hosted animated SVGs for the GitHub profile README.

Usage:  python scripts/generate_assets.py [--html contributions.html]
Reads your public contribution calendar from GitHub (no token needed) and writes
header, section titles, typing text, skills grid, contribution matrix and snake
into ./assets. No third-party image services are used at view time.
"""
import base64, os, random, re, sys, urllib.request
from html import escape

USER = os.environ.get("GH_USER", "karthikesh15")
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
A = os.path.join(ROOT, "assets")
EMOJI = "'Segoe UI Emoji','Apple Color Emoji','Noto Color Emoji',sans-serif"


# ---------------------------------------------------------------- helpers
def font_css():
    def b64(name):
        with open(os.path.join(A, "fonts", name), "rb") as f:
            return base64.b64encode(f.read()).decode()
    faces = [("Orbitron", 900, "orbitron-latin-900-normal.woff2"),
             ("Orbitron", 700, "orbitron-latin-700-normal.woff2"),
             ("Poppins", 600, "poppins-latin-600-normal.woff2")]
    return "".join(
        "@font-face{font-family:'%s';font-weight:%d;src:url(data:font/woff2;base64,%s) format('woff2');}"
        % (fam, w, b64(fn)) for fam, w, fn in faces)


FONTS = None


def svg(w, h, body, defs=""):
    global FONTS
    if FONTS is None:
        FONTS = font_css()
    return ('<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" '
            'width="%d" height="%d" viewBox="0 0 %d %d"><defs><style>%s</style>%s</defs>%s</svg>'
            % (w, h, w, h, FONTS, defs, body))


def write(name, content):
    with open(os.path.join(A, name), "w", encoding="utf-8") as f:
        f.write(content)
    print("wrote", name, len(content) // 1024, "KB")


def anim_grad(gid, colors, dur=8, x2="100%"):
    """Horizontally sliding rainbow gradient (for text and bars)."""
    stops = "".join('<stop offset="%.2f" stop-color="%s"/>' % (i / (len(colors) - 1), c)
                    for i, c in enumerate(colors + []))
    return ('<linearGradient id="%s" x1="0" y1="0" x2="%s" y2="0" gradientUnits="userSpaceOnUse" '
            'spreadMethod="repeat">%s<animateTransform attributeName="gradientTransform" type="translate" '
            'from="0 0" to="1000 0" dur="%ss" repeatCount="indefinite"/></linearGradient>'
            % (gid, "1000", stops, dur))


RAINBOW = ["#00E5FF", "#7C4DFF", "#FF4DCC", "#FFB300", "#00E5FF"]


# ---------------------------------------------------------------- header
def header():
    w, h = 1000, 300
    rnd = random.Random(7)
    defs = (
        '<linearGradient id="bg" x1="0" y1="0" x2="1" y2="1">'
        '<stop offset="0" stop-color="#0b1026"><animate attributeName="stop-color" values="#0b1026;#1a0b3d;#05243b;#0b1026" dur="12s" repeatCount="indefinite"/></stop>'
        '<stop offset="1" stop-color="#2b0f54"><animate attributeName="stop-color" values="#2b0f54;#06324d;#3b0a45;#2b0f54" dur="12s" repeatCount="indefinite"/></stop>'
        '</linearGradient>'
        + anim_grad("tg", RAINBOW, 6) +
        '<filter id="glow" x="-20%%" y="-20%%" width="140%%" height="140%%"><feGaussianBlur stdDeviation="4" result="b"/>'
        '<feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>'
        '<clipPath id="c"><rect width="%d" height="%d" rx="22"/></clipPath>' % (w, h))
    b = ['<g clip-path="url(#c)"><rect width="%d" height="%d" fill="url(#bg)"/>' % (w, h)]
    # twinkling stars
    for _ in range(60):
        x, y, r = rnd.randint(5, w - 5), rnd.randint(5, h - 60), rnd.choice([1, 1.4, 1.8, 2.2])
        b.append('<circle cx="%d" cy="%d" r="%s" fill="#fff"><animate attributeName="opacity" values="0.1;1;0.1" '
                 'dur="%.1fs" begin="%.1fs" repeatCount="indefinite"/></circle>' % (x, y, r, rnd.uniform(2, 5), rnd.uniform(0, 4)))
    # glowing orbs
    for cx, cy, r, col, d in [(120, 80, 70, "#7C4DFF", 9), (880, 70, 85, "#00E5FF", 11), (700, 230, 60, "#FF4DCC", 8)]:
        b.append('<circle cx="%d" cy="%d" r="%d" fill="%s" opacity=".18"><animate attributeName="r" values="%d;%d;%d" '
                 'dur="%ds" repeatCount="indefinite"/></circle>' % (cx, cy, r, col, r, r + 18, r, d))
    # floating emojis
    for i, (e, x, y) in enumerate([("💻", 50, 215), ("🤖", 180, 60), ("🛡️", 925, 245), ("🚀", 930, 70),
                                    ("🧠", 800, 40), ("⚡", 110, 140), ("🔐", 920, 150), ("✨", 45, 265)]):
        b.append('<text x="%d" y="%d" font-size="30" font-family="%s" opacity=".9">%s'
                 '<animate attributeName="y" values="%d;%d;%d" dur="%ds" begin="%ds" repeatCount="indefinite"/>'
                 '<animate attributeName="opacity" values=".35;1;.35" dur="%ds" repeatCount="indefinite"/></text>'
                 % (x, y, EMOJI, e, y, y - 14, y, 4 + i % 3, i % 3, 4 + i % 3))
    # name
    b.append('<text x="500" y="130" text-anchor="middle" font-family="Orbitron,sans-serif" font-weight="900" '
             'font-size="58" letter-spacing="5" fill="url(#tg)" filter="url(#glow)">S D KARTHIKESH'
             '<animate attributeName="opacity" from="0" to="1" dur="1.4s" fill="freeze"/></text>')
    b.append('<text x="500" y="182" text-anchor="middle" font-family="Poppins,%s" font-weight="600" font-size="22" fill="#e8ecff">'
             '👨‍💻 Software Engineer  ✦  🤖 AI / GenAI Engineer  ✦  🛡️ Cyber Defence'
             '<animate attributeName="opacity" from="0" to="1" begin=".8s" dur="1.4s" fill="freeze"/></text>' % EMOJI)
    b.append('<text x="500" y="222" text-anchor="middle" font-family="Poppins,%s" font-weight="600" font-size="15" fill="#9fb4ff" letter-spacing="1">'
             '🎓 VIT Chennai  •  📚 IIT Madras  •  🏆 Patent Published  •  🎯 Class of 2027'
             '<animate attributeName="opacity" from="0" to="1" begin="1.6s" dur="1.4s" fill="freeze"/></text>' % EMOJI)
    # waves
    for i, (col, op, dur, off) in enumerate([("#7C4DFF", .35, 9, 0), ("#00E5FF", .30, 13, 40), ("#FF4DCC", .25, 17, 80)]):
        pts = "M0 %d " % (h - 38 + off // 4)
        for k in range(0, 3):
            x0 = k * 1000
            pts += ("Q%d %d %d %d T%d %d " % (x0 + 250, h - 75 + off // 3, x0 + 500, h - 38 + off // 4, x0 + 1000, h - 38 + off // 4))
        pts += "V%d H0 Z" % h
        b.append('<path d="%s" fill="%s" opacity="%s"><animateTransform attributeName="transform" type="translate" '
                 'from="0 0" to="-1000 0" dur="%ds" repeatCount="indefinite"/></path>' % (pts, col, op, dur))
    b.append('</g>')
    write("header.svg", svg(w, h, "".join(b), defs))


# ---------------------------------------------------------------- typing
def typing():
    lines = ["💡 Building LLM-powered applications", "🛠️ Full-stack  •  Python  •  Java  •  Node.js",
             "🛡️ Cyber defence meets AI engineering", "📩 Open to 2027 graduate roles"]
    w, h, slot = 1000, 70, 4.0
    total = slot * len(lines)
    defs = anim_grad("tg2", ["#00E5FF", "#7C4DFF", "#FF4DCC", "#FFB300", "#00E5FF"], 5)
    body = []
    for i, t in enumerate(lines):
        tw = int(len(t) * 15.2)
        x0 = (w - tw) // 2
        kt = "0;%.4f;%.4f;%.4f;1" % (1.4 / total, (slot - 0.5) / total, (slot - 0.45) / total)
        begin = "%.1fs" % (i * slot)
        body.append('<clipPath id="k%d"><rect x="%d" y="0" height="%d" width="0">'
                    '<animate attributeName="width" values="0;%d;%d;0;0" keyTimes="%s" dur="%ss" begin="%s" repeatCount="indefinite"/>'
                    '</rect></clipPath>' % (i, x0 - 4, h, tw + 8, tw + 8, kt, total, begin))
        body.append('<g clip-path="url(#k%d)"><text x="%d" y="44" font-family="Poppins,%s" font-weight="600" font-size="26" '
                    'fill="url(#tg2)" textLength="%d" lengthAdjust="spacingAndGlyphs">%s</text></g>' % (i, x0, EMOJI, tw, escape(t)))
        body.append('<rect y="14" width="3" height="38" rx="1.5" fill="#00E5FF" opacity="0">'
                    '<animate attributeName="x" values="%d;%d;%d;%d;%d" keyTimes="%s" dur="%ss" begin="%s" repeatCount="indefinite"/>'
                    '<animate attributeName="opacity" values="0;1;1;0;0" keyTimes="%s" dur="%ss" begin="%s" repeatCount="indefinite"/></rect>'
                    % (x0 - 4, x0 + tw + 2, x0 + tw + 2, x0 - 4, x0 - 4, kt, total, begin, kt, total, begin))
    write("typing.svg", svg(w, h, "".join(body), defs))


# ---------------------------------------------------------------- section titles
SECTIONS = [("sec-about", "👨‍💻", "ABOUT ME"), ("sec-projects", "🚀", "FEATURED PROJECTS"),
            ("sec-exp", "💼", "EXPERIENCE"), ("sec-skills", "🛠️", "TECH ARSENAL"),
            ("sec-ach", "🏆", "ACHIEVEMENTS"), ("sec-edu", "🎓", "EDUCATION"),
            ("sec-activity", "📈", "CODING ACTIVITY"), ("sec-connect", "🤝", "LET'S CONNECT")]


def sections():
    for name, emo, text in SECTIONS:
        w, h = 1000, 78
        defs = anim_grad("g", RAINBOW, 5) + (
            '<linearGradient id="bar" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#00E5FF"/>'
            '<stop offset=".5" stop-color="#7C4DFF"/><stop offset="1" stop-color="#FF4DCC" stop-opacity="0"/></linearGradient>')
        body = ('<text x="8" y="46" font-size="38" font-family="%s">%s<animate attributeName="y" values="46;40;46" dur="2.6s" repeatCount="indefinite"/></text>'
                '<text x="64" y="46" font-family="Orbitron,sans-serif" font-weight="900" font-size="32" letter-spacing="3" fill="url(#g)">%s</text>'
                '<rect x="8" y="62" height="5" rx="2.5" fill="url(#bar)" width="0"><animate attributeName="width" values="0;960;960" keyTimes="0;.35;1" dur="7s" repeatCount="indefinite"/></rect>'
                % (EMOJI, emo, escape(text)))
        write(name + ".svg", svg(w, h, body, defs))


def divider():
    w, h = 1000, 16
    defs = ('<linearGradient id="d" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#00E5FF" stop-opacity="0"/>'
            '<stop offset=".5" stop-color="#7C4DFF"/><stop offset="1" stop-color="#FF4DCC" stop-opacity="0"/></linearGradient>'
            '<filter id="gl"><feGaussianBlur stdDeviation="2.5"/></filter>')
    body = ('<rect x="0" y="7" width="1000" height="2" rx="1" fill="url(#d)"/>'
            '<circle cy="8" r="5" fill="#00E5FF" filter="url(#gl)"><animate attributeName="cx" values="0;1000" dur="4s" repeatCount="indefinite"/></circle>'
            '<circle cy="8" r="2.4" fill="#fff"><animate attributeName="cx" values="0;1000" dur="4s" repeatCount="indefinite"/></circle>')
    write("divider.svg", svg(w, h, body, defs))


# ---------------------------------------------------------------- skills
SKILLS = [
    ("💻 Languages", [("python", "Python"), ("java", "Java"), ("cplusplus", "C++"), ("c", "C"), ("javascript", "JavaScript")]),
    ("🌐 Backend & Web", [("flask", "Flask"), ("nodejs", "Node.js"), ("express", "Express"), ("react", "React"), ("spring", "Spring Boot"), ("html5", "HTML5"), ("css3", "CSS3")]),
    ("🤖 AI / ML", [("pytorch", "PyTorch"), ("tensorflow", "TensorFlow"), ("scikitlearn", "scikit-learn"), ("pandas", "Pandas"), ("numpy", "NumPy"), ("huggingface", "Hugging Face"), ("jupyter", "Jupyter")]),
    ("🗄️ Data & Cloud", [("postgresql", "PostgreSQL"), ("mysql", "MySQL"), ("mongodb", "MongoDB"), ("amazonwebservices", "AWS"), ("googlecloud", "GCP"), ("docker", "Docker"), ("git", "Git"), ("githubactions", "CI/CD"), ("linux", "Linux"), ("solidity", "Solidity")]),
]


DARK = {"flask", "express", "solidity", "pandas"}


def skills():
    w = 1000
    chip, gap = 74, 14
    y = 10
    body, defs = [], ('<linearGradient id="chip" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#1c2340"/>'
                      '<stop offset="1" stop-color="#0d1226"/></linearGradient>' + anim_grad("lg", RAINBOW, 6))
    k = 0
    for title, items in SKILLS:
        total_w = len(items) * (chip + gap) - gap
        x = (w - total_w) // 2
        body.append('<text x="%d" y="%d" font-family="Poppins,%s" font-weight="600" font-size="18" fill="url(#lg)">%s</text>' % (x, y + 20, EMOJI, escape(title)))
        y += 34
        for icon, label in items:
            with open(os.path.join(A, "icons", icon + ".svg"), "rb") as f:
                data = base64.b64encode(f.read()).decode()
            d = 3 + (k % 4)
            body.append('<g><animateTransform attributeName="transform" type="translate" values="0 0;0 -5;0 0" dur="%ds" begin="%.1fs" repeatCount="indefinite"/>'
                        '<rect x="%d" y="%d" width="%d" height="%d" rx="18" fill="url(#chip)" stroke="#3a4577" stroke-width="1.2"/>'
                        '%s<image x="%d" y="%d" width="40" height="40" href="data:image/svg+xml;base64,%s"/>'
                        '<text x="%d" y="%d" text-anchor="middle" font-family="Poppins,sans-serif" font-weight="600" font-size="10" fill="#cfd8ff">%s</text></g>'
                        % (d, (k % 5) * .4, x, y, chip, chip,
                           ('<rect x="%d" y="%d" width="46" height="46" rx="12" fill="#e8ecff"/>' % (x + (chip - 46) // 2, y + 6)) if icon in DARK else '',
                           x + (chip - 40) // 2, y + 9, data, x + chip // 2, y + chip - 8, escape(label)))
            x += chip + gap
            k += 1
        y += chip + 18
    write("skills.svg", svg(w, y + 4, "".join(body), defs))


# ---------------------------------------------------------------- contributions
def load_contribs():
    html = None
    if "--html" in sys.argv:
        html = open(sys.argv[sys.argv.index("--html") + 1], encoding="utf-8").read()
    else:
        req = urllib.request.Request("https://github.com/users/%s/contributions" % USER, headers={"User-Agent": "Mozilla/5.0"})
        html = urllib.request.urlopen(req, timeout=30).read().decode("utf-8")
    cells = {}
    for m in re.finditer(r'data-date="(\d{4}-\d{2}-\d{2})"[^>]*?id="contribution-day-component-(\d)-(\d+)"[^>]*?data-level="(\d)"', html):
        date, r, c, lvl = m.group(1), int(m.group(2)), int(m.group(3)), int(m.group(4))
        cells[(c, r)] = (date, lvl, 0)
    tips = {m.group(1): m.group(2) for m in re.finditer(r'for="contribution-day-component-(\d-\d+)"[^>]*>([^<\n]*)', html)}
    for (c, r), (date, lvl, _) in list(cells.items()):
        t = tips.get("%d-%d" % (r, c), "")
        mm = re.match(r"(\d+) contribution", t)
        cells[(c, r)] = (date, lvl, int(mm.group(1)) if mm else 0)
    total = sum(v[2] for v in cells.values())
    return cells, total


PAL = ["#161b33", "#2563eb", "#7c3aed", "#ec4899", "#fbbf24"]
MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]


def grid_geometry(cells):
    cols = max(c for c, _ in cells) + 1
    cs, gp = 14, 3
    step = cs + gp
    x0, y0 = 46, 78
    w = x0 + cols * step + 30
    return cols, cs, step, x0, y0, w


def card_header(w, h, title, total):
    return ('<rect x="1" y="1" width="%d" height="%d" rx="22" fill="#0b1026" stroke="url(#bd)" stroke-width="2"/>'
            '<text x="28" y="40" font-family="Orbitron,sans-serif" font-weight="700" font-size="20" fill="url(#tt)">%s</text>'
            '<text x="%d" y="40" text-anchor="end" font-family="Poppins,%s" font-weight="600" font-size="15" fill="#9fb4ff">🔥 %d contributions in the last year</text>'
            % (w - 2, h - 2, escape(title), w - 28, EMOJI, total))


def common_defs():
    return (anim_grad("tt", RAINBOW, 6) +
            '<linearGradient id="bd" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#00E5FF"/><stop offset=".5" stop-color="#7C4DFF"/>'
            '<stop offset="1" stop-color="#FF4DCC"/><animateTransform attributeName="gradientTransform" type="rotate" from="0 .5 .5" to="360 .5 .5" dur="12s" repeatCount="indefinite"/></linearGradient>'
            '<filter id="gw" x="-60%" y="-60%" width="220%" height="220%"><feGaussianBlur stdDeviation="2.2" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>')


def month_labels(cells, x0, step, y):
    marks, last = [], -1
    for c in sorted({c for c, _ in cells}):
        d = cells.get((c, 0)) or cells.get((c, 1))
        if not d:
            continue
        mth = int(d[0][5:7]) - 1
        if mth != last:
            marks.append((c, mth))
            last = mth
    if len(marks) > 1 and marks[1][0] - marks[0][0] < 3:
        marks = marks[1:]
    return "".join('<text x="%d" y="%d" font-family="Poppins,sans-serif" font-weight="600" font-size="11" fill="#7f8bc4">%s</text>'
                   % (x0 + c * step, y, MONTHS[m]) for c, m in marks)


def day_labels(x0, y0, step):
    return "".join('<text x="14" y="%d" font-family="Poppins,sans-serif" font-weight="600" font-size="10" fill="#7f8bc4">%s</text>' % (y0 + r * step + 11, n)
                   for r, n in [(1, "Mon"), (3, "Wed"), (5, "Fri")])


def legend(w, h):
    x = w - 230
    out = '<text x="%d" y="%d" font-family="Poppins,sans-serif" font-weight="600" font-size="11" fill="#7f8bc4">Less</text>' % (x, h - 20)
    for i, col in enumerate(PAL):
        out += '<rect x="%d" y="%d" width="14" height="14" rx="4" fill="%s"/>' % (x + 34 + i * 20, h - 32, col)
    out += '<text x="%d" y="%d" font-family="Poppins,sans-serif" font-weight="600" font-size="11" fill="#7f8bc4">More</text>' % (x + 34 + 5 * 20 + 4, h - 20)
    return out


def matrix(cells, total):
    cols, cs, step, x0, y0, w = grid_geometry(cells)
    h = y0 + 7 * step + 52
    b = [card_header(w, h, "⚡ CONTRIBUTION MATRIX", total), month_labels(cells, x0, step, y0 - 10), day_labels(x0, y0, step)]
    for (c, r), (date, lvl, n) in sorted(cells.items()):
        x, y = x0 + c * step, y0 + r * step
        glow = ' filter="url(#gw)"' if lvl >= 2 else ""
        pulse = ('<animate attributeName="opacity" values="1;.45;1" dur="%.1fs" begin="%.2fs" repeatCount="indefinite"/>' % (2.6 + (c % 5) * .3, (c * .06 + r * .04) % 3)) if lvl else \
                ('<animate attributeName="opacity" values=".55;1;.55" dur="5s" begin="%.2fs" repeatCount="indefinite"/>' % ((c * .09) % 5))
        b.append('<rect x="%d" y="%d" width="%d" height="%d" rx="4" fill="%s"%s>%s<title>%d contributions on %s</title></rect>' % (x, y, cs, cs, PAL[lvl], glow, pulse, n, date))
    b.append(legend(w, h))
    write("matrix.svg", svg(w, h, "".join(b), common_defs()))


def snake(cells, total):
    cols, cs, step, x0, y0, w = grid_geometry(cells)
    h = y0 + 7 * step + 52
    dt = 0.075
    pre, post = 6, 14

    def center(c, r):
        return x0 + c * step + cs / 2, y0 + r * step + cs / 2

    order = []
    for c in range(cols):
        rows = range(7) if c % 2 == 0 else range(6, -1, -1)
        for r in rows:
            order.append((c, r))
    pts = [(center(0, 0)[0] - (pre - i) * step, center(0, 0)[1]) for i in range(pre)]
    pts += [center(c, r) for c, r in order]
    lx, ly = pts[-1]
    pts += [(lx + (i + 1) * step, ly) for i in range(post)]
    nseg = len(pts) - 1
    T = nseg * dt
    path = "M" + " L".join("%.1f %.1f" % p for p in pts)
    b = [card_header(w, h, "🐍 CONTRIBUTION SNAKE", total), month_labels(cells, x0, step, y0 - 10), day_labels(x0, y0, step)]
    for idx, (c, r) in enumerate(order):
        cell = cells.get((c, r))
        x, y = x0 + c * step, y0 + r * step
        if not cell:
            continue
        date, lvl, n = cell
        if lvl == 0:
            b.append('<rect x="%d" y="%d" width="%d" height="%d" rx="4" fill="%s" opacity=".8"/>' % (x, y, cs, cs, PAL[0]))
            continue
        t = (pre + idx) / nseg
        t2 = min(t + 0.004, 0.998)
        b.append('<rect x="%d" y="%d" width="%d" height="%d" rx="4" fill="%s" filter="url(#gw)">'
                 '<animate attributeName="fill" calcMode="discrete" values="%s;%s;%s" keyTimes="0;%.4f;0.999" dur="%.1fs" repeatCount="indefinite"/>'
                 '<title>%d contributions on %s</title></rect>' % (x, y, cs, cs, PAL[lvl], PAL[lvl], PAL[0], PAL[lvl], t, T, n, date))
        # tiny burst when eaten
        b.append('<circle cx="%.1f" cy="%.1f" r="0" fill="none" stroke="%s" stroke-width="1.5" opacity="0">'
                 '<animate attributeName="r" values="0;0;12;12" keyTimes="0;%.4f;%.4f;1" dur="%.1fs" repeatCount="indefinite"/>'
                 '<animate attributeName="opacity" values="0;0;.9;0;0" keyTimes="0;%.4f;%.4f;%.4f;1" dur="%.1fs" repeatCount="indefinite"/></circle>'
                 % (x + cs / 2, y + cs / 2, PAL[min(lvl + 1, 4)], t, min(t + 0.012, 0.995), T, t, t + 0.001, min(t + 0.012, 0.995), T))
    segs = 9
    colors = ["#22d3ee", "#38bdf8", "#60a5fa", "#818cf8", "#a78bfa", "#c084fc", "#e879f9", "#f472b6", "#fb7185"]
    for i in range(segs - 1, -1, -1):
        size = 13 if i == 0 else 12 - i * 0.35
        off = (cs - size) / 2
        begin = i * 1.35 * dt
        b.append('<g opacity="0"><animate attributeName="opacity" from="0" to="1" begin="%.3fs" dur="0.01s" fill="freeze"/>'
                 '<rect x="%.2f" y="%.2f" width="%.2f" height="%.2f" rx="%.1f" fill="%s" filter="url(#gw)"/>'
                 '<animateMotion dur="%.2fs" begin="%.3fs" repeatCount="indefinite" rotate="0" path="%s"/></g>'
                 % (begin, -size / 2, -size / 2, size, size, 3 if i else 5, colors[i], T, begin, path))
    # eyes on head
    b.append('<g opacity="0"><animate attributeName="opacity" from="0" to="1" begin="0.01s" dur="0.01s" fill="freeze"/>'
             '<circle cx="2" cy="-2.2" r="1.6" fill="#0b1026"/><circle cx="2" cy="2.2" r="1.6" fill="#0b1026"/>'
             '<animateMotion dur="%.2fs" repeatCount="indefinite" rotate="0" path="%s"/></g>' % (T, path))
    b.append(legend(w, h))
    write("snake.svg", svg(w, h, "".join(b), common_defs()))


if __name__ == "__main__":
    os.makedirs(A, exist_ok=True)
    header(); typing(); sections(); divider(); skills()
    cells, total = load_contribs()
    print("contribution cells:", len(cells), "total:", total)
    matrix(cells, total)
    snake(cells, total)
