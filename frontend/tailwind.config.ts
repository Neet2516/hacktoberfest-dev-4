import type { Config } from "tailwindcss";

export default {
  content: [
    "./src/pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/components/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        background: "var(--background)",
        foreground: "var(--foreground)",
        specter: {
          50: "#f4f6f8",
          100: "#e5e9ee",
          500: "#3b82f6",
          900: "#0f172a",
        },
      },
    },
  },
  plugins: [],
} satisfies Config;

