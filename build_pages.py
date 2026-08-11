#!/usr/bin/env python3
"""
Generate the FlexiSoft sub-pages (Solutions, Partners, Case Studies,
Resources, About, Contact) at the repo root, and unify the header/footer +
navigation across every page including the existing home page.

Content is taken from the project's "Website Content" brief. Case-study and
resource entries are clearly-labelled SAMPLE placeholders (the brief provided
only templates for those). Run from the project root:

    python3 build_pages.py
"""
import os, re

HERE = os.path.dirname(os.path.abspath(__file__))
DIST = HERE  # site files live at the repo root

# ---------------------------------------------------------------- design tokens
GREEN   = "#00BD8E"
INK     = "#111827"
BODY    = "#4B5350"
MUTED   = "#6B7472"
FAINT   = "#9CA5A2"
PANEL   = "#F4F7F6"
LINE    = "#E5E9E8"
ACCENT  = "#00A17A"
TILE    = "#E6F9F3"
DARK    = "#052416"

WRAP = "max-width:1200px; margin:0 auto"
EYEBROW = f"font-size:11px; font-weight:700; letter-spacing:0.12em; text-transform:uppercase; color:{ACCENT}"
H2 = f"margin:0; font-size:clamp(26px, 3.2vw, 34px); line-height:1.2; font-weight:700; letter-spacing:-0.02em; color:{INK}"
LEAD = f"margin:0; font-size:15px; line-height:24px; color:{MUTED}; max-width:56ch; text-wrap:pretty"
CARD = f"background:#FFFFFF; border:1px solid {LINE}; border-radius:16px; padding:26px; box-shadow:0 1px 3px rgba(17,24,39,0.05); transition:box-shadow 200ms cubic-bezier(.2,0,.2,1), transform 200ms cubic-bezier(.2,0,.2,1)"

# Lucide-style icon glyphs (inner markup)
ICONS = {
    "shield": '<path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/>',
    "clock":  '<circle cx="12" cy="12" r="9"/><path d="M12 7.5V12l3 1.8"/>',
    "edit":   '<path d="M12 20h9"/><path d="M16.5 3.5a2.12 2.12 0 0 1 3 3L7 19l-4 1 1-4 12.5-12.5z"/>',
    "moon":   '<path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"/>',
    "wallet": '<path d="M21 12V7H5a2 2 0 0 1 0-4h14v4"/><path d="M3 5v14a2 2 0 0 0 2 2h16v-5"/><path d="M18 12a2 2 0 0 0 0 4h4v-4z"/>',
    "users":  '<path d="M17 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2"/><circle cx="9.5" cy="7" r="4"/><path d="M22 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/>',
    "check":  '<path d="M20 6 9 17l-5-5"/>',
    "chart":  '<line x1="18" y1="20" x2="18" y2="10"/><line x1="12" y1="20" x2="12" y2="4"/><line x1="6" y1="20" x2="6" y2="14"/>',
    "link":   '<path d="M10 13a5 5 0 0 0 7 0l3-3a5 5 0 0 0-7-7l-1.5 1.5"/><path d="M14 11a5 5 0 0 0-7 0l-3 3a5 5 0 0 0 7 7l1.5-1.5"/>',
    "zap":    '<polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"/>',
    "trend":  '<polyline points="22 7 13.5 15.5 8.5 10.5 2 17"/><polyline points="16 7 22 7 22 13"/>',
    "target": '<circle cx="12" cy="12" r="9"/><circle cx="12" cy="12" r="5"/><circle cx="12" cy="12" r="1"/>',
    "compass":'<circle cx="12" cy="12" r="9"/><polygon points="16.24 7.76 14.12 14.12 7.76 16.24 9.88 9.88 16.24 7.76"/>',
    "layers": '<polygon points="12 2 2 7 12 12 22 7 12 2"/><polyline points="2 17 12 22 22 17"/><polyline points="2 12 12 17 22 12"/>',
    "database":'<ellipse cx="12" cy="5" rx="9" ry="3"/><path d="M3 5v14c0 1.66 4 3 9 3s9-1.34 9-3V5"/><path d="M3 12c0 1.66 4 3 9 3s9-1.34 9-3"/>',
    "cog":    '<circle cx="12" cy="12" r="3"/><path d="M12 2v3M12 19v3M4.2 4.2l2.1 2.1M17.7 17.7l2.1 2.1M2 12h3M19 12h3M4.2 19.8l2.1-2.1M17.7 6.3l2.1-2.1"/>',
    "life":   '<circle cx="12" cy="12" r="9"/><circle cx="12" cy="12" r="4"/><path d="M4.9 4.9l4.2 4.2M14.9 14.9l4.2 4.2M14.9 9.1l4.2-4.2M4.9 19.1l4.2-4.2"/>',
    "book":   '<path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20"/><path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z"/>',
    "flag":   '<path d="M4 15s1-1 4-1 5 2 8 2 4-1 4-1V3s-1 1-4 1-5-2-8-2-4 1-4 1z"/><line x1="4" y1="22" x2="4" y2="15"/>',
    "heart":  '<path d="M20.8 4.6a5.5 5.5 0 0 0-7.8 0L12 5.6l-1-1a5.5 5.5 0 0 0-7.8 7.8l1 1L12 21l7.8-7.6 1-1a5.5 5.5 0 0 0 0-7.8z"/>',
    "star":   '<polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"/>',
    "clip":   '<path d="M20.59 13.41 12 22a5 5 0 0 1-7-7l9.59-8.59a3 3 0 0 1 4.24 4.24L9.41 18.59a1 1 0 0 1-1.41-1.41L16 9"/>',
}

def icon(name, size=20, color=ACCENT):
    return (f'<span style="flex:0 0 auto; width:40px; height:40px; border-radius:11px; '
            f'background:{TILE}; display:inline-flex; align-items:center; justify-content:center; color:{color}">'
            f'<svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="currentColor" '
            f'stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">{ICONS[name]}</svg></span>')

# ------------------------------------------------------------------- components
def btn_primary(label, href, big=True):
    h = "46px" if big else "40px"; pad = "0 26px" if big else "0 20px"; fs = "15px" if big else "14px"
    return (f'<a href="{href}" class="fx-h2" style="display:inline-flex; align-items:center; justify-content:center; '
            f'height:{h}; padding:{pad}; border-radius:999px; background:{GREEN}; color:{DARK}; font-size:{fs}; '
            f'font-weight:700; text-decoration:none">{label}</a>')

def btn_ghost(label, href, big=True):
    h = "46px" if big else "40px"; pad = "0 26px" if big else "0 20px"; fs = "15px" if big else "14px"
    return (f'<a href="{href}" class="fx-h3" style="display:inline-flex; align-items:center; justify-content:center; '
            f'height:{h}; padding:{pad}; border-radius:999px; background:#FFFFFF; border:1px solid #CFD5D3; '
            f'color:{INK}; font-size:{fs}; font-weight:600; text-decoration:none">{label}</a>')

def link_arrow(label, href):
    return (f'<a href="{href}" class="fx-h0" style="display:inline-flex; align-items:center; gap:7px; '
            f'align-self:flex-start; font-size:14px; font-weight:600; color:#006B52; text-decoration:underline">{label} →</a>')

def eyebrow(text):
    return f'<span style="{EYEBROW}">{text}</span>'

def section(inner, pad="72px 32px", bg=None):
    style = f"padding:{pad}" + (f"; background:{bg}" if bg else "")
    return f'<section style="{style}"><div style="{WRAP}">{inner}</div></section>'

def hero(eyebrow_text, title, subhead, cta_html=""):
    cta = f'<div style="display:flex; flex-wrap:wrap; gap:12px; padding-top:8px">{cta_html}</div>' if cta_html else ""
    return (f'<section style="padding:40px 32px 0">'
            f'<div style="{WRAP}; background:{PANEL}; border-radius:24px; padding:clamp(36px, 5vw, 72px)">'
            f'<div style="display:flex; flex-direction:column; gap:16px; max-width:660px">'
            f'{eyebrow(eyebrow_text)}'
            f'<h1 style="margin:0; font-size:clamp(30px, 4vw, 46px); line-height:1.1; font-weight:800; '
            f'letter-spacing:-0.025em; color:{INK}; text-wrap:balance">{title}</h1>'
            f'<p style="margin:0; font-size:16px; line-height:26px; color:{BODY}; max-width:60ch; text-wrap:pretty">{subhead}</p>'
            f'{cta}</div></div></section>')

def section_head(eyebrow_text, title, sub=None, center=True):
    align = "align-items:center; text-align:center" if center else "align-items:flex-start"
    sub_html = f'<p style="{LEAD}">{sub}</p>' if sub else ""
    eb = eyebrow(eyebrow_text) if eyebrow_text else ""
    return (f'<div style="display:flex; flex-direction:column; gap:12px; {align}; margin-bottom:44px">'
            f'{eb}<h2 style="{H2}">{title}</h2>{sub_html}</div>')

def value_card(icon_name, title, body):
    return (f'<div class="fx-h4" style="{CARD}; display:flex; flex-direction:column; gap:0">'
            f'{icon(icon_name)}'
            f'<h3 style="margin:20px 0 8px; font-size:16px; line-height:22px; font-weight:700; letter-spacing:-0.01em; color:{INK}">{title}</h3>'
            f'<p style="margin:0; font-size:13.5px; line-height:21px; color:{MUTED}">{body}</p></div>')

def feature_row(icon_name, title, body):
    return (f'<div style="display:flex; gap:18px; background:#FFFFFF; border:1px solid {LINE}; border-radius:14px; '
            f'padding:22px; box-shadow:0 1px 3px rgba(17,24,39,0.05)">{icon(icon_name)}'
            f'<div style="display:flex; flex-direction:column; gap:7px">'
            f'<h3 style="margin:0; font-size:15.5px; line-height:22px; font-weight:700; letter-spacing:-0.01em; color:{INK}">{title}</h3>'
            f'<p style="margin:0; font-size:13.5px; line-height:21px; color:{MUTED}">{body}</p></div></div>')

def grid(items, minpx=230, gap=24):
    cells = "".join(items)
    return f'<div style="display:grid; grid-template-columns:repeat(auto-fit, minmax({minpx}px, 1fr)); gap:{gap}px">{cells}</div>'

def check_item(text):
    return (f'<li style="display:flex; align-items:flex-start; gap:10px; font-size:14.5px; line-height:23px; color:{BODY}">'
            f'<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="{ACCENT}" stroke-width="2.5" '
            f'stroke-linecap="round" stroke-linejoin="round" style="flex:0 0 auto; margin-top:3px" aria-hidden="true">'
            f'<path d="M20 6 9 17l-5-5"/></svg><span>{text}</span></li>')

def check_list(items):
    return f'<ul style="list-style:none; margin:0; padding:0; display:flex; flex-direction:column; gap:12px">{"".join(check_item(i) for i in items)}</ul>'

def cta_banner(title, sub, buttons):
    return (f'<section style="padding:88px 32px">'
            f'<div style="{WRAP}; border-radius:24px; padding:clamp(56px, 8vw, 96px) 40px; '
            f'background:radial-gradient(120% 140% at 8% 50%, #0A4030 0%, {DARK} 58%, #041B10 100%); '
            f'box-shadow:0 24px 48px rgba(5,36,22,0.12); display:flex; flex-direction:column; align-items:center; gap:18px">'
            f'<h2 style="margin:0; font-size:clamp(30px, 4vw, 44px); line-height:1.14; font-weight:800; letter-spacing:-0.025em; '
            f'color:#FFFFFF; text-align:center; max-width:22ch; text-wrap:balance">{title}</h2>'
            f'<p style="margin:0; font-size:15px; line-height:24px; color:rgba(255,255,255,0.68); text-align:center; max-width:54ch">{sub}</p>'
            f'<div style="display:flex; flex-wrap:wrap; gap:12px; justify-content:center; margin-top:14px">{buttons}</div>'
            f'</div></section>')

def sample_tag():
    return (f'<span style="align-self:flex-start; font-size:10px; font-weight:700; letter-spacing:0.08em; '
            f'text-transform:uppercase; color:{ACCENT}; background:{TILE}; border-radius:999px; padding:4px 9px">Sample</span>')

# ---------------------------------------------------------------- shared chrome
NAV = [
    ("Solutions",    "solutions.html"),
    ("Partners",     "partners.html"),
    ("Case Studies", "case-studies.html"),
    ("Resources",    "resources.html"),
    ("About",        "about.html"),
    ("Contact",      "contact.html"),
]
FOOTER_COLS = [
    ("Platform", [("Solutions", "solutions.html"), ("Neptus", "solutions.html#neptus"), ("DCS", "solutions.html#dcs")]),
    ("Company",  [("About", "about.html"), ("Partners", "partners.html"), ("Contact", "contact.html")]),
    ("Resources",[("Case Studies", "case-studies.html"), ("Blog", "resources.html"), ("Request a Demo", "contact.html")]),
]

def header(active):
    links = []
    for label, href in NAV:
        if label == active:
            style = f"font-size:14.5px; font-weight:600; color:{INK}; text-decoration:none"
        else:
            style = "font-size:14.5px; font-weight:500; color:#343A38; text-decoration:none"
        links.append(f'<a href="{href}" class="fx-h0" style="{style}">{label}</a>')
    nav = "\n          ".join(links)
    return f'''<header style="position:sticky; top:0; z-index:20; background:rgba(255,255,255,0.92); backdrop-filter:blur(10px); border-bottom:1px solid {LINE}">
    <div style="display:flex; flex-wrap:wrap; align-items:center; justify-content:space-between; gap:16px 32px; max-width:1200px; min-height:72px; margin:0 auto; padding:14px 32px">
      <a href="index.html" style="display:flex; align-items:center; text-decoration:none">
        <img src="assets/flexisoft-logo.svg" alt="FlexiSoft" style="height:22px; width:auto; display:block">
      </a>
      <nav style="display:flex; flex-wrap:wrap; align-items:center; gap:28px">
          {nav}
      </nav>
      <div style="display:flex; flex-wrap:wrap; align-items:center; gap:12px">
        <a href="#" class="fx-h1" style="display:inline-flex; align-items:center; height:40px; padding:0 20px; border-radius:999px; border:1px solid #CFD5D3; background:#FFFFFF; font-size:14px; font-weight:500; color:{INK}; text-decoration:none">Portal Log in</a>
        <a href="contact.html" class="fx-h2" style="display:inline-flex; align-items:center; height:40px; padding:0 20px; border-radius:999px; background:{GREEN}; color:{DARK}; font-size:14px; font-weight:700; text-decoration:none">Book a Demo</a>
      </div>
    </div>
  </header>'''

def footer():
    cols = []
    for title, links in FOOTER_COLS:
        ls = "\n          ".join(
            f'<a href="{href}" class="fx-h0" style="font-size:13.5px; color:{MUTED}; text-decoration:none">{label}</a>'
            for label, href in links)
        cols.append(f'''<div style="display:flex; flex-direction:column; gap:12px">
          <span style="font-size:11px; font-weight:700; letter-spacing:0.12em; text-transform:uppercase; color:{INK}">{title}</span>
          {ls}
        </div>''')
    cols_html = "\n      ".join(cols)
    return f'''<footer style="border-top:1px solid {LINE}; background:#FFFFFF">
    <div style="max-width:1200px; margin:0 auto; padding:56px 32px 40px; display:grid; grid-template-columns:repeat(auto-fit, minmax(170px, 1fr)); gap:40px">
      <div style="display:flex; flex-direction:column; gap:14px; max-width:34ch">
        <img src="assets/flexisoft-logo.svg" alt="FlexiSoft" style="height:22px; width:auto; align-self:flex-start; display:block">
        <p style="margin:0; font-size:13.5px; line-height:21px; color:{MUTED}">Next-generation micro-lending software for modern financial institutions.</p>
      </div>
      {cols_html}
    </div>
    <div style="border-top:1px solid {LINE}">
      <div style="max-width:1200px; margin:0 auto; padding:20px 32px; display:flex; flex-wrap:wrap; align-items:center; justify-content:space-between; gap:12px 24px">
        <span style="font-size:12.5px; color:{FAINT}">© 2026 FlexiSoft Inc. All rights reserved.</span>
        <div style="display:flex; flex-wrap:wrap; gap:24px">
          <a href="#" class="fx-h0" style="font-size:12.5px; color:{FAINT}; text-decoration:none">Privacy Policy</a>
          <a href="#" class="fx-h0" style="font-size:12.5px; color:{FAINT}; text-decoration:none">Terms of Service</a>
        </div>
      </div>
    </div>
  </footer>'''

def page(title, description, active, main_html):
    return f'''<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{title}</title>
  <meta name="description" content="{description}">
  <link rel="icon" href="assets/flexisoft-logo.svg" type="image/svg+xml">
  <link rel="stylesheet" href="styles.css">
</head>
<body>
<div style="display:flex; flex-direction:column; min-height:100vh; background:#FFFFFF">
  {header(active)}
  <main style="display:flex; flex-direction:column">
{main_html}
  </main>
  {footer()}
</div>
</body>
</html>
'''

# ============================================================ PAGE CONTENT
DEMO = "contact.html"

# ---- Solutions -------------------------------------------------------------
def solutions_main():
    h = hero("Solutions",
             "One connected platform for micro-lending",
             "FlexiSoft provides a complete software solution for micro-lenders, combining powerful core systems with integrated tools to streamline operations and support growth.",
             btn_primary("Request a Demo", DEMO))

    core = section(
        section_head("Core systems", "Two systems, one ecosystem",
                     "A powerful core platform backed by supporting tools — built to work together.")
        + grid([
            (f'<div class="fx-h4" style="{CARD}; display:flex; flex-direction:column; gap:14px; min-height:210px">'
             f'{icon("layers")}'
             f'<h3 style="margin:6px 0 0; font-size:20px; line-height:26px; font-weight:700; letter-spacing:-0.015em; color:{INK}">Neptus — Core Lending Platform</h3>'
             f'<p style="margin:0; font-size:14px; line-height:22px; color:{MUTED}">Your central platform for managing loans, clients, and reporting.</p>'
             f'<div style="margin-top:auto">{link_arrow("Learn More", "solutions.html#neptus")}</div></div>'),
            (f'<div class="fx-h4" style="{CARD}; display:flex; flex-direction:column; gap:14px; min-height:210px">'
             f'{icon("database")}'
             f'<h3 style="margin:6px 0 0; font-size:20px; line-height:26px; font-weight:700; letter-spacing:-0.015em; color:{INK}">DCS — Supporting System</h3>'
             f'<p style="margin:0; font-size:14px; line-height:22px; color:{MUTED}">Supporting tools designed to enhance operational efficiency.</p>'
             f'<div style="margin-top:auto">{link_arrow("Learn More", "solutions.html#dcs")}</div></div>'),
        ], minpx=320, gap=24),
        pad="64px 32px")

    # Neptus deep-dive
    neptus = (f'<section id="neptus" style="padding:56px 32px; background:{PANEL}; scroll-margin-top:88px">'
              f'<div style="{WRAP}; display:grid; grid-template-columns:repeat(auto-fit, minmax(300px, 1fr)); gap:48px; align-items:start">'
              f'<div style="display:flex; flex-direction:column; gap:16px">'
              f'{eyebrow("Core platform")}'
              f'<h2 style="{H2}">Neptus</h2>'
              f'<p style="{LEAD}">Neptus is the core FlexiSoft platform designed specifically for micro-lending businesses.</p>'
              f'<div style="padding-top:8px">{btn_primary("Book a Demo", DEMO)}</div></div>'
              f'<div style="display:flex; flex-direction:column; gap:28px">'
              f'<div><h3 style="margin:0 0 14px; font-size:13px; font-weight:700; letter-spacing:0.08em; text-transform:uppercase; color:{ACCENT}">Features</h3>'
              f'{check_list(["Loan management", "Client tracking", "Reporting tools", "Workflow automation"])}</div>'
              f'<div><h3 style="margin:0 0 14px; font-size:13px; font-weight:700; letter-spacing:0.08em; text-transform:uppercase; color:{ACCENT}">Benefits</h3>'
              f'{check_list(["Save time on admin", "Improve accuracy", "Scale your operations"])}</div>'
              f'</div></div></section>')

    # DCS deep-dive
    dcs = (f'<section id="dcs" style="padding:56px 32px; scroll-margin-top:88px">'
           f'<div style="{WRAP}; display:grid; grid-template-columns:repeat(auto-fit, minmax(300px, 1fr)); gap:48px; align-items:start">'
           f'<div style="display:flex; flex-direction:column; gap:16px">'
           f'{eyebrow("Supporting system")}'
           f'<h2 style="{H2}">DCS</h2>'
           f'<p style="{LEAD}">DCS enhances your operational capabilities by supporting key processes and improving efficiency.</p>'
           f'<div style="padding-top:8px">{btn_ghost("Request More Info", DEMO)}</div></div>'
           f'<div><h3 style="margin:0 0 14px; font-size:13px; font-weight:700; letter-spacing:0.08em; text-transform:uppercase; color:{ACCENT}">Features</h3>'
           f'{check_list(["Data handling", "Process automation", "System support"])}</div>'
           f'</div></section>')

    cta = cta_banner("Ready to see FlexiSoft in action?",
                     "Join over 100+ institutions scaling their lending business with FlexiSoft.",
                     btn_primary("Request a Demo", DEMO) + btn_ghost("Contact Us", DEMO))
    return h + core + neptus + dcs + cta

# ---- Partners --------------------------------------------------------------
def partners_main():
    h = hero("Partners",
             "A connected, credible ecosystem",
             "FlexiSoft integrates with leading platforms to create a powerful, connected ecosystem.",
             btn_primary("Request a Demo", DEMO))
    benefits = section(
        section_head("Why it matters", "Built to connect",
                     "Centralised systems, automated communication, and scalable infrastructure.")
        + grid([
            value_card("layers", "Centralised systems", "Bring your core tools together so data flows in one place — no more disconnected spreadsheets."),
            value_card("zap", "Automated communication", "Trigger reminders, notifications, and updates automatically across your connected platforms."),
            value_card("trend", "Scalable infrastructure", "Grow without re-platforming — integrations scale with your loan book and your team."),
        ], minpx=260),
        pad="64px 32px")
    partners_grid = section(
        section_head("Integrations", "Works with the tools you already use",
                     "A selection of platforms FlexiSoft connects with. (Sample partner set — replace with your real integrations.)")
        + grid([
            f'<div style="display:flex; align-items:center; justify-content:center; height:88px; background:{PANEL}; border-radius:14px; font-size:17px; font-weight:600; letter-spacing:-0.01em; color:{FAINT}">{name}</div>'
            for name in ["FINTECHIA", "LendForward", "MicroScale", "GlobalCred", "ApexFunds", "PayBridge", "SignFlow", "DataSync"]
        ], minpx=180, gap=16),
        pad="24px 32px 72px")
    cta = cta_banner("Let's connect your stack.",
                     "Talk to us about the integrations that matter to your business.",
                     btn_primary("Request a Demo", DEMO) + btn_ghost("Contact Us", DEMO))
    return h + benefits + partners_grid + cta

# ---- Case Studies ----------------------------------------------------------
CASES = [
    ("MicroScale Finance", "trend",
     "Manual loan tracking across spreadsheets caused errors and slow month-end reporting.",
     "Migrated the full loan book onto Neptus with automated interest and repayment schedules.",
     "Cut month-end reporting time by 70% and eliminated reconciliation errors."),
    ("LendForward", "clock",
     "Field agents collected client data on paper, delaying approvals by days.",
     "Rolled out DCS for offline data capture that syncs automatically to Neptus.",
     "Reduced approval turnaround from 4 days to under 24 hours."),
    ("ApexFunds", "users",
     "Rapid growth made it hard to keep a clear view of borrower risk and history.",
     "Adopted FlexiSoft client management with a 360° borrower view and KYC records.",
     "Scaled to 3× more active loans with the same operations team."),
]
def case_card(name, icon_name, challenge, solution, result):
    def step(label, text, color):
        return (f'<div style="display:flex; flex-direction:column; gap:4px">'
                f'<span style="font-size:11px; font-weight:700; letter-spacing:0.08em; text-transform:uppercase; color:{color}">{label}</span>'
                f'<p style="margin:0; font-size:13.5px; line-height:20px; color:{MUTED}">{text}</p></div>')
    return (f'<div class="fx-h4" style="{CARD}; display:flex; flex-direction:column; gap:16px">'
            f'<div style="display:flex; align-items:center; gap:12px">{icon(icon_name)}'
            f'<h3 style="margin:0; font-size:17px; font-weight:700; letter-spacing:-0.01em; color:{INK}">{name}</h3></div>'
            f'{sample_tag()}'
            f'{step("Challenge", challenge, FAINT)}'
            f'{step("Solution", solution, ACCENT)}'
            f'{step("Result", result, "#006B52")}</div>')
def case_studies_main():
    h = hero("Case Studies",
             "Proven results for lenders",
             "See how FlexiSoft helps businesses improve operations and grow.")
    cases = section(grid([case_card(*c) for c in CASES], minpx=300, gap=24), pad="56px 32px 32px")
    cta = cta_banner("Want results like these?",
                     "Book a demo and we'll show you what FlexiSoft can do for your loan book.",
                     btn_primary("Request a Demo", DEMO))
    return h + cases + cta

# ---- Resources -------------------------------------------------------------
ARTICLES = [
    ("Operations", "5 admin tasks every micro-lender should automate", "Practical automations that free your team from repetitive work and reduce errors."),
    ("Growth", "How to scale a lending book without scaling headcount", "The systems and workflows that let small teams manage far more active loans."),
    ("Compliance", "A simple framework for KYC and regulatory reporting", "Keep borrower records audit-ready without slowing down origination."),
    ("Product", "Neptus vs DCS: which FlexiSoft tools do you need?", "A quick guide to how the core platform and supporting system fit together."),
    ("Data", "Getting clean data out of the field with offline capture", "Why offline-first data collection matters for agents working on the ground."),
    ("Playbook", "Your first 30 days on FlexiSoft", "A week-by-week plan for a smooth onboarding and fast time-to-value."),
]
def article_card(tag, title, excerpt):
    return (f'<a href="#" class="fx-h4" style="{CARD}; display:flex; flex-direction:column; gap:12px; text-decoration:none">'
            f'<div style="display:flex; align-items:center; gap:8px">'
            f'<span style="font-size:10.5px; font-weight:700; letter-spacing:0.08em; text-transform:uppercase; color:{ACCENT}; background:{TILE}; border-radius:999px; padding:4px 9px">{tag}</span>'
            f'<span style="font-size:10px; font-weight:700; letter-spacing:0.08em; text-transform:uppercase; color:{FAINT}">Sample</span></div>'
            f'<h3 style="margin:4px 0 0; font-size:17px; line-height:23px; font-weight:700; letter-spacing:-0.01em; color:{INK}">{title}</h3>'
            f'<p style="margin:0; font-size:13.5px; line-height:21px; color:{MUTED}">{excerpt}</p>'
            f'<span class="fx-h0" style="margin-top:auto; padding-top:6px; font-size:13.5px; font-weight:600; color:#006B52">Read more →</span></a>')
def resources_main():
    h = hero("Resources",
             "Insights & guides for micro-lenders",
             "Practical articles on lending operations, compliance, and growth. (Sample articles below — swap in your real blog posts.)")
    arts = section(grid([article_card(*a) for a in ARTICLES], minpx=300, gap=22), pad="56px 32px 32px")
    cta = cta_banner("Get the FlexiSoft newsletter",
                     "Ideas and product updates for people building lending businesses.",
                     btn_primary("Request a Demo", DEMO) + btn_ghost("Contact Us", DEMO))
    return h + arts + cta

# ---- About -----------------------------------------------------------------
def about_main():
    h = hero("About",
             "Built for micro-lenders, from the ground up",
             "FlexiSoft has grown from a small startup into a trusted provider of micro-lending software, supporting businesses with reliable technology and strong client service.")
    vm = section(
        grid([
            (f'<div style="{CARD}; display:flex; flex-direction:column; gap:14px">{icon("compass")}'
             f'<h3 style="margin:6px 0 0; font-size:20px; font-weight:700; letter-spacing:-0.015em; color:{INK}">Vision</h3>'
             f'<p style="margin:0; font-size:14.5px; line-height:23px; color:{MUTED}">To become the leading micro-loan software provider in South Africa and expand across Africa.</p></div>'),
            (f'<div style="{CARD}; display:flex; flex-direction:column; gap:14px">{icon("target")}'
             f'<h3 style="margin:6px 0 0; font-size:20px; font-weight:700; letter-spacing:-0.015em; color:{INK}">Mission</h3>'
             f'<p style="margin:0; font-size:14.5px; line-height:23px; color:{MUTED}">To stay at the forefront of technology while delivering exceptional client service.</p></div>'),
        ], minpx=320, gap=24),
        pad="56px 32px")
    values = section(
        section_head("Values", "What we stand for")
        + grid([
            value_card("shield", "Reliability", "Dependable technology and support our clients can build their business on."),
            value_card("heart", "Honesty", "Straightforward relationships, clear communication, and no surprises."),
            value_card("users", "Client-first approach", "We adapt to your processes and success — not the other way around."),
        ], minpx=260),
        pad="16px 32px 72px")
    cta = cta_banner("Let's grow together.",
                     "Partner with a team that's invested in your success.",
                     btn_primary("Request a Demo", DEMO) + btn_ghost("Contact Us", DEMO))
    return h + vm + values + cta

# ---- Contact ---------------------------------------------------------------
def field(label, name, input_html):
    return (f'<label style="display:flex; flex-direction:column; gap:7px">'
            f'<span style="font-size:13px; font-weight:600; color:{INK}">{label}</span>{input_html}</label>')
INPUT = (f'style="height:46px; padding:0 14px; border-radius:10px; border:1px solid #CFD5D3; background:#FFFFFF; '
         f'font:inherit; font-size:14.5px; color:{INK}; width:100%"')
def contact_main():
    h = hero("Contact",
             "Let's build the right solution for your business.",
             "Tell us what you need — a demo, more information, training, or support — and our team will be in touch.")
    form = f'''<div style="display:grid; grid-template-columns:repeat(auto-fit, minmax(300px, 1fr)); gap:40px; align-items:start">
      <form action="#" method="post" style="display:flex; flex-direction:column; gap:18px; background:#FFFFFF; border:1px solid {LINE}; border-radius:16px; padding:clamp(24px, 3vw, 36px); box-shadow:0 1px 3px rgba(17,24,39,0.05)">
        <div style="display:grid; grid-template-columns:repeat(auto-fit, minmax(200px, 1fr)); gap:18px">
          {field("Name", "name", f'<input type="text" name="name" autocomplete="name" required {INPUT}>')}
          {field("Company", "company", f'<input type="text" name="company" autocomplete="organization" {INPUT}>')}
          {field("Email", "email", f'<input type="email" name="email" autocomplete="email" required {INPUT}>')}
          {field("Phone", "phone", f'<input type="tel" name="phone" autocomplete="tel" {INPUT}>')}
        </div>
        {field("Request Type", "request_type", f'<select name="request_type" {INPUT}><option value="demo">Demo</option><option value="info">Info</option><option value="training">Training</option><option value="support">Support</option></select>')}
        {field("Message", "message", f'<textarea name="message" rows="4" style="padding:12px 14px; border-radius:10px; border:1px solid #CFD5D3; background:#FFFFFF; font:inherit; font-size:14.5px; color:{INK}; width:100%; resize:vertical"></textarea>')}
        <button type="submit" class="fx-h2" style="align-self:flex-start; display:inline-flex; align-items:center; justify-content:center; height:46px; padding:0 28px; border-radius:999px; background:{GREEN}; color:{DARK}; font-size:15px; font-weight:700; border:none; cursor:pointer">Submit Request</button>
        <p style="margin:0; font-size:12px; line-height:18px; color:{FAINT}">This form is a front-end placeholder. Drop in your Zoho Forms embed code here, or wire it to a handler (e.g. Cloudflare Pages Forms) to start receiving submissions.</p>
      </form>
      <aside style="display:flex; flex-direction:column; gap:20px">
        <div style="{CARD}; display:flex; flex-direction:column; gap:8px">
          <span style="{EYEBROW}">Prefer email?</span>
          <a href="mailto:hello@flexisoft.co.za" class="fx-h0" style="font-size:16px; font-weight:600; color:#006B52; text-decoration:none">hello@flexisoft.co.za</a>
        </div>
        <div style="{CARD}; display:flex; flex-direction:column; gap:10px">
          <span style="{EYEBROW}">What happens next</span>
          {check_list(["We review your request", "A specialist reaches out within 1 business day", "We tailor a demo to your business"])}
        </div>
      </aside>
    </div>'''
    return h + section(form, pad="56px 32px 80px")

# ============================================================ WRITE PAGES
PAGES = {
    "solutions.html":    ("FlexiSoft — Solutions", "A complete micro-lending software solution: the Neptus core platform and the DCS supporting system.", "Solutions", solutions_main),
    "partners.html":     ("FlexiSoft — Partners", "FlexiSoft integrates with leading platforms to create a powerful, connected ecosystem.", "Partners", partners_main),
    "case-studies.html": ("FlexiSoft — Case Studies", "See how FlexiSoft helps micro-lenders improve operations and grow.", "Case Studies", case_studies_main),
    "resources.html":    ("FlexiSoft — Resources", "Insights and guides on micro-lending operations, compliance, and growth.", "Resources", resources_main),
    "about.html":        ("FlexiSoft — About", "FlexiSoft is a trusted provider of micro-lending software, built for reliability and client service.", "About", about_main),
    "contact.html":      ("FlexiSoft — Contact", "Request a demo, more information, training, or support from the FlexiSoft team.", "Contact", contact_main),
}

for fname, (title, desc, active, builder) in PAGES.items():
    html = page(title, desc, active, builder())
    with open(os.path.join(DIST, fname), "w", encoding="utf-8") as f:
        f.write(html)
    print(f"wrote {fname:22s} {len(html):>7,d} bytes")

# ============================================================ PATCH HOME PAGE
idx_path = os.path.join(DIST, "index.html")
idx = open(idx_path, encoding="utf-8").read()
# swap header + footer for the shared, linked versions
idx = re.sub(r'<header\b.*?</header>', lambda m: header(None), idx, count=1, flags=re.S)
idx = re.sub(r'<footer\b.*?</footer>', lambda m: footer(), idx, count=1, flags=re.S)
# route on-page demo/CTA buttons to the contact page
idx = idx.replace('href="#cta"', 'href="contact.html"')
# product "Learn More" links -> solutions deep-dive sections (first Neptus, second DCS)
_lm = {"n": 0}
def _lm_repl(m):
    _lm["n"] += 1
    return f'href="solutions.html#{"neptus" if _lm["n"] == 1 else "dcs"}"'
idx = re.sub(r'href="#top"(?=[^>]*>Learn More)', _lm_repl, idx)
with open(idx_path, "w", encoding="utf-8") as f:
    f.write(idx)
print("patched index.html (shared header/footer + links)")
print("remaining #cta hrefs in index:", idx.count('href="#cta"'), "| Learn More rewrites:", _lm["n"])
