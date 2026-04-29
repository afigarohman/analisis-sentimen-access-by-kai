<script setup lang="ts">
import { computed, nextTick, onMounted, onUnmounted, ref } from 'vue'
import { isAxiosError } from 'axios'
import type { Plugin } from 'chart.js'
import { Doughnut, Line } from 'vue-chartjs'

import {
  predictSentiment,
  trainModel,
  type SentimentPredictionResponse,
  type TrainResponse,
} from '@/api/ai'
import {
  fetchSentimentDistribution,
  type SentimentDistributionItem,
} from '@/api/dashboard'

// --- Summary KPI (dummy dashboard) ---
const kpis = computed(() => [
  { label: 'Total Reviews', value: '2,650', hint: '+12% minggu ini' },
  { label: 'Positive %', value: '72%', hint: 'Skor 4–5 dominan' },
  { label: 'Negative %', value: '11%', hint: 'Perlu perhatian' },
  { label: 'AI Replies', value: '438', hint: 'Menunggu approval' },
])

const lineData = computed(() => ({
  labels: ['Sen', 'Sel', 'Rab', 'Kam', 'Jum', 'Sab', 'Min'],
  datasets: [
    {
      label: 'Reviews',
      data: [120, 160, 140, 210, 180, 260, 230],
      borderColor: '#60a5fa',
      backgroundColor: 'rgba(96, 165, 250, 0.15)',
      fill: true,
      tension: 0.35,
      pointRadius: 2,
      borderWidth: 2,
    },
  ],
}))

const lineOptions = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: { display: false },
  },
  scales: {
    x: { grid: { display: false }, ticks: { color: '#94a3b8' } },
    y: {
      grid: { color: 'rgba(148,163,184,0.15)' },
      ticks: { color: '#94a3b8' },
    },
  },
}

const pieData = computed(() => ({
  labels: ['Positive', 'Neutral', 'Negative'],
  datasets: [
    {
      data: [72, 17, 11],
      backgroundColor: ['#3b82f6', '#a855f7', '#ef4444'],
      borderWidth: 0,
    },
  ],
}))

const pieOptions = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    glow: { color: 'rgba(168,85,247,0.35)', blur: 22 },
    legend: {
      position: 'bottom' as const,
      labels: {
        color: '#94a3b8',
        boxWidth: 10,
        padding: 14,
        font: { size: 11 },
      },
    },
  },
  cutout: '65%',
}

const glowPlugin: Plugin<'doughnut'> = {
  id: 'glow',
  beforeDatasetDraw(chart) {
    const ctx = chart.ctx
    const opts = (
      chart.config.options as
        | { plugins?: { glow?: { color: string; blur: number } } }
        | undefined
    )?.plugins?.glow
    if (!opts) return
    ctx.save()
    ctx.shadowColor = opts.color
    ctx.shadowBlur = opts.blur
  },
  afterDatasetDraw(chart) {
    chart.ctx.restore()
  },
}

// --- AI Predict (analisis) ---
const inputText = ref('')
const result = ref<SentimentPredictionResponse['result'] | null>(null)
const echoedText = ref<string | null>(null)
const loading = ref(false)
const error = ref<string | null>(null)

const pipelineActiveIndex = ref(-1)
const pipelineSteps = [
  { title: 'Input Review', subtitle: 'Teks ulasan masuk' },
  { title: 'Preprocessing', subtitle: 'Cleaning & tokenisasi' },
  { title: 'Sentiment Analysis', subtitle: 'Model klasifikasi' },
  { title: 'Output Result', subtitle: 'Label & confidence' },
] as const

const STEP_MS = 380

function delay(ms: number) {
  return new Promise<void>((resolve) => {
    setTimeout(resolve, ms)
  })
}

function parseApiError(e: unknown): string {
  if (isAxiosError(e)) {
    const d = e.response?.data as { detail?: unknown } | undefined
    const detail = d?.detail
    if (typeof detail === 'string') return detail
    if (Array.isArray(detail)) {
      return detail
        .map((x: { msg?: string }) => x?.msg)
        .filter(Boolean)
        .join(', ')
    }
    if (e.message) return e.message
  }
  if (e instanceof Error) return e.message
  return 'Gagal menghubungi server. Pastikan backend berjalan di port 8000.'
}

function normalizeLabel(label: string): 'positive' | 'negative' | 'neutral' {
  const l = label.toLowerCase()
  if (l === 'positive' || l === 'negative' || l === 'neutral') return l
  return 'neutral'
}

const confidencePercent = computed(() => {
  if (!result.value) return 0
  return Math.round(result.value.confidence * 1000) / 10
})

const labelNormalized = computed(() =>
  result.value ? normalizeLabel(result.value.label) : null,
)

const labelUi = computed(() => {
  if (!labelNormalized.value) return ''
  return labelNormalized.value.toUpperCase()
})

const sentimentStyles = computed(() => {
  const key = labelNormalized.value
  if (key === 'positive') {
    return {
      ring: 'ring-green-400/40',
      badge: 'border-green-400/35 bg-green-500/10 text-green-400',
      bar: 'from-green-400 to-emerald-500',
      glow: 'shadow-[0_0_28px_rgba(74,222,128,0.35)]',
    }
  }
  if (key === 'negative') {
    return {
      ring: 'ring-red-400/40',
      badge: 'border-red-400/35 bg-red-500/10 text-red-400',
      bar: 'from-red-400 to-rose-600',
      glow: 'shadow-[0_0_28px_rgba(248,113,113,0.35)]',
    }
  }
  return {
    ring: 'ring-yellow-400/40',
    badge: 'border-yellow-400/35 bg-yellow-500/10 text-yellow-400',
    bar: 'from-yellow-400 to-amber-500',
    glow: 'shadow-[0_0_28px_rgba(250,204,21,0.3)]',
  }
})

async function analyze() {
  const text = inputText.value.trim()
  if (!text || loading.value) return

  loading.value = true
  error.value = null
  result.value = null
  echoedText.value = null
  pipelineActiveIndex.value = -1

  pipelineActiveIndex.value = 0
  await delay(STEP_MS)
  pipelineActiveIndex.value = 1
  await delay(STEP_MS)
  pipelineActiveIndex.value = 2

  try {
    const data = await predictSentiment(text)
    echoedText.value = data.text
    result.value = data.result
    pipelineActiveIndex.value = 3
  } catch (e) {
    error.value = parseApiError(e)
    pipelineActiveIndex.value = -1
  } finally {
    loading.value = false
  }
}

// --- Data summary (pre-training) ---
const summaryLoading = ref(false)
const summaryError = ref<string | null>(null)
const summaryItems = ref<SentimentDistributionItem[] | null>(null)

const summaryCounts = computed(() => {
  const items =
    summaryItems.value ??
    ([
      { score: 1, total: 140 },
      { score: 2, total: 150 },
      { score: 3, total: 420 },
      { score: 4, total: 980 },
      { score: 5, total: 960 },
    ] satisfies SentimentDistributionItem[])

  const total = items.reduce((acc, x) => acc + (x.total ?? 0), 0)
  const positive = items
    .filter((x) => x.score === 4 || x.score === 5)
    .reduce((acc, x) => acc + x.total, 0)
  const neutral = items
    .filter((x) => x.score === 3)
    .reduce((acc, x) => acc + x.total, 0)
  const negative = items
    .filter((x) => x.score === 1 || x.score === 2)
    .reduce((acc, x) => acc + x.total, 0)

  return { total, positive, neutral, negative }
})

async function loadSummary() {
  summaryLoading.value = true
  summaryError.value = null
  try {
    summaryItems.value = await fetchSentimentDistribution()
  } catch (e) {
    summaryError.value = parseApiError(e)
    summaryItems.value = null
  } finally {
    summaryLoading.value = false
  }
}

// --- Training ---
const trainingSamplesInput = ref<string | number>('')
const trainingLoading = ref(false)
const trainingProgress = ref(0)
const trainingStatus = ref('')
const trainingError = ref<string | null>(null)
const trainingResult = ref<TrainResponse | null>(null)

let trainingTimer: ReturnType<typeof setInterval> | null = null
let trainingTimeouts: ReturnType<typeof setTimeout>[] = []

const logs = ref<string[]>([])
const logBoxRef = ref<HTMLDivElement | null>(null)

const GAUGE_ARC_LEN = Math.PI * 75

const trainingEpochLabel = computed(() => {
  const p = trainingProgress.value
  const e = Math.min(3, Math.max(1, Math.floor(p / 34) + 1))
  return `Epoch ${e}/3`
})

const gaugeDashOffset = computed(() => {
  const p = Math.min(100, Math.max(0, trainingProgress.value))
  return GAUGE_ARC_LEN * (1 - p / 100)
})

const gaugeNeedleTransform = computed(() => {
  const p = Math.min(100, Math.max(0, trainingProgress.value))
  const deg = 180 - (p / 100) * 180
  return `rotate(${deg} 100 100)`
})

function clearTrainingTimers() {
  if (trainingTimer) {
    clearInterval(trainingTimer)
    trainingTimer = null
  }
  trainingTimeouts.forEach((t) => clearTimeout(t))
  trainingTimeouts = []
}

async function pushLog(line: string) {
  logs.value.push(line)
  await nextTick()
  const el = logBoxRef.value
  if (el) el.scrollTop = el.scrollHeight
}

function clearLogs() {
  logs.value = []
  void nextTick().then(() => {
    const el = logBoxRef.value
    if (el) el.scrollTop = el.scrollHeight
  })
}

async function startTraining() {
  if (trainingLoading.value) return

  const raw = trainingSamplesInput.value
  const trimmed = (typeof raw === 'string' ? raw : String(raw ?? '')).trim()
  let samples: number | undefined
  if (trimmed !== '') {
    const n = Number(trimmed)
    if (Number.isNaN(n) || n < 1) {
      trainingError.value = 'Jumlah data tidak valid'
      return
    }
    samples = n
  }

  trainingLoading.value = true
  trainingProgress.value = 0
  trainingError.value = null
  trainingResult.value = null
  trainingStatus.value = 'Starting training...'

  clearLogs()
  await pushLog('🚀 Starting training...')

  clearTrainingTimers()

  // Simulasi progress 0 -> 90 sambil menunggu API.
  const milestones = {
    p20: false,
    p40: false,
    p60: false,
    p80: false,
  }

  trainingTimer = setInterval(() => {
    if (trainingProgress.value >= 90) return
    const next = Math.min(
      90,
      trainingProgress.value + Math.floor(4 + Math.random() * 9),
    )
    trainingProgress.value = next

    if (!milestones.p20 && next >= 20) {
      milestones.p20 = true
      trainingStatus.value = 'Loading dataset...'
      void pushLog('📦 Loading dataset...')
      return
    }
    if (!milestones.p40 && next >= 40) {
      milestones.p40 = true
      trainingStatus.value = 'Cleaning text...'
      void pushLog('🧹 Cleaning text...')
      return
    }
    if (!milestones.p60 && next >= 60) {
      milestones.p60 = true
      trainingStatus.value = 'Training model...'
      void pushLog('🤖 Training model...')
      return
    }
    if (!milestones.p80 && next >= 80) {
      milestones.p80 = true
      trainingStatus.value = 'Evaluating...'
      void pushLog('📊 Evaluating...')
    }
  }, 420)

  try {
    const res = await trainModel(samples, 5000)
    trainingResult.value = res

    clearTrainingTimers()
    trainingProgress.value = 100

    await pushLog(`Accuracy: ${(res.accuracy * 100).toFixed(2)}%`)
    await pushLog(`Total data: ${res.samples}`)
    await pushLog('✅ Training selesai')

    trainingStatus.value = `Training selesai · akurasi ${(res.accuracy * 100).toFixed(2)}%`
  } catch (e) {
    trainingError.value = parseApiError(e)
    trainingStatus.value = 'Training gagal'
    trainingProgress.value = 0
    clearTrainingTimers()
    await pushLog('❌ Training gagal')
    await pushLog(String(trainingError.value ?? 'Unknown error'))
  } finally {
    trainingLoading.value = false
  }
}

onMounted(loadSummary)

onUnmounted(() => {
  clearTrainingTimers()
})
</script>

<template>
  <div
    class="relative min-h-full overflow-hidden rounded-2xl bg-gradient-to-br from-blue-950/90 via-slate-950/95 to-slate-900 p-4 sm:p-6"
  >
    <div
      class="pointer-events-none absolute -top-24 left-1/2 h-[480px] w-[480px] -translate-x-1/2 rounded-full bg-gradient-to-tr from-blue-600/25 via-indigo-500/15 to-transparent blur-3xl"
    />
    <div
      class="pointer-events-none absolute -bottom-32 -right-16 h-[420px] w-[420px] rounded-full bg-gradient-to-tl from-slate-800/40 via-blue-900/20 to-transparent blur-3xl"
    />

    <div class="relative mx-auto w-full max-w-6xl space-y-6">
      <!-- Header -->
      <section
        class="relative overflow-hidden rounded-xl border border-white/10 bg-white/5 p-6 shadow-[0_0_30px_rgba(59,130,246,0.3)] backdrop-blur-xl transition hover:shadow-[0_0_40px_rgba(59,130,246,0.4)]"
      >
        <div
          class="pointer-events-none absolute -left-16 -top-16 h-48 w-48 rounded-full bg-blue-500/20 blur-2xl"
        />
        <h2 class="relative text-lg font-semibold tracking-tight text-white">
          <span
            class="bg-gradient-to-r from-blue-200 via-cyan-200 to-blue-100 bg-clip-text text-transparent"
          >
            AI Pipeline
          </span>
        </h2>
        <p class="relative mt-1 text-sm text-slate-300/90">
          Dashboard AI: statistik, analisis sentimen, dan training model (TF-IDF +
          Logistic Regression).
        </p>
      </section>

      <!-- KPI -->
      <section class="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <div
          v-for="k in kpis"
          :key="k.label"
          class="group relative overflow-hidden rounded-xl border border-white/10 bg-white/5 p-5 shadow-[0_0_24px_rgba(59,130,246,0.2)] backdrop-blur-xl transition duration-300 hover:-translate-y-0.5 hover:shadow-[0_0_32px_rgba(59,130,246,0.35)]"
        >
          <div
            class="pointer-events-none absolute -right-24 -top-24 h-56 w-56 rounded-full bg-gradient-to-tr from-blue-500/18 via-purple-500/16 to-red-500/12 blur-2xl opacity-80 transition group-hover:opacity-100"
          />
          <p class="text-xs font-semibold text-slate-400">{{ k.label }}</p>
          <p class="mt-2 text-2xl font-extrabold tracking-tight text-white">
            {{ k.value }}
          </p>
          <p class="mt-1 text-xs text-slate-400">{{ k.hint }}</p>
        </div>
      </section>

      <!-- Charts -->
      <section class="grid grid-cols-1 gap-6 lg:grid-cols-3">
        <div
          class="group relative overflow-hidden lg:col-span-2 rounded-xl border border-white/10 bg-white/5 p-6 shadow-[0_0_30px_rgba(59,130,246,0.25)] backdrop-blur-xl transition hover:shadow-[0_0_36px_rgba(59,130,246,0.35)]"
        >
          <div
            class="pointer-events-none absolute -left-24 -bottom-24 h-72 w-72 rounded-full bg-gradient-to-tr from-blue-500/18 via-purple-500/16 to-red-500/12 blur-2xl opacity-80 transition group-hover:opacity-100"
          />
          <div class="flex items-center justify-between">
            <div>
              <p class="text-sm font-semibold text-white">Trend ulasan</p>
              <p class="mt-0.5 text-xs text-slate-400">Ringkasan mingguan (demo)</p>
            </div>
            <span
              class="rounded-full bg-blue-500/15 px-3 py-1 text-xs font-semibold text-blue-300"
            >
              Statistik
            </span>
          </div>
          <div class="mt-4 h-72">
            <Line :data="lineData" :options="lineOptions" />
          </div>
        </div>

        <div
          class="group relative overflow-hidden rounded-xl border border-white/10 bg-white/5 p-6 shadow-[0_0_30px_rgba(59,130,246,0.25)] backdrop-blur-xl transition hover:shadow-[0_0_36px_rgba(59,130,246,0.35)]"
        >
          <div
            class="pointer-events-none absolute -right-24 -bottom-24 h-72 w-72 rounded-full bg-gradient-to-tr from-purple-500/18 via-blue-500/14 to-red-500/10 blur-2xl opacity-80 transition group-hover:opacity-100"
          />
          <p class="text-sm font-semibold text-white">Distribusi sentimen</p>
          <p class="mt-0.5 text-xs text-slate-400">Positive / Neutral / Negative</p>
          <div class="mt-4 h-72">
            <Doughnut
              :data="pieData"
              :options="pieOptions"
              :plugins="[glowPlugin]"
            />
          </div>
        </div>
      </section>

      <!-- Pipeline flow (analisis) -->
      <section
        class="relative overflow-hidden rounded-xl border border-white/10 bg-white/5 p-6 shadow-[0_0_30px_rgba(59,130,246,0.25)] backdrop-blur-xl"
      >
        <div>
          <p class="text-sm font-semibold text-white">Pipeline analisis</p>
          <p class="mt-0.5 text-xs text-slate-400">
            Alur saat Anda menjalankan tes sentimen di bawah
          </p>
        </div>

        <div class="mt-5 overflow-x-auto pb-1">
          <div
            class="flex min-w-[720px] items-center gap-3 sm:min-w-0 sm:justify-between"
          >
            <template v-for="(s, idx) in pipelineSteps" :key="s.title">
              <div
                class="w-[9.5rem] shrink-0 rounded-xl border px-3 py-3 transition-all duration-500 sm:w-auto sm:flex-1"
                :class="
                  pipelineActiveIndex === idx
                    ? 'border-blue-400/70 bg-blue-500/15 shadow-[0_0_24px_-4px_rgba(59,130,246,0.65)]'
                    : pipelineActiveIndex > idx
                      ? 'border-emerald-500/25 bg-emerald-500/5'
                      : 'border-white/10 bg-slate-950/40'
                "
              >
                <div class="flex items-start gap-2">
                  <span
                    class="flex h-8 w-8 shrink-0 items-center justify-center rounded-lg text-xs font-bold transition-colors duration-300"
                    :class="
                      pipelineActiveIndex === idx
                        ? 'bg-gradient-to-br from-blue-500 to-indigo-600 text-white shadow-lg shadow-blue-500/40'
                        : pipelineActiveIndex > idx
                          ? 'bg-emerald-500/20 text-emerald-200'
                          : 'bg-slate-800 text-slate-400'
                    "
                  >
                    {{ idx + 1 }}
                  </span>
                  <div class="min-w-0">
                    <p class="truncate text-xs font-semibold text-white sm:text-sm">
                      {{ s.title }}
                    </p>
                    <p class="truncate text-[11px] text-slate-400 sm:text-xs">
                      {{ s.subtitle }}
                    </p>
                  </div>
                </div>
              </div>

              <div
                v-if="idx !== pipelineSteps.length - 1"
                class="flex shrink-0 items-center"
              >
                <div
                  class="h-0.5 w-6 rounded-full transition-colors duration-500 sm:w-10"
                  :class="
                    pipelineActiveIndex > idx
                      ? 'bg-gradient-to-r from-emerald-400/80 to-blue-500/80'
                      : 'bg-slate-700/80'
                  "
                />
                <svg
                  viewBox="0 0 24 24"
                  class="ml-0.5 h-4 w-4 shrink-0 transition-colors duration-500"
                  :class="
                    pipelineActiveIndex > idx ? 'text-blue-400' : 'text-slate-600'
                  "
                  fill="none"
                  stroke="currentColor"
                  stroke-width="2"
                >
                  <path
                    stroke-linecap="round"
                    stroke-linejoin="round"
                    d="M9 5l7 7-7 7"
                  />
                </svg>
              </div>
            </template>
          </div>
        </div>
      </section>

      <!-- AI Test -->
      <section
        class="relative overflow-hidden rounded-xl border border-white/10 bg-white/5 p-6 shadow-[0_0_30px_rgba(59,130,246,0.25)] backdrop-blur-xl"
      >
        <div
          class="pointer-events-none absolute -right-20 -top-20 h-56 w-56 rounded-full bg-indigo-500/15 blur-3xl"
        />
        <h3 class="relative text-sm font-semibold text-white">AI Test — analisis sentimen</h3>
        <p class="relative mt-0.5 text-xs text-slate-400">
          Endpoint:
          <code class="rounded bg-white/10 px-1 py-0.5 text-[11px] text-cyan-200/90"
            >POST /ai/predict</code
          >
        </p>

        <label class="relative mt-4 block text-sm font-medium text-slate-200">
          Ulasan
        </label>
        <textarea
          v-model="inputText"
          rows="5"
          :disabled="loading"
          placeholder="Contoh: Aplikasinya cepat dan UI-nya enak dipakai."
          class="relative mt-2 w-full resize-y rounded-xl border border-white/10 bg-slate-950/50 px-4 py-3 text-sm text-slate-100 placeholder:text-slate-500 focus:border-blue-400/50 focus:outline-none focus:ring-2 focus:ring-blue-500/30 disabled:cursor-not-allowed disabled:opacity-60"
        />

        <div
          class="relative mt-4 flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between"
        >
          <button
            type="button"
            class="inline-flex items-center justify-center rounded-xl bg-gradient-to-r from-blue-600 to-indigo-600 px-6 py-2.5 text-sm font-semibold text-white shadow-[0_8px_30px_-6px_rgba(37,99,235,0.65)] transition hover:from-blue-500 hover:to-indigo-500 hover:shadow-[0_12px_40px_-8px_rgba(59,130,246,0.75)] active:scale-[0.98] disabled:cursor-not-allowed disabled:opacity-50"
            :disabled="loading || !inputText.trim()"
            @click="analyze"
          >
            Analisis AI
          </button>
          <p v-if="loading" class="text-sm font-medium text-cyan-200/90">
            AI sedang menganalisis…
          </p>
        </div>

        <div
          v-if="error"
          class="relative mt-4 rounded-xl border border-red-400/35 bg-red-950/50 px-4 py-3 text-sm text-red-100 backdrop-blur-sm"
        >
          {{ error }}
        </div>
      </section>

      <!-- Result predict -->
      <section
        v-if="result && !error"
        class="relative overflow-hidden rounded-xl border border-white/10 bg-white/5 p-6 shadow-[0_0_36px_-10px_rgba(59,130,246,0.4)] backdrop-blur-xl transition duration-500"
        :class="[sentimentStyles.ring, sentimentStyles.glow]"
      >
        <div
          class="pointer-events-none absolute -left-24 bottom-0 h-48 w-48 rounded-full bg-gradient-to-tr from-blue-500/20 to-transparent blur-3xl"
        />
        <div class="relative flex flex-col gap-4 sm:flex-row sm:items-start sm:justify-between">
          <div class="min-w-0 flex-1">
            <p class="text-xs font-semibold uppercase tracking-wide text-slate-400">
              Hasil
            </p>
            <p class="mt-1 line-clamp-4 text-sm text-slate-200">
              {{ echoedText }}
            </p>
          </div>
          <div class="flex flex-col items-start gap-2 sm:items-end">
            <span
              class="inline-flex rounded-full border px-4 py-1.5 text-sm font-bold tracking-wide"
              :class="sentimentStyles.badge"
            >
              {{ labelUi }}
            </span>
            <p class="text-xs text-slate-400">
              Confidence:
              <span class="font-semibold text-white">{{ confidencePercent }}%</span>
            </p>
          </div>
        </div>

        <div class="relative mt-5">
          <div class="mb-1 flex justify-between text-[11px] text-slate-500">
            <span>Keyakinan model</span>
            <span>{{ confidencePercent }}%</span>
          </div>
          <div
            class="h-2.5 w-full overflow-hidden rounded-full bg-slate-800/90 ring-1 ring-white/10"
          >
            <div
              class="h-full rounded-full bg-gradient-to-r transition-all duration-700 ease-out"
              :class="sentimentStyles.bar"
              :style="{ width: `${Math.min(100, confidencePercent)}%` }"
            />
          </div>
        </div>
      </section>

      <!-- Training control -->
      <section
        class="relative overflow-hidden rounded-xl border border-white/10 bg-white/5 p-6 shadow-[0_0_30px_rgba(59,130,246,0.25)] backdrop-blur-xl"
      >
        <h3 class="text-sm font-semibold text-white">Training control</h3>
        <p class="mt-0.5 text-xs text-slate-400">
          Ekspor ulasan dari database ke CSV lalu latih model (
          <code class="rounded bg-white/10 px-1 text-[11px]">POST /ai/train</code>
          ).
        </p>

        <!-- Data summary -->
        <div
          class="mt-4 rounded-xl border border-white/10 bg-white/5 p-4 shadow-[0_0_30px_rgba(59,130,246,0.12)] backdrop-blur-xl"
        >
          <div class="flex items-center justify-between">
            <p class="text-xs font-semibold text-slate-200">Data summary</p>
            <p v-if="summaryLoading" class="text-[11px] text-slate-400">
              Memuat…
            </p>
          </div>

          <div
            v-if="summaryError"
            class="mt-3 rounded-lg border border-red-400/30 bg-red-950/40 px-3 py-2 text-xs text-red-100"
          >
            {{ summaryError }}
          </div>

          <div class="mt-3 grid grid-cols-2 gap-3 sm:grid-cols-4">
            <div class="rounded-xl border border-white/10 bg-slate-950/35 p-3">
              <p class="text-[11px] text-slate-400">Total data</p>
              <p class="mt-1 text-lg font-extrabold text-white">
                {{ summaryCounts.total }}
              </p>
            </div>
            <div class="rounded-xl border border-white/10 bg-slate-950/35 p-3">
              <p class="text-[11px] text-slate-400">Positive</p>
              <p class="mt-1 text-lg font-extrabold text-green-400">
                {{ summaryCounts.positive }}
              </p>
            </div>
            <div class="rounded-xl border border-white/10 bg-slate-950/35 p-3">
              <p class="text-[11px] text-slate-400">Neutral</p>
              <p class="mt-1 text-lg font-extrabold text-yellow-400">
                {{ summaryCounts.neutral }}
              </p>
            </div>
            <div class="rounded-xl border border-white/10 bg-slate-950/35 p-3">
              <p class="text-[11px] text-slate-400">Negative</p>
              <p class="mt-1 text-lg font-extrabold text-red-400">
                {{ summaryCounts.negative }}
              </p>
            </div>
          </div>
        </div>

        <div class="mt-4 flex flex-wrap items-end gap-3">
          <label class="flex flex-col text-xs font-medium text-slate-300">
            Jumlah data (opsional)
            <input
              v-model="trainingSamplesInput"
              type="number"
              min="20"
              placeholder="Semua"
              :disabled="trainingLoading"
              class="mt-1 w-40 rounded-xl border border-white/10 bg-slate-950/50 px-3 py-2 text-sm text-slate-100 placeholder:text-slate-500 focus:border-blue-400/50 focus:outline-none focus:ring-2 focus:ring-blue-500/30 disabled:opacity-50"
            />
          </label>
          <button
            type="button"
            class="rounded-xl bg-gradient-to-r from-sky-600 to-cyan-600 px-5 py-2.5 text-sm font-semibold text-white shadow-lg shadow-cyan-500/20 transition hover:from-sky-500 hover:to-cyan-500 active:scale-[0.98] disabled:cursor-not-allowed disabled:opacity-50"
            :disabled="trainingLoading"
            @click="startTraining"
          >
            {{ trainingLoading ? 'Training…' : 'Start Training' }}
          </button>
        </div>

        <!-- Training log -->
        <div class="mt-4">
          <div class="mb-2 flex items-center justify-between">
            <p class="text-xs font-semibold text-slate-200">Training log</p>
            <button
              type="button"
              class="text-[11px] text-slate-400 transition hover:text-slate-200"
              @click="clearLogs"
            >
              Clear
            </button>
          </div>
          <div
            ref="logBoxRef"
            class="h-40 overflow-y-auto rounded-xl border border-white/10 bg-black/40 p-3 font-mono text-[12px] leading-5 text-green-400 shadow-[inset_0_0_0_1px_rgba(255,255,255,0.02)]"
          >
            <p v-if="logs.length === 0" class="text-green-400/60">
              (log akan muncul saat training dimulai)
            </p>
            <p v-for="(l, i) in logs" :key="i">{{ l }}</p>
          </div>
        </div>

        <div v-if="trainingLoading || trainingProgress > 0" class="mt-4 space-y-2">
          <div class="flex justify-between text-xs text-slate-400">
            <span>Progress</span>
            <span>{{ Math.round(trainingProgress) }}%</span>
          </div>
          <div
            class="h-2 w-full overflow-hidden rounded-full bg-slate-800 ring-1 ring-white/10"
          >
            <div
              class="h-full rounded-full bg-gradient-to-r from-blue-500 via-cyan-400 to-cyan-300 transition-all duration-300 ease-out"
              :style="{ width: `${Math.min(100, trainingProgress)}%` }"
            />
          </div>
          <p class="text-xs text-slate-300">{{ trainingStatus }}</p>
        </div>

        <div
          v-if="trainingError"
          class="mt-3 rounded-xl border border-red-400/35 bg-red-950/45 px-3 py-2 text-sm text-red-100"
        >
          {{ trainingError }}
        </div>
        <div
          v-if="trainingResult && !trainingError"
          class="mt-3 rounded-xl border border-emerald-400/25 bg-emerald-950/30 px-3 py-2 text-xs text-emerald-100"
        >
          Sampel: {{ trainingResult.samples }} · Akurasi test:
          {{ (trainingResult.accuracy * 100).toFixed(2) }}%
        </div>
      </section>

      <!-- Speedometer training viz -->
      <section
        class="relative overflow-hidden rounded-xl border border-white/10 bg-white/5 p-6 shadow-[0_0_30px_rgba(59,130,246,0.3)] backdrop-blur-xl"
      >
        <h3 class="text-center text-sm font-semibold text-white">
          Visualisasi training
        </h3>
        <p class="mt-1 text-center text-xs text-slate-400">
          Speedometer progres (simulasi + respons API)
        </p>

        <div class="relative mx-auto mt-6 max-w-sm">
          <svg
            class="mx-auto block w-full max-w-[280px]"
            viewBox="0 0 200 120"
            aria-hidden="true"
          >
            <defs>
              <linearGradient id="gaugeGrad" x1="0%" y1="0%" x2="100%" y2="0%">
                <stop offset="0%" stop-color="#3b82f6" />
                <stop offset="100%" stop-color="#22d3ee" />
              </linearGradient>
            </defs>
            <!-- Track -->
            <path
              d="M 25 100 A 75 75 0 0 1 175 100"
              fill="none"
              stroke="rgba(51,65,85,0.9)"
              stroke-width="14"
              stroke-linecap="round"
            />
            <!-- Progress arc -->
            <path
              d="M 25 100 A 75 75 0 0 1 175 100"
              fill="none"
              stroke="url(#gaugeGrad)"
              stroke-width="14"
              stroke-linecap="round"
              :stroke-dasharray="GAUGE_ARC_LEN"
              :stroke-dashoffset="gaugeDashOffset"
              class="transition-[stroke-dashoffset] duration-300 ease-out"
            />
            <!-- Needle -->
            <g :transform="gaugeNeedleTransform">
              <line
                x1="100"
                y1="100"
                x2="175"
                y2="100"
                stroke="#e2e8f0"
                stroke-width="3"
                stroke-linecap="round"
              />
              <circle cx="100" cy="100" r="8" fill="#1e293b" stroke="#38bdf8" stroke-width="2" />
            </g>
          </svg>

          <div class="mt-4 space-y-1 text-center text-xs text-slate-300">
            <p class="font-medium text-cyan-200/90">Training Model...</p>
            <p>{{ trainingEpochLabel }}</p>
            <p class="text-slate-500">{{ trainingStatus || 'Siap memulai training' }}</p>
          </div>
        </div>
      </section>
    </div>
  </div>
</template>
