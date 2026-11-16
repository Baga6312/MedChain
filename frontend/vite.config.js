import { defineConfig, loadEnv } from 'vite';
import react from '@vitejs/plugin-react';

export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd(), '');
  return {
    plugins: [react()],
    test: {
  environment: 'jsdom',
  globals: true,
  setupFiles: './tests/setup.js',
  include: ['tests/**/*.test.{js,jsx}']
},
    server: { proxy: { '/api': env.VITE_API_PROXY_TARGET } },
  };
});