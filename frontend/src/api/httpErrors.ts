import axios from 'axios'
import type { AxiosError } from 'axios'

/** Ambil teks error dari body FastAPI / umum: detail, message, validasi array */
export function extractApiErrorDetail(data: unknown): string | null {
  if (data == null) return null
  if (typeof data === 'string') return data.trim() || null
  if (typeof data !== 'object') return String(data)

  const o = data as Record<string, unknown>

  if (typeof o.detail === 'string' && o.detail.trim()) return o.detail.trim()

  if (Array.isArray(o.detail)) {
    const parts = o.detail
      .map((x: unknown) => {
        if (typeof x === 'object' && x !== null && 'msg' in x) {
          return String((x as { msg: unknown }).msg).trim()
        }
        if (typeof x === 'string') return x.trim()
        return ''
      })
      .filter(Boolean)
    if (parts.length) return parts.join(' ')
  }

  if (typeof o.message === 'string' && o.message.trim()) return o.message.trim()
  if (typeof o.error === 'string' && o.error.trim()) return o.error.trim()
  if (typeof o.msg === 'string' && o.msg.trim()) return o.msg.trim()

  return null
}

/** Log respons error API ke konsol (debug). */
export function logAxiosErrorResponse(context: string, err: AxiosError): void {
  console.log(`[${context}] error response:`, {
    status: err.response?.status,
    statusText: err.response?.statusText,
    data: err.response?.data,
    url: err.config?.url,
    baseURL: err.config?.baseURL,
  })
}

/** Teks bantuan agar pesan error selaras dengan base URL yang dipakai axios */
export function apiBaseDisplay(): string {
  if (import.meta.env.DEV) {
    return '/api (proxy Vite → http://127.0.0.1:8000)'
  }
  const u = import.meta.env.VITE_API_BASE_URL
  if (typeof u === 'string' && u.trim() !== '') {
    return u.trim().replace(/\/$/, '')
  }
  return 'http://127.0.0.1:8000'
}

/**
 * Pesan ramah pengguna untuk error network/timeout Axios (dashboard, dsb.).
 */
export function formatHttpClientError(error: unknown): string {
  if (!axios.isAxiosError(error)) {
    return error instanceof Error ? error.message : 'Gagal menghubungi server.'
  }

  const base = apiBaseDisplay()
  const msg = (error.message || '').toLowerCase()

  if (error.code === 'ECONNABORTED' || msg.includes('timeout')) {
    return (
      `Permintaan ke API habis waktu. Backend mungkin tidak merespons — pastikan uvicorn berjalan, ` +
      `PostgreSQL dapat dijangkau (DB_HOST/DB_PORT di .env backend), lalu coba lagi. Target: ${base}`
    )
  }

  if (!error.response) {
    const hint = import.meta.env.DEV
      ? ' Pastikan uvicorn berjalan di port 8000, lalu restart npm run dev setelah mengubah proxy.'
      : ' Periksa VITE_API_BASE_URL di build production dan pastikan backend dapat dijangkau.'
    return (
      `Tidak terhubung ke API (${base}). Jalankan backend (uvicorn app.main:app --reload).` + hint
    )
  }

  const body = error.response.data
  const extracted = extractApiErrorDetail(body)
  if (extracted) return extracted

  const status = error.response.status
  if (status >= 500) {
    return `Terjadi kesalahan di server (HTTP ${status}). Periksa log terminal backend (uvicorn).`
  }
  return `Permintaan ditolak (HTTP ${status}).`
}
