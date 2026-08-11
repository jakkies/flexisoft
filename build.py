#!/usr/bin/env python3
"""
Rebuild the static FlexiSoft site (dist/) from the source artifact bundle.

The source "FlexiSoft Homepage.html" is a self-unpacking Claude artifact:
a template + data + gzip-compressed resources (logo, Inter fonts) that a
runtime assembles in the browser. This script does that assembly ahead of
time and emits a plain, JS-free static site at the repo root:

    ./index.html              fully-rendered semantic markup
    ./styles.css              reset + @font-face + hover rules
    ./assets/flexisoft-logo.svg
    ./assets/fonts/*.woff2     self-hosted Inter subsets

What it does:
  1. Reads the bundle's template, render data, and resource manifest.
  2. Expands every <sc-for> loop and {{ interpolation }} using the data.
  3. Converts the runtime's style-hover="..." attrs into real CSS :hover rules.
  4. Replaces the placeholder icon boxes with real inline SVG icons.
  5. Extracts the logo + fonts from the (gzipped, base64) manifest to files.

Usage:
    python3 build.py

Note: file naming aside, this parses the specific bundle shipped in this repo.
If you regenerate the artifact from Claude, re-check the section markers below.
"""
import json, re, base64, gzip, os, html

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "FlexiSoft Homepage.html")
OUT = HERE  # site files live at the repo root

# ---- locate the bundle's <script> payloads by type marker (robust to line moves) ----
raw = open(SRC, encoding="utf-8").read()

def script_payload(script_type):
    m = re.search(
        r'<script type="__bundler/%s">\s*(.*?)\s*</script>' % re.escape(script_type),
        raw, re.S)
    if not m:
        raise SystemExit("could not find __bundler/%s payload" % script_type)
    return json.loads(m.group(1))

manifest = script_payload("manifest")
template = script_payload("template")

# ---- extract renderVals data from the <script data-dc-script> block ----
mscript = re.search(r'renderVals\(\)\s*\{\s*return\s*(\{.*?\});\s*\}', template, re.S)
js_obj = mscript.group(1)
def js_to_json(s):
    # quote unquoted object keys:  key:  ->  "key":
    return re.sub(r'([{,]\s*)([A-Za-z_]\w*)\s*:', r'\1"\2":', s)
data = json.loads(js_to_json(js_obj))

# ---- template body (between </helmet> and </x-dc>) ----
body_tpl = template[template.find('</helmet>') + len('</helmet>'):template.find('</x-dc>')]

# ---- font-face css + reset css from helmet ----
helmet = template[template.find('<helmet>'):template.find('</helmet>')]
style_blocks = re.findall(r'<style>(.*?)</style>', helmet, re.S)
font_css = style_blocks[0]
reset_css = style_blocks[1].strip()

# ---- rendering engine: sc-for + {{ }} ----
def resolve(expr, ctx):
    parts = expr.strip().split('.')
    val = ctx[parts[0]]
    for p in parts[1:]:
        val = val[p]
    return val

def interp(text, ctx):
    return re.sub(r'\{\{\s*(.*?)\s*\}\}',
                  lambda m: html.escape(str(resolve(m.group(1), ctx))), text)

OPEN_RE = re.compile(r'<sc-for\b[^>]*>')
def expand(s, ctx):
    out = []
    i = 0
    while True:
        m = OPEN_RE.search(s, i)
        if not m:
            out.append(interp(s[i:], ctx))
            break
        out.append(interp(s[i:m.start()], ctx))
        tag = m.group(0)
        list_expr = re.search(r'list="\{\{\s*(.*?)\s*\}\}"', tag).group(1)
        as_var = re.search(r'as="([^"]*)"', tag).group(1)
        body_start = m.end()
        depth = 1
        for mm in re.finditer(r'<sc-for\b|</sc-for>', s[body_start:]):
            if mm.group(0) == '</sc-for>':
                depth -= 1
                if depth == 0:
                    close_start = body_start + mm.start()
                    close_end = body_start + mm.end()
                    break
            else:
                depth += 1
        inner = s[body_start:close_start]
        for item in resolve(list_expr, ctx):
            newctx = dict(ctx); newctx[as_var] = item
            out.append(expand(inner, newctx))
        i = close_end
    return ''.join(out)

rendered = expand(body_tpl, data)

# ---- convert style-hover -> hover classes ----
hover_values = []  # preserve first-seen order
for v in re.findall(r'style-hover="([^"]*)"', rendered):
    if v not in hover_values:
        hover_values.append(v)
hover_class = {v: f"fx-h{i}" for i, v in enumerate(hover_values)}

def add_hover_class(m):
    tag_open, attrs = m.group(1), m.group(2)
    val = m.group('val')
    attrs = attrs.replace(f' style-hover="{val}"', '')
    cls = hover_class[val]
    if re.search(r'\sclass="', attrs):
        attrs = re.sub(r'class="([^"]*)"', lambda mm: f'class="{mm.group(1)} {cls}"', attrs, count=1)
    else:
        attrs = attrs + f' class="{cls}"'
    return f'<{tag_open}{attrs}>'

rendered = re.sub(
    r'<(\w+)((?:[^>]*?)\sstyle-hover="(?P<val>[^"]*)"(?:[^>]*?))>',
    add_hover_class, rendered)

def hover_rule(cls, val):
    decls = [re.sub(r'\s*:\s*', ': ', d.strip()) + ' !important'
             for d in val.split(';') if d.strip()]
    return f".{cls}:hover {{ {'; '.join(decls)}; }}"

hover_css = "\n".join(hover_rule(hover_class[v], v) for v in hover_values)

# ---- swap placeholder icon boxes for real inline SVG icons ----
# Lucide-style 24x24 stroke glyphs (inner markup only).
ICON_PATHS = {
    "shield": '<path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/>',
    "clock":  '<circle cx="12" cy="12" r="9"/><path d="M12 7.5V12l3 1.8"/>',
    "edit":   '<path d="M12 20h9"/><path d="M16.5 3.5a2.12 2.12 0 0 1 3 3L7 19l-4 1 1-4 12.5-12.5z"/>',
    "moon":   '<path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"/>',
    "wallet": '<path d="M21 12V7H5a2 2 0 0 1 0-4h14v4"/><path d="M3 5v14a2 2 0 0 0 2 2h16v-5"/><path d="M18 12a2 2 0 0 0 0 4h4v-4z"/>',
    "users":  '<path d="M17 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2"/><circle cx="9.5" cy="7" r="4"/><path d="M22 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/>',
    "check":  '<path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/><path d="M22 4 12 14.01l-3-3"/>',
    "chart":  '<line x1="18" y1="20" x2="18" y2="10"/><line x1="12" y1="20" x2="12" y2="4"/><line x1="6" y1="20" x2="6" y2="14"/>',
}

def svg_for(name, size):
    return (f'<svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" '
            f'stroke="currentColor" stroke-width="2" stroke-linecap="round" '
            f'stroke-linejoin="round" aria-hidden="true">{ICON_PATHS[name]}</svg>')

ICON_BOX_RE = re.compile(
    r'<div style="([^"]*?border:1px dashed[^"]*?)">(' + '|'.join(ICON_PATHS) + r')</div>')

def icon_box_repl(m):
    style, name = m.group(1), m.group(2)
    flex = 'flex:0 0 auto; ' if 'flex:0 0 auto' in style else ''
    w = re.search(r'width:(\d+)px', style).group(1)
    h = re.search(r'height:(\d+)px', style).group(1)
    size = round(int(w) * 0.5)
    new_style = (f'{flex}width:{w}px; height:{h}px; border-radius:11px; '
                 f'background:#E6F9F3; display:flex; align-items:center; '
                 f'justify-content:center; color:#00A17A')
    return f'<div style="{new_style}">{svg_for(name, size)}</div>'

rendered, n_icons = ICON_BOX_RE.subn(icon_box_repl, rendered)

# ---- resource UUIDs -> asset files ----
def raw_bytes(uuid):
    v = manifest[uuid]
    b = base64.b64decode(v['data'])
    return gzip.decompress(b) if v.get('compressed') else b

logo_uuid = re.search(r'<img src="([0-9a-f-]{36})"', template).group(1)
rendered = rendered.replace(f'src="{logo_uuid}"', 'src="assets/flexisoft-logo.svg"')

# fonts: map each uuid -> friendly subset name from preceding /* comment */
font_name = {}
for comment, uuid in re.findall(
        r'/\*\s*([\w-]+)\s*\*/\s*@font-face\s*\{[^}]*?url\("([0-9a-f-]{36})"\)', font_css):
    font_name.setdefault(uuid, comment)
font_css_out = re.sub(
    r'url\("([0-9a-f-]{36})"\)',
    lambda m: f'url("assets/fonts/inter-{font_name[m.group(1)]}.woff2")',
    font_css).strip()

# ---- write output tree ----
os.makedirs(f"{OUT}/assets/fonts", exist_ok=True)

with open(f"{OUT}/assets/flexisoft-logo.svg", "wb") as f:
    f.write(raw_bytes(logo_uuid))

for uuid, name in font_name.items():
    with open(f"{OUT}/assets/fonts/inter-{name}.woff2", "wb") as f:
        f.write(raw_bytes(uuid))

styles = f"""/* FlexiSoft — extracted static styles */

/* ---------- Base / reset ---------- */
{reset_css}

/* ---------- Fonts (Inter, self-hosted subsets) ---------- */
{font_css_out}

/* ---------- Hover interactions ---------- */
{hover_css}
"""
with open(f"{OUT}/styles.css", "w") as f:
    f.write(styles)

index = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>FlexiSoft — Micro-Lending Software Built Around Your Business</title>
  <meta name="description" content="A flexible, reliable, and scalable micro-lending platform designed to streamline your lending operations from origination to collections.">
  <link rel="icon" href="assets/flexisoft-logo.svg" type="image/svg+xml">
  <link rel="stylesheet" href="styles.css">
</head>
<body>
{rendered.strip()}
</body>
</html>
"""
with open(f"{OUT}/index.html", "w") as f:
    f.write(index)

print(f"Built {OUT}")
print(f"  icons swapped : {n_icons}")
print(f"  hover classes : {len(hover_class)}")
print(f"  fonts written : {len(font_name)}")
