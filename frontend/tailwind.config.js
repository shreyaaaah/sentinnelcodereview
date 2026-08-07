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
          950: '#05080E',
          900: '#0A0E17',
          800: '#111827',
          700: '#1A2333',
          600: '#25334D',
        },
        cyber: {
          emerald: '#00F59B',
          cyan: '#00D2FF',
          teal: '#0D9488',
          rose: '#FF3366',
          amber: '#FFB800',
          silver: '#94A3B8',
        }
      }
    },
  },
  plugins: [],
}
