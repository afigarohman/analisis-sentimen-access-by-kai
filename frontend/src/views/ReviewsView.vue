<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { isAxiosError } from 'axios'

import { api } from '@/api/client'
import { generateAIReply, scrapeReviews } from '@/api/ai'
import DashboardCardShell from '@/components/dashboard/DashboardCardShell.vue'

function scrapeErrorMessage(e: unknown): string {
  if (isAxiosError(e)) {
    const d = e.response?.data as { detail?: string } | undefined
    if (typeof d?.detail === 'string') return d.detail
    if (e.message) return e.message
  }
  if (e instanceof Error) return e.message
  return 'Scraping gagal'
}

function aiErrorMessage(e: unknown): string {
  if (isAxiosError(e)) {
    const d = e.response?.data as { detail?: unknown } | undefined
    if (typeof d?.detail === 'string') return d.detail
    if (e.message) return e.message
  }
  if (e instanceof Error) return e.message
  return 'Gagal generate balasan AI'
}

type Review = {
  id: number
  content: string
  score: number
  user_name: string
  aspect?: string
  status?: string
  scraped_at?: string | null
}

const FIVE_MIN_MS = 5 * 60 * 1000

const reviews = ref<Review[]>([])
const selectedReview = ref<Review | null>(null)
const aiReply = ref<string>('')
const loading = ref(false)

const scrapeTotal = ref(30)
const scrapeLoading = ref(false)
const scrapeError = ref<string | null>(null)

const selectedFilter = ref<string>('all')

function isFreshScrape(scrapedAt: string | null | undefined): boolean {
  if (!scrapedAt) return false
  const t = new Date(scrapedAt).getTime()
  if (Number.isNaN(t)) return false
  return Date.now() - t < FIVE_MIN_MS
}

function formatScrapedAt(scrapedAt: string | null | undefined): string {
  if (!scrapedAt) return ''
  return new Date(scrapedAt).toLocaleString()
}

async function load() {
  try {
    const { data } = await api.get<Review[]>('/reviews')
    reviews.value = data.filter(
      (r: Review) => r.status !== 'approved' && r.status !== 'rejected',
    )
  } catch (err) {
    console.error('Gagal load reviews:', err)
  }
}

async function startScraping() {
  const n = Number(scrapeTotal.value)
  if (!Number.isFinite(n) || n < 1) {
    scrapeError.value = 'Masukkan jumlah yang valid (≥ 1)'
    return
  }
  scrapeLoading.value = true
  scrapeError.value = null
  try {
    await scrapeReviews(Math.floor(n))
    await load()
  } catch (err: unknown) {
    scrapeError.value = scrapeErrorMessage(err)
  } finally {
    scrapeLoading.value = false
  }
}

const filteredReviews = computed(() => {
  const f = selectedFilter.value
  if (f === 'all') return reviews.value

  if (f === 'positive') return reviews.value.filter((r) => r.score >= 4)
  if (f === 'negative') return reviews.value.filter((r) => r.score <= 2)
  if (f === 'neutral') return reviews.value.filter((r) => r.score === 3)

  return reviews.value.filter((r) => r.aspect === f)
})

function selectReview(item: Review) {
  selectedReview.value = item
  aiReply.value = ''
}

async function generateReply() {
  if (!selectedReview.value) return

  loading.value = true
  aiReply.value = ''

  try {
    const data = await generateAIReply(selectedReview.value.content)
    aiReply.value = data?.reply ?? ''
  } catch (err) {
    console.error('AI error:', err)
    aiReply.value = aiErrorMessage(err)
  } finally {
    loading.value = false
  }
}

async function approveReview() {
  if (!selectedReview.value || !aiReply.value) return

  try {
    await api.post(`/reviews/${selectedReview.value.id}/approve`, {
      ai_reply: aiReply.value,
    })

    selectedReview.value = null
    aiReply.value = ''

    await load()
  } catch (err) {
    console.error('Approve error:', err)
  }
}

async function rejectReview() {
  if (!selectedReview.value) return

  try {
    await api.post(`/reviews/${selectedReview.value.id}/reject`)

    selectedReview.value = null
    aiReply.value = ''

    await load()
  } catch (err) {
    console.error('Reject error:', err)
  }
}

onMounted(load)
</script>

<template>
  <div class="mx-auto w-full max-w-6xl space-y-4 sm:space-y-6">
    <!-- Scraping control -->
    <DashboardCardShell tag="section" variant="tr" class="p-6">
      <div class="flex flex-col gap-4 sm:flex-row sm:items-end sm:justify-between">
        <div>
          <h2 class="text-base font-semibold text-white">
            Kontrol scraping
          </h2>
          <p class="mt-1 text-sm text-slate-300/85">
            Tarik ulasan terbaru dari Google Play ke database. Setelah selesai, daftar
            di bawah akan di-refresh otomatis.
          </p>
        </div>
        <div class="flex flex-wrap items-end gap-3">
          <label class="flex flex-col text-xs font-medium text-slate-300">
            Jumlah ulasan
            <input
              v-model.number="scrapeTotal"
              type="number"
              min="1"
              max="500"
              :disabled="scrapeLoading"
              class="mt-1 w-32 rounded-xl border border-white/10 bg-slate-950/55 px-3 py-2 text-sm text-slate-100 focus:border-fuchsia-400/45 focus:outline-none focus:ring-2 focus:ring-purple-500/35 disabled:opacity-50"
            />
          </label>
          <button
            type="button"
            class="rounded-xl bg-gradient-to-r from-purple-600 via-fuchsia-600 to-purple-600 px-5 py-2.5 text-sm font-semibold text-white shadow-[0_10px_40px_-8px_rgba(168,85,247,0.75)] transition hover:shadow-[0_14px_48px_-10px_rgba(217,70,239,0.55)] active:scale-[0.98] disabled:cursor-not-allowed disabled:opacity-50"
            :disabled="scrapeLoading"
            @click="startScraping"
          >
            {{ scrapeLoading ? 'Memproses…' : 'Mulai Scraping' }}
          </button>
        </div>
      </div>
      <div
        v-if="scrapeLoading"
        class="relative mt-4 flex items-center gap-2 text-sm text-fuchsia-200/90"
      >
        <span
          class="inline-block h-2 w-2 animate-pulse rounded-full bg-fuchsia-400"
        />
        Mengambil ulasan dari Google Play…
      </div>
      <div
        v-if="scrapeError"
        class="mt-3 rounded-xl border border-red-400/35 bg-red-950/45 px-3 py-2 text-sm text-red-100 transition duration-300 hover:border-red-300/40 hover:shadow-[0_16px_40px_-16px_rgba(239,68,68,0.25)]"
      >
        {{ scrapeError }}
      </div>
    </DashboardCardShell>

    <DashboardCardShell class="p-4 sm:p-6" variant="bl">
      <!-- HEADER -->
      <div>
        <h1 class="text-lg font-semibold text-white sm:text-xl">
          <span
            class="bg-gradient-to-r from-purple-200 via-fuchsia-200 to-purple-100 bg-clip-text text-transparent"
          >
            Pantau feedback, rating, dan keluhan penumpang secara real-time
          </span>
        </h1>
      </div>

      <!-- FILTER -->
      <div class="mt-4">
        <label
          class="block text-xs font-medium text-slate-300"
        >
          Filter
        </label>
        <select
          v-model="selectedFilter"
          class="mt-1 w-full rounded-xl border border-white/10 bg-slate-950/55 px-3 py-2 text-sm text-slate-100 focus:border-fuchsia-400/45 focus:outline-none focus:ring-2 focus:ring-purple-500/35"
        >
          <option value="all">Semua</option>
          <option value="positive">Positive</option>
          <option value="neutral">Netral</option>
          <option value="negative">Negative</option>
          <option value="Login">Login</option>
          <option value="Sistem">Sistem</option>
          <option value="Pembayaran">Pembayaran</option>
          <option value="UI/UX">UI/UX</option>
          <option value="Performa">Performa</option>
          <option value="Lainnya">Lainnya</option>
        </select>
      </div>

      <!-- LAYOUT -->
      <div class="mt-4 grid grid-cols-1 gap-6 lg:grid-cols-3">
        <!-- LEFT -->
        <div class="lg:col-span-2">
          <div class="max-h-[500px] space-y-3 overflow-y-auto pr-1">
            <button
              v-for="item in filteredReviews"
              :key="item.id"
              type="button"
              class="group/rev relative w-full overflow-hidden rounded-xl border p-4 text-left transition duration-300 hover:-translate-y-0.5 hover:shadow-[0_26px_60px_-22px_rgba(168,85,247,0.38),0_14px_40px_-16px_rgba(217,70,239,0.14)]"
              :class="[
                selectedReview?.id === item.id
                  ? 'border-fuchsia-400/45 bg-white/10 shadow-[0_0_28px_-8px_rgba(217,70,239,0.45)] ring-1 ring-fuchsia-400/35 hover:shadow-[0_0_32px_-6px_rgba(217,70,239,0.55)]'
                  : 'border-white/[0.1] bg-black/25 hover:border-purple-400/35 hover:bg-black/35',
                isFreshScrape(item.scraped_at)
                  ? 'border-purple-400/35 bg-purple-500/12'
                  : '',
              ]"
              @click="selectReview(item)"
            >
              <div
                class="pointer-events-none absolute -right-24 -top-24 h-56 w-56 rounded-full bg-gradient-to-tr from-purple-500/20 via-fuchsia-500/12 to-transparent blur-2xl opacity-65 transition-opacity duration-300 group-hover/rev:opacity-100"
              />
              <div class="relative flex justify-between gap-2">
                <p class="text-sm text-slate-100">
                  {{ item.content }}
                </p>
                <span
                  class="shrink-0 text-xs font-semibold text-slate-300"
                  >⭐ {{ item.score }}</span
                >
              </div>
              <div
                class="relative mt-2 flex flex-wrap items-center gap-2 text-xs text-slate-400"
              >
                <span>{{ item.user_name }}</span>
                <span
                  v-if="item.aspect"
                  class="rounded-full bg-white/10 px-2 py-0.5 font-semibold text-slate-200 ring-1 ring-white/10"
                >
                  {{ item.aspect }}
                </span>
                <span
                  v-if="isFreshScrape(item.scraped_at)"
                  class="rounded-full bg-fuchsia-500/20 px-2 py-0.5 font-semibold text-fuchsia-100 ring-1 ring-fuchsia-400/35"
                >
                  Baru
                </span>
              </div>
              <p
                v-if="item.scraped_at"
                class="relative mt-1 text-[11px] text-slate-500"
              >
                Di-scrape: {{ formatScrapedAt(item.scraped_at) }}
              </p>
            </button>

            <div
              v-if="!filteredReviews.length"
              class="rounded-xl border border-white/[0.1] bg-black/25 p-4 text-center text-sm text-slate-400 ring-1 ring-white/10 transition duration-300 hover:-translate-y-0.5 hover:border-white/[0.14] hover:shadow-[0_24px_50px_-20px_rgba(168,85,247,0.32)]"
            >
              Tidak ada ulasan
            </div>
          </div>
        </div>

        <!-- RIGHT -->
        <DashboardCardShell compact class="p-4 ring-1 ring-white/[0.08]" variant="tm">
          <div>
            <div>
              <p class="text-sm font-semibold text-white">
                Ulasan terpilih
              </p>
              <DashboardCardShell compact class="mt-2 p-3 text-sm text-slate-200" variant="tl">
                <p v-if="selectedReview">
                  {{ selectedReview.content }}
                </p>
                <p
                  v-if="selectedReview?.aspect"
                  class="mt-2 text-xs text-slate-400"
                >
                  Kategori: <span class="font-semibold text-white">{{ selectedReview.aspect }}</span>
                </p>
                <p v-else class="text-slate-400">
                  Pilih ulasan dulu
                </p>
              </DashboardCardShell>
            </div>

            <div class="mt-4">
              <p class="text-sm font-semibold text-white">
                Rekomendasi AI
              </p>
              <DashboardCardShell compact class="mt-2 p-3 text-sm text-slate-200" variant="br">
                <p v-if="loading" class="text-slate-400">
                  Loading...
                </p>
                <p v-else-if="aiReply">{{ aiReply }}</p>
                <p v-else class="text-slate-400">Generate AI</p>
              </DashboardCardShell>
            </div>

            <div class="mt-3 flex flex-wrap gap-2">
              <button
                class="rounded-xl bg-gradient-to-r from-purple-600 via-fuchsia-600 to-purple-600 px-4 py-2 text-sm font-semibold text-white shadow-[0_8px_28px_-6px_rgba(168,85,247,0.65)] transition hover:shadow-[0_12px_36px_-8px_rgba(217,70,239,0.45)] disabled:cursor-not-allowed disabled:opacity-50"
                :disabled="!selectedReview || loading"
                @click="generateReply"
              >
                Generate AI Reply
              </button>

              <button
                class="rounded-xl bg-emerald-600 px-4 py-2 text-sm font-semibold text-white shadow-[0_0_20px_-4px_rgba(52,211,153,0.35)] transition hover:bg-emerald-500 disabled:cursor-not-allowed disabled:opacity-50"
                :disabled="!selectedReview || !aiReply || loading"
                @click="approveReview"
              >
                Tandai selesai
              </button>

              <button
                class="rounded-xl bg-red-500 px-4 py-2 text-sm font-semibold text-white shadow-[0_0_20px_-4px_rgba(239,68,68,0.35)] transition hover:bg-red-400 disabled:cursor-not-allowed disabled:opacity-50"
                :disabled="!selectedReview || loading"
                @click="rejectReview"
              >
                Reject
              </button>
            </div>
          </div>
        </DashboardCardShell>
      </div>
    </DashboardCardShell>
  </div>
</template>
