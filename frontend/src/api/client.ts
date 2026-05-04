import axios from 'axios'

function resolveApiBaseURL(): string {
  if (import.meta.env.DEV) {
    return '/api'
  }
  const u = import.meta.env.VITE_API_BASE_URL
  if (typeof u === 'string' && u.trim() !== '') {
    return u.trim().replace(/\/$/, '')
  }
  return 'http://127.0.0.1:8000'
}

export const api = axios.create({
  baseURL: resolveApiBaseURL(),
  timeout: 30000,
})

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})
