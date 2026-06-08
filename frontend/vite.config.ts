import path from "path";

import react from "@vitejs/plugin-react";
import { defineConfig } from "vite";

// Прод-сборка кладётся в media/static_spa, откуда её отдаёт Django (см. Фазу E).
export default defineConfig(({ command }) => ({
  // В проде Django/WhiteNoise отдаёт ассеты по /static/; в dev — корень.
  base: command === "build" ? "/static/" : "/",
  plugins: [react()],
  resolve: {
    alias: {
      "@": path.resolve(__dirname, "./src"),
    },
  },
  build: {
    outDir: path.resolve(__dirname, "../media/static_spa"),
    emptyOutDir: true,
    manifest: true,
  },
  server: {
    port: 5173,
    proxy: {
      // В dev-режиме API проксируется на Django, чтобы cookie/CSRF были first-party.
      "/api": {
        target: "http://127.0.0.1:8000",
        changeOrigin: false,
      },
    },
  },
}));
