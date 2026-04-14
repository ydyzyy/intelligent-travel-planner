import axios from 'axios'
import type { TripFormData, TripPlanResponse } from '@/types'

// 使用Vite的代理配置,不需要手动指定API_BASE_URL
// 开发环境下通过vite.config.ts的proxy转发到后端
const API_BASE_URL = import.meta.env.DEV ? '' : (import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000')

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 180000, // 3分钟超时（LLM生成可能需要60-90秒）
  headers: {
    'Content-Type': 'application/json'
  }
})

// 请求拦截器
apiClient.interceptors.request.use(
  (config) => {
    console.log('发送请求:', config.method?.toUpperCase(), config.url)
    return config
  },
  (error) => {
    console.error('请求错误:', error)
    return Promise.reject(error)
  }
)

// 响应拦截器
apiClient.interceptors.response.use(
  (response) => {
    console.log('收到响应:', response.status, response.config.url)
    return response
  },
  (error) => {
    console.error('响应错误:', error.response?.status, error.message)
    return Promise.reject(error)
  }
)

/**
 * 生成旅行计划
 */
export async function generateTripPlan(formData: TripFormData): Promise<TripPlanResponse> {
  try {
    console.log('🚀 开始生成旅行计划...')
    console.log('请求数据:', formData)
    
    const response = await apiClient.post<TripPlanResponse>('/api/trip/plan', formData)
    
    console.log('✅ 收到响应:', response.data)
    return response.data
  } catch (error: any) {
    console.error('❌ 生成旅行计划失败:', error)
    
    // 区分不同类型的错误
    if (error.code === 'ECONNABORTED') {
      throw new Error('请求超时，请稍后重试。LLM生成可能需要较长时间。')
    }
    
    if (error.response) {
      const status = error.response.status
      const detail = error.response.data?.detail
      
      switch (status) {
        case 400:
          throw new Error(`请求参数错误: ${detail}`)
        case 422:
          throw new Error(`数据验证失败: ${detail}`)
        case 500:
          throw new Error(`服务器内部错误: ${detail}`)
        case 503:
          throw new Error('服务暂时不可用，请稍后重试')
        default:
          throw new Error(detail || `请求失败 (${status})`)
      }
    }
    
    if (error.request) {
      throw new Error('网络连接失败，请检查网络设置或后端服务是否启动')
    }
    
    throw new Error(error.message || '未知错误，请重试')
  }
}

/**
 * 健康检查
 */
export async function healthCheck(): Promise<any> {
  try {
    const response = await apiClient.get('/health')
    return response.data
  } catch (error: any) {
    console.error('健康检查失败:', error)
    throw new Error(error.message || '健康检查失败')
  }
}

export default apiClient

