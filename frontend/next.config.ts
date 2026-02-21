import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  async rewrites() {
    return [
      {
        source: "/api/:path*",
        destination: "http://localhost:8000/api/:path*",
      },
    ];
  },
  webpack: (config, { dev }) => {
    if (dev) {
      config.watchOptions = {
        ignored: [
          "**/node_modules/**",
          "**/.git/**",
          "**/venv/**",
          "**/data/**",
          "**/api/**",
          "**/src/**",
          "**/tests/**",
          "**/__pycache__/**",
          "**/*.db",
          "**/*.pyc",
        ],
      };
    }
    return config;
  },
};

export default nextConfig;
