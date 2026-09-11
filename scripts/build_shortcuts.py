#!/usr/bin/env python3
"""Render docs/shortcuts.md as a standalone HTML guide (stdlib only).

Supports the guide's Markdown subset: headings, paragraphs, unordered lists,
tables, fenced code, links, inline code and emphasis. Keep Markdown as the source.
"""
import argparse
import html
from pathlib import Path
import re
import unicodedata

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "docs/shortcuts.md"
OUTPUT = SOURCE.with_suffix(".html")


def inline(text):
    tokens = []

    def keep(value):
        tokens.append(value)
        return f"\x00{len(tokens) - 1}\x00"

    text = re.sub(r"`([^`]+)`", lambda m: keep("<code>" + html.escape(m[1]) + "</code>"), text)
    text = re.sub(r"\[([^\]]+)\]\(([^)]+)\)",
                  lambda m: keep(f'<a href="{html.escape(m[2], quote=True)}">{html.escape(m[1])}</a>'), text)
    text = html.escape(text)
    text = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", text)
    return re.sub(r"\x00(\d+)\x00", lambda m: tokens[int(m[1])], text)


def slug(text):
    plain = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9]+", "-", plain.lower()).strip("-")


def render(markdown):
    lines = markdown.splitlines()
    blocks, navigation = [], []
    i = 0
    while i < len(lines):
        line = lines[i]
        if not line.strip():
            i += 1
            continue
        if line.startswith("```"):
            code = []
            i += 1
            while i < len(lines) and not lines[i].startswith("```"):
                code.append(lines[i])
                i += 1
            if i == len(lines):
                raise ValueError("Unclosed Markdown code fence")
            blocks.append('<pre><code>' + html.escape("\n".join(code)) + '</code></pre>')
        elif line.startswith("#"):
            match = re.fullmatch(r"(#{1,6}) (.+)", line)
            if not match:
                raise ValueError(f"Unsupported heading: {line}")
            level, title = len(match[1]), match[2]
            anchor = slug(title)
            blocks.append(f'<h{level} id="{anchor}">{inline(title)}</h{level}>')
            if level == 2:
                navigation.append(f'<li><a href="#{anchor}">{html.escape(title)}</a></li>')
        elif line.startswith("| "):
            rows = []
            while i < len(lines) and lines[i].startswith("| "):
                cells = [cell.strip() for cell in lines[i].strip().strip("|").split("|")]
                if not all(re.fullmatch(r":?-+:?", cell) for cell in cells):
                    rows.append(cells)
                i += 1
            width = len(rows[0])
            if any(len(row) != width for row in rows):
                raise ValueError("Inconsistent table columns")
            header = '<tr>' + ''.join(f'<th scope="col">{inline(c)}</th>' for c in rows[0]) + '</tr>'
            body = ''.join('<tr>' + ''.join(f'<td>{inline(c)}</td>' for c in row) + '</tr>' for row in rows[1:])
            blocks.append(f'<div class="table-wrap" tabindex="0" role="region" aria-label="Tabla de referencia"><table><thead>{header}</thead><tbody>{body}</tbody></table></div>')
            continue
        elif line.startswith("- "):
            items = []
            while i < len(lines) and lines[i].startswith("- "):
                items.append('<li>' + inline(lines[i][2:]) + '</li>')
                i += 1
            blocks.append('<ul>' + ''.join(items) + '</ul>')
            continue
        else:
            paragraph = [line]
            i += 1
            while i < len(lines) and lines[i].strip() and not lines[i].startswith(("#", "| ", "- ", "```")):
                paragraph.append(lines[i])
                i += 1
            blocks.append('<p>' + inline(' '.join(paragraph)) + '</p>')
            continue
        i += 1
    return '\n'.join(blocks), '\n'.join(navigation)


STYLE = """
:root {color-scheme: light; --ink:#192b3d; --muted:#506277; --accent:#006978; --line:#d5e1e8; --paper:#fff}
* {box-sizing:border-box} html {scroll-behavior:smooth;scroll-padding-top:24px}
body {margin:0;background:#eef3f6;color:var(--ink);font:16px/1.7 system-ui,-apple-system,"Segoe UI",sans-serif}
a {color:var(--accent);text-underline-offset:3px} a:hover {color:#003b47}
:focus-visible {outline:3px solid #d87300;outline-offset:4px}
.skip {position:absolute;left:20px;top:-100px;background:white;padding:12px;z-index:2}.skip:focus{top:12px}
.banner {background:#122939;color:white;padding:34px max(24px,calc((100vw - 1320px)/2));border-bottom:5px solid #68c7cf}
.banner p {margin:0;color:#cfdee8}.banner strong {display:block;font-size:14px;letter-spacing:.14em;color:#8bdae0}
.layout {max-width:1320px;margin:32px auto;display:grid;grid-template-columns:260px minmax(0,1fr);gap:30px;padding:0 24px}
nav {position:sticky;top:24px;align-self:start;max-height:calc(100vh - 48px);overflow:auto;font-size:14px}
nav h2 {font-size:13px;text-transform:uppercase;letter-spacing:.1em;margin:0 0 12px;color:var(--muted)}
nav ol {list-style:none;padding:0;margin:0}nav li {margin:0 0 3px}nav a{display:block;padding:7px 10px;text-decoration:none;border-radius:6px}
nav a:hover{background:#dcebef}nav .download{margin-top:18px;border:1px solid var(--line)}
main {min-width:0;background:var(--paper);padding:36px 42px;border:1px solid var(--line);border-radius:12px}
h1 {font-size:clamp(1.8rem,3vw,2.65rem);line-height:1.17;letter-spacing:-.035em;margin:0 0 24px;max-width:760px}
main h2 {font-size:1.45rem;line-height:1.35;margin:48px 0 18px;padding-top:22px;border-top:2px solid var(--line)}
p {margin:0 0 18px}li{margin:6px 0}strong{font-weight:650}
.table-wrap {overflow-x:auto;margin:20px 0 24px;border:1px solid var(--line);border-radius:8px}
table {width:100%;border-collapse:collapse;font-size:14px;line-height:1.55}
th {background:#e5f1f3;text-align:left;font-size:12px;text-transform:uppercase;letter-spacing:.04em}
th,td {padding:12px 14px;vertical-align:top;border-bottom:1px solid var(--line)}tr:last-child td{border-bottom:0}
tbody tr:nth-child(even){background:#f7f9fb}td:first-child{min-width:160px}td:first-child strong{color:#004c5a}
code {font-family:ui-monospace,Consolas,monospace;font-size:.88em;overflow-wrap:anywhere;background:#edf2f6;padding:2px 5px;border-radius:4px}
pre {background:#142c3d;color:#e1f2f4;padding:18px 20px;border-radius:8px;overflow:auto;line-height:1.6}
pre code {background:none;color:inherit;padding:0;white-space:pre;overflow-wrap:normal}
footer {max-width:1320px;margin:0 auto 32px;padding:0 24px;color:var(--muted);font-size:13px}
@media(max-width:900px){.layout{grid-template-columns:1fr;gap:18px;margin-top:20px}nav{position:static;max-height:none}nav ol{columns:2}main{padding:28px 24px}}
@media(max-width:520px){.layout{padding:0 12px}main{padding:24px 16px}nav ol{columns:1}th,td{padding:10px}h1{font-size:1.9rem}.banner{padding:24px}}
@media(prefers-reduced-motion:reduce){html{scroll-behavior:auto}}
@media print{body{background:white;font-size:10pt;color:black}.skip,.banner,nav,footer{display:none}.layout{display:block;max-width:none;margin:0;padding:0}main{padding:0;border:0}h1{font-size:24pt}main h2{font-size:15pt;break-after:avoid;margin-top:24px}table{font-size:9pt}thead{display:table-header-group}tr,pre{break-inside:avoid}.table-wrap{overflow:visible}pre{white-space:pre-wrap;background:#eee;color:black}pre code{white-space:pre-wrap}a{color:inherit}}
"""


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true', help='Fail if the generated HTML is stale')
    args = parser.parse_args()
    content, navigation = render(SOURCE.read_text(encoding='utf-8'))
    result = f'''<!doctype html>
<!-- Generated by scripts/build_shortcuts.py from docs/shortcuts.md. -->
<html lang="es"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="description" content="Guía de atajos de bspwm, sxhkd, Kitty y Polybar para Parrot 7 y Kali: ejemplos, capturas y recuperación.">
<title>Guía de atajos · auto-bspwm · Parrot y Kali</title><style>{STYLE}</style></head>
<body><a class="skip" href="#contenido">Saltar al contenido</a>
<header class="banner"><strong>AUTO-BSPWM / GUÍA DE USO</strong><p>Parrot 7 · Kali Linux · Sesión X11</p></header>
<div class="layout"><nav aria-label="Índice de la guía"><h2>Contenido</h2><ol>{navigation}</ol><a class="download" href="shortcuts.md">Versión Markdown</a></nav>
<main id="contenido">{content}</main></div>
<footer>Guía basada en la configuración del repositorio. Abre el diálogo de impresión del navegador para imprimir o guardar como PDF.</footer>
</body></html>
'''
    if args.check:
        if not OUTPUT.exists() or OUTPUT.read_text(encoding='utf-8') != result:
            parser.exit(1, 'HTML desactualizado; ejecuta python3 scripts/build_shortcuts.py\n')
        print('Markdown y HTML sincronizados.')
    else:
        OUTPUT.write_text(result, encoding='utf-8', newline='\n')
        print(f'Generado: {OUTPUT}')


if __name__ == '__main__':
    main()
