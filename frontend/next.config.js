/** @type {import('next').NextConfig} */
const nextConfig = {
    reactStrictMode: true,
    output: 'export',
    async rewrites() {
        return [
            {
                source: '/api/:path*',
                destination: process.env.BACKEND_URL
                    ? `${process.env.BACKEND_URL}/api/:path*`
                    : 'http://localhost:8000/api/:path*',
            },
        ];
    },
};

module.exports = nextConfig;
