/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ["./grocery/templates/**/*.html", "./grocery/static/**/*.js"],
  theme: {
    extend: {
      colors: {
        avocado: "#568203",
        "avocado-dark": "#3D5C02",
        "avocado-light": "#8BB174",
        cream: "#F7F4E9",
      },
    },
  },
  plugins: [],
};
