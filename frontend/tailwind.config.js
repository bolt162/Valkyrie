/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        'neon-green': '#22c55e',
        'neon-bright': '#00ff7f',
        'dark-bg': '#000000',
        'dark-card': '#0a0a0a',
        'dark-border': '#1a1a1a',
        'light-bg': '#f9fafb',
        'light-card': '#ffffff',
        'light-border': '#e5e7eb',
      },
      fontFamily: {
        'mono': ['JetBrains Mono', 'Fira Code', 'Consolas', 'monospace'],
      },
    },
  },
  plugins: [],
}
