import jsDefaults from "@eslint/js";
import vueDefaults from "eslint-plugin-vue";
import prettierConfig from "@vue/eslint-config-prettier";
import { defineConfigWithVueTs, vueTsConfigs } from "@vue/eslint-config-typescript";

export default defineConfigWithVueTs(
    {
        ignores: ["src/api/", ".vite/", ".gitignore", "env.d.ts"],
    },
    jsDefaults.configs.recommended,
    ...vueDefaults.configs["flat/recommended"],
    vueTsConfigs.recommended,
    prettierConfig,
    {
        files: ["**/*.mjs", "**/*.cjs", "**/*.js", "**/*.vue", "**/*.mts", "**/*.cts", "**/*.ts"],
        languageOptions: {
            ecmaVersion: "latest",
        },
        rules: {
            "vue/valid-v-slot": [
                "error",
                {
                    allowModifiers: true,
                },
            ],
            "@typescript-eslint/no-unused-vars": ["error", { argsIgnorePattern: "^_" }],
            "@typescript-eslint/no-explicit-any": ["error"],
            "vue/no-template-shadow": ["off"],
        },
    }
);
