# instanssi administration frontend

This is the administration frontend for the Instanssi event website.

## Development setup

1. Install Node 20.x LTS
2. Install packages (cleanly), run: `npm ci`
3. Start up in dev mode, run: `npm run dev``
`
For development, VSCode with Volar + eslint + prettier plugins will do fine.

## Building for production

Just run:
```sh
npm run build
```

### Running code quality tools

```sh
npm run format
npm run type-check
npm run lint
npm run test
```

### Checking bundle size

```sh
npx vite-bundle-visualizer
```