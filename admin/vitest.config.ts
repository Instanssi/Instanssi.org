import { fileURLToPath } from "node:url";

import vue from "@vitejs/plugin-vue";
import { defineConfig } from "vitest/config";

export default defineConfig({
    plugins: [vue()],
    test: {
        environment: "happy-dom",
        globals: true,
        include: ["src/**/*.test.ts"],
        setupFiles: ["src/test/setup.ts"],
        css: true,
        server: {
            deps: {
                inline: ["vuetify"],
            },
        },
    },
    resolve: {
        alias: {
            "@": fileURLToPath(new URL("./src", import.meta.url)),
        },
    },
});
