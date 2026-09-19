import type { Config } from "tailwindcss";

// DOCURA visual system (APP-1 §6). Near-black ground, metallic monochrome accents,
// thin low-contrast borders, mono for system labels + sans for content. Colours are
// driven by CSS variables defined in src/index.css so the palette lives in one place.
const config: Config = {
  darkMode: "class",
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      spacing: {
        // Custom steps used by the adaptive notch navigation component.
        "8.5": "2.125rem",
        "17.5": "4.375rem",
      },
      colors: {
        bg: "hsl(var(--bg))",
        // `background`/`foreground` aliases so the copied shadcn-style notch component resolves.
        background: "hsl(var(--bg))",
        surface: "hsl(var(--surface))",
        "surface-2": "hsl(var(--surface-2))",
        border: "hsl(var(--border))",
        input: "hsl(var(--border))",
        ring: "hsl(var(--ring))",
        foreground: "hsl(var(--foreground))",
        muted: "hsl(var(--muted))",
        "muted-foreground": "hsl(var(--muted-foreground))",
        mercury: "hsl(var(--mercury))",
        "mercury-dark": "hsl(var(--mercury-dark))",
        primary: {
          DEFAULT: "hsl(var(--primary))",
          foreground: "hsl(var(--primary-foreground))",
        },
        destructive: {
          DEFAULT: "hsl(var(--destructive))",
          foreground: "hsl(var(--destructive-foreground))",
        },
        elevated: "hsl(var(--elevated))",
        "elevated-2": "hsl(var(--elevated-2))",
      },
      fontFamily: {
        sans: ["Inter", "ui-sans-serif", "system-ui", "sans-serif"],
        mono: ["'Space Mono'", "ui-monospace", "SFMono-Regular", "monospace"],
      },
      letterSpacing: {
        system: "0.25em",
      },
      borderRadius: {
        DEFAULT: "2px",
        md: "4px",
      },
      keyframes: {
        "docura-float": {
          "0%": { transform: "translate(0, 0) scale(1)" },
          "33%": { transform: "translate(10vw, 20vh) scale(1.2)" },
          "66%": { transform: "translate(-5vw, 10vh) scale(0.8)" },
          "100%": { transform: "translate(5vw, -10vh) scale(1.1)" },
        },
        "docura-fade-in": {
          from: { opacity: "0", transform: "translateY(6px)" },
          to: { opacity: "1", transform: "translateY(0)" },
        },
        "docura-message-in": {
          from: { opacity: "0", transform: "translateY(8px)" },
          to: { opacity: "1", transform: "translateY(0)" },
        },
        "docura-typing": {
          "0%, 60%, 100%": { opacity: "0.25", transform: "translateY(0)" },
          "30%": { opacity: "1", transform: "translateY(-2px)" },
        },
      },
      animation: {
        float: "docura-float 20s infinite alternate ease-in-out",
        "fade-in": "docura-fade-in 0.5s cubic-bezier(0.2,1,0.3,1) both",
        "message-in": "docura-message-in 0.35s cubic-bezier(0.2,1,0.3,1) both",
      },
    },
  },
  plugins: [],
};

export default config;
