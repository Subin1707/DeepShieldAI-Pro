export default {
  content: ["./index.html", "./src/**/*.{js,jsx}"],
  theme: {
    extend: {
      colors: {
        shield: {
          bg: "#020617",
          panel: "#0f172a",
          line: "#1e293b",
          cyan: "#22d3ee",
          blue: "#38bdf8",
          danger: "#f87171",
          warning: "#facc15",
          success: "#4ade80",
        },
      },
      boxShadow: {
        glow: "0 0 30px rgba(34, 211, 238, 0.16)",
      },
    },
  },
  plugins: [],
};
