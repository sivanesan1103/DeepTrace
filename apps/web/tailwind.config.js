/** @type {import('tailwindcss').Config} */
export default {
  darkMode: 'class',
  content: [
    './src/app/**/*.{js,ts,jsx,tsx}',
    './src/components/**/*.{js,ts,jsx,tsx}',
  ],
  theme: {
    extend: {
      colors: {
        background: '#0a0a0a',
        foreground: '#e2e8f0',
        primary: {
          DEFAULT: '#1e40af',
          glow: 'rgba(30, 64, 175, 0.5)',
        },
        secondary: '#334155',
        accent: '#06b6d4',
        destructive: '#ef4444',
        muted: '#1e293b',
        card: '#111827',
        cardForeground: '#f1f5f9',
        border: '#1e293b',
      },
      borderRadius: {
        lg: '0.5rem',
      },
      fontFamily: {
        sans: ['Inter', 'sans-serif'],
        mono: ['JetBrains Mono', 'monospace'],
      },
      keyframes: {
        'glow-pulse': {
          '0%, 100%': { opacity: '1' },
          '50%': { opacity: '0.5' },
        },
        scanline: {
          '0%': { backgroundPosition: '0 0' },
          '100%': { backgroundPosition: '0 100%' },
        },
        'fade-in': {
          '0%': { opacity: '0' },
          '100%': { opacity: '1' },
        },
      },
      animation: {
        'glow-pulse': 'glow-pulse 2s ease-in-out infinite',
        scanline: 'scanline 4s linear infinite',
        'fade-in': 'fade-in 0.5s ease-in-out',
      },
    },
  },
  plugins: [
    require('@tailwindcss/typography'),
    require('@tailwindcss/forms'),
  ],
};