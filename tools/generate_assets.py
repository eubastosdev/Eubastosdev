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
def typed_line(text, cx, y, size, char_w, fill, delay0=1.0, step=0.045, cursor=True):
    """Linha de texto monoespaçada revelada letra a letra + cursor piscando.

    Revelamos com `fill-opacity` por <tspan> (funciona em todos os navegadores,
    ao contrário de animar clipPath). `textLength` trava a largura total, então
    o resultado não depende da fonte que o visitante tem instalada.
    """
    n = len(text) + (1 if cursor else 0)
    width = char_w * n
    x0 = cx - width / 2
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
    """Botão de idioma. O ativo ganha borda e etiqueta na cor de destaque."""
    lab, tw = _label(58, text, color=TEXT if active else MUTED)
    w = round(58 + tw + 18)
    chip_fill = ACCENT if active else SURFACE
    chip_text = BG if active else MUTED
    chip = (
        f'<rect x="14" y="11" width="32" height="22" rx="6" fill="{chip_fill}"/>'
        f'<text x="30" y="27" text-anchor="middle" font-family="{MONO}" font-size="13" '
        f'font-weight="700" fill="{chip_text}">{code}</text>'
    )
    frame = _frame(w, stroke=ACCENT if active else BORDER, fill=SURFACE if active else BG)
    write(filename, svg_wrap(w, BTN_H, label, frame + chip + lab))


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


# --- Geração ---------------------------------------------------------------
def main():
    # Banners (desktop 960x260 e mobile 480x260)
    for lang, role_d, role_m, tech, alt in [
        ("pt", "Desenvolvedor full-stack em formação", "Dev full-stack em formação",
         "REACT  ·  PYTHON", "Banner: EUBASTOSDEV, desenvolvedor full-stack em formação"),
        ("en", "Aspiring full-stack developer", "Aspiring full-stack dev",
         "REACT  ·  PYTHON", "Banner: EUBASTOSDEV, aspiring full-stack developer"),
    ]:
        hero(f"hero-{lang}.svg", 960, 260, 66, 640, role_d, 24, 14.4, tech, 15, alt)
        hero(f"hero-{lang}-mobile.svg", 480, 260, 38, 380, role_m, 17, 10.2, tech, 13, alt)

    # Idioma (rótulos neutros, servem aos dois READMEs)
    for code, name in [("PT", "Português"), ("EN", "English")]:
        for active in (True, False):
            suffix = "on" if active else "off"
            lang_button(f"lang-{code.lower()}-{suffix}.svg", code, name, active,
                        f"{name}{' (idioma atual)' if active else ''}")

    # Navegação
    nav = {
        "pt": [("about", "Sobre mim"), ("tech", "Tecnologias"), ("activity", "Atividade"), ("contact", "Contato")],
        "en": [("about", "About"), ("tech", "Technologies"), ("activity", "Activity"), ("contact", "Contact")],
    }
    for lang, items in nav.items():
        for key, text in items:
            nav_button(f"nav-{key}-{lang}.svg", text, text)

    # Contato (rótulos iguais nos dois idiomas)
    contact_button("contact-linkedin.svg", "LinkedIn", "LinkedIn")
    contact_button("contact-email.svg", "E-mail", "E-mail")
    contact_button("contact-github.svg", "GitHub", "GitHub")

    # Rodapé
    footer("footer-pt.svg", "Aprendendo em público, um commit de cada vez.",
           "Aprendendo em público, um commit de cada vez.")
    footer("footer-en.svg", "Learning in public, one commit at a time.",
           "Learning in public, one commit at a time.")
    # Rodapé mobile: canvas menor => texto maior depois que o GitHub reduz a imagem
    footer("footer-pt-mobile.svg", "Aprendendo em público, um commit de cada vez.",
           "Aprendendo em público, um commit de cada vez.", w=480, cw=9.0, fs=15)
    footer("footer-en-mobile.svg", "Learning in public, one commit at a time.",
           "Learning in public, one commit at a time.", w=480, cw=9.0, fs=15)


if __name__ == "__main__":
    main()
