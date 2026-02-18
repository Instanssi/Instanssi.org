# Instanssi.org Style Guide

Design guidelines for the Instanssi.org frontend. Applies to both the Django backend templates and the Vue admin panel.

## Fonts

All fonts are self-hosted — never load from external CDNs like Google Fonts.

**Exo 2** — headings and branding. Bold, geometric, gives the site its demoscene feel.
- h1: weight 900 (Black)
- h2, h3: weight 600 (SemiBold)

**Open Sans** — body text. Clean and readable at all sizes.
- Weight 400 (Regular)

**Fira Mono** — code and technical content.
- Weight 400 (Regular)

CSS fallbacks: `sans-serif` for Exo 2 and Open Sans, `monospace` for Fira Mono.

### Where the font files live

- **Backend:** Fontsource CSS in `backend/Instanssi/static/fonts/`. Include only the weights you need (e.g. `fonts/exo-2/latin-600.css`).
- **Admin:** Fontsource npm packages (`@fontsource/exo-2`, `@fontsource/open-sans`, `@fontsource/fira-mono`).

## Icons

**Font Awesome 7 Free**, self-hosted in `backend/Instanssi/static/fonts/fontawesome-free-7.2.0/`.

- **Backend:** Webfont approach — include `css/all.min.css` in the head. Use standard `<i class="fa-solid fa-check">` markup.
- **Admin:** Vue `FontAwesomeIcon` component with tree-shaken icon imports.

## CSS Frameworks

- **Backend:** Bootstrap 5, self-hosted in `backend/Instanssi/static/libs/bootstrap-5.3.8/`.
- **Admin:** Vuetify 3 (Material Design).

## General Rules

- **Self-host everything.** Fonts, CSS frameworks, icons — no external CDN links.
- **Keep the dark theme consistent** across user-facing pages.
