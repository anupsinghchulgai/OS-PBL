/** @type {import('tailwindcss').Config} */
export default {
  darkMode: "class",
  content: ["./index.html", "./src/**/*.{js,jsx}"],
  theme: {
    extend: {
      colors: {
        navy: { 950: "#06101f", 900: "#0a1730", 800: "#10213f" },
        cyanx: "#22d3ee",
        purplex: "#8b5cf6"
      },
      boxShadow: {
        panel: "0 18px 60px rgba(2, 8, 23, .20)"
      }
    }
  },
  plugins: []
};
