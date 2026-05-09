# AGENTS.md

This is a monorepo for Instanssi.org, a Finnish demoparty event management system. It contains the following subprojects, each with their own detailed instructions:

- **backend/** - Django REST Framework backend. See @./backend/AGENTS.md
- **admin/** - Vue 3 + Vuetify organizer administration panel (uses APIv2). See @./admin/AGENTS.md
- **kompomaatti/** - React + MobX public-facing compo participation frontend (uses APIv1). See @./kompomaatti/AGENTS.md
- **store/** - Vue 3 store widget embedded in Django-rendered store pages. See @./store/AGENTS.md

For visual design guidelines (fonts, colors, icons, CSS frameworks), see @./STYLE_GUIDE.md.

## Quick Reference

### Running All Checks

After making changes, run the relevant checks for whichever subproject(s) you touched:

```bash
# Backend (from backend/)
make check

# Admin panel (from admin/)
pnpm run type-check && pnpm run lint && pnpm run format && pnpm run test

# Kompomaatti (from kompomaatti/)
yarn run test

# Store widget (from store/)
pnpm run test
```

### Regenerating the API Client

The `admin/` panel consumes APIv2 via an auto-generated TypeScript client. When backend APIv2 changes affect it:

```bash
# 1. Generate the OpenAPI spec (from backend/)
make openapi

# 2. Regenerate the TypeScript client (from admin/)
pnpm run generate-api
```

Note: `kompomaatti/` uses APIv1 with a hand-written client — there is no codegen step for it.
