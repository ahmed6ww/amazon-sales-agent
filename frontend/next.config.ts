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

  // API proxy for development
  async rewrites() {
    return [
      {
        source: '/api/:path*',
        destination: `${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/api/:path*`,
      },
    ];
  },

  // Image optimization configuration
  images: {
    remotePatterns: [
      {
        protocol: 'https',
        hostname: 'm.media-amazon.com',
        port: '',
        pathname: '/images/**',
      },
      {
        protocol: 'https',
        hostname: 'images-na.ssl-images-amazon.com',
        port: '',
        pathname: '/images/**',
      },
    ],
    unoptimized: false,
  },
};

export default nextConfig;
