import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

// 本地开发代理目标：默认本机后端；要测试线上后端时用 VITE_API_BASE_URL 覆盖为临时公网地址
const API_BASE_URL = process.env.VITE_API_BASE_URL || 'http://localhost:8000'

// 仅本地开发生效：将 /api 代理到后端；生产构建不受影响（构建产物使用 /api 同源）
export default defineConfig({
  plugins: [vue()],
  server: {
    port: 5173,
    proxy: {
      '/api': {
        target: API_BASE_URL,
        changeOrigin: true,
      },
    },
  },
})
