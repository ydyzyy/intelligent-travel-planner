import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import { resolve } from 'path'
import { loadEnv } from 'vite'

// https://vite.dev/config/
export default defineConfig(({ mode }) => {
  // 从项目根目录加载 .env 文件
  const rootEnvPath = resolve(__dirname, '..')
  const env = loadEnv(mode, rootEnvPath, '')
  
  return {
    plugins: [vue()],
    resolve: {
      alias: {
        '@': resolve(__dirname, 'src')
      }
    },
    define: {
      // 将根目录的环境变量注入到前端代码中
      // Vite会自动处理以VITE_开头的环境变量
      // 这里手动映射AMAP_API_KEY为前端可用的格式
      'import.meta.env.VITE_AMAP_WEB_JS_KEY': JSON.stringify(env.AMAP_API_KEY || ''),
    },
    server: {
      port: 5173,
      proxy: {
        '/api': {
          target: 'http://localhost:8000',
          changeOrigin: true
        }
      }
    }
  }
})