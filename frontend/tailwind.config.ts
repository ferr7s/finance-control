import type { Config } from "tailwindcss";

const config: Config = {
  darkMode: ["class"],
  content: ["./app/**/*.{ts,tsx}", "./components/**/*.{ts,tsx}", "./lib/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        background: "#0b0f14",
        foreground: "#eef2f7",
        muted: "#151b23",
        border: "#273241",
        accent: "#2dd4bf",
        warning: "#f59e0b",
        danger: "#ef4444",
        success: "#22c55e"
      }
    }
  },
  plugins: []
};

export default config;
