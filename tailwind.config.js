/** @type {import('tailwindcss').Config} */
module.exports = {
    content: [
        "./templates/**/*.html",
        "./static/js/**/*.js"
    ],
    theme: {
        extend: {
            colors: {
                brand: {
                    DEFAULT: '#2563eb',
                    500: '#2563eb',
                    600: '#1d4ed8',
                    light: '#60a5fa' // brand-2
                },
                muted: '#475569',
                bg: {
                    0: '#f8fbff',
                    1: '#eef4ff',
                    2: '#e7efff'
                }
            },
            fontFamily: {
                sans: ['Inter', 'sans-serif'], // You might want to add a font link for Inter if not present
            },
            backgroundImage: {
                'hero-pattern': "/static/image/background.png",
            }
        },
    },
    plugins: [],
}
