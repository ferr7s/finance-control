import type { Config } from "tailwindcss";

const config: Config = {
  darkMode: ["class"],
  content: ["./app/**/*.{ts,tsx}", "./components/**/*.{ts,tsx}", "./lib/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        background: "#0a0a0a",
        foreground: "#ffffff",
        muted: "#111111",
        border: "#1e1e1e",
        accent: "#ffffff",
        warning: "#d4a017",
        danger: "#c0392b",
        success: "#27ae60"
      },
      fontFamily: {
        mono: ["JetBrains Mono", "Fira Code", "Cascadia Code", "Consolas", "monospace"]
      }
    }
  },
  plugins: []
};

export default config;
