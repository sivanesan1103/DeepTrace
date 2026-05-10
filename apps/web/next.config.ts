import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  output: 'standalone',
  serverExternalPackages: ['neo4j', 'faiss', 'opencv'],
  images: {
    remotePatterns: [
      {
        hostname: '**',
      },
    ],
  },
  env: {},
};

export default nextConfig;
