/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
    "./app/components/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}",
    "./pages/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        dark: {
          950: '#060609',
          900: '#0A0A0F',
          800: '#12121A',
          700: '#1C1C28',
          600: '#2A2A3C',
        },
        gold: {
          500: '#F59E0B',
          400: '#FBBF24',
          300: '#FDE68A',
          bronze: '#D97706',
          rose: '#FB7185',
        }
      }
    },
  },
  plugins: [],
}
