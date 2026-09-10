import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

// https://vite.dev/config/
export default defineConfig(({ command }) => (
  {
    plugins: [vue()],
    build: {
        outDir: command === "serve" ? "../public" : "./dist",
        emptyOutDir: true,
      },
    server: {
      proxy: {
        "/socket": "ws://localhost:8000",
        "/api": "http://localhost:8000",
        "/static/": "http://localhost:8000",
      }
    }
  }
))
