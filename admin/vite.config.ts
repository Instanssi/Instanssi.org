import vue from "@vitejs/plugin-vue";
import { URL, fileURLToPath } from "node:url";
import { defineConfig } from "vite";
import compression from "vite-plugin-compression2";
import vuetify from "vite-plugin-vuetify";

export default defineConfig({
    base: "/management/",
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
        emptyOutDir: true,
        outDir: fileURLToPath(new URL("../backend/Instanssi/management/site/", import.meta.url)),
    },
    resolve: {
        alias: {
            "@": fileURLToPath(new URL("./src", import.meta.url)),
        },
    },
    server: {
        proxy: {
            "/api": {
                target: "http://localhost:8000",
                changeOrigin: false,
                secure: false,
            },
        },
    },
});
