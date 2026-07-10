 import axios from 'axios'
 import { ElMessage } from 'element-plus'
 
 const request = axios.create({
   baseURL: '/api/v1',
   timeout: 30000,
   headers: {
     'Content-Type': 'application/json',
   },
 })
 
 // Request interceptor: add auth token
 request.interceptors.request.use(
   (config) => {
     const token = localStorage.getItem('access_token')
     if (token) {
       config.headers.Authorization = `Bearer ${token}`
     }
     return config
   },
   (error) => Promise.reject(error)
 )
 
 // Response interceptor: handle errors
 request.interceptors.response.use(
   (response) => response.data,
   (error) => {
     const status = error.response?.status
     const detail = error.response?.data?.detail || '请求失败'
     
     if (status === 401) {
       localStorage.removeItem('access_token')
       localStorage.removeItem('user_info')
       window.location.hash = '#/login'
       ElMessage.error('登录已过期，请重新登录')
     } else if (status === 403) {
       ElMessage.error('权限不足')
     } else if (status === 404) {
       ElMessage.warning('资源不存在')
     } else if (status === 500) {
       ElMessage.error('服务器错误')
     } else {
       ElMessage.error(detail)
     }
     return Promise.reject(error)
   }
 )
 
 export default request
