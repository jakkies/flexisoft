# FlexiSoft Website

Marketing website for FlexiSoft — micro-lending software. A fast, JS-free
static site (plain HTML/CSS with self-hosted Inter fonts). The site files live
at the repo root, so the repository **is** the deployable site.

## Pages

| File | Page |
|---|---|
| `index.html` | Home |
| `solutions.html` | Solutions (incl. Neptus + DCS sections) |
| `partners.html` | Partners |
| `case-studies.html` | Case Studies (sample content) |
| `resources.html` | Resources / blog (sample content) |
| `about.html` | About |
| `contact.html` | Contact (request form) |

Shared assets: `styles.css` (reset, `@font-face`, hover interactions),
`assets/flexisoft-logo.svg`, `assets/fonts/*.woff2` (self-hosted Inter subsets),
and `_headers` (Cloudflare Pages caching + security headers).

All pages share one header/footer and navigation. Content comes from the
project "Website Content" brief; case-study and resource entries are clearly
labelled **Sample** placeholders to be replaced with real content. The contact
form is a styled front-end placeholder — connect a Zoho Forms embed or a form
handler (e.g. Cloudflare Pages Forms) to receive submissions.

## Source & build

The pages are generated, not hand-maintained:

- `FlexiSoft Homepage.html` — the source artifact bundle for the home page.
- `build.py` — rebuilds `index.html` + `styles.css` + `assets/` from the bundle.
- `build_pages.py` — rebuilds the sub-pages and shared nav, and patches
  `index.html` to use the shared header/footer.

```bash
python3 build.py         # 1. home page, from the source bundle
python3 build_pages.py   # 2. sub-pages + shared nav (run after build.py)
```

Both scripts write to the repo root. Editing the `*.html` / `styles.css` files
directly is fine too — just note that re-running the scripts overwrites them.

## Local preview

```bash
python3 -m http.server 8000    # then open http://localhost:8000
```

## Deploy to Cloudflare Pages

**Wrangler (direct upload)** — output directory is the repo root:

```bash
npx wrangler pages deploy . --project-name=flexisoft
```

**Git-connected build** — connect this repo in the Cloudflare dashboard with:

- **Build command:** *(leave empty)*
- **Build output directory:** `/`

`.assetsignore` keeps the source, build scripts, and reference material in the
repo but excludes them from the deployed site, so only the actual pages and
their assets are published.
