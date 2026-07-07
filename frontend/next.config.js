/** @type {import('next').NextConfig} */

// The frontend never calls the backend's URL directly from the browser.
// Instead it calls its own origin at /api/*, and Next.js's server-side
// rewrite proxies that to wherever the backend actually lives (read from
// BACKEND_INTERNAL_URL, a plain runtime env var - not a NEXT_PUBLIC_ one, so
// it does NOT need to be known at Docker build time and can be changed by
// just restarting the container). Two benefits:
//   1. No CORS configuration needed at all - the browser only ever talks to
//      one origin.
//   2. Works identically whether the backend is a sibling docker-compose
//      service (http://backend:8000) or a separately-hosted Render service
//      (https://<backend-service>.onrender.com) - only the env var changes.
const nextConfig = {
  reactStrictMode: true,
  async rewrites() {
    const raw = process.env.BACKEND_INTERNAL_URL || "http://localhost:8000";
    // Accept either a full URL (docker-compose sets "http://backend:8000")
    // or a bare "host:port" pair (Render's Blueprint fromService wiring
    // only injects host/hostport, with no scheme) and normalize to a URL.
    const hasScheme = raw.indexOf("://") !== -1;
    const backend = hasScheme ? raw : "http://" + raw;
    return [
      {
        source: "/api/:path*",
        destination: backend + "/api/:path*",
      },
    ];
  },
};

module.exports = nextConfig;
