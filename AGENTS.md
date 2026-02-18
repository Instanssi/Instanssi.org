# AGENTS.md

This is a monorepo for Instanssi.org, a Finnish demoparty event management system. It contains two subprojects, each with their own detailed instructions:

- **backend/** - Django REST Framework backend. See @./backend/AGENTS.md
- **admin/** - Vue 3 + Vuetify administration panel. See @./admin/AGENTS.md

For visual design guidelines (fonts, colors, icons, CSS frameworks), see @./STYLE_GUIDE.md.

## Quick Reference

### Running All Checks

After making changes, run the relevant checks:

```bash
# Backend (from backend/)
make check

# Frontend (from admin/)
pnpm run type-check && pnpm run lint && pnpm run format
```

### Regenerating the API Client

When backend API changes affect the frontend:

```bash
# 1. Generate the OpenAPI spec (from backend/)
make openapi

# 2. Regenerate the TypeScript client (from admin/)
pnpm run generate-api
```
