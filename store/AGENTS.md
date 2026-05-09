# AGENTS.md - Instanssi Store Frontend

> This project is **not actively edited via AI agents**. This file exists only to give enough context that the codebase is recognizable when an agent encounters it (e.g. while reading from a sibling project).

Embedded Vue 3 widget — *not* a standalone SPA. Mounted on `#store` inside a Django-rendered HTML page; handles cart, customer info, and Paytrail checkout.

- **Stack**: Vue 3 (Options API, plain JavaScript), Vite 7 in library/IIFE mode, Vitest.
- **Vue is external**: marked external in the rollup config; the host Django page must load Vue as a `Vue` global before this bundle runs.
- **Backend**: APIv1 store endpoints only (`/api/v1/store_items/`, `/api/v1/store_transaction/`).
- **Package manager**: pnpm 10.x, Node 24 LTS.
- **Build target**: `pnpm run build` writes the IIFE bundle straight into `../backend/Instanssi/store/static/store/js/bundle.js` — there is no separate deploy step.
- **Templates**: HTML files imported via a custom `?minify` Vite plugin (`minifyHtmlTemplatePlugin.ts`), kept as strings on Vue component `template:` properties.

Counterpart projects in the monorepo: `../backend/` (Django REST API + the page that hosts this widget), `../admin/` (organizer admin, APIv2), `../kompomaatti/` (compo participation SPA, APIv1).
