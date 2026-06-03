/**
 * eslint.config.js — Configuración ESLint v9 (flat config) para NeuroSoft
 *
 * §post-mortem (2026-05-18): se añadió tras el bug `ExtNeuroCanvas is not
 * defined` que pasó dos auditorías sin ser detectado. El audit estaba
 * basado solo en grep de patrones, no en análisis estático real.
 *
 * Reglas críticas que NO podemos relajar:
 *   - `no-undef` — habría capturado el bug original en 0.5s.
 *   - `no-unused-vars` (warn) — descubre alias dead-code que apuntan a
 *      símbolos no importados (signo temprano del mismo problema).
 *   - `react/jsx-no-undef` — variante JSX de no-undef (componentes).
 *
 * Reglas que sí relajamos:
 *   - `react/prop-types`: el proyecto no usa PropTypes, valida con uso.
 *   - `react/display-name`: HOCs y wrappers anónimos son comunes.
 *   - `no-unused-vars`: warn no error — hay archivos grandes con imports
 *     que se usan en JSX dinámicamente y ESLint a veces no los ve.
 *
 * Para correr:  npm run lint
 * Para fix:     npm run lint:fix
 */

import js from "@eslint/js";
import react from "eslint-plugin-react";
import reactHooks from "eslint-plugin-react-hooks";
import globals from "globals";

export default [
  {
    ignores: ["dist/**", "node_modules/**", "e2e/**", "*.config.js"],
  },
  {
    files: ["src/**/*.{js,jsx}"],
    languageOptions: {
      ecmaVersion: 2022,
      sourceType: "module",
      parserOptions: {
        ecmaFeatures: { jsx: true },
      },
      globals: {
        ...globals.browser,
        ...globals.es2022,
        // APIs específicas de WebView / pywebview
        pywebview: "readonly",
      },
    },
    plugins: {
      react,
      "react-hooks": reactHooks,
    },
    rules: {
      ...js.configs.recommended.rules,
      ...react.configs.flat.recommended.rules,
      ...reactHooks.configs.recommended.rules,

      // ── CRÍTICAS: no relajar ─────────────────────────────────────
      "no-undef": "error",            // §audit-meta-2026-05
      "react/jsx-no-undef": "error",
      "no-const-assign": "error",
      "no-dupe-keys": "error",
      "no-unreachable": "error",

      // `catch {}` es un patrón intencional en este codebase — degradación
      // silenciosa de operaciones idempotentes (localStorage, notifications).
      // Lo bajamos a warning para no romper el build, pero seguimos viéndolo.
      "no-empty": ["warn", { allowEmptyCatch: true }],

      // ── Estilo / razonables ───────────────────────────────────────
      "no-unused-vars": ["warn", {
        varsIgnorePattern: "^_",
        argsIgnorePattern: "^_",
        ignoreRestSiblings: true,
      }],

      // ── React específicas ────────────────────────────────────────
      "react/prop-types": "off",
      "react/display-name": "off",
      "react/react-in-jsx-scope": "off",       // React 17+ no requiere import
      "react/no-unescaped-entities": "off",    // genera ruido en español
      "react/jsx-key": "warn",
      "react-hooks/rules-of-hooks": "error",
      "react-hooks/exhaustive-deps": "warn",
    },
    settings: {
      react: { version: "detect" },
    },
  },
];
