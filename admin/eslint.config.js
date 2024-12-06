import jsDefaults from "@eslint/js";
import vueDefaults from "eslint-plugin-vue";
import prettierConfig from "@vue/eslint-config-prettier";
import typescriptDefaults from "@vue/eslint-config-typescript";

export default [
    {
        ignores: ["src/api/", ".vite/", ".gitignore", "env.d.ts"],
    },
    jsDefaults.configs.recommended,
    ...vueDefaults.configs["flat/recommended"],
    prettierConfig,
    ...typescriptDefaults(),
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
            "@typescript-eslint/no-unused-vars": ["off"],
            "@typescript-eslint/no-explicit-any": ["off"],
            "vue/no-template-shadow": ["off"],
        },
    },
];
