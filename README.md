# FlexiSoft Website

Marketing website for FlexiSoft — micro-lending software. A fast, JS-free
static site (plain HTML/CSS with self-hosted Inter fonts) ready to deploy on
Cloudflare Pages.

## Repository layout

```
.
├── FlexiSoft Homepage.html   # source artifact bundle for the home page
├── build.py                  # builds dist/index.html from the bundle
├── build_pages.py            # builds the sub-pages + shared nav; patches index.html
└── dist/                     # ← the deployable static site (deploy this folder)
    ├── index.html            # Home
    ├── solutions.html        # Solutions (incl. Neptus + DCS sections)
    ├── partners.html         # Partners
    ├── case-studies.html     # Case Studies (sample content)
    ├── resources.html        # Resources / blog (sample content)
    ├── about.html            # About
    ├── contact.html          # Contact (request form)
    ├── styles.css            # reset, @font-face, hover interactions
    ├── _headers              # Cloudflare Pages caching + security headers
    └── assets/               # logo + self-hosted Inter woff2 subsets
```

## Build

```bash
python3 build.py         # 1. home page, from the source bundle
python3 build_pages.py   # 2. sub-pages + shared nav (run after build.py)
```

## Deploy (Cloudflare Pages)

```bash
npx wrangler pages deploy dist --project-name=flexisoft
```

Or connect this repo in the Cloudflare dashboard with **build command:** *(none)*
and **output directory:** `dist`. See [dist/README.md](dist/README.md) for full
deploy options and notes (the contact form is a front-end placeholder to wire up
to Zoho Forms or Cloudflare Pages Forms).
