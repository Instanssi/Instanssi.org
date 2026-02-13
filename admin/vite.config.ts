import vue from "@vitejs/plugin-vue";
import { URL, fileURLToPath } from "node:url";
import { defineConfig } from "vite";
import compression from "vite-plugin-compression2";
import { VitePWA } from "vite-plugin-pwa";
import vuetify from "vite-plugin-vuetify";

export default defineConfig({
    base: "/management/",
    plugins: [
        vue(),
        vuetify(),
        VitePWA({
            strategies: "injectManifest",
            injectRegister: "inline",
            srcDir: "src",
            filename: "sw.ts",
            manifest: false,
            injectManifest: {
                injectionPoint: undefined,
            },
            devOptions: {
                enabled: true,
            },
        }),
        compression({
            include: /\.(js|map|css|html|ico|svg)$/i,
            threshold: 1500,
            algorithms: ["gzip"],
        }),
    ],
    esbuild: {
        pure: ["console.debug", "console.log"],
    },
    build: {
        sourcemap: true,
        reportCompressedSize: false,
        emptyOutDir: true,
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
            "/uploads": {
                target: "http://localhost:8000",
                changeOrigin: false,
                secure: false,
            },
        },
    },
});
