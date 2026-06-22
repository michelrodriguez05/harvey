export default {
  content: ["./index.html", "./src/**/*.{js,jsx}"],
  theme: {
    extend: {
      colors: {
        harvey: {
          50: "#f0f4ff",
          100: "#dbe4ff",
          400: "#74c0fc",
          500: "#4c6ef5",
          600: "#3b5bdb",
          700: "#2f4ac0",
          900: "#1a2b7a",
        },
        yarbis: {
          cyan: "#22d3ee",
          indigo: "#818cf8",
        },
      },
      fontFamily: {
        display: ["Segoe UI", "system-ui", "sans-serif"],
      },
      animation: {
        "fade-in": "fadeIn 0.4s ease-out",
      },
      keyframes: {
        fadeIn: {
          "0%": { opacity: "0", transform: "translateY(8px)" },
          "100%": { opacity: "1", transform: "translateY(0)" },
        },
      },
    },
  },
  plugins: [],
};
