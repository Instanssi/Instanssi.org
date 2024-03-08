import { fileURLToPath, URL } from "node:url";
import { defineConfig } from "vite";
import vue from "@vitejs/plugin-vue";
import Vuetify, { transformAssetUrls } from "vite-plugin-vuetify";

export default defineConfig({
    plugins: [
        vue({
            template: { transformAssetUrls },
        }),
        Vuetify(),
    ],
    esbuild: {
        pure: ["console.debug", "console.log"],
    },
    resolve: {
        alias: {
            "@": fileURLToPath(new URL("./src", import.meta.url)),
        },
    },
});
