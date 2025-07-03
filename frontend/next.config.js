/** @type {import('next').NextConfig} */
const nextConfig = {
  /* config options here */
  typescript: {
    // !! WARN !!
    // Dangerously allow production builds to successfully complete even if
    // your project has type errors.
    // !! WARN !!
    ignoreBuildErrors: true,
  },
  eslint: {
    // Warning: This allows production builds to successfully complete even if
    // your project has ESLint errors.
    ignoreDuringBuilds: true,
  },  async rewrites() {
    return [
      {
        source: '/api/:path*',
        destination: `${process.env.API_URL || 'http://127.0.0.1:8089'}/api/:path*`,
      },
      // Add specific proxy bypass for authentication endpoint
      {
        source: '/auth-proxy/:path*',
        destination: 'http://127.0.0.1:8088/api/v1/auth/:path*',
      },
      // Add specific proxy bypass for companies endpoints
      {
        source: '/companies-proxy/:path*',
        destination: 'http://127.0.0.1:8088/api/v1/companies/:path*',
      },
      // Add additional debugging route to diagnose API issues
      {
        source: '/api-debug/:path*',
        destination: 'http://127.0.0.1:8088/api/v1/:path*',
      },
      // Direct company proxy for absolute certainty (no path mangling)
      {
        source: '/direct-company-api/:id',
        destination: 'http://127.0.0.1:8088/api/v1/companies/:id',
      },
      // Proxy bypass for token verification (fix for the current issue)
      {
        source: '/verify-proxy/:path*',
        destination: 'http://127.0.0.1:8088/api/v1/auth/:path*',
      },
    ];
  },
  images: {
    remotePatterns: [
      {
        protocol: 'https',
        hostname: 'picsum.photos',
        port: '',
        pathname: '/**',
      },
      {
        protocol: 'https',
        hostname: 'source.unsplash.com',
        port: '',
        pathname: '/**',
      },
      {
        protocol: 'https',
        hostname: 'images.unsplash.com',
        port: '',
        pathname: '/**',
      },
      {
        protocol: 'https',
        hostname: 'unsplash.com',
        port: '',
        pathname: '/**',
      },
      {
        protocol: 'https',
        hostname: 'via.placeholder.com',
        port: '',
        pathname: '/**',
      },
      {
        protocol: 'https',
        hostname: 'placeholder.com',
        port: '',
        pathname: '/**',
      },
      {
        protocol: 'https',
        hostname: 'example.com',
        port: '',
        pathname: '/**',
      },
      // Allow common image CDNs and placeholder services
      {
        protocol: 'https',
        hostname: 'dummyimage.com',
        port: '',
        pathname: '/**',
      },
      {
        protocol: 'https',
        hostname: 'placehold.it',
        port: '',
        pathname: '/**',
      },
      {
        protocol: 'https',
        hostname: 'placeimg.com',
        port: '',
        pathname: '/**',
      },
    ],
  },
  // output: 'standalone',
};

module.exports = nextConfig;
