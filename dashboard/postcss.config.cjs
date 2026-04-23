const tailwindcss = require('tailwindcss');
const nesting = require('tailwindcss/nesting');
const autoprefixer = require('autoprefixer');

module.exports = {
	plugins: [nesting(), tailwindcss(), autoprefixer]
};
