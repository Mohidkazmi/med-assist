import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    host: true, // Bind to all interfaces (necessary for Docker port mapping)
    port: 5173,
    watch: {
      usePolling: true, // Enables HMR file change detection in VMs/Docker containers
    },
  },
});
