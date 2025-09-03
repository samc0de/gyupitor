/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./src/**/*.{js,jsx,ts,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        primary: '#3B82F6',
        background: '#F8FAFC',
        surface: '#FFFFFF',
        'text-primary': '#1E293B',
        'text-secondary': '#64748B',
        'border-color': '#E2E8F0',
        success: '#10B981',
        warning: '#F59E0B',
        info: '#0EA5E9',
        danger: '#EF4444',
      },
      fontFamily: {
        sans: ['Inter', 'sans-serif'],
        mono: ['Fira Code', 'Roboto Mono', 'monospace'],
      }
    },
  },
  plugins: [],
}
