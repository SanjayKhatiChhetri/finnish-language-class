/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./App.tsx",
    "./index.tsx",
    "./components/**/*.tsx",
  ],
  theme: {
    extend: {
      colors: {
        'brand-bg': '#f8f9fa',
        'brand-surface': '#ffffff',
        'brand-primary': '#4f46e5',
        'brand-primary-hover': '#4338ca',
        'brand-text-main': '#1f2937',
        'brand-text-secondary': '#6b7280',
        'brand-border': '#e5e7eb',
      },
      fontFamily: {
        sans: ['Inter', 'sans-serif'],
      },
    },
  },
  plugins: [],
}