/** @type {import('tailwindcss').Config} */
/* ═══════════════════════════════════════════════════════════════════════
 * tailwind.config.js — NeuroSoft
 * ───────────────────────────────────────────────────────────────────────
 * Reemplaza el CDN runtime (cdn.tailwindcss.com) por compilación local
 * con tree-shaking real. El bundle final pesa ~12 KB en vez de los
 * ~380 KB que carga el CDN.
 *
 * Tokens de marca expuestos como utilidades:
 *   bg-brand, text-brand, border-brand        → TEAL #0D9488
 *   bg-brand-light                            → TEAL_LIGHT #67E8F9
 *   bg-brand-deep                             → NAVY #1E293B
 *   bg-cream                                  → CREAM #FDFBF7
 *   text-{success,warning,danger,info}        → semánticos
 * ═══════════════════════════════════════════════════════════════════════ */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,jsx,ts,tsx}",
  ],
  darkMode: ["class", ".dark-mode"],
  theme: {
    extend: {
      fontFamily: {
        sans: ["Manrope", "ui-sans-serif", "system-ui", "sans-serif"],
      },
      colors: {
        brand: {
          DEFAULT: "#0D9488",
          light:   "#67E8F9",
          deep:    "#1E293B",
          50:      "#f0fdfa",
          100:     "#ccfbf1",
          200:     "#99f6e4",
          500:     "#0D9488",
          600:     "#0d9488",
          700:     "#0f766e",
        },
        cream: "#FDFBF7",
        success: "#10b981",
        warning: "#d97706",
        danger:  "#dc2626",
        info:    "#6366f1",
        navy:    "#1E293B",
      },
      borderRadius: {
        "4xl": "2rem",
      },
      boxShadow: {
        "brand":      "0 12px 30px -6px rgba(13,148,136,0.35)",
        "brand-soft": "0 8px 20px -4px rgba(13,148,136,0.25)",
        "card":       "0 20px 50px -20px rgba(0,0,0,0.04)",
      },
      keyframes: {
        fadeIn: {
          "0%":   { opacity: 0, transform: "translateY(8px)" },
          "100%": { opacity: 1, transform: "translateY(0)" },
        },
        float: {
          "0%, 100%": { transform: "translateY(0)" },
          "50%":      { transform: "translateY(-6px)" },
        },
        pulseGlow: {
          "0%, 100%": { opacity: 0.4 },
          "50%":      { opacity: 1 },
        },
      },
      animation: {
        "fade-in":    "fadeIn 0.3s ease-out",
        "float":      "float 6s ease-in-out infinite",
        "pulse-glow": "pulseGlow 2s ease-in-out infinite",
      },
    },
  },
  plugins: [],
};
