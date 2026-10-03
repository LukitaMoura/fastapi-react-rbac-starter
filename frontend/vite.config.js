import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import tailwindcss from '@tailwindcss/vite';

export default defineConfig({
  plugins: [react(), tailwindcss()],
  server: {
    port: 5173,
    // Em dev, /api vai para o FastAPI; em produção o proxy reverso faz o mesmo
    proxy: { '/api': 'http://127.0.0.1:8000' },
  },
});
