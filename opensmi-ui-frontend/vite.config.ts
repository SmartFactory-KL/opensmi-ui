import { fileURLToPath, URL } from "node:url";

import { defineConfig } from "vite";
import vue from "@vitejs/plugin-vue";
import vueDevTools from "vite-plugin-vue-devtools";

import tailwindcss from "@tailwindcss/vite";

// https://vite.dev/config/
export default defineConfig(({ command }) => ({
  plugins: [vue(), vueDevTools(), tailwindcss()],
  resolve: {
    alias: {
      "@": fileURLToPath(new URL("./src", import.meta.url)),
    },
  },
  build: {
    outDir: command === "serve" ? "../public" : "./dist",
    emptyOutDir: true,
  },
  server: {
    proxy: {
      "/socket": "ws://localhost:8000",
      "/api": "http://localhost:8000",
      "/static": "http://localhost:8000",
    },
  },
}));
