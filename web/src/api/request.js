import axios from 'axios'
import notify from "@/components/notify.js";

const instance = axios.create({
  baseURL: import.meta.env.VITE_APP_BASE_URL + import.meta.env.VITE_APP_BASE_API,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json'
  }
})

// 请求拦截器
instance.interceptors.request.use(
  config => {
    // 在发送请求之前做些什么
    // 例如添加 token
    const token = localStorage.getItem('token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  error => {
    // 对请求错误做些什么
    return Promise.reject(error)
  }
)

// 响应拦截器
instance.interceptors.response.use(
  response => {
    return response.data
  },
  error => {
    if (error.response) {
      switch (error.response.status) {
        case 400:
          notify.error(error.response.data.msg)
          break
        case 401:
          notify.error("登录过期")
          localStorage.removeItem('token')
          setTimeout(() => {
            window.location.reload()
          }, 1000)
          break
        case 500:
          notify.error(error.response.data.msg)
          break
      }
    }
    return Promise.reject(error)
  }
)

export default instance
