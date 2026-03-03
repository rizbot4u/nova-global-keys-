import type { NextConfig } from 'next';

const nextConfig: NextConfig = {
  eslint: {
    ignoreDuringBuilds: true,
  },
  typescript: {
    ignoreBuildErrors: true,
  },
  // Add this to fix cross-origin warnings
  allowedDevOrigins: ['localhost', '31.97.220.195', 'www.novatradingkeys.com', 'novatradingkeys.com'],
};

export default nextConfig;
