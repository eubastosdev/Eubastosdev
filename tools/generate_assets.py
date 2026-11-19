#!/usr/bin/env python3
"""Gera os SVGs do README do perfil (banner, botões e rodapé).

Uso:  python tools/generate_assets.py
Saída: pasta assets/ na raiz do repositório.

Por que um script? Cada botão e banner é um SVG. Editar 20 arquivos à mão
seria um pesadelo; aqui, trocar uma cor ou um texto é mexer em UMA linha
e rodar de novo.

Regras de SVG no GitHub (por isso o código é como é):
- O SVG é carregado via <img>: scripts e fontes externas NÃO funcionam,
  então usamos só fontes do sistema.
- Animação CSS dentro do SVG funciona, e `prefers-reduced-motion` é respeitado.
- O estado base do CSS é sempre o estado FINAL; as animações só definem o
  `from`. Assim, sem animação (ou com movimento reduzido), tudo aparece completo.
"""
from pathlib import Path
from xml.sax.saxutils import escape

OUT = Path(__file__).resolve().parent.parent / "assets"

# --- Paleta (BG é o azul do seu banner original) ---------------------------
BG = "#0F172A"
SURFACE = "#1E293B"
BORDER = "#334155"
TEXT = "#E2E8F0"
MUTED = "#94A3B8"
ACCENT = "#38BDF8"

SANS = "'Segoe UI', 'Helvetica Neue', Arial, sans-serif"
MONO = "ui-monospace, 'Cascadia Code', Consolas, Menlo, 'DejaVu Sans Mono', monospace"

REDUCED_MOTION = "@media (prefers-reduced-motion: reduce){*{animation:none !important}}"


def write(name: str, svg: str) -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / name).write_text(svg, encoding="utf-8")
    print("ok", name)


def svg_wrap(w: int, h: int, label: str, body: str, css: str = "") -> str:
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" '
        f'viewBox="0 0 {w} {h}" role="img" aria-label="{escape(label)}">\n'
        f"<title>{escape(label)}</title>\n"
        f"<style>{css}{REDUCED_MOTION}</style>\n{body}</svg>\n"
    )


# --- Texto "digitado" ------------------------------------------------------
def typed_line(text, cx, y, size, char_w, fill, delay0=1.0, step=0.045, cursor=True, left=False):
    """Linha de texto monoespaçada revelada letra a letra + cursor piscando.

    Revelamos com `fill-opacity` por <tspan> (funciona em todos os navegadores,
    ao contrário de animar clipPath). `textLength` trava a largura total, então
    o resultado não depende da fonte que o visitante tem instalada.
    """
    n = len(text) + (1 if cursor else 0)
    width = char_w * n
    x0 = cx if left else cx - width / 2
    spans = []
    for i, ch in enumerate(text):
        d = delay0 + i * step
        spans.append(f'<tspan class="ch" style="animation-delay:{d:.2f}s">{escape(ch)}</tspan>')
    if cursor:
        d = delay0 + len(text) * step
        spans.append(f'<tspan class="cur" fill="{ACCENT}" style="animation-delay:{d:.2f}s">_</tspan>')
    return (
        f'<text x="{x0:.1f}" y="{y}" font-family="{MONO}" font-size="{size}" '
        f'fill="{fill}" xml:space="preserve" textLength="{width:.1f}" '
        f'lengthAdjust="spacing">{"".join(spans)}</text>\n'
    )


HERO_CSS = f"""
.rise{{animation:rise .8s ease-out .1s backwards}}
.line{{transform-box:fill-box;transform-origin:center;animation:grow .7s ease-out .5s backwards}}
.ch{{animation:show .01s steps(1) backwards}}
.cur{{animation:appear .01s steps(1) backwards,blink 1.1s steps(1) infinite}}
.fade{{animation:rise .8s ease-out 2.6s backwards}}
@keyframes rise{{from{{opacity:0;transform:translateY(10px)}}}}
@keyframes grow{{from{{transform:scaleX(0)}}}}
@keyframes show{{from{{fill-opacity:0}}}}
@keyframes appear{{from{{fill-opacity:0}}}}
@keyframes blink{{0%,49%{{fill-opacity:1}}50%,100%{{fill-opacity:0}}}}
"""


def hero(filename, w, h, name_size, name_w, role, role_size, role_cw, tech, tech_size, label):
    cx = w / 2
    name_y = h * 0.46
    line_y = name_y + h * 0.075
    role_y = line_y + h * 0.17
    tech_y = role_y + h * 0.15
    deco = h * 0.95
    body = f"""<defs>
  <pattern id="dots" width="24" height="24" patternUnits="userSpaceOnUse">
    <circle cx="2" cy="2" r="1.2" fill="{SURFACE}"/>
  </pattern>
  <radialGradient id="glow" cx="50%" cy="0%" r="75%">
    <stop offset="0" stop-color="{ACCENT}" stop-opacity=".20"/>
    <stop offset="1" stop-color="{ACCENT}" stop-opacity="0"/>
  </radialGradient>
</defs>
<rect width="{w}" height="{h}" rx="20" fill="{BG}"/>
<rect width="{w}" height="{h}" rx="20" fill="url(#dots)"/>
<rect width="{w}" height="{h}" rx="20" fill="url(#glow)"/>
<rect x=".75" y=".75" width="{w-1.5}" height="{h-1.5}" rx="19.5" fill="none" stroke="{BORDER}" stroke-width="1.5"/>
<text x="{w*0.04:.0f}" y="{deco:.0f}" font-family="{MONO}" font-size="{h*0.85:.0f}" font-weight="700" fill="{ACCENT}" fill-opacity=".10">‹</text>
<text x="{w*0.96:.0f}" y="{deco:.0f}" text-anchor="end" font-family="{MONO}" font-size="{h*0.85:.0f}" font-weight="700" fill="{ACCENT}" fill-opacity=".10">›</text>
<text class="rise" x="{cx}" y="{name_y:.0f}" text-anchor="middle" font-family="{SANS}" font-size="{name_size}" font-weight="800" fill="{TEXT}" textLength="{name_w}" lengthAdjust="spacing"><tspan fill="{ACCENT}">‹</tspan>EUBASTOSDEV<tspan fill="{ACCENT}">/›</tspan></text>
<rect class="line" x="{cx-50}" y="{line_y:.0f}" width="100" height="3" rx="1.5" fill="{ACCENT}"/>
{typed_line(role, cx, f"{role_y:.0f}", role_size, role_cw, TEXT)}<text class="fade" x="{cx}" y="{tech_y:.0f}" text-anchor="middle" font-family="{SANS}" font-size="{tech_size}" fill="{MUTED}" letter-spacing="2">{escape(tech)}</text>
"""
    write(filename, svg_wrap(w, h, label, body, HERO_CSS))


# --- Botões ----------------------------------------------------------------
BTN_H = 44


def _label(x, text, color=TEXT, char_w=8.4, size=15):
    w = len(text) * char_w
    return (
        f'<text x="{x}" y="27.5" font-family="{SANS}" font-size="{size}" font-weight="600" '
        f'fill="{color}" textLength="{w:.1f}" lengthAdjust="spacingAndGlyphs">{escape(text)}</text>',
        w,
    )


def _frame(w, stroke=BORDER, fill=BG, sw=1.5):
    return (
        f'<rect x="{sw/2}" y="{sw/2}" width="{w-sw}" height="{BTN_H-sw}" rx="10" '
        f'fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>'
    )


def nav_button(filename, text, label):
    """Botão de navegação: '# Texto' (referência ao título markdown)."""
    lab, tw = _label(34, text)
    w = round(34 + tw + 18)
    body = (
        _frame(w)
        + f'<text x="16" y="28" font-family="{MONO}" font-size="17" font-weight="700" fill="{ACCENT}">#</text>'
        + lab
    )
    write(filename, svg_wrap(w, BTN_H, label, body))


def contact_button(filename, text, label):
    """Botão de contato: 'Texto ↗' com a seta desenhada (sem depender de glifo)."""
    lab, tw = _label(18, text)
    w = round(18 + tw + 14 + 12 + 16)
    ax = 18 + tw + 14
    arrow = (
        f'<path d="M{ax} 29 L{ax+10} 19 M{ax+2} 19 H{ax+10} V27" fill="none" '
        f'stroke="{ACCENT}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>'
    )
    write(filename, svg_wrap(w, BTN_H, label, _frame(w) + lab + arrow))


def lang_button(filename, code, text, active, label):
    """Botão de idioma no formato 'PT · Português →'.

    Ativo: preenchido na cor de destaque. Inativo: escuro, com contorno.
    A seta é desenhada (path), então não depende de nenhum glifo da fonte.
    """
    full = f"{code} · {text}"
    fg = BG if active else TEXT
    lab, tw = _label(18, full, color=fg)
    w = round(18 + tw + 14 + 12 + 16)
    ax = 18 + tw + 14
    arrow = (
        f'<path d="M{ax} 22 H{ax+13} M{ax+7} 15 L{ax+14} 22 L{ax+7} 29" fill="none" '
        f'stroke="{BG if active else ACCENT}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>'
    )
    frame = _frame(w, stroke=ACCENT if active else BORDER, fill=ACCENT if active else BG)
    write(filename, svg_wrap(w, BTN_H, label, frame + lab + arrow))


# --- Rodapé ----------------------------------------------------------------
FOOT_CSS = f".cur{{animation:blink 1.1s steps(1) infinite}}@keyframes blink{{0%,49%{{fill-opacity:1}}50%,100%{{fill-opacity:0}}}}"


def footer(filename, text, label, w=960, h=120, cw=9.6, fs=16):
    cx = w / 2
    body = f"""<defs>
  <pattern id="dots" width="24" height="24" patternUnits="userSpaceOnUse">
    <circle cx="2" cy="2" r="1.2" fill="{SURFACE}"/>
  </pattern>
  <radialGradient id="glow" cx="50%" cy="100%" r="75%">
    <stop offset="0" stop-color="{ACCENT}" stop-opacity=".16"/>
    <stop offset="1" stop-color="{ACCENT}" stop-opacity="0"/>
  </radialGradient>
</defs>
<rect width="{w}" height="{h}" rx="20" fill="{BG}"/>
<rect width="{w}" height="{h}" rx="20" fill="url(#dots)"/>
<rect width="{w}" height="{h}" rx="20" fill="url(#glow)"/>
<rect x=".75" y=".75" width="{w-1.5}" height="{h-1.5}" rx="19.5" fill="none" stroke="{BORDER}" stroke-width="1.5"/>
<text x="{cx}" y="52" text-anchor="middle" font-family="{MONO}" font-size="30" font-weight="700" fill="{ACCENT}">‹/›</text>
"""
    n = len(text) + 1
    width = cw * n
    x0 = cx - width / 2
    body += (
        f'<text x="{x0:.1f}" y="92" font-family="{MONO}" font-size="{fs}" fill="{MUTED}" '
        f'xml:space="preserve" textLength="{width:.1f}" lengthAdjust="spacing">{escape(text)}'
        f'<tspan class="cur" fill="{ACCENT}">_</tspan></text>\n'
    )
    write(filename, svg_wrap(w, h, label, body, FOOT_CSS))


# --- Card de perfil --------------------------------------------------------
CARD_CSS = HERO_CSS + """
.float{animation:float 4s ease-in-out infinite}
.tw{animation:twinkle 3s ease-in-out infinite}
@keyframes float{0%,100%{transform:translateY(0)}50%{transform:translateY(-6px)}}
@keyframes twinkle{0%,100%{opacity:1}50%{opacity:.3}}
"""

INDIGO = "#818CF8"
GREEN = "#34D399"

# Bitmaps 3x5 dos símbolos que aparecem na tela do monitor pixelado.
GLYPHS = {
    "<": ["..a", ".a.", "a..", ".a.", "..a"],
    "/": ["..a", "..a", ".a.", "a..", "a.."],
    ">": ["a..", ".a.", "..a", ".a.", "a.."],
}


def pixel_monitor(x, y, cell=14):
    """Monitor em pixel art com '</>' na tela. Desenho original, montado por grade."""
    W, SCR, FRAME = 13, "#0B1220", "#CBD5E1"
    grid = [["." for _ in range(W)] for _ in range(11)]
    for c in range(W):                      # moldura (linhas 0 e 8)
        grid[0][c] = grid[8][c] = "f"
    for r in range(1, 8):                   # laterais + tela
        grid[r][0] = grid[r][W - 1] = "f"
        for c in range(1, W - 1):
            grid[r][c] = "s"
    for c in range(5, 8):                   # pescoço
        grid[9][c] = "n"
    for c in range(3, 10):                  # base
        grid[10][c] = "n"
    glyph_rows = ["".join(GLYPHS[g][i] + ("." if k < 2 else "")
                          for k, g in enumerate("</>")) for i in range(5)]
    for i, row in enumerate(glyph_rows):    # centraliza 11 colunas na tela (cols 1..11)
        for j, ch in enumerate(row):
            if ch == "a":
                grid[2 + i][1 + j] = "a"
    color = {"f": FRAME, "s": SCR, "a": ACCENT, "n": "#64748B"}
    rects = [
        f'<rect x="{x + c * cell}" y="{y + r * cell}" width="{cell}" height="{cell}" fill="{color[v]}"/>'
        for r, row in enumerate(grid) for c, v in enumerate(row) if v != "."
    ]
    return f'<g class="float" shape-rendering="crispEdges">{"".join(rects)}</g>'


def sparkle(cx, cy, r, color=ACCENT, delay=0.0):
    k = r * 0.28
    d = (f"M{cx} {cy-r} L{cx+k:.1f} {cy-k:.1f} L{cx+r} {cy} L{cx+k:.1f} {cy+k:.1f} "
         f"L{cx} {cy+r} L{cx-k:.1f} {cy+k:.1f} L{cx-r} {cy} L{cx-k:.1f} {cy-k:.1f} Z")
    return f'<path class="tw" style="animation-delay:{delay}s" d="{d}" fill="{color}"/>'


def chips(items, x, y, h=30):
    """Bolhas de informação (pills) com um ponto colorido à esquerda."""
    out, cx = [], x
    for (text, dot) in items:
        tw = len(text) * 8.3
        w = round(16 + 14 + tw + 16)
        out.append(
            f'<rect x="{cx}" y="{y}" width="{w}" height="{h}" rx="{h/2}" fill="{SURFACE}" stroke="{BORDER}" stroke-width="1.2"/>'
            f'<circle cx="{cx+17}" cy="{y+h/2}" r="4" fill="{dot}"/>'
            f'<text x="{cx+30}" y="{y+h/2+5}" font-family="{SANS}" font-size="14" font-weight="600" fill="{TEXT}" '
            f'textLength="{tw:.1f}" lengthAdjust="spacingAndGlyphs">{escape(text)}</text>'
        )
        cx += w + 12
    return "".join(out)


COPY = {
    "pt": dict(
        top="EUBASTOSDEV / PORTFÓLIO EM EVOLUÇÃO", eyebrow="DEV LOG // EM CONSTRUÇÃO",
        hi="olá, eu sou o ", name="Luiz", bang="!",
        sub="Eubastosdev · desenvolvedor full-stack em formação",
        t1="construindo, quebrando e aprendendo.", t2="React, Python e projetos que saem do papel.",
        cmd='$ git commit -m "evoluindo"',
        chips=["desenvolvedor", "engenheiro", "estudante"], status="STATUS / EM EVOLUÇÃO",
        alt="Card de perfil: olá, eu sou o Luiz. Desenvolvedor, engenheiro e estudante.",
    ),
    "es": dict(
        top="EUBASTOSDEV / PORTAFOLIO EN EVOLUCIÓN", eyebrow="DEV LOG // EN CONSTRUCCIÓN",
        hi="¡hola, soy ", name="Luiz", bang="!",
        sub="Eubastosdev · desarrollador full-stack en formación",
        t1="construyendo, rompiendo y aprendiendo.", t2="React, Python y proyectos que salen del papel.",
        cmd='$ git commit -m "evolucionando"',
        chips=["desarrollador", "ingeniero", "estudiante"], status="STATUS / EN EVOLUCIÓN",
        alt="Tarjeta de perfil: ¡hola, soy Luiz! Desarrollador, ingeniero y estudiante.",
    ),
    "en": dict(
        top="EUBASTOSDEV / EVOLVING PORTFOLIO", eyebrow="DEV LOG // WORK IN PROGRESS",
        hi="hi, I'm ", name="Luiz", bang="!",
        sub="Eubastosdev · aspiring full-stack developer",
        t1="building, breaking and learning.", t2="React, Python and projects that ship.",
        cmd='$ git commit -m "evolving"',
        chips=["developer", "engineer", "student"], status="STATUS / EVOLVING",
        alt="Profile card: hi, I'm Luiz. Developer, engineer and student.",
    ),
}


def profile_card(lang, mobile=False):
    c = COPY[lang]
    W, H = (480, 392) if mobile else (960, 428)
    L = 28 if mobile else 56                      # margem esquerda
    col_w = W - 2 * L if mobile else 524          # largura da coluna de texto
    s = lambda desk, mob: mob if mobile else desk  # escolhe tamanho por layout

    top_y = s(62, 50)
    y_eyebrow = s(100, 88)
    y_hi = s(156, 130)
    y_sub = s(190, 158)
    y_t1 = s(228, 194)
    y_t2 = s(254, 218)
    box_y = s(274, 238)
    box_h = s(72, 76)
    y_chip = s(366, box_y + box_h + 20)

    hi_size = s(46, 30)
    hi_len = (len(c["hi"]) + len(c["name"]) + 1) * hi_size * 0.50

    body = f"""<defs>
  <pattern id="dots" width="24" height="24" patternUnits="userSpaceOnUse"><circle cx="2" cy="2" r="1.2" fill="{SURFACE}"/></pattern>
  <radialGradient id="glow" cx="75%" cy="45%" r="55%"><stop offset="0" stop-color="{ACCENT}" stop-opacity=".16"/><stop offset="1" stop-color="{ACCENT}" stop-opacity="0"/></radialGradient>
</defs>
<rect width="{W}" height="{H}" rx="24" fill="{BG}"/>
<rect width="{W}" height="{H}" rx="24" fill="url(#dots)"/>
<rect width="{W}" height="{H}" rx="24" fill="url(#glow)"/>
<rect x=".75" y=".75" width="{W-1.5}" height="{H-1.5}" rx="23.5" fill="none" stroke="{BORDER}" stroke-width="1.5"/>
<circle cx="{L}" cy="{s(32,26)}" r="6" fill="{ACCENT}"/><circle cx="{L+20}" cy="{s(32,26)}" r="6" fill="{INDIGO}"/><circle cx="{L+40}" cy="{s(32,26)}" r="6" fill="{GREEN}"/>
"""
    if not mobile:
        body += (f'<text x="{W/2}" y="37" text-anchor="middle" font-family="{MONO}" font-size="12" letter-spacing="3" '
                 f'fill="{MUTED}">{escape(c["top"])}</text>\n')
    body += f'<line x1="24" y1="{top_y}" x2="{W-24}" y2="{top_y}" stroke="{BORDER}" stroke-width="1.5"/>\n'
    body += (f'<text x="{L}" y="{y_eyebrow}" font-family="{MONO}" font-size="{s(13,11)}" letter-spacing="3" '
             f'fill="{ACCENT}" font-weight="700">{escape(c["eyebrow"])}</text>\n')
    body += (f'<text class="rise" x="{L}" y="{y_hi}" font-family="{SANS}" font-size="{hi_size}" font-weight="800" fill="{TEXT}" '
             f'textLength="{hi_len:.0f}" lengthAdjust="spacing">{escape(c["hi"])}<tspan fill="{ACCENT}">{c["name"]}</tspan>{c["bang"]}</text>\n')
    sub_len = min(col_w, len(c["sub"]) * s(18, 13) * 0.5)
    body += (f'<text x="{L}" y="{y_sub}" font-family="{SANS}" font-size="{s(18,13)}" fill="{MUTED}" '
             f'textLength="{sub_len:.0f}" lengthAdjust="spacing">{escape(c["sub"])}</text>\n')
    t1_len = min(col_w, len(c["t1"]) * s(22, 17) * 0.52)
    body += (f'<text x="{L}" y="{y_t1}" font-family="{SANS}" font-size="{s(22,17)}" font-weight="600" fill="{TEXT}" '
             f'textLength="{t1_len:.0f}" lengthAdjust="spacing">{escape(c["t1"])}</text>\n')
    t2_len = min(col_w, len(c["t2"]) * s(17, 14) * 0.5)
    body += (f'<text x="{L}" y="{y_t2}" font-family="{SANS}" font-size="{s(17,14)}" fill="{MUTED}" '
             f'textLength="{t2_len:.0f}" lengthAdjust="spacing">{escape(c["t2"])}</text>\n')
    # caixa de terminal
    body += (f'<rect x="{L}" y="{box_y}" width="{col_w if mobile else 520}" height="{box_h}" rx="14" fill="{SURFACE}" fill-opacity=".6" '
             f'stroke="{BORDER}" stroke-width="1.3"/>\n')
    body += (f'<text x="{L+22}" y="{box_y+26}" font-family="{MONO}" font-size="{s(13,12)}" fill="{MUTED}">eubastosdev@github:~</text>\n')
    body += typed_line(c["cmd"], L + 22, box_y + s(54, 56), s(17, 15), s(10.2, 9.0), TEXT, delay0=1.0, left=True)
    # bolhas
    dots = [ACCENT, INDIGO, GREEN]
    body += chips(list(zip(c["chips"], dots)), L, y_chip)

    if not mobile:
        cx, cy = 762, 236
        body += (f'<circle cx="{cx}" cy="{cy}" r="112" fill="{SURFACE}" fill-opacity=".55"/>'
                 f'<circle cx="{cx}" cy="{cy}" r="130" fill="none" stroke="{BORDER}" stroke-width="1.5" stroke-dasharray="3 7"/>\n')
        body += pixel_monitor(cx - 91, cy - 82)
        for (sx, sy, r, col, d) in [(640, 118, 8, ACCENT, 0), (900, 128, 5, TEXT, .8), (884, 322, 7, INDIGO, 1.6),
                                    (646, 330, 4, TEXT, .4), (888, 224, 3, ACCENT, 1.2)]:
            body += sparkle(sx, sy, r, col, d)
        body += (f'<circle cx="{cx-84}" cy="394" r="4" fill="{GREEN}"/>'
                 f'<text x="{cx-70}" y="399" font-family="{MONO}" font-size="12" letter-spacing="2" fill="{MUTED}">{escape(c["status"])}</text>\n')

    name = f"card-{lang}{'-mobile' if mobile else ''}.svg"
    write(name, svg_wrap(W, H, c["alt"], body, CARD_CSS))


# --- Cartões de tecnologia -------------------------------------------------
import re

ICONS = Path(__file__).resolve().parent / "icons"

# Ordem = a mesma do README original (não reordenar sem querer!).
TOOLS = [
    ("html5", "HTML5"), ("css3", "CSS"), ("javascript", "JavaScript"), ("react", "React"),
    ("tailwindcss", "Tailwind CSS"), ("typescript", "TypeScript"), ("bootstrap", "Bootstrap"),
    ("figma", "Figma"), ("python", "Python"), ("nodejs", "Node.js"), ("mysql", "MySQL"),
    ("sqlite", "SQLite"), ("postgresql", "PostgreSQL"), ("mongodb", "MongoDB"), ("git", "Git"),
    ("github", "GitHub"), ("amazonwebservices", "Amazon AWS"), ("googlecloud", "Google Cloud"),
    ("npm", "npm"),
]
TILE = "#F8FAFC"
AW_BOLD = {' ': 278, '.': 278, '5': 556, 'A': 722, 'B': 722, 'C': 722, 'D': 722, 'F': 611, 'G': 778, 'H': 722, 'J': 556, 'L': 611, 'M': 833, 'N': 722, 'P': 667, 'Q': 778, 'R': 722, 'S': 667, 'T': 611, 'W': 944, 'a': 556, 'b': 611, 'c': 556, 'd': 611, 'e': 556, 'g': 611, 'h': 611, 'i': 278, 'j': 278, 'l': 278, 'm': 889, 'n': 611, 'o': 611, 'p': 611, 'r': 389, 's': 556, 't': 333, 'u': 611, 'v': 556, 'w': 778, 'y': 556, 'z': 500}  # Liberation Sans Bold (métrica do Arial)
TOOL_H = 56


def _icon_inner(key):
    """Conteúdo do SVG do ícone (sem a tag raiz), para embutir no cartão."""
    raw = (ICONS / f"{key}.svg").read_text(encoding="utf-8")
    m = re.search(r"<svg[^>]*>(.*)</svg>", raw, re.S)
    assert m, key
    inner = m.group(1)
    assert "<script" not in inner and "href=\"http" not in inner, f"{key}: conteúdo suspeito"
    return inner


def text_width(name, size=15):
    """Largura estimada (px) do rótulo em negrito. Margem de 6% p/ fontes mais largas (ex.: Inter)."""
    return sum(AW_BOLD.get(c, 600) for c in name) / 1000 * size * 1.06


def tool_card(key, name):
    """Cartão no estilo: [ quadrado claro com logo ] Nome."""
    tw = text_width(name)
    w = round(60 + tw + 18)
    body = (
        f'<rect x=".75" y=".75" width="{w-1.5}" height="{TOOL_H-1.5}" rx="12" fill="{BG}" stroke="{BORDER}" stroke-width="1.5"/>'
        f'<rect x="8" y="8" width="40" height="40" rx="9" fill="{TILE}"/>'
        f'<svg x="13" y="13" width="30" height="30" viewBox="0 0 128 128">{_icon_inner(key)}</svg>'
        f'<text x="60" y="33.5" font-family="{SANS}" font-size="15" font-weight="700" fill="{TEXT}">{escape(name)}</text>'
    )
    (OUT / "toolkit").mkdir(parents=True, exist_ok=True)
    out = OUT / "toolkit" / f"{key}.svg"
    out.write_text(svg_wrap(w, TOOL_H, name, body), encoding="utf-8")
    print("ok toolkit/" + out.name)


# --- Geração ---------------------------------------------------------------
def main():
    # Banners (desktop 960x260 e mobile 480x260)
    for lang, role_d, role_m, tech, alt in [
        ("pt", "Desenvolvedor full-stack em formação", "Dev full-stack em formação",
         "REACT  ·  PYTHON", "Banner: EUBASTOSDEV, desenvolvedor full-stack em formação"),
        ("en", "Aspiring full-stack developer", "Aspiring full-stack dev",
         "REACT  ·  PYTHON", "Banner: EUBASTOSDEV, aspiring full-stack developer"),
        ("es", "Desarrollador full-stack en formación", "Dev full-stack en formación",
         "REACT  ·  PYTHON", "Banner: EUBASTOSDEV, desarrollador full-stack en formación"),
    ]:
        hero(f"hero-{lang}.svg", 960, 260, 66, 640, role_d, 24, 14.4, tech, 15, alt)
        hero(f"hero-{lang}-mobile.svg", 480, 260, 38, 380, role_m, 17, 10.2, tech, 13, alt)

    # Idioma (rótulos neutros, servem aos dois READMEs)
    for code, name in [("PT", "Português"), ("EN", "English"), ("ES", "Español")]:
        for active in (True, False):
            suffix = "on" if active else "off"
            lang_button(f"lang-{code.lower()}-{suffix}.svg", code, name, active,
                        f"{name}{' (idioma atual)' if active else ''}")

    # Navegação
    nav = {
        "pt": [("about", "Sobre mim"), ("tech", "Tecnologias"), ("activity", "Atividade"), ("contact", "Contato")],
        "en": [("about", "About"), ("tech", "Technologies"), ("activity", "Activity"), ("contact", "Contact")],
        "es": [("about", "Sobre mí"), ("tech", "Tecnologías"), ("activity", "Actividad"), ("contact", "Contacto")],
    }
    for lang, items in nav.items():
        for key, text in items:
            nav_button(f"nav-{key}-{lang}.svg", text, text)

    # Contato (rótulos iguais nos dois idiomas)
    contact_button("contact-linkedin.svg", "LinkedIn", "LinkedIn")
    contact_button("contact-email.svg", "E-mail", "E-mail")
    contact_button("contact-github.svg", "GitHub", "GitHub")

    # Card de perfil (desktop 960 e mobile 480)
    for lang in COPY:
        profile_card(lang)
        profile_card(lang, mobile=True)

    # Cartões de tecnologia
    for key, name in TOOLS:
        tool_card(key, name)

    # Rodapé
    footer("footer-pt.svg", "Aprendendo em público, um commit de cada vez.",
           "Aprendendo em público, um commit de cada vez.")
    footer("footer-en.svg", "Learning in public, one commit at a time.",
           "Learning in public, one commit at a time.")
    footer("footer-es.svg", "Aprendiendo en público, un commit a la vez.",
           "Aprendiendo en público, un commit a la vez.")
    footer("footer-es-mobile.svg", "Aprendiendo en público, un commit a la vez.",
           "Aprendiendo en público, un commit a la vez.", w=480, cw=9.0, fs=15)
    # Rodapé mobile: canvas menor => texto maior depois que o GitHub reduz a imagem
    footer("footer-pt-mobile.svg", "Aprendendo em público, um commit de cada vez.",
           "Aprendendo em público, um commit de cada vez.", w=480, cw=9.0, fs=15)
    footer("footer-en-mobile.svg", "Learning in public, one commit at a time.",
           "Learning in public, one commit at a time.", w=480, cw=9.0, fs=15)


if __name__ == "__main__":
    main()
