import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // General config
  reactStrictMode: true,

  // Use .env.* files per Next.js docs; NEXT_PUBLIC_* are automatically exposed
  // Ref: https://nextjs.org/docs/app/building-your-application/configuring/environment-variables
  // No inline env mapping needed here

  // Security headers (kept as-is)
  async headers() {
    return [
      {
        source: '/api/:path*',
        headers: [
          {
            key: 'Access-Control-Allow-Origin',
            value: process.env.NODE_ENV === 'development' ? '*' : 'https://amazon-sales-agent.onrender.com',
          },
          {
            key: 'Access-Control-Allow-Methods',
            value: 'GET, POST, PUT, DELETE, OPTIONS',
          },
          {
            key: 'Access-Control-Allow-Headers',
            value: 'Content-Type, Authorization',
          },
        ],
      },
    ];
  },

  // Redirects configuration (placeholder)
  async redirects() {
    return [];
  },

  // Image optimization configuration
  images: {
    domains: [],
    unoptimized: false,
  },
};

export default nextConfig;
