import { fileURLToPath, URL } from 'node:url'

import { defineConfig, loadEnv } from 'vite'
import vue from '@vitejs/plugin-vue'
import vueDevTools from 'vite-plugin-vue-devtools'

export default defineConfig(({ mode }) => {
  // 加载环境变量
  const env = loadEnv(mode, process.cwd())

  // 将端口转换为数字
  const port = parseInt(env.VITE_APP_PORT) || 8882

  return {
    server: {
      port: port, // 使用从环境变量中获取的端口
      host: true
    },
    plugins: [
      vue(),
      vueDevTools()
    ],
    optimizeDeps: {
      include: ['animejs']
    },
    resolve: {
      alias: {
        '@': fileURLToPath(new URL('./src', import.meta.url))
      }
    }
  }
})
