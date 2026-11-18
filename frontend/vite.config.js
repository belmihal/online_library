import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

// Простая конфигурация сборщика Vite для базового React 18 (.jsx)
export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    open: false,
    proxy: {
      '/api': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true
      }
    }
  }
});
