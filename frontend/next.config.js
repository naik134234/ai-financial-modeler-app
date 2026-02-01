/** @type {import('next').NextConfig} */
const nextConfig = {
    reactStrictMode: true,
    output: 'export',
    // Rewrites are NOT supported in static export
    // We handle API routing via NEXT_PUBLIC_API_URL in the frontend code
    // async rewrites() { ... }
};

module.exports = nextConfig;
