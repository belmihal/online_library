import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

// Простая и понятная конфигурация сборщика Vite для React 18 (.jsx)
export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    open: false,
    // Проксируем запросы /api на наш Django-бэкенд (http://127.0.0.1:8000),
    // если фронтенд обращается по относительному пути
    proxy: {
      '/api': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true
      }
    }
  }
});
