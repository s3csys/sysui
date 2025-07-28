import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import path from 'path'
import { loadEnv } from 'vite'

// https://vitejs.dev/config/
export default defineConfig(({ mode }) => {
  // Load env file based on `mode` in the current working directory.
  // Set the third parameter to '' to load all env regardless of the `VITE_` prefix.
  const env = loadEnv(mode, process.cwd(), '')
  
  // Parse allowed hosts from env variable
  const allowedHosts = env.VITE_SERVER_ALLOWED_HOSTS ? 
    env.VITE_SERVER_ALLOWED_HOSTS.split(',').map(host => host.trim()) : 
    []
    
  return {
  plugins: [react()],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },
  server: {
    host: env.VITE_SERVER_HOST || '0.0.0.0',
    port: parseInt(env.VITE_SERVER_PORT || '5173'),
    allowedHosts: allowedHosts,
    proxy: {
      '/api': {  // Proxy API requests to the backend
        target: env.VITE_API_URL || 'http://127.0.0.1:8000',
        changeOrigin: true,
        secure: false,
        // The backend expects requests at /api/v1/auth/register
        rewrite: (path) => path.replace(/^\/api/, '/api/v1'),
      }
    }
  },
  test: {
    globals: true,
    environment: 'jsdom',
    setupFiles: ['./src/test/setup.ts'],
  },
  }
})