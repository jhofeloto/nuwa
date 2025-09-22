import type { NextConfig } from "next";
import TsconfigPathsPlugin from 'tsconfig-paths-webpack-plugin';
import { i18n } from "./next-i18next.config";

const nextConfig: NextConfig = {
  productionBrowserSourceMaps: true,
  i18n,
  
  // Enable static file serving for locales directory
  async rewrites() {
    return [
      {
        source: '/locales/:locale/:file',
        destination: '/public/locales/:locale/:file',
      },
    ];
  },
  
  webpack: (config, { isServer }) => {
    // Ensure `resolve.plugins` exists
    config.resolve.plugins = [
      ...(config.resolve.plugins || []), // Keep existing plugins
      new TsconfigPathsPlugin({
        configFile: './tsconfig.json', // Adjust the path to your tsconfig.json if necessary
      }),
    ];
    
    config.experiments = {
      ...config.experiments,
      asyncWebAssembly: true, // Enable async WebAssembly
      topLevelAwait: true,
      layers: true
    };
    if (!isServer) {
      config.output.environment = { ...config.output.environment, asyncFunction: true };
    }
    
    return config;
  },
};

export default nextConfig;
