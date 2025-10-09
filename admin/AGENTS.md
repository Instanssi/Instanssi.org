# AGENTS.md - Instanssi Admin Panel

This document provides AI coding assistants with comprehensive context about the Instanssi administration panel project to enable effective assistance with development tasks.

## Project Overview

**Project Type**: Single-page administration application for demoscene event management

**Tech Stack**:
- **Frontend**: Vue 3 (Composition API) + TypeScript
- **UI Framework**: Vuetify 3 (Material Design components)
- **Build Tool**: Vite
- **Routing**: Vue Router 4
- **State Management**: Composables pattern with Vue reactivity
- **API Client**: Auto-generated from OpenAPI spec using @hey-api/openapi-ts
- **Rich Text Editor**: vuetify-pro-tiptap
- **Form Validation**: vee-validate + yup
- **HTTP Client**: Axios
- **Internationalization**: vue-i18n
- **Icons**: FontAwesome via vue-fontawesome

**Backend**: Django REST Framework API (located in `../backend`)
- API base URL: `/api/v2/`
- OpenAPI spec available at: `http://localhost:8000/api/v2/openapi/`

**Purpose**: Web-based management interface for organizing demoscene events (demoparties). Manages events, blog posts, users, competitions, store items, and various event-related content.

## Project Structure

```
admin/
├── src/
│   ├── api/              # Auto-generated API client (DO NOT EDIT MANUALLY)
│   ├── assets/           # Static assets, styles (main.scss)
│   ├── components/       # Reusable Vue components
│   ├── locales/          # i18n translation files
│   ├── services/         # Business logic and state management
│   ├── utils/            # Helper utilities
│   ├── views/            # Page-level components
│   ├── App.vue           # Root component
│   ├── client.ts         # API client configuration
│   ├── i18n.ts           # i18n setup
│   ├── icons.ts          # FontAwesome icon registration
│   ├── main.ts           # App entry point
│   ├── router.ts         # Route configuration
│   ├── symbols.ts        # Vue injection symbols
│   └── tiptap.ts         # Rich text editor configuration
├── openapi/              # OpenAPI spec storage
├── public/               # Public static files
├── package.json
├── vite.config.ts
├── tsconfig.json
└── README.md
```

## Key Architecture Patterns

### 1. Composables for State Management

The project uses Vue 3 composables pattern instead of Vuex/Pinia:

```typescript
// services/auth.ts - Example composable
export function useAuth() {
  const loggedIn: Ref<boolean> = ref(false);
  const userInfo: Ref<CurrentUserInfo> = ref({...});

  function isLoggedIn(): boolean { ... }
  async function login(...) { ... }

  return { isLoggedIn, login, ... };
}

// Usage in components
const { isLoggedIn, login } = useAuth();
```

Main composables:
- `useAuth()` - Authentication state and permissions
- `useEvents()` - Event selection and caching

### 2. Auto-Generated API Client

**CRITICAL**: Never manually edit files in `src/api/`. The API client is generated from the Django backend's OpenAPI specification.

To update the API client:
```bash
npm run fetch-apidoc   # Fetch OpenAPI spec from backend
npm run generate-api   # Generate TypeScript client
```

API usage example:
```typescript
import * as api from "@/api";

const result = await api.userInfo();
const events = await api.listEvents();
```

### 3. Permission-Based Routing

Routes use meta fields for authentication and permission checks:

```typescript
{
  path: "/events",
  meta: {
    requireAuth: true,
    requireViewPermission: PermissionTarget.EVENT,
  },
  component: () => import("@/views/EventView.vue"),
}
```

Permission system:
- Permission types: `add`, `change`, `delete`, `view`
- Permission targets: Defined in `PermissionTarget` enum in `services/auth.ts`
- Check permissions: `authService.canView(PermissionTarget.EVENT)`

### 4. Dialog-Based Forms

Forms are implemented as dialog components for create/edit operations:
- `BaseDialog.vue` - Basic dialog wrapper
- `BaseFormDialog.vue` - Form dialog with validation
- `*Dialog.vue` - Specific entity dialogs (EventDialog, UserDialog, etc.)

### 5. Build Output Location

**Important**: The build output goes to `../backend/Instanssi/management/site/` so Django can serve it.

```typescript
// vite.config.ts
build: {
  outDir: fileURLToPath(new URL("../backend/Instanssi/management/site/", import.meta.url)),
}
```

## Development Workflow

### Starting Development

```bash
npm ci                    # Clean install dependencies
npm run dev              # Start dev server (http://localhost:5173)
```

Dev server proxies `/api` requests to Django backend at `http://localhost:8000`.

### Code Quality

```bash
npm run format           # Format code with Prettier
npm run lint             # Lint and auto-fix with ESLint
npm run type-check       # TypeScript type checking
npm run format-check     # Check formatting
npm run lint-check       # Check linting
```

### Building for Production

```bash
npm run build            # Build and output to ../backend/Instanssi/management/site/
npm run preview          # Preview production build
```

### Analyzing Bundle Size

```bash
npx vite-bundle-visualizer
```

## Common Development Tasks

### Adding a New View/Page

1. Create view component in `src/views/NewView.vue`
2. Add route in `src/router.ts` with appropriate meta fields
3. Add navigation link in `src/components/MainNavigation.vue` or `NavigationList.vue`
4. Add required permissions check if needed

### Adding a New API Endpoint

1. Add/modify endpoint in Django backend
2. Run `npm run fetch-apidoc` to fetch updated OpenAPI spec
3. Run `npm run generate-api` to regenerate client
4. Use the new API function from `@/api`

### Adding a New Permission Target

1. Add enum value to `PermissionTarget` in `src/services/auth.ts`
2. Use in route meta or component logic: `canView(PermissionTarget.NEW_TARGET)`

### Creating a New Dialog Component

1. Extend `BaseDialog` or `BaseFormDialog` component
2. Use vee-validate for form validation
3. Use yup for validation schemas
4. Emit events for save/cancel actions

Example structure:
```vue
<template>
  <base-form-dialog :visible="visible" @update:visible="emit('update:visible', $event)">
    <v-form @submit="onSubmit">
      <!-- Form fields -->
    </v-form>
  </base-form-dialog>
</template>

<script setup lang="ts">
import { useForm } from 'vee-validate';
import * as yup from 'yup';

const schema = yup.object({...});
const { handleSubmit } = useForm({ validationSchema: schema });

const onSubmit = handleSubmit(async (values) => {
  // API call
});
</script>
```

## Important Configuration Files

### vite.config.ts
- Base URL: `/management/`
- Proxy configuration for API calls
- Build output directory
- Compression settings
- Source maps enabled

### tsconfig.json
- TypeScript strict mode enabled
- Path alias `@` → `./src`
- Vue JSX support

### package.json Scripts
- `dev` - Development server
- `build` - Production build
- `preview` - Preview production build
- `type-check` - TypeScript checking
- `lint` / `lint-check` - ESLint
- `format` / `format-check` - Prettier
- `generate-api` - Generate API client
- `fetch-apidoc` - Fetch OpenAPI spec

## Styling

- **Framework**: Vuetify 3 Material Design components
- **Icons**: FontAwesome (imported in `src/icons.ts`)
- **Fonts**:
  - Exo 2 (weights: 600, 900)
  - Open Sans (weight: 400)
  - Fira Mono (weight: 400)
- **Custom styles**: `src/assets/main.scss`
- **CSS preprocessor**: Sass

## API Integration

### Authentication Flow

1. User lands on app → `useAuth().refreshStatus()` checks login state
2. If not authenticated → redirect to `/login`
3. Login via username/password or social auth
4. After login → fetch user permissions
5. Router guards check permissions before allowing route access

### API Client Setup

```typescript
// src/client.ts
export function setupClient() {
  client.setConfig({
    baseURL: import.meta.env.BASE_URL,
  });
  client.instance.interceptors.request.use(addCSRFHeader);
  client.instance.interceptors.response.use(okResponse, errorResponse);
}
```

Interceptors handle:
- CSRF token injection
- Cookie-based authentication
- Error responses and redirects

## Common Pitfalls

1. **Never manually edit `src/api/`** - It's auto-generated and will be overwritten
2. **Build output location** - Remember builds go to Django's static directory
3. **CSRF tokens** - Required for POST/PUT/DELETE. Handled automatically by interceptors
4. **Permissions** - Always check permissions for UI elements and routes
5. **Event context** - Many operations require an active event ID from route params
6. **Base URL** - App runs at `/management/` not root path

## Backend Context

The Django backend (located at `../backend/`) provides:
- RESTful API at `/api/v2/`
- Auto-generated OpenAPI documentation
- Django admin interface (separate from this Vue admin)
- User authentication and permission management
- Models for events, blog posts, competitions, store, etc.

Backend runs on `http://localhost:8000` during development.

## Testing

Currently no frontend tests are configured. When adding tests, consider:
- Vue Test Utils for component testing
- Vitest for unit testing (Vite-native)
- Testing auth flows and permission checks
- Mocking API calls

## Browser Support

Modern browsers with ES6+ support required. No IE11 support needed.

## Environment Variables

- `BASE_URL` - Set to `/management/` in vite.config.ts
- No `.env` file configuration needed for basic development

## Performance Considerations

- Route-based code splitting (lazy-loaded views)
- Compression enabled for production builds (Brotli + Gzip)
- Source maps generated for debugging
- Console.log/debug stripped in production builds
- Bundle size monitoring via vite-bundle-visualizer

## Deployment

1. Build frontend: `npm run build`
2. Files are output to `../backend/Instanssi/management/site/`
3. Django serves these static files
4. In production, typically served directly via nginx

## Additional Notes for AI Assistants

- **Composition API**: Always use Vue 3 Composition API with `<script setup>`, never Options API
- **TypeScript**: Maintain strict typing, avoid `any` types
- **Vuetify**: Use Vuetify 3 components (not Vuetify 2 syntax)
- **Code style**: Follow existing patterns in the codebase
- **Imports**: Use `@/` alias for src imports
- **Reactivity**: Use `ref()` and `reactive()` appropriately
- **Async/await**: Prefer async/await over promise chains
- **Error handling**: Use toast notifications for user-facing errors
- **Comments**: Add JSDoc comments for complex functions

## Related Documentation

- Vue 3: https://vuejs.org/
- Vuetify 3: https://vuetifyjs.com/
- Vite: https://vitejs.dev/
- TypeScript: https://www.typescriptlang.org/
- Backend README: `../backend/README.md`
