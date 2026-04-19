import path from "path";
import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import tailwindcss from "@tailwindcss/vite";

export default defineConfig({
  plugins: [react(), tailwindcss()],
  resolve: {
    alias: {
      "@": path.resolve(__dirname, "./src"),
    },
  },
  base: "./",
  build: {
    outDir: "../../data/gui",
    emptyOutDir: true,
    rollupOptions: {
      output: {
        format: "iife",
        entryFileNames: "main.js",
        assetFileNames: "[name][extname]",
        chunkFileNames: "[name].js",
        inlineDynamicImports: true,
      },
    },
  },
  server: {
    proxy: {
      "/ws": {
        target: "ws://127.0.0.1:24880",
        ws: true,
      },
      "/api": {
        target: "http://127.0.0.1:24880",
      },
    },
  },
});
