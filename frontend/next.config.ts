import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // FIX #5 / #15: Expose API base URL as a public env var so no page ever
  // hardcodes localhost:8000. Set NEXT_PUBLIC_API_URL in your .env.local for dev
  // and in your host's environment variables for production.
  env: {
    NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000",
  },
};

export default nextConfig;
