import type { NextConfig } from "next";
import path from "path";

const nextConfig: NextConfig = {
  /* config options here */
  
  // Environment variables configuration
  env: {
    CUSTOM_KEY: process.env.CUSTOM_KEY,
  },
  
  // Webpack configuration for path aliases
  webpack: (config) => {
    config.resolve.alias = {
      ...config.resolve.alias,
      '@': path.resolve(__dirname),
      '@/lib': path.resolve(__dirname, 'lib'),
      '@/components': path.resolve(__dirname, 'components'),
      '@/app': path.resolve(__dirname, 'app'),
    };
    return config;
  },
  
  // Public runtime configuration for client-side access
  publicRuntimeConfig: {
    apiUrl: process.env.NEXT_PUBLIC_API_URL,
    environment: process.env.NEXT_PUBLIC_ENVIRONMENT,
  },
  
  // Image optimization configuration
  images: {
    domains: [],
    unoptimized: false,
  },
  
  // Security headers
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
  
  // Redirects configuration
  async redirects() {
    return [
      // Add any redirects here if needed
    ];
  },
  
  // Output configuration for different deployment environments
  output: process.env.NODE_ENV === 'production' ? 'standalone' : undefined,
  
  // Experimental features
  experimental: {
    // Enable any experimental features here
  },
};

export default nextConfig;
