# AGENTS.md - Kompomaatti Frontend

> This project is **not actively edited via AI agents**. This file exists only to give enough context that the codebase is recognizable when an agent encounters it (e.g. while reading from a sibling project).

Public-facing single-page app for compo participation at Instanssi.org events: browsing events, submitting compo entries, joining competitions, voting.

- **Stack**: React 18 + TypeScript (class components), MobX 4 with legacy decorators, React Router 5, react-bootstrap 0.32 / bootstrap-sass 3, Vite 7, Vitest.
- **Backend**: APIv1 (`/api/v1/`) via the hand-written client in `src/api/`. Not the same API surface as `admin/`.
- **Package manager**: yarn (not pnpm).
- **Build output**: `build/` (not `dist/`), served by nginx at `/kompomaatti/`.
- **Setup quirk**: `src/config.ts` is gitignored — copy from `src/config.dist.ts` after cloning.

Counterpart projects in the monorepo: `../admin/` (organizer admin, Vue 3, APIv2), `../store/` (store checkout widget, Vue 3, APIv1), `../backend/` (Django REST API).
