import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

export default defineConfig({
  plugins: [react()],
  build: {
    target: "es2022",
    chunkSizeWarningLimit: 1100,
    rollupOptions: {
      output: {
        // Long-lived vendor chunks: app deploys don't invalidate the 3D engine cache.
        manualChunks(id) {
          if (!id.includes("node_modules")) return undefined;
          if (/three|@react-three|troika|maath|camera-controls|meshline|stats-gl|suspend-react|its-fine|zustand/.test(id)) return "vendor-3d";
          if (/motion|framer/.test(id)) return "vendor-motion";
          if (/react-router|react-dom|scheduler|\/react\//.test(id)) return "vendor-react";
          return undefined;
        },
      },
    },
  },
  server: {
    proxy: {
      "/api": {
        target: "http://127.0.0.1:8000",
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api/, ""),
      },
    },
  },
});
