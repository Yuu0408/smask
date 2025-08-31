import js from '@eslint/js';
import globals from 'globals';
import tseslint from 'typescript-eslint';
import pluginVue from 'eslint-plugin-vue';
import { defineConfig } from 'eslint/config';
import prettierPlugin from 'eslint-plugin-prettier';

export default defineConfig([
    {
        files: ['**/*.{js,mjs,cjs,ts,vue}'],
        plugins: { js },
        extends: ['js/recommended'],
        languageOptions: { globals: globals.browser },
    },
    tseslint.configs.recommended,
    pluginVue.configs['flat/essential'],
    {
        languageOptions: { parserOptions: { parser: tseslint.parser } },
    },
    {
        ignores: [
            '**/node_modules/**',
            '**/.vite/**',
            '**/dist/**',
            '**/components/ui/**/*',
        ],
    },
    {
        plugins: {
            prettier: prettierPlugin,
        },
        rules: {
            'prettier/prettier': 'error',
            '@typescript-eslint/no-explicit-any': 'off',
        },
    },
]);
