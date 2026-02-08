# AGENTS.md

This is a monorepo for Instanssi.org, a Finnish demoparty event management system. It contains two subprojects, each with their own detailed instructions:

- **backend/** - Django REST Framework backend. See @./backend/AGENTS.md
- **admin/** - Vue 3 + Vuetify administration panel. See @./admin/AGENTS.md

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
# From admin/, with the backend dev server running on port 8000
pnpm run fetch-apidoc && pnpm run generate-api
```
