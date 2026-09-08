/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        'vs-dark': '#0f172a',
        'vs-panel': '#1e293b',
        'vs-accent': '#22d3ee',
        'vs-danger': '#ef4444',
        'vs-warning': '#f59e0b',
        'vs-safe': '#22c55e',
      },
    },
  },
  plugins: [],
}