import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

export default defineConfig({
  plugins: [vue()],
  server: {
    port: 5173, // 前端端口
    proxy: {
      // 匹配所有以/api开头的请求，转发到后端
      '/api': {
        target: 'http://127.0.0.1:8000', // 你的Python后端地址
        changeOrigin: true, // 关键：开启跨域代理
        ws: true, // 可选，支持websocket
        rewrite: (path) => path.replace(/^\/api/, '') // 可选：如果后端接口不带/api，就加这个（把前端的/api去掉再转发）
      }
    }
  }
})