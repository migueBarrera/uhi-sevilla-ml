import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import copyAssetsPlugin from './copy-assets-plugin.js';

// https://vite.dev/config/
export default defineConfig({
  plugins: [react(), copyAssetsPlugin()],
})
