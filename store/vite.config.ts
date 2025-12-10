/// <reference types="vitest/config" />
import { defineConfig } from "vite";
import { resolve } from "node:path";
import { minifyHtmlTemplatePlugin } from "./minifyHtmlTemplatePlugin.js";

export default defineConfig({
    build: {
        // Put output in the store static files dir
        outDir: resolve(__dirname, "../backend/Instanssi/store/static/store/js/"),
        lib: {
            entry: resolve(__dirname, "js/index.js"),
            name: "store",
            // immediately invoked function expression (just run the script when it loads)
            formats: ["iife"],
            // stop appending format to the file name
            fileName: () => "bundle.js",
        },
        rollupOptions: {
            external: ["vue"],
            output: {
                // Globals for external deps
                globals: {
                    vue: "Vue",
                },
            },
        },
    },
    plugins: [minifyHtmlTemplatePlugin()],
    test: {
        environment: "jsdom",
        clearMocks: true,
    }
});
