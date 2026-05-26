// Simple Vite plugin to copy src/assets to dist/assets after build
import { promises as fs } from 'fs';
import path from 'path';

export default function copyAssetsPlugin() {
  return {
    name: 'copy-assets-plugin',
    closeBundle: async () => {
      const srcDir = path.resolve('src/assets');
      const distDir = path.resolve('dist/assets');
      async function copyDir(src, dest) {
        await fs.mkdir(dest, { recursive: true });
        const entries = await fs.readdir(src, { withFileTypes: true });
        for (const entry of entries) {
          const srcPath = path.join(src, entry.name);
          const destPath = path.join(dest, entry.name);
          if (entry.isDirectory()) {
            await copyDir(srcPath, destPath);
          } else {
            await fs.copyFile(srcPath, destPath);
          }
        }
      }
      await copyDir(srcDir, distDir);
      console.log('Assets copiados a dist/assets');
    }
  };
}
