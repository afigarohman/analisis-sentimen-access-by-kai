<script setup lang="ts">
import axios from 'axios'
import { computed, onMounted, reactive, ref, watch } from 'vue'
import { useRouter } from 'vue-router'

import { api } from '@/api/client'
import { formatAuthError } from '@/api/auth'
import {
  extractApiErrorDetail,
  logAxiosErrorResponse,
} from '@/api/httpErrors'
import type { TokenResponse } from '@/api/auth'

const router = useRouter()

const STORAGE_EMAIL = 'auth_saved_email'

const isLogin = ref(true)

const loginForm = reactive({
  email: '',
  password: '',
})

const registerForm = reactive({
  name: '',
  email: '',
  password: '',
  confirmPassword: '',
})

const rememberMe = ref(false)
const loginPwVisible = ref(false)
const registerPwVisible = ref(false)
const registerPw2Visible = ref(false)

const errorMessage = ref('')
const loading = ref(false)

const headline = computed(() =>
  isLogin.value ? 'Welcome back 👋' : 'Create your account',
)

const subtitle = computed(() =>
  isLogin.value
    ? 'Masuk untuk melanjutkan analisis sentimen'
    : 'Buat akun untuk mengakses dashboard Access by KAI',
)

/** Kelas konsisten untuk field teks premium */
const inputClass =
  'w-full rounded-2xl border border-white/[0.08] bg-white/5 px-3.5 py-2.5 text-sm text-white shadow-[inset_0_1px_0_rgba(255,255,255,0.03)] backdrop-blur-sm placeholder:text-purple-300/35 transition-colors duration-200 focus:border-purple-400/55 focus:outline-none focus:ring-2 focus:ring-purple-500/40'

const passwordInputClass = `${inputClass} pr-11`

onMounted(() => {
  const saved = localStorage.getItem(STORAGE_EMAIL)
  if (saved) loginForm.email = saved
})

watch(isLogin, () => {
  errorMessage.value = ''
})

function validateLogin(): boolean {
  if (!loginForm.email.trim()) {
    errorMessage.value = 'Email wajib diisi.'
    return false
  }
  if (!loginForm.password) {
    errorMessage.value = 'Kata sandi wajib diisi.'
    return false
  }
  return true
}

function validateRegister(): boolean {
  const name = registerForm.name.trim()
  const email = registerForm.email.trim()
  const pw = registerForm.password
  const confirm = registerForm.confirmPassword

  if (!name) {
    errorMessage.value = 'Nama lengkap wajib diisi.'
    return false
  }
  if (!email) {
    errorMessage.value = 'Email wajib diisi.'
    return false
  }
  if (!pw) {
    errorMessage.value = 'Kata sandi wajib diisi.'
    return false
  }
  if (!confirm) {
    errorMessage.value = 'Konfirmasi kata sandi wajib diisi.'
    return false
  }
  if (pw !== confirm) {
    errorMessage.value = 'Kata sandi dan konfirmasi tidak sama.'
    return false
  }
  if (pw.length < 6) {
    errorMessage.value = 'Kata sandi minimal 6 karakter.'
    return false
  }
  return true
}

async function handleLogin() {
  errorMessage.value = ''
  if (!validateLogin()) return
  loading.value = true
  try {
    const res = await api.post<{ access_token: string; token_type?: string }>(
      '/auth/login',
      {
        email: loginForm.email.trim(),
        password: loginForm.password,
      },
    )
    const token = res.data?.access_token
    if (!token) throw new Error('Respon server tidak menyertakan token')
    localStorage.setItem('token', token)
    if (rememberMe.value) localStorage.setItem(STORAGE_EMAIL, loginForm.email.trim())
    else localStorage.removeItem(STORAGE_EMAIL)
    await router.push('/dashboard')
  } catch (err: unknown) {
    let msg = ''
    if (axios.isAxiosError(err)) {
      const raw = err.response?.data?.detail
      if (typeof raw === 'string') msg = raw
      else msg = formatAuthError(err)
    } else {
      msg = formatAuthError(err)
    }
    errorMessage.value = msg || 'Login gagal'
  } finally {
    loading.value = false
  }
}

async function handleRegister() {
  errorMessage.value = ''
  if (!validateRegister()) return
  loading.value = true
  const payload = {
    name: registerForm.name.trim(),
    email: registerForm.email.trim(),
    password: registerForm.password,
  }
  try {
    const res = await api.post<TokenResponse>('/auth/register', payload)
    const token = res.data?.access_token
    if (!token) throw new Error('Respon tidak menyertakan access_token')
    localStorage.setItem('token', token)
    await router.push('/dashboard')
  } catch (err: unknown) {
    if (axios.isAxiosError(err)) {
      logAxiosErrorResponse('register', err)
      const raw = extractApiErrorDetail(err.response?.data)
      errorMessage.value =
        raw ||
        formatAuthError(err)
    } else {
      console.log('[register] error:', err)
      errorMessage.value = formatAuthError(err)
    }
    if (!errorMessage.value) errorMessage.value = 'Pendaftaran gagal'
  } finally {
    loading.value = false
  }
}

const fadeTransitionClasses = {
  enterActiveClass:
    'transition-all duration-500 ease-in-out [&_input]:transition-[colors,box-shadow]',
  enterFromClass: 'opacity-0 translate-y-[10px]',
  enterToClass: 'opacity-100 translate-y-0',
  leaveActiveClass:
    'transition-all duration-500 ease-in-out [&_input]:transition-[colors,box-shadow]',
  leaveFromClass: 'opacity-100 translate-y-0',
  leaveToClass: 'opacity-0 -translate-y-[10px]',
} as const

const btnPrimary =
  'w-full rounded-xl bg-gradient-to-r from-purple-600 via-purple-500 to-purple-700 py-2.5 text-sm font-semibold text-white shadow-[0_12px_36px_-8px_rgba(168,85,247,0.55),inset_0_1px_0_rgba(255,255,255,0.12)] transition duration-300 ease-out hover:-translate-y-0.5 hover:brightness-[1.08] hover:shadow-[0_18px_48px_-6px_rgba(192,132,252,0.5),inset_0_1px_0_rgba(255,255,255,0.18)] focus:outline-none focus:ring-2 focus:ring-purple-400/55 disabled:pointer-events-none disabled:cursor-not-allowed disabled:opacity-[0.52]'
</script>

<template>
  <div
    class="relative min-h-screen w-full overflow-x-hidden bg-[#07070d] text-white selection:bg-purple-500/35 antialiased"
  >
    <!-- Spotlight kiri atas (di luar card) -->
    <div class="pointer-events-none fixed inset-0" aria-hidden="true">
      <div
        class="fixed left-[-12%] top-[-18%] h-[85vh] w-[92vw] max-w-[900px]"
        style="
          background: radial-gradient(
            ellipse 70% 60% at 18% 12%,
            rgba(147, 51, 234, 0.38) 0%,
            rgba(88, 28, 135, 0.14) 42%,
            transparent 72%
          );
        "
      />
      <div
        class="fixed left-[4%] top-[14%] h-[380px] w-[540px] max-w-[80vw] opacity-95 blur-[100px]"
        style="
          background: radial-gradient(
            circle at 30% 30%,
            rgba(192, 132, 252, 0.22),
            transparent 68%
          );
        "
      />
    </div>

    <div class="relative z-10 mx-auto grid min-h-screen max-w-[1200px] md:grid-cols-2">
      <!-- Kiri: form -->
      <div
        class="flex flex-col justify-center px-5 py-12 sm:px-10 md:min-h-screen md:py-16 lg:px-14"
      >
        <div
          class="group/card relative mx-auto w-full max-w-md overflow-hidden rounded-3xl border border-white/[0.1] bg-white/[0.05] p-8 shadow-[0_0_0_1px_rgba(168,85,247,0.08),0_8px_40px_-12px_rgba(0,0,0,0.75),0_24px_80px_-24px_rgba(126,58,242,0.35)] backdrop-blur-xl transition-shadow duration-500 hover:shadow-[0_0_0_1px_rgba(196,181,253,0.12),0_12px_48px_-14px_rgba(0,0,0,0.8),0_32px_96px_-28px_rgba(147,51,234,0.42)] sm:p-9"
        >
          <div
            class="pointer-events-none absolute -right-24 -top-24 h-48 w-48 rounded-full bg-purple-500/[0.12] blur-3xl transition-opacity duration-500 group-hover/card:opacity-90"
          />
          <div
            class="pointer-events-none absolute -bottom-20 -left-16 h-40 w-48 rounded-full bg-fuchsia-500/[0.1] blur-[72px]"
          />

          <div class="relative z-10">
            <h1 class="text-2xl font-semibold tracking-tight text-white">
              {{ headline }}
            </h1>
            <p class="mt-2 text-sm leading-relaxed text-purple-200/[0.72]">{{ subtitle }}</p>

            <div class="mt-8 min-h-[300px] sm:min-h-[320px]">
              <Transition mode="out-in" v-bind="fadeTransitionClasses">
                <form v-if="isLogin" key="login" class="space-y-4" @submit.prevent="handleLogin">
                  <div>
                    <label class="text-xs font-medium text-purple-200/72" for="lv-email">
                      Email
                    </label>
                    <input
                      id="lv-email"
                      v-model="loginForm.email"
                      type="email"
                      autocomplete="username"
                      class="mt-1.5"
                      :class="inputClass"
                      placeholder="nama@domain.com"
                    />
                  </div>
                  <div>
                    <label class="text-xs font-medium text-purple-200/72" for="lv-pw">
                      Kata sandi
                    </label>
                    <div class="relative mt-1.5">
                      <input
                        id="lv-pw"
                        v-model="loginForm.password"
                        :type="loginPwVisible ? 'text' : 'password'"
                        autocomplete="current-password"
                        :class="passwordInputClass"
                        placeholder="••••••••"
                      />
                      <button
                        type="button"
                        class="absolute right-2 top-1/2 -translate-y-1/2 rounded-lg p-1.5 text-purple-200/55 transition hover:bg-white/10 hover:text-purple-100"
                        :aria-pressed="loginPwVisible"
                        aria-label="Tampilkan kata sandi"
                        @click="loginPwVisible = !loginPwVisible"
                      >
                        <svg class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                          <path
                            v-if="!loginPwVisible"
                            stroke-linecap="round"
                            stroke-linejoin="round"
                            stroke-width="2"
                            d="M15 12a3 3 0 11-6 0 3 3 0 016 0z M2 12s4-7 10-7 10 7 10 7-4 7-10 7-10-7-10-7z"
                          />
                          <path
                            v-else
                            stroke-linecap="round"
                            stroke-linejoin="round"
                            stroke-width="2"
                            d="M3 3l18 18M10.6 10.6a3 3 0 014.24 4.24M9.88 9.88A10.94 10.94 0 012 12s4 7 10 7c2.04 0 3.95-.62 5.61-1.68M17.94 17.94A13.93 13.93 0 0122 12s-4-7-10-7a9.8 9.8 0 00-4.53 1.13"
                          />
                        </svg>
                      </button>
                    </div>
                  </div>

                  <!-- Error login: di bawah field input -->
                  <div
                    v-if="errorMessage && isLogin"
                    class="rounded-xl border border-red-400/35 bg-red-950/48 px-3 py-2.5 text-sm text-red-100"
                    role="alert"
                  >
                    {{ errorMessage }}
                  </div>

                  <div class="flex flex-wrap items-center gap-3 text-xs">
                    <label class="inline-flex cursor-pointer items-center gap-2 text-purple-200/70">
                      <input
                        v-model="rememberMe"
                        type="checkbox"
                        class="size-3.5 rounded border-white/22 bg-white/5 text-purple-600 focus:ring-2 focus:ring-purple-500/45"
                      />
                      Ingat saya
                    </label>
                    <button type="button" class="ml-auto text-purple-300 hover:text-purple-200 hover:underline">
                      Lupa kata sandi?
                    </button>
                  </div>

                  <button type="submit" :disabled="loading" :class="btnPrimary">
                    {{ loading ? 'Loading...' : 'Masuk' }}
                  </button>
                  <p class="text-center text-xs text-purple-200/55">
                    Belum punya akun?
                    <button
                      type="button"
                      class="font-semibold text-purple-300 hover:text-purple-200"
                      @click="isLogin = false"
                    >
                      Daftar
                    </button>
                  </p>
                </form>

                <form
                  v-else
                  key="register"
                  class="space-y-4"
                  @submit.prevent="handleRegister"
                >
                  <div>
                    <label class="text-xs font-medium text-purple-200/72" for="lv-name">
                      Nama lengkap
                    </label>
                    <input
                      id="lv-name"
                      v-model="registerForm.name"
                      type="text"
                      autocomplete="name"
                      class="mt-1.5"
                      :class="inputClass"
                      placeholder="Nama Anda"
                    />
                  </div>
                  <div>
                    <label class="text-xs font-medium text-purple-200/72" for="lv-er">
                      Email
                    </label>
                    <input
                      id="lv-er"
                      v-model="registerForm.email"
                      type="email"
                      autocomplete="email"
                      class="mt-1.5"
                      :class="inputClass"
                      placeholder="nama@domain.com"
                    />
                  </div>
                  <div>
                    <label class="text-xs font-medium text-purple-200/72" for="lv-rp">
                      Kata sandi
                    </label>
                    <div class="relative mt-1.5">
                      <input
                        id="lv-rp"
                        v-model="registerForm.password"
                        :type="registerPwVisible ? 'text' : 'password'"
                        autocomplete="new-password"
                        :class="passwordInputClass"
                        placeholder="Minimal 6 karakter"
                      />
                      <button
                        type="button"
                        class="absolute right-2 top-1/2 -translate-y-1/2 rounded-lg p-1.5 text-purple-200/55 hover:bg-white/10 hover:text-purple-100"
                        :aria-pressed="registerPwVisible"
                        aria-label="Tampilkan kata sandi"
                        @click="registerPwVisible = !registerPwVisible"
                      >
                        <svg class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                          <path
                            v-if="!registerPwVisible"
                            stroke-linecap="round"
                            stroke-linejoin="round"
                            stroke-width="2"
                            d="M15 12a3 3 0 11-6 0 3 3 0 016 0z M2 12s4-7 10-7 10 7 10 7-4 7-10 7-10-7-10-7z"
                          />
                          <path
                            v-else
                            stroke-linecap="round"
                            stroke-linejoin="round"
                            stroke-width="2"
                            d="M3 3l18 18M10.6 10.6a3 3 0 014.24 4.24M9.88 9.88A10.94 10.94 0 012 12s4 7 10 7c2.04 0 3.95-.62 5.61-1.68M17.94 17.94A13.93 13.93 0 0122 12s-4-7-10-7a9.8 9.8 0 00-4.53 1.13"
                          />
                        </svg>
                      </button>
                    </div>
                  </div>
                  <div>
                    <label class="text-xs font-medium text-purple-200/72" for="lv-rc">
                      Konfirmasi kata sandi
                    </label>
                    <div class="relative mt-1.5">
                      <input
                        id="lv-rc"
                        v-model="registerForm.confirmPassword"
                        :type="registerPw2Visible ? 'text' : 'password'"
                        autocomplete="new-password"
                        :class="passwordInputClass"
                        placeholder="Ulangi kata sandi"
                      />
                      <button
                        type="button"
                        class="absolute right-2 top-1/2 -translate-y-1/2 rounded-lg p-1.5 text-purple-200/55 hover:bg-white/10 hover:text-purple-100"
                        :aria-pressed="registerPw2Visible"
                        aria-label="Tampilkan konfirmasi kata sandi"
                        @click="registerPw2Visible = !registerPw2Visible"
                      >
                        <svg class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                          <path
                            v-if="!registerPw2Visible"
                            stroke-linecap="round"
                            stroke-linejoin="round"
                            stroke-width="2"
                            d="M15 12a3 3 0 11-6 0 3 3 0 016 0z M2 12s4-7 10-7 10 7 10 7-4 7-10 7-10-7-10-7z"
                          />
                          <path
                            v-else
                            stroke-linecap="round"
                            stroke-linejoin="round"
                            stroke-width="2"
                            d="M3 3l18 18M10.6 10.6a3 3 0 014.24 4.24M9.88 9.88A10.94 10.94 0 012 12s4 7 10 7c2.04 0 3.95-.62 5.61-1.68M17.94 17.94A13.93 13.93 0 0122 12s-4-7-10-7a9.8 9.8 0 00-4.53 1.13"
                          />
                        </svg>
                      </button>
                    </div>
                  </div>

                  <div
                    v-if="errorMessage && !isLogin"
                    class="rounded-xl border border-red-400/35 bg-red-950/48 px-3 py-2.5 text-sm text-red-100"
                    role="alert"
                  >
                    {{ errorMessage }}
                  </div>

                  <button type="submit" :disabled="loading" :class="btnPrimary">
                    {{ loading ? 'Loading...' : 'Daftar' }}
                  </button>
                  <p class="text-center text-xs text-purple-200/55">
                    Sudah punya akun?
                    <button
                      type="button"
                      class="font-semibold text-purple-300 hover:text-purple-200"
                      @click="isLogin = true"
                    >
                      Masuk
                    </button>
                  </p>
                </form>
              </Transition>
            </div>
          </div>
        </div>
      </div>

      <!-- Kanan: gambar lebih redup (~60–80% feel) -->
      <div class="relative hidden min-h-[320px] md:block md:min-h-screen">
        <img
          src="@/assets/kai.jpg"
          alt="Visual branding"
          class="absolute inset-0 h-full w-full object-cover brightness-[0.72] contrast-[1.02]"
        />
        <div class="pointer-events-none absolute inset-0 bg-purple-950/78" />
        <div class="pointer-events-none absolute inset-0 bg-gradient-to-br from-purple-950/92 via-purple-900/74 to-purple-950/88" />
        <div class="pointer-events-none absolute inset-0 bg-gradient-to-t from-black/72 via-purple-950/45 to-purple-900/52" />
        <div
          class="pointer-events-none absolute inset-0 opacity-90 mix-blend-soft-light bg-[radial-gradient(ellipse_90%_70%_at_65%_40%,transparent_36%,rgba(24,14,41,0.88)_92%)]"
        />
      </div>
    </div>
  </div>
</template>
