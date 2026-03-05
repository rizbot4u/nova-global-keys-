import type { NextConfig } from 'next';

const nextConfig: NextConfig = {
  // We removed the eslint block because it's no longer supported here
  typescript: {
    ignoreBuildErrors: true,
  },
  // Keeps your VPS memory usage lower and stability higher
  output: 'standalone',
  
  // Cross-origin settings
  allowedDevOrigins: ['localhost', '31.97.220.195', 'www.novatradingkeys.com', 'novatradingkeys.com'],
};

export default nextConfig;
