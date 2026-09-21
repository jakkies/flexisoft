#!/usr/bin/env python3
"""
Build a COPY of the site into v2/ with the content from
"FlexiSoft Website edits.docx" applied.

- Reuses the component library + design tokens from build_pages.py (imported
  without side effects).
- 5-page structure: Home, Solutions, Partners, About, Contact
  (Case Studies + Resources are dropped per the brief).
- Home is transformed from the current index.html so its bespoke hero
  dashboard mock-up and section styling are preserved verbatim.

Run from the repo root:  python3 build_v2.py
"""
import os, re, shutil
import build_pages as bp

HERE = os.path.dirname(os.path.abspath(__file__))
SRC  = HERE            # current (v1) site lives at the repo root
OUT  = os.path.join(HERE, "v2")
EMAIL = "hello@flexisoft.co.za"          # <- placeholder address, confirm/replace
MAILTO = f"mailto:{EMAIL}"
DEMO = "contact.html"

# ---- extra icons used by the new content --------------------------------
bp.ICONS.update({
    "card":   '<rect x="2" y="5" width="20" height="14" rx="2"/><line x1="2" y1="10" x2="22" y2="10"/>',
    "search": '<circle cx="11" cy="11" r="7"/><line x1="21" y1="21" x2="16.65" y2="16.65"/>',
    "umbrella":'<path d="M12 12v7a2 2 0 0 0 4 0"/><path d="M2 12a10 10 0 0 1 20 0Z"/>',
    "message":'<path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/>',
    "lock":   '<rect x="4" y="11" width="16" height="10" rx="2"/><path d="M8 11V7a4 4 0 0 1 8 0v4"/>',
    "file":   '<path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/>',
    "sliders":'<line x1="4" y1="21" x2="4" y2="14"/><line x1="4" y1="10" x2="4" y2="3"/><line x1="12" y1="21" x2="12" y2="12"/><line x1="12" y1="8" x2="12" y2="3"/><line x1="20" y1="21" x2="20" y2="16"/><line x1="20" y1="12" x2="20" y2="3"/><line x1="1" y1="14" x2="7" y2="14"/><line x1="9" y1="8" x2="15" y2="8"/><line x1="17" y1="16" x2="23" y2="16"/>',
    "cloud":  '<path d="M17.5 19a4.5 4.5 0 1 0 0-9h-1.26A8 8 0 1 0 4 16.25"/>',
    "fingerprint":'<path d="M2 12C2 6.5 6.5 2 12 2a10 10 0 0 1 8 4"/><path d="M5 19.5C5.5 18 6 15 6 12a6 6 0 0 1 .34-2"/><path d="M17.29 21.02c.12-.6.43-2.3.5-3.02"/><path d="M12 10a2 2 0 0 0-2 2c0 1.02-.1 2.51-.26 4"/><path d="M8.65 22c.21-.66.45-1.32.57-2"/><path d="M14 13.12c0 2.38 0 6.38-1 8.88"/><path d="M2 16h.01"/><path d="M21.8 16c.2-2 .131-5.354 0-6"/><path d="M8.8 7.5a6 6 0 0 1 9.2 5v1.5"/>',
})

# ---- shared chrome (5-page nav) -----------------------------------------
NAV = [("Solutions", "solutions.html"), ("Partners", "partners.html"),
       ("About", "about.html"), ("Contact", "contact.html")]

def header_v2(active):
    links = "\n            ".join(
        f'<a href="{href}" class="nav-link{" is-active" if label == active else ""}">{label}</a>'
        for label, href in NAV)
    return f'''<header style="position:sticky; top:0; z-index:20; background:rgba(255,255,255,0.92); backdrop-filter:blur(10px); border-bottom:1px solid #E5E9E8">
    <div class="nav-bar">
      <a href="index.html" class="brand" aria-label="FlexiSoft — home">
        <img src="assets/flexisoft-logo.svg" alt="FlexiSoft" style="height:22px; width:auto; display:block">
      </a>
      <input type="checkbox" id="nav-toggle" class="nav-toggle" aria-label="Toggle navigation menu">
      <label for="nav-toggle" class="nav-burger" aria-label="Menu"><svg class="fx-bars" width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" aria-hidden="true"><line x1="3" y1="6" x2="21" y2="6"/><line x1="3" y1="12" x2="21" y2="12"/><line x1="3" y1="18" x2="21" y2="18"/></svg><svg class="fx-x" width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" aria-hidden="true"><line x1="6" y1="6" x2="18" y2="18"/><line x1="6" y1="18" x2="18" y2="6"/></svg></label>
      <div class="nav-menu">
        <nav class="nav-links">
            {links}
        </nav>
        <div class="nav-actions">
          <a href="#" class="nav-btn nav-btn-ghost">Portal Log in</a>
          <a href="contact.html" class="nav-btn nav-btn-solid">Book a Demo</a>
        </div>
      </div>
    </div>
  </header>'''

def _fcol(title, links):
    ls = "\n          ".join(
        f'<a href="{h}" class="fx-h0" style="font-size:13.5px; color:#6B7472; text-decoration:none">{l}</a>'
        for l, h in links)
    return (f'<div style="display:flex; flex-direction:column; gap:12px">\n'
            f'          <span style="font-size:11px; font-weight:700; letter-spacing:0.12em; text-transform:uppercase; color:#111827">{title}</span>\n'
            f'          {ls}\n        </div>')

def footer_v2():
    cols = "\n      ".join([
        _fcol("Platform", [("Solutions", "solutions.html"), ("Neptus", "solutions.html#neptus"), ("DCS", "solutions.html#dcs")]),
        _fcol("Company",  [("About", "about.html"), ("Partners", "partners.html"), ("Contact", "contact.html")]),
        _fcol("Get started", [("Book a Demo", "contact.html"), ("Email us", MAILTO)]),
    ])
    return f'''<footer style="border-top:1px solid #E5E9E8; background:#FFFFFF">
    <div style="max-width:1200px; margin:0 auto; padding:56px 32px 40px; display:grid; grid-template-columns:repeat(auto-fit, minmax(170px, 1fr)); gap:40px">
      <div style="display:flex; flex-direction:column; gap:14px; max-width:34ch">
        <img src="assets/flexisoft-logo.svg" alt="FlexiSoft" style="height:22px; width:auto; align-self:flex-start; display:block">
        <p style="margin:0; font-size:13.5px; line-height:21px; color:#6B7472">The leading micro-lending software platform in South Africa.</p>
      </div>
      {cols}
    </div>
    <div style="border-top:1px solid #E5E9E8">
      <div style="max-width:1200px; margin:0 auto; padding:20px 32px; display:flex; flex-wrap:wrap; align-items:center; justify-content:space-between; gap:12px 24px">
        <span style="font-size:12.5px; color:#9CA5A2">© 2026 FlexiSoft. All rights reserved.</span>
        <div style="display:flex; flex-wrap:wrap; gap:24px">
          <a href="#" class="fx-h0" style="font-size:12.5px; color:#9CA5A2; text-decoration:none">Privacy Policy</a>
          <a href="#" class="fx-h0" style="font-size:12.5px; color:#9CA5A2; text-decoration:none">Terms of Service</a>
        </div>
      </div>
    </div>
  </footer>'''

# make bp.page() use the v2 chrome (page() resolves header/footer at call time)
bp.header = header_v2
bp.footer = footer_v2

INK, MUTED, ACCENT, LINE, PANEL, TILE = bp.INK, bp.MUTED, bp.ACCENT, bp.LINE, bp.PANEL, bp.TILE

# ---- small local helpers -------------------------------------------------
def area_head(icon_name, title, intro=None):
    intro_html = f'<p style="{bp.LEAD}">{intro}</p>' if intro else ''
    return (f'<div style="display:flex; flex-direction:column; gap:14px">'
            f'<div style="display:flex; align-items:center; gap:14px">{bp.icon(icon_name)}'
            f'<h2 style="margin:0; font-size:clamp(22px, 2.6vw, 28px); line-height:1.2; font-weight:700; letter-spacing:-0.02em; color:{INK}">{title}</h2></div>'
            f'{intro_html}</div>')

def partner_card(title, bullets=None, desc=None):
    body = ''
    if desc:
        body = f'<p style="margin:0; font-size:13.5px; line-height:21px; color:{MUTED}">{desc}</p>'
    if bullets:
        body = bp.check_list(bullets)
    return (f'<div class="fx-h4" style="{bp.CARD}; display:flex; flex-direction:column; gap:14px">'
            f'<h3 style="margin:0; font-size:16px; font-weight:700; letter-spacing:-0.01em; color:{INK}">{title}</h3>'
            f'{body}</div>')

def hero_with_image(eyebrow_text, title, subhead, img, alt, cta_html="", img_max=620):
    cta = f'<div style="display:flex; flex-wrap:wrap; gap:12px; padding-top:8px">{cta_html}</div>' if cta_html else ''
    left = (f'<div style="display:flex; flex-direction:column; gap:16px; max-width:520px">'
            f'{bp.eyebrow(eyebrow_text)}'
            f'<h1 style="margin:0; font-size:clamp(30px, 4vw, 46px); line-height:1.1; font-weight:800; letter-spacing:-0.025em; color:{INK}; text-wrap:balance">{title}</h1>'
            f'<p style="margin:0; font-size:16px; line-height:26px; color:#4B5350; max-width:52ch; text-wrap:pretty">{subhead}</p>'
            f'{cta}</div>')
    visual = (f'<div style="display:flex; justify-content:center">'
              f'<img src="{img}" alt="{alt}" style="width:100%; max-width:{img_max}px; height:auto; display:block"></div>')
    return (f'<section style="padding:40px 32px 0">'
            f'<div style="max-width:1200px; margin:0 auto; background:{PANEL}; border-radius:24px; padding:clamp(36px, 5vw, 72px)">'
            f'<div style="display:grid; grid-template-columns:repeat(auto-fit, minmax(320px, 1fr)); gap:48px; align-items:center">'
            f'{left}{visual}</div></div></section>')

# =========================================================================
# SOLUTIONS
# =========================================================================
def solutions_v2():
    left = (f'<div style="display:flex; flex-direction:column; gap:16px; max-width:520px">'
            f'{bp.eyebrow("Solutions")}'
            f'<h1 style="margin:0; font-size:clamp(30px, 4vw, 46px); line-height:1.1; font-weight:800; letter-spacing:-0.025em; color:{INK}; text-wrap:balance">Complete micro-lending platform solutions</h1>'
            f'<p style="margin:0; font-size:16px; line-height:26px; color:#4B5350; max-width:52ch; text-wrap:pretty">One powerful, secure platform to run your entire micro-lending operation — from loan origination to collections.</p>'
            f'<div style="display:flex; flex-wrap:wrap; gap:12px; padding-top:8px">{bp.btn_primary("Book a Demo", DEMO)}</div></div>')
    visual = ('<div style="display:flex; justify-content:center">'
              '<img src="assets/core-platfom.png" alt="FlexiSoft Core Platform — loan pipeline dashboard" '
              'style="width:100%; max-width:620px; height:auto; display:block"></div>')
    h = (f'<section style="padding:40px 32px 0">'
         f'<div style="max-width:1200px; margin:0 auto; background:{PANEL}; border-radius:24px; padding:clamp(36px, 5vw, 72px)">'
         f'<div style="display:grid; grid-template-columns:repeat(auto-fit, minmax(320px, 1fr)); gap:48px; align-items:center">'
         f'{left}{visual}</div></div></section>')

    def group(num, title, cards):
        return (f'<div style="display:flex; flex-direction:column; gap:20px">'
                f'<h3 style="margin:0; font-size:13px; font-weight:700; letter-spacing:0.08em; text-transform:uppercase; color:{ACCENT}">{num}. {title}</h3>'
                f'{bp.grid(cards, minpx=280)}</div>')

    g1 = group(1, "Core Loan &amp; Business Management", [
        bp.value_card("sliders", "Customisable Loan Modules", "Configure custom loan products, loan types, borrowing limits, and interest rates tailored to your business rules."),
        bp.value_card("lock", "Granular User Permissions &amp; Control", "Security-conscious user management ensures staff access is restricted by role. System owners retain full override and document management control."),
        bp.value_card("file", "Document Management &amp; Scanning", "Upload, attach, and scan essential customer documentation directly into client profiles — including IDs, payslips, and bank statements."),
    ])
    g2 = group(2, "Advanced Security &amp; Fraud Prevention", [
        bp.value_card("fingerprint", "Biometric Fingerprint Module", "Eliminate ghost loans and internal fraud by requiring client fingerprint verification before granting loans. Secure staff logins via fingerprint scanners and print fingerprint images directly onto contracts."),
        bp.value_card("edit", "Digital &amp; SMS E-Signatures", "Eliminate paper costs and printing delays. Link a tablet or mobile device for Advanced Electronic Signatures, or send loan contracts and mandates via SMS for remote signing."),
    ])
    g3 = group(3, "Customer Communication", [
        bp.value_card("message", "SMS Messaging", "Send single or batch SMS notifications directly from the system."),
    ])

    neptus = (f'<section id="neptus" style="padding:56px 32px; background:{PANEL}; scroll-margin-top:88px">'
              f'<div style="max-width:1200px; margin:0 auto; display:flex; flex-direction:column; gap:40px">'
              f'<div style="display:flex; flex-direction:column; gap:14px">{bp.eyebrow("Core platform")}'
              f'<h2 style="{bp.H2}">Neptus — Complete Micro-Lending Platform</h2>'
              f'<p style="{bp.LEAD}; max-width:64ch">FlexiSoft delivers an all-in-one management platform designed to automate loan processing, payment collections, fraud prevention, and client communication.</p></div>'
              f'{g1}{g2}{g3}</div></section>')

    dcs = (f'<section id="dcs" style="padding:56px 32px; scroll-margin-top:88px">'
           f'<div style="max-width:1200px; margin:0 auto; display:flex; flex-direction:column; gap:14px">'
           f'<div style="display:flex; align-items:center; gap:10px">{bp.eyebrow("Supporting system")}'
           f'<span style="font-size:10px; font-weight:700; letter-spacing:0.06em; text-transform:uppercase; color:#8A6D00; background:#FBEFC6; border-radius:999px; padding:3px 8px">Coming soon</span></div>'
           f'<h2 style="{bp.H2}">DCS</h2>'
           f'<p style="{bp.LEAD}; max-width:60ch">A supporting system to enhance your operations with additional tools and automation. Coming soon.</p></div></section>')

    cta = bp.cta_banner("Ready to see FlexiSoft in action?",
                        "Book a personalised demo and we'll show you how FlexiSoft fits your lending business.",
                        bp.btn_primary("Book a Demo", DEMO) + bp.btn_ghost("Email us", MAILTO))
    return h + neptus + dcs + cta

# =========================================================================
# PARTNERS
# =========================================================================
def partners_v2():
    h = hero_with_image("Partners", "Integrated with the industry's leading providers",
                        "FlexiSoft is integrated with the following leading service providers in the South African micro-lending industry.",
                        "assets/FlexiSoft-Hero-Partners.png",
                        "FlexiSoft partner analytics — portfolio and scheduled reports",
                        bp.btn_primary("Book a Demo", DEMO), img_max=640)

    pay = bp.section(
        area_head("card", "Payment System Integration",
                  "Our platform features integration with South Africa's premier payment processing engines across AEDO, NAEDO, MPS, and DebiCheck networks to ensure effortless collection and payout management:")
        + '<div style="height:24px"></div>'
        + bp.grid([
            partner_card("ALLPS / Amplifin", bullets=[
                "Social Grant EFT, TT1, and TT3 mandate creations.",
                "Electronic document signing for Amplifin documents.",
                "Direct mandate and instalment amendments, cancellations, and batch receipting.",
                "Client credits and eWallet creation with card issuance."]),
            partner_card("SureSystems / SureDebit", bullets=[
                "Social Grant EFT, TT1, and TT3 mandate creations.",
                "Electronic mandate signing and real-time amendments / cancellations.",
                "Client credits via Cash Access cards and instant transfers.",
                "Direct-to-client immediate payments via Neptus / SureDebit integration."]),
            partner_card("NuPay", bullets=[
                "Complete NuCard integration (payouts, re-issues, balance checks, and deductions).",
                "Full mandate management, amendments, cancellations, and batch receipting.",
                "Cash Access card creation and instant credit transfers."]),
            partner_card("Realpay", bullets=[
                "Complete payment integration with full mandate management, amendments, cancellations, and batch receipting.",
                "Instant credit transfers and Cash Access card creation.",
                "Payouts, balance checks, and deduction management."]),
        ], minpx=320),
        pad="64px 32px")

    bureau = bp.section(
        area_head("search", "Bureau Integration &amp; Credit Vetting")
        + '<div style="height:24px"></div>'
        + bp.grid([
            partner_card("XDS (Xpert Decision Systems)", desc="Direct integration with one of South Africa's premier credit bureaus, enabling instant credit scoring and detailed credit report retrieval at affordable rates directly within the loan workflow."),
            partner_card("Finintel", desc="Integrated financial intelligence and credit risk assessment solutions to streamline applicant vetting."),
        ], minpx=320),
        pad="64px 32px", bg=PANEL)

    insurance = bp.section(
        area_head("umbrella", "Loan Insurance Partners",
                  "Avoid lending risks and offer complete protection for your loans through seamless integration with leading credit life insurance providers:")
        + '<div style="height:24px"></div>'
        + bp.grid([
            partner_card("UIA (Universal Insurance Administrators)", desc="Embedded insurance processing to easily add credit life coverage to loan agreements."),
            partner_card("Groups R Us", desc="Integrated credit insurance administration to safeguard both lender and borrower in the event of unforeseen client circumstances."),
        ], minpx=320),
        pad="64px 32px")

    sms = bp.section(
        area_head("message", "SMS Portal &amp; Client Communication")
        + '<div style="height:24px"></div>'
        + bp.grid([
            partner_card("Direct SMS Messaging", desc="Send single or bulk automated SMS notifications directly from the platform to streamline operations."),
            partner_card("Remote Document E-Signing", desc="Enable borrowers to securely review and sign loan contracts and mandates via SMS, eliminating paper costs and reducing turn-around time."),
        ], minpx=320),
        pad="64px 32px", bg=PANEL)

    cta = bp.cta_banner("Let's connect your stack.",
                        "Talk to us about the integrations that matter to your lending business.",
                        bp.btn_primary("Book a Demo", DEMO) + bp.btn_ghost("Email us", MAILTO))
    return h + pay + bureau + insurance + sms + cta

# =========================================================================
# ABOUT
# =========================================================================
def about_v2():
    left = (f'<div style="display:flex; flex-direction:column; gap:16px; max-width:520px">'
            f'{bp.eyebrow("About")}'
            f'<h1 style="margin:0; font-size:clamp(30px, 4vw, 46px); line-height:1.1; font-weight:800; letter-spacing:-0.025em; color:{INK}; text-wrap:balance">About FlexiSoft</h1>'
            f'<p style="margin:0; font-size:16px; line-height:26px; color:#4B5350; max-width:52ch; text-wrap:pretty">Welcome to FlexiSoft, the leading micro-lending software platform in South Africa.</p></div>')
    visual = ('<div style="display:flex; justify-content:center">'
              '<img src="assets/FlexiSoft-Hero-About.png" alt="FlexiSoft field capture — offline-first data collection" '
              'style="width:100%; max-width:460px; height:auto; display:block"></div>')
    h = (f'<section style="padding:40px 32px 0">'
         f'<div style="max-width:1200px; margin:0 auto; background:{PANEL}; border-radius:24px; padding:clamp(36px, 5vw, 72px)">'
         f'<div style="display:grid; grid-template-columns:repeat(auto-fit, minmax(320px, 1fr)); gap:48px; align-items:center">'
         f'{left}{visual}</div></div></section>')

    intro = bp.section(
        '<div style="max-width:760px; display:flex; flex-direction:column; gap:18px">'
        f'<p style="margin:0; font-size:16px; line-height:26px; color:#4B5350">We have been at the forefront of the micro-lending software industry, empowering lenders of all sizes — from single-location branch offices and growing enterprise groups to established banking institutions.</p>'
        f'<p style="margin:0; font-size:16px; line-height:26px; color:#4B5350">Our mission is to simplify micro-lending operations using cutting-edge, secure, and intuitive technology. Built from the ground up with compliance, credit bureau integration, and operational stability in mind, FlexiSoft gives business owners full control over their lending ecosystem — anytime, anywhere.</p>'
        '</div>', pad="56px 32px")

    why = bp.section(
        bp.section_head("Why FlexiSoft", "Why choose FlexiSoft?")
        + bp.grid([
            bp.value_card("cloud", "Cloud &amp; Global Accessibility", "Login from anywhere to manage clients, loan settings, and reports seamlessly."),
            bp.value_card("trend", "Scalable Architecture", "Designed to cater to all business sizes, whether you operate a small office or a large-scale institution."),
            bp.value_card("shield", "Built for Compliance &amp; Security", "Built with strict compliance and top South African credit bureaus in mind, featuring custom user permissions and advanced biometric security."),
            bp.value_card("sliders", "Complete Flexibility", "FlexiSoft lets you fully configure loan products, types, limits, interest rates, and document templates to suit your specific business model."),
        ], minpx=250),
        pad="16px 32px 40px")

    values = bp.section(
        bp.section_head("Values", "Our core values")
        + bp.grid([
            bp.value_card("shield", "Reliability", "We build stable cloud systems you can trust to keep your branches running smoothly without unexpected disruptions."),
            bp.value_card("heart", "Honesty", "We operate with complete transparency in our relationships, software capabilities, and business practices."),
            bp.value_card("users", "Client-First Approach", "Your operational success is our priority. We listen to your feedback, adapt to your needs, and provide support whenever assistance is needed."),
        ], minpx=260),
        pad="16px 32px 72px")

    cta = bp.cta_banner("Let's grow together.",
                        "Partner with a team invested in your success.",
                        bp.btn_primary("Book a Demo", DEMO) + bp.btn_ghost("Email us", MAILTO))
    return h + intro + why + values + cta

# =========================================================================
# CONTACT
# =========================================================================
def contact_v2():
    h = hero_with_image("Contact", "Let's build the right solution for your business.",
                        "Partner with us to create an environment that perfectly aligns with your business needs.",
                        "assets/FlexiSoft-Hero-Contact.png",
                        "FlexiSoft onboarding schedule and demo booking",
                        img_max=640)
    IN = f'style="height:46px; padding:0 14px; border-radius:10px; border:1px solid #CFD5D3; background:#FFFFFF; font:inherit; font-size:14.5px; color:{INK}; width:100%"'
    def field(label, inp):
        return (f'<label style="display:flex; flex-direction:column; gap:7px">'
                f'<span style="font-size:13px; font-weight:600; color:{INK}">{label}</span>{inp}</label>')
    form = f'''<div style="display:grid; grid-template-columns:repeat(auto-fit, minmax(300px, 1fr)); gap:40px; align-items:start">
      <form action="#" method="post" style="display:flex; flex-direction:column; gap:18px; background:#FFFFFF; border:1px solid {LINE}; border-radius:16px; padding:clamp(24px, 3vw, 36px); box-shadow:0 1px 3px rgba(17,24,39,0.05)">
        <div style="display:grid; grid-template-columns:repeat(auto-fit, minmax(200px, 1fr)); gap:18px">
          {field("Name", f'<input type="text" name="name" autocomplete="name" required {IN}>')}
          {field("Company", f'<input type="text" name="company" autocomplete="organization" {IN}>')}
          {field("Email", f'<input type="email" name="email" autocomplete="email" required {IN}>')}
          {field("Phone", f'<input type="tel" name="phone" autocomplete="tel" {IN}>')}
        </div>
        {field("Request Type", f'<select name="request_type" {IN}><option value="demo">Demo</option><option value="info">Info</option><option value="training">Training</option><option value="support">Support</option></select>')}
        {field("Message", f'<textarea name="message" rows="4" style="padding:12px 14px; border-radius:10px; border:1px solid #CFD5D3; background:#FFFFFF; font:inherit; font-size:14.5px; color:{INK}; width:100%; resize:vertical"></textarea>')}
        <button type="submit" class="fx-h2" style="align-self:flex-start; display:inline-flex; align-items:center; justify-content:center; height:46px; padding:0 28px; border-radius:999px; background:#00BD8E; color:#052416; font-size:15px; font-weight:700; border:none; cursor:pointer">Submit Request</button>
      </form>
      <aside style="display:flex; flex-direction:column; gap:20px">
        <div style="{bp.CARD}; display:flex; flex-direction:column; gap:8px">
          <span style="{bp.EYEBROW}">Prefer email?</span>
          <a href="{MAILTO}" class="fx-h0" style="font-size:16px; font-weight:600; color:#006B52; text-decoration:none">{EMAIL}</a>
        </div>
        <div style="{bp.CARD}; display:flex; flex-direction:column; gap:10px">
          <span style="{bp.EYEBROW}">What happens next</span>
          {bp.check_list(["We review your request", "A specialist reaches out within 1 business day", "We tailor a demo to your business"])}
        </div>
      </aside>
    </div>'''
    return h + bp.section(form, pad="56px 32px 80px")

# =========================================================================
# HOME — transform the existing index.html so its bespoke markup is kept
# =========================================================================
def _step(num, title, body):
    return (f'<div style="display:flex; flex-direction:column; gap:10px; max-width:34ch">'
            f'<span style="font-size:13px; font-weight:700; letter-spacing:0.06em; color:{ACCENT}">{num}</span>'
            f'<h3 style="margin:0; font-size:17px; line-height:24px; font-weight:700; letter-spacing:-0.01em; color:{INK}">{title}</h3>'
            f'<p style="margin:0; font-size:13.5px; line-height:22px; color:{MUTED}">{body}</p></div>')

def build_home():
    s = open(os.path.join(SRC, "index.html"), encoding="utf-8").read()
    n = {"ok": 0, "warn": []}
    def rep(old, new, label, count=1):
        nonlocal s
        if s.count(old) < count:
            n["warn"].append(label); return
        s = s.replace(old, new, count); n["ok"] += 1

    # header + footer
    s = re.sub(r'<header\b.*?</header>', lambda m: header_v2(None), s, count=1, flags=re.S)
    s = re.sub(r'<footer\b.*?</footer>', lambda m: footer_v2(), s, count=1, flags=re.S)

    # <title> + description
    s = re.sub(r'<title>.*?</title>', '<title>FlexiSoft — Micro-Lending Software for South African Lenders</title>', s, count=1)
    s = re.sub(r'(<meta name="description" content=")[^"]*(">)',
               r'\1Focus on your customers while our technology handles the complexity of your micro-lending business — the leading micro-lending platform in South Africa.\2', s, count=1)

    # Hero: rebuild with the new headline, CTAs (Book a Demo + Email us) and the hero image
    hero_new = '''    <section data-screen-label="Hero" style="padding:40px 32px 0">
      <div style="max-width:1200px; margin:0 auto; background:#F4F7F6; border-radius:24px; padding:clamp(36px, 5vw, 72px)">
        <div style="display:grid; grid-template-columns:repeat(auto-fit, minmax(320px, 1fr)); gap:48px; align-items:center">
          <div style="display:flex; flex-direction:column; gap:24px; max-width:520px">
            <h1 style="margin:0; font-size:clamp(28px, 3.4vw, 42px); line-height:1.14; font-weight:800; letter-spacing:-0.03em; color:#111827; text-wrap:balance">Focus on your customers while our technology handles the complexity of your micro-lending business.</h1>
            <div style="display:flex; flex-wrap:wrap; gap:12px; padding-top:4px">
              <a href="contact.html" style="display:inline-flex; align-items:center; justify-content:center; height:46px; padding:0 26px; border-radius:999px; background:#00BD8E; color:#052416; font-size:15px; font-weight:700; text-decoration:none" class="fx-h2">Book a Demo</a>
              <a href="__MAILTO__" style="display:inline-flex; align-items:center; justify-content:center; height:46px; padding:0 26px; border-radius:999px; background:#FFFFFF; border:1px solid #CFD5D3; color:#111827; font-size:15px; font-weight:600; text-decoration:none" class="fx-h3">Email us</a>
            </div>
          </div>
          <div style="display:flex; justify-content:center">
            <img src="assets/FlexiSoft-Hero-Home.png" alt="FlexiSoft lending dashboard — approval rate and disbursements" style="width:100%; max-width:640px; height:auto; display:block">
          </div>
        </div>
      </div>
    </section>'''.replace("__MAILTO__", MAILTO)
    s2 = re.sub(r'    <section data-screen-label="Hero".*?</section>', lambda m: hero_new, s, count=1, flags=re.S)
    if s2 != s: n["ok"] += 1
    else: n["warn"].append("hero")
    s = s2

    # trust bar
    rep("Trusted by forward-thinking institutions",
        "Powered by South Africa's Leading Financial &amp; Payment Partners", "trust-copy")
    partners = ["Amplifin", "SureSystems", "NuPay", "UIA", "Groups R Us", "XDS Finintel", "Realpay", "SMS Portal"]
    spans = "\n          ".join(
        f'<span style="font-size:17px; font-weight:600; letter-spacing:-0.01em; color:#CFD5D3">{p}</span>'
        for p in partners)
    s2 = re.sub(r'(gap:28px 48px">)\s*(?:<span[^>]*>[^<]*</span>\s*)+',
                lambda m: m.group(1) + "\n          " + spans + "\n        ", s, count=1, flags=re.S)
    if s2 != s: n["ok"] += 1
    else: n["warn"].append("trust-partners")
    s = s2

    # value proposition subheading + card 4 body
    rep("Focus on your borrowers while our technology handles the complexity of your lending lifecycle.",
        "Focus on your customers while our technology handles the complexity of your micro-lending business.", "valueprop-sub")
    rep("99.9% uptime with bank-grade security and automated data backups.",
        "99.9% uptime with a dedicated support team and automated data backups.", "card4")

    # Solutions Overview (replace the whole Products section)
    products_new = f'''    <section data-screen-label="Solutions Overview" style="padding:56px 32px">
      <div style="max-width:1200px; margin:0 auto; display:flex; flex-direction:column; gap:44px">
        <div style="display:flex; flex-direction:column; gap:14px; align-items:center; text-align:center">
          <h2 style="margin:0; font-size:clamp(26px, 3.2vw, 34px); line-height:1.2; font-weight:700; letter-spacing:-0.02em; color:#111827">Our Solutions</h2>
          <p style="margin:0; font-size:15px; line-height:24px; color:#6B7472; max-width:56ch; text-wrap:pretty">With built-in expertise and integrated partner solutions, your success is almost guaranteed.</p>
        </div>
        <div style="display:grid; grid-template-columns:repeat(auto-fit, minmax(320px, 1fr)); gap:24px">
          <div style="background:#F4F7F6; border-radius:16px; padding:clamp(26px, 3vw, 40px); display:flex; flex-direction:column; gap:14px; min-height:220px">
            <span style="font-size:11px; font-weight:700; letter-spacing:0.12em; text-transform:uppercase; color:#00A17A">Core Lending Platform</span>
            <h3 style="margin:0; font-size:24px; line-height:32px; font-weight:700; letter-spacing:-0.015em; color:#111827">Neptus</h3>
            <p style="margin:0; font-size:14.5px; line-height:23px; color:#4B5350; max-width:48ch">Manage loans, clients, and operations in one powerful system.</p>
            <a href="solutions.html#neptus" style="margin-top:auto; display:inline-flex; align-items:center; gap:7px; align-self:flex-start; font-size:14px; font-weight:600; color:#006B52; text-decoration:underline" class="fx-h0">Learn More →</a>
          </div>
          <div style="background:#F4F7F6; border-radius:16px; padding:clamp(26px, 3vw, 40px); display:flex; flex-direction:column; gap:14px; min-height:220px">
            <div style="display:flex; align-items:center; gap:10px">
              <span style="font-size:11px; font-weight:700; letter-spacing:0.12em; text-transform:uppercase; color:#00A17A">Supporting system</span>
              <span style="font-size:10px; font-weight:700; letter-spacing:0.06em; text-transform:uppercase; color:#8A6D00; background:#FBEFC6; border-radius:999px; padding:3px 8px">Coming soon</span>
            </div>
            <h3 style="margin:0; font-size:24px; line-height:32px; font-weight:700; letter-spacing:-0.015em; color:#111827">DCS</h3>
            <p style="margin:0; font-size:14.5px; line-height:23px; color:#4B5350; max-width:48ch">Enhance your operations with supporting tools and automation.</p>
            <a href="solutions.html#dcs" style="margin-top:auto; display:inline-flex; align-items:center; gap:7px; align-self:flex-start; font-size:14px; font-weight:600; color:#006B52; text-decoration:underline" class="fx-h0">Learn More →</a>
          </div>
        </div>
      </div>
    </section>'''
    s2 = re.sub(r'    <section data-screen-label="Products".*?</section>', lambda m: products_new, s, count=1, flags=re.S)
    if s2 != s: n["ok"] += 1
    else: n["warn"].append("products")
    s = s2

    # How It Works (replace whole section with new subheading + 4 steps)
    pathgrowth_new = f'''    <section data-screen-label="The path to growth" style="padding:56px 32px 88px">
      <div style="max-width:1200px; margin:0 auto; display:flex; flex-direction:column; gap:48px">
        <div style="display:flex; flex-direction:column; gap:14px; align-items:center; text-align:center">
          <h2 style="margin:0; font-size:clamp(26px, 3.2vw, 34px); line-height:1.2; font-weight:700; letter-spacing:-0.02em; color:#111827">The Path to Growth</h2>
          <p style="margin:0; font-size:15px; line-height:24px; color:#6B7472; max-width:56ch; text-wrap:pretty">With built-in expertise and integrated partner solutions, your success is almost guaranteed.</p>
        </div>
        <div style="display:grid; grid-template-columns:repeat(auto-fit, minmax(240px, 1fr)); gap:36px">
          {_step("01", "Understand Your Business", "We take time to try and understand your business processes, operational workflows, and specific lending requirements.")}
          {_step("02", "Configure Your System", "We tailor the platform modules to match your lending products and credit policies.")}
          {_step("03", "Support", "We guide your staff through practical training and stay on hand with local support whenever assistance is needed.")}
          {_step("04", "Growth", "Systems can be seamlessly adjusted to support your growth.")}
        </div>
      </div>
    </section>'''
    s2 = re.sub(r'    <section data-screen-label="The path to growth".*?</section>', lambda m: pathgrowth_new, s, count=1, flags=re.S)
    if s2 != s: n["ok"] += 1
    else: n["warn"].append("pathgrowth")
    s = s2

    # remove Powerful Features section
    s2 = re.sub(r'\s*<section data-screen-label="Powerful features".*?</section>', '', s, count=1, flags=re.S)
    if s2 != s: n["ok"] += 1
    else: n["warn"].append("features-remove")
    s = s2

    # CTA banner: single button -> Book a Demo + Email us
    rep('<a href="#top" style="margin-top:14px; display:inline-flex; align-items:center; justify-content:center; height:48px; padding:0 28px; border-radius:999px; background:#00BD8E; color:#052416; font-size:15px; font-weight:700; text-decoration:none" class="fx-h2">Book a Demo</a>',
        '<div style="display:flex; flex-wrap:wrap; gap:12px; justify-content:center; margin-top:14px">'
        '<a href="contact.html" style="display:inline-flex; align-items:center; justify-content:center; height:48px; padding:0 28px; border-radius:999px; background:#00BD8E; color:#052416; font-size:15px; font-weight:700; text-decoration:none" class="fx-h2">Book a Demo</a>'
        f'<a href="{MAILTO}" style="display:inline-flex; align-items:center; justify-content:center; height:48px; padding:0 28px; border-radius:999px; background:transparent; border:1px solid rgba(255,255,255,0.35); color:#FFFFFF; font-size:15px; font-weight:600; text-decoration:none">Email us</a>'
        '</div>', "cta-buttons")

    return s, n

# =========================================================================
# BUILD
# =========================================================================
def main():
    os.makedirs(OUT, exist_ok=True)
    # static assets
    if os.path.isdir(os.path.join(OUT, "assets")):
        shutil.rmtree(os.path.join(OUT, "assets"))
    shutil.copytree(os.path.join(SRC, "assets"), os.path.join(OUT, "assets"))
    shutil.copy(os.path.join(SRC, "styles.css"), os.path.join(OUT, "styles.css"))
    # No per-copy _headers: the root _headers already applies to /v2/* paths.

    # subpages
    pages = {
        "solutions.html": ("FlexiSoft — Solutions", "The complete FlexiSoft micro-lending platform: loan management, biometric fraud prevention, e-signatures, and client communication.", "Solutions", solutions_v2),
        "partners.html":  ("FlexiSoft — Partners", "Integrated with South Africa's leading payment, credit bureau, insurance, and SMS providers.", "Partners", partners_v2),
        "about.html":     ("FlexiSoft — About", "FlexiSoft is the leading micro-lending software platform in South Africa, built for compliance, security, and reliability.", "About", about_v2),
        "contact.html":   ("FlexiSoft — Contact", "Partner with FlexiSoft to build a lending environment that fits your business. Request a demo, info, training, or support.", "Contact", contact_v2),
    }
    for fname, (title, desc, active, builder) in pages.items():
        html = bp.page(title, desc, active, builder())
        open(os.path.join(OUT, fname), "w", encoding="utf-8").write(html)
        print(f"wrote v2/{fname:16s} {len(html):>7,d} bytes")

    # home
    home, report = build_home()
    open(os.path.join(OUT, "index.html"), "w", encoding="utf-8").write(home)
    print(f"wrote v2/index.html      {len(home):>7,d} bytes  (edits applied: {report['ok']}, warnings: {report['warn'] or 'none'})")

if __name__ == "__main__":
    main()
