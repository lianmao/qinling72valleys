import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import tailwindcss from '@tailwindcss/vite'

// GitHub Pages 二级路径托管：base 必须与仓库名一致
export default defineConfig({
  base: '/qinling72valleys/',
  plugins: [vue(), tailwindcss()],
  build: { target: 'es2020', chunkSizeWarningLimit: 900 },
})
