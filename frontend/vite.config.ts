import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

export default defineConfig({
  plugins: [react()],
  server: {
    host: true,
    port: 5173,
    proxy: {
      '^/(api|auth|report|attachments)': {
        target: 'http://127.0.0.1:8000',  // куда слушает FastAPI
        changeOrigin: false,
        ws: true,
        secure: false,
        timeout: 60000,
        proxyTimeout: 60000,
      },
    },
  },
});
