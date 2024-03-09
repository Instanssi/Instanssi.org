import { fileURLToPath, URL } from "node:url";
import { defineConfig } from "vite";
import compression from "vite-plugin-compression2";
import vue from "@vitejs/plugin-vue";
import vuetify from "vite-plugin-vuetify";

export default defineConfig({
    plugins: [
        vue(),
        vuetify(),
        compression({
            include: /\.(js|map|css|html|ico|svg)$/i,
            threshold: 1500,
        }),
    ],
    esbuild: {
        pure: ["console.debug", "console.log"],
    },
    build: {
        sourcemap: true,
        reportCompressedSize: false,
    },
    resolve: {
        alias: {
            "@": fileURLToPath(new URL("./src", import.meta.url)),
        },
    },
});
