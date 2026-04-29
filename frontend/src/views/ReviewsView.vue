<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue'
import { isAxiosError } from 'axios'

import { api } from '@/api/client'
import { scrapeReviews } from '@/api/ai'

function scrapeErrorMessage(e: unknown): string {
  if (isAxiosError(e)) {
    const d = e.response?.data as { detail?: string } | undefined
    if (typeof d?.detail === 'string') return d.detail
    if (e.message) return e.message
  }
  if (e instanceof Error) return e.message
  return 'Scraping gagal'
}

type Review = {
  id: number
  content: string
  score: number
  user_name: string
  status?: string
  scraped_at?: string | null
}

const FIVE_MIN_MS = 5 * 60 * 1000

const reviews = ref<Review[]>([])
const selectedScore = ref<number | null>(null)
const selectedReview = ref<Review | null>(null)
const aiReply = ref<string>('')
const loading = ref(false)

const scrapeTotal = ref(30)
const scrapeLoading = ref(false)
const scrapeError = ref<string | null>(null)

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
  if (!selectedScore.value) return reviews.value
  return reviews.value.filter((r) => r.score === selectedScore.value)
})

function selectReview(item: Review) {
  selectedReview.value = item
}

async function generateReply() {
  if (!selectedReview.value) return

  loading.value = true
  aiReply.value = ''

  try {
    const { data } = await api.post<{ reply: string }>('/ai/generate-reply', {
      content: selectedReview.value.content,
    })
    aiReply.value = data?.reply ?? ''
  } catch (err) {
    console.error('AI error:', err)
    aiReply.value = 'Gagal generate balasan AI'
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

watch(
  () => selectedReview.value?.content,
  async (next) => {
    if (!next) return
    await generateReply()
  },
)

onMounted(load)
</script>

<template>
  <div class="mx-auto w-full max-w-6xl space-y-6">
    <!-- Scraping control -->
    <section
      class="relative overflow-hidden rounded-2xl border border-white/10 bg-white/5 p-5 shadow-[0_0_30px_rgba(59,130,246,0.15)] backdrop-blur-xl dark:bg-white/5"
    >
      <div
        class="pointer-events-none absolute -right-16 -top-16 h-48 w-48 rounded-full bg-purple-500/20 blur-3xl"
      />
      <div class="relative flex flex-col gap-4 sm:flex-row sm:items-end sm:justify-between">
        <div>
          <h2 class="text-base font-semibold text-slate-900 dark:text-white">
            Kontrol scraping
          </h2>
          <p class="mt-1 text-sm text-slate-600 dark:text-slate-400">
            Tarik ulasan terbaru dari Google Play ke database. Setelah selesai, daftar
            di bawah akan di-refresh otomatis.
          </p>
        </div>
        <div class="flex flex-wrap items-end gap-3">
          <label class="flex flex-col text-xs font-medium text-slate-600 dark:text-slate-300">
            Jumlah ulasan
            <input
              v-model.number="scrapeTotal"
              type="number"
              min="1"
              max="500"
              :disabled="scrapeLoading"
              class="mt-1 w-32 rounded-xl border border-white/10 bg-slate-950/40 px-3 py-2 text-sm text-slate-100 focus:border-purple-400/50 focus:outline-none focus:ring-2 focus:ring-purple-500/30 disabled:opacity-50 dark:bg-slate-950/60"
            />
          </label>
          <button
            type="button"
            class="rounded-xl bg-purple-600 px-5 py-2.5 text-sm font-semibold text-white shadow-lg shadow-purple-500/25 transition hover:bg-purple-500 hover:shadow-purple-500/40 active:scale-[0.98] disabled:cursor-not-allowed disabled:opacity-50"
            :disabled="scrapeLoading"
            @click="startScraping"
          >
            {{ scrapeLoading ? 'Memproses…' : 'Mulai Scraping' }}
          </button>
        </div>
      </div>
      <div
        v-if="scrapeLoading"
        class="relative mt-4 flex items-center gap-2 text-sm text-purple-200"
      >
        <span
          class="inline-block h-2 w-2 animate-pulse rounded-full bg-purple-400"
        />
        Mengambil ulasan dari Google Play…
      </div>
      <div
        v-if="scrapeError"
        class="relative mt-3 rounded-xl border border-red-400/30 bg-red-950/40 px-3 py-2 text-sm text-red-100"
      >
        {{ scrapeError }}
      </div>
    </section>

    <div
      class="group relative overflow-hidden rounded-2xl bg-white/90 p-4 shadow-sm backdrop-blur sm:p-6 dark:bg-slate-900/40 dark:shadow-[0_0_30px_rgba(59,130,246,0.12)]"
    >
      <div
        class="pointer-events-none absolute -left-24 -top-24 h-72 w-72 rounded-full bg-gradient-to-tr from-blue-500/22 via-cyan-400/12 to-transparent blur-2xl opacity-80"
      />

      <!-- HEADER -->
      <div class="relative overflow-hidden rounded-xl bg-blue-50 p-4 dark:bg-slate-950/35">
        <div
          class="pointer-events-none absolute -right-24 -top-24 h-56 w-56 rounded-full bg-gradient-to-tr from-cyan-400/18 via-blue-500/12 to-transparent blur-2xl"
        />
        <h1 class="text-lg font-semibold text-slate-900 sm:text-xl dark:text-white">
          <span
            class="bg-gradient-to-r from-blue-600 to-cyan-400 bg-clip-text text-transparent"
          >
            Pantau feedback, rating, dan keluhan penumpang secara real-time
          </span>
        </h1>
      </div>

      <!-- FILTER -->
      <div class="mt-4 flex flex-wrap gap-2">
        <button
          class="rounded-xl px-4 py-2 text-sm font-semibold shadow-sm transition"
          :class="
            selectedScore === null
              ? 'bg-blue-500 text-white ring-blue-500'
              : 'bg-slate-100 text-slate-700 hover:bg-slate-200/60 dark:bg-slate-950/40 dark:text-slate-200 dark:hover:bg-slate-900'
          "
          @click="selectedScore = null"
        >
          Semua
        </button>

        <button
          v-for="n in 5"
          :key="n"
          class="rounded-xl px-4 py-2 text-sm font-semibold shadow-sm transition"
          :class="
            selectedScore === n
              ? 'bg-blue-500 text-white ring-blue-500'
              : 'bg-slate-100 text-slate-700 hover:bg-slate-200/60 dark:bg-slate-950/40 dark:text-slate-200 dark:hover:bg-slate-900'
          "
          @click="selectedScore = n"
        >
          ⭐ {{ n }}
        </button>
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
              class="group/rev relative w-full overflow-hidden rounded-xl p-4 text-left shadow-sm transition-all duration-300 hover:shadow-md dark:shadow-[0_0_20px_rgba(59,130,246,0.08)]"
              :class="[
                selectedReview?.id === item.id
                  ? 'shadow-blue-500/25 ring-1 ring-blue-400/40'
                  : '',
                isFreshScrape(item.scraped_at)
                  ? 'border border-purple-500/35 bg-purple-500/10 dark:bg-purple-500/10'
                  : 'border border-transparent bg-slate-50 dark:bg-slate-950/35',
              ]"
              @click="selectReview(item)"
            >
              <div
                class="pointer-events-none absolute -right-24 -top-24 h-56 w-56 rounded-full bg-gradient-to-tr from-blue-500/14 via-cyan-400/10 to-transparent blur-2xl opacity-75 transition group-hover/rev:opacity-100"
              />
              <div class="relative flex justify-between gap-2">
                <p class="text-sm text-slate-800 dark:text-slate-200">
                  {{ item.content }}
                </p>
                <span
                  class="shrink-0 text-xs font-semibold text-slate-600 dark:text-slate-300"
                  >⭐ {{ item.score }}</span
                >
              </div>
              <div
                class="relative mt-2 flex flex-wrap items-center gap-2 text-xs text-slate-500 dark:text-slate-400"
              >
                <span>{{ item.user_name }}</span>
                <span
                  v-if="isFreshScrape(item.scraped_at)"
                  class="rounded-full bg-purple-500/25 px-2 py-0.5 font-semibold text-purple-200 ring-1 ring-purple-400/40"
                >
                  Baru
                </span>
              </div>
              <p
                v-if="item.scraped_at"
                class="relative mt-1 text-[11px] text-slate-500 dark:text-slate-500"
              >
                Di-scrape: {{ formatScrapedAt(item.scraped_at) }}
              </p>
            </button>

            <div
              v-if="!filteredReviews.length"
              class="rounded-xl bg-slate-50 p-4 text-center text-sm text-slate-500 shadow-sm dark:bg-slate-950/35 dark:text-slate-400 dark:shadow-blue-500/10"
            >
              Tidak ada ulasan
            </div>
          </div>
        </div>

        <!-- RIGHT -->
        <aside
          class="group relative overflow-hidden rounded-xl bg-white/90 p-4 shadow-sm backdrop-blur dark:bg-slate-900/40 dark:shadow-blue-500/10"
        >
          <div
            class="pointer-events-none absolute -left-24 -bottom-24 h-72 w-72 rounded-full bg-gradient-to-tr from-cyan-400/16 via-blue-500/12 to-transparent blur-2xl opacity-80"
          />
          <div>
            <div>
              <p class="text-sm font-semibold text-slate-900 dark:text-white">
                Ulasan terpilih
              </p>
              <div
                class="mt-2 rounded-xl bg-slate-50 p-3 text-sm text-slate-700 shadow-sm dark:bg-slate-950/35 dark:text-slate-200 dark:shadow-blue-500/10"
              >
                <p v-if="selectedReview">
                  {{ selectedReview.content }}
                </p>
                <p v-else class="text-slate-500 dark:text-slate-400">
                  Pilih ulasan dulu
                </p>
              </div>
            </div>

            <div class="mt-4">
              <p class="text-sm font-semibold text-slate-900 dark:text-white">
                Rekomendasi AI
              </p>
              <div
                class="mt-2 rounded-xl bg-slate-50 p-3 text-sm text-slate-700 shadow-sm dark:bg-slate-950/35 dark:text-slate-200 dark:shadow-blue-500/10"
              >
                <p v-if="loading" class="text-slate-500 dark:text-slate-400">
                  Loading...
                </p>
                <p v-else-if="aiReply">{{ aiReply }}</p>
                <p v-else class="text-slate-500 dark:text-slate-400">Pilih ulasan</p>
              </div>
            </div>

            <div class="mt-3 flex gap-2">
              <button
                class="rounded-xl bg-emerald-600 px-4 py-2 text-sm font-semibold text-white shadow-sm transition hover:bg-emerald-700 disabled:cursor-not-allowed disabled:opacity-50"
                :disabled="!aiReply"
                @click="approveReview"
              >
                Approve
              </button>

              <button
                class="rounded-xl bg-red-500 px-4 py-2 text-sm font-semibold text-white shadow-sm transition hover:bg-red-600 disabled:cursor-not-allowed disabled:opacity-50"
                :disabled="!selectedReview"
                @click="rejectReview"
              >
                Reject
              </button>
            </div>
          </div>
        </aside>
      </div>
    </div>
  </div>
</template>
