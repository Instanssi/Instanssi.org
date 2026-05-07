import { defineConfig } from 'vitest/config'
import react from '@vitejs/plugin-react';
import path from 'node:path';

import getBuildId from "./scripts/build-id.js";

// https://vitejs.dev/config/
export default defineConfig({
    base: "/kompomaatti",
    build: {
        outDir: "build",
        assetsDir: "assets"
    },
    define: {
        __BUILD_ID__: JSON.stringify(getBuildId()),
    },
    server: {
        proxy: {
            '^(?!/kompomaatti/)': {
                target: process.env.INSTANSSI_URL || 'http://localhost:8000',
                secure: false,
                changeOrigin: true,
            }
        },
    },
    plugins: [react({
        babel: {
            parserOpts: {
                plugins: ["decorators-legacy", "classProperties"]
            }
        }
    })],
    resolve: {
        alias: {
            src: path.resolve(process.cwd(), 'src'),
        }
    },
    test: {
        globals: true,
        environment: 'jsdom',
        clearMocks: true,
        setupFiles: [
            './scripts/tests/testSetup.ts',
        ],
    }
})
