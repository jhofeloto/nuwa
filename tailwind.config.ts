/** @type {import('tailwindcss').Config} */
const { fontFamily } = require('tailwindcss/defaultTheme')
module.exports = {
  content: [
    "./src/**/*.{js,jsx,ts,tsx}",
    "./app/**/*.{js,jsx,ts,tsx}",
    "./components/**/*.{js,jsx,ts,tsx}",
    "./public/index.html",
  ],
  darkMode: ["class"],
  theme: {
    extend: {
      fontFamily: {
        sans: ['var(--font-lusitana)', ...fontFamily.serif],
        serif: ['var(--font-lusitana)', ...fontFamily.serif],
        lusitana: ['var(--font-lusitana)', ...fontFamily.serif],
        mono: fontFamily.mono,
      },
      colors: {
        mint: {
          1: 'var(--mint-1)',
          2: 'var(--mint-2)',
          3: 'var(--mint-3)',
          4: 'var(--mint-4)',
          5: 'var(--mint-5)',
          6: 'var(--mint-6)',
          7: 'var(--mint-7)',
          8: 'var(--mint-8)',
          9: 'var(--mint-9)',
          10: 'var(--mint-10)',
          11: 'var(--mint-11)',
          12: 'var(--mint-12)',
        },
        'logo-deep': '#0A5E5C', // Deep teal-blue at the bottom
        'logo-mid': '#16A396', // Mid teal shade
        'logo-light': '#21DDB8', // Bright mint/turquoise at the top
        'logo-accent': '#FFFFFF', // White sparkle/dots
        
        background: "hsl(var(--background))",
        foreground: "hsl(var(--foreground))",
        border: "hsl(var(--border))",
        
        // Add semantic color tokens
        primary: {
          DEFAULT: "var(--mint-9)",
          foreground: "white",
        },
        secondary: {
          DEFAULT: "var(--mint-3)",
          foreground: "var(--mint-11)",
        },
        accent: {
          DEFAULT: "var(--mint-8)",
          foreground: "var(--mint-12)",
        },
        muted: {
          DEFAULT: "#f9fafb",
          foreground: "#6b7280",
        },
      },
      gradientColorStops: {
        'logo-gradient-from': '#0A5E5C', // Deep teal-blue
        'logo-gradient-via': '#16A396', // Mid teal
        'logo-gradient-to': '#21DDB8', // Bright mint/turquoise
      },
      backgroundImage: {
        'logo-gradient': 'linear-gradient(to top, #0A5E5C, #16A396, #21DDB8)',
        'gradient-mint-light': 'linear-gradient(135deg, var(--mint-3) 0%, var(--mint-7) 50%, var(--mint-11) 100%)',
        'gradient-mint-dark': 'linear-gradient(135deg, var(--mint-3) 0%, var(--mint-5) 50%, var(--mint-8) 100%)',
      },
      borderRadius: {
        lg: "var(--radius)",
        md: "calc(var(--radius) - 2px)",
        sm: "calc(var(--radius) - 4px)",
      },
      keyframes: {
        "accordion-down": {
          from: { height: 0 },
          to: { height: "var(--radix-accordion-content-height)" },
        },
        "accordion-up": {
          from: { height: "var(--radix-accordion-content-height)" },
          to: { height: 0 },
        },
      },
      animation: {
        "accordion-down": "accordion-down 0.2s ease-out",
        "accordion-up": "accordion-up 0.2s ease-out",
      },
    },
  },
  plugins: [],
}