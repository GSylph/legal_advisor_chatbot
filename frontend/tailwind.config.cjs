/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ["./index.html", "./src/**/*.{js,jsx}"],
  theme: {
    extend: {
      fontFamily: {
        ui:      ['Space Grotesk', 'system-ui', 'sans-serif'],
        display: ['Fraunces', 'Georgia', 'serif'],
      },
      boxShadow: {
        card:         '0 2px 12px rgba(0,0,0,0.07), 0 1px 3px rgba(0,0,0,0.05)',
        'card-focus': '0 4px 24px rgba(0,0,0,0.12), 0 2px 6px rgba(0,0,0,0.08)',
      },
      borderRadius: {
        card: '1.25rem',
      },
      width: {
        sidebar:      '64px',
        'sidebar-open': '220px',
      },
      transitionTimingFunction: {
        smooth: 'cubic-bezier(0.4, 0, 0.2, 1)',
      },
      colors: {
        brand: {
          bg:      '#EBEBEB',
          surface: '#FFFFFF',
          ink:     '#1A1A1A',
          muted:   '#71717A',
        },
      },
      keyframes: {
        'hero-fade': {
          from: { opacity: '0', transform: 'translateY(16px)' },
          to:   { opacity: '1', transform: 'translateY(0)' },
        },
        'msg-in': {
          from: { opacity: '0', transform: 'translateY(10px)' },
          to:   { opacity: '1', transform: 'translateY(0)' },
        },
        'welcome-float': {
          '0%, 100%': { transform: 'translateY(0px)' },
          '50%':      { transform: 'translateY(-4px)' },
        },
        'dot-bounce': {
          '0%, 80%, 100%': { transform: 'translateY(0)', opacity: '0.4' },
          '40%':           { transform: 'translateY(-5px)', opacity: '1' },
        },
        'send-pulse': {
          '0%':   { boxShadow: '0 0 0 0 rgba(26,26,26,0.35)' },
          '70%':  { boxShadow: '0 0 0 7px rgba(26,26,26,0)' },
          '100%': { boxShadow: '0 0 0 0 rgba(26,26,26,0)' },
        },
        'status-up': {
          from: { transform: 'translateY(100%)', opacity: '0' },
          to:   { transform: 'translateY(0)',    opacity: '1' },
        },
        'trace-expand': {
          from: { opacity: '0', transform: 'translateY(-6px)' },
          to:   { opacity: '1', transform: 'translateY(0)' },
        },
        'blink': {
          '0%, 100%': { opacity: '1' },
          '50%':      { opacity: '0' },
        },
      },
      animation: {
        'msg-in':        'msg-in 320ms cubic-bezier(0.34,1.56,0.64,1) both',
        'welcome-float': 'welcome-float 5s ease-in-out infinite',
        'dot-bounce-1':  'dot-bounce 1.2s ease-in-out infinite',
        'dot-bounce-2':  'dot-bounce 1.2s ease-in-out 0.2s infinite',
        'dot-bounce-3':  'dot-bounce 1.2s ease-in-out 0.4s infinite',
        'send-pulse':    'send-pulse 600ms ease-out forwards',
        'status-up':     'status-up 300ms ease-out both',
        'trace-expand':  'trace-expand 220ms ease-out both',
        'blink':         'blink 0.9s step-start infinite',
        'hero-fade':     'hero-fade 700ms cubic-bezier(0.34,1.2,0.64,1) both',
        'hero-fade-2':   'hero-fade 700ms 120ms cubic-bezier(0.34,1.2,0.64,1) both',
        'hero-fade-3':   'hero-fade 700ms 240ms cubic-bezier(0.34,1.2,0.64,1) both',
      },
    },
  },
  plugins: [],
};
