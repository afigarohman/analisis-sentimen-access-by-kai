import { api } from '@/api/client'
import { formatHttpClientError } from '@/api/httpErrors'

export interface TokenResponse {
  access_token: string
  token_type: string
}

export async function authLogin(email: string, password: string): Promise<TokenResponse> {
  const { data } = await api.post<TokenResponse>('/auth/login', { email, password })
  return data
}

export async function authRegister(payload: {
  name: string
  email: string
  password: string
}): Promise<TokenResponse> {
  const { data } = await api.post<TokenResponse>('/auth/register', payload)
  return data
}

/** Pesan ringkas untuk UI dari error Axios / FastAPI */
export function formatAuthError(error: unknown): string {
  return formatHttpClientError(error)
}
