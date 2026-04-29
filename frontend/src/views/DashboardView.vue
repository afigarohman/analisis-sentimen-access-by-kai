<script setup lang="ts">
import { onMounted, ref } from 'vue'

import {
  fetchDashboardStats,
  fetchReviewGrowth,
  fetchSentimentDistribution,
  fetchSentimentTrend,
  type DashboardStats,
  type ReviewGrowthItem,
  type SentimentDistributionItem,
  type SentimentTrendItem,
} from '@/api/dashboard'
import KpiCard from '@/components/dashboard/KpiCard.vue'
import ReviewGrowthChart from '@/components/dashboard/ReviewGrowthChart.vue'
import SentimentDistributionChart from '@/components/dashboard/SentimentDistributionChart.vue'
import SentimentTrendChart from '@/components/dashboard/SentimentTrendChart.vue'

const loading = ref(true)
const error = ref<string | null>(null)
const stats = ref<DashboardStats | null>(null)
const distribution = ref<SentimentDistributionItem[]>([])
const growth = ref<ReviewGrowthItem[]>([])
const trend = ref<SentimentTrendItem[]>([])

async function load() {
  loading.value = true
  error.value = null
  try {
    const [s, d, g, t] = await Promise.all([
      fetchDashboardStats(),
      fetchSentimentDistribution(),
      fetchReviewGrowth(),
      fetchSentimentTrend(),
    ])
    stats.value = s
    distribution.value = d
    growth.value = g
    trend.value = t
  } catch (e) {
    error.value =
      e instanceof Error ? e.message : 'Gagal memuat data dari server'
  } finally {
    loading.value = false
  }
}

onMounted(load)
</script>

<template>
  <div class="mx-auto w-full max-w-6xl space-y-4 sm:space-y-6">
    <div
      v-if="loading"
      class="flex h-64 items-center justify-center text-slate-500 dark:text-slate-400"
    >
      Memuat data…
    </div>
    <div
      v-else-if="error"
      class="rounded-xl bg-red-50 p-4 text-red-700 shadow-sm dark:bg-red-950/40 dark:text-red-200 dark:shadow-blue-500/10"
    >
      {{ error }}
    </div>
    <div v-else class="space-y-4 sm:space-y-6">
      <div class="grid grid-cols-1 gap-4 sm:grid-cols-2 xl:grid-cols-5">
        <KpiCard
          title="Total ulasan"
          :value="stats?.total_reviews ?? 0"
          accent="text-slate-800 dark:text-slate-100"
        />
        <KpiCard
          title="Positif (4–5)"
          :value="stats?.total_positive ?? 0"
          accent="text-emerald-600"
        />
        <KpiCard
          title="Netral (3)"
          :value="stats?.total_neutral ?? 0"
          accent="text-slate-600"
        />
        <KpiCard
          title="Negatif (1–2)"
          :value="stats?.total_negative ?? 0"
          accent="text-rose-600"
        />
        <KpiCard
          title="Rata-rata Rating"
          :value="stats?.average_score?.toFixed(1) ?? 0"
          accent="text-yellow-500"
        />
      </div>

      <div class="grid grid-cols-1 gap-6 lg:grid-cols-2">
        <section
          class="group relative overflow-hidden rounded-2xl bg-white/90 p-4 shadow-sm backdrop-blur transition-all duration-300 hover:shadow-md sm:p-6 dark:bg-slate-900/40 dark:shadow-blue-500/10"
        >
          <div class="pointer-events-none absolute -left-24 -bottom-24 h-72 w-72 rounded-full bg-gradient-to-tr from-blue-500/22 via-cyan-400/12 to-transparent blur-2xl opacity-80 transition group-hover:opacity-100" />
          <h2 class="text-base font-semibold text-slate-900 dark:text-white">
            Distribusi sentimen (skor)
          </h2>
          <p class="mt-1 text-xs text-slate-500 dark:text-slate-400">
            Proporsi ulasan per star rating
          </p>
          <SentimentDistributionChart :items="distribution" />
        </section>
        <section
          class="group relative overflow-hidden rounded-2xl bg-white/90 p-4 shadow-sm backdrop-blur transition-all duration-300 hover:shadow-md sm:p-6 dark:bg-slate-900/40 dark:shadow-blue-500/10"
        >
          <div class="pointer-events-none absolute -right-24 -bottom-24 h-72 w-72 rounded-full bg-gradient-to-tr from-cyan-400/20 via-blue-500/12 to-transparent blur-2xl opacity-80 transition group-hover:opacity-100" />
          <h2 class="text-base font-semibold text-slate-900 dark:text-white">
            Pertumbuhan ulasan
          </h2>
          <p class="mt-1 text-xs text-slate-500 dark:text-slate-400">
            Jumlah ulasan per tanggal
          </p>
          <ReviewGrowthChart :items="growth" />
        </section>
      </div>

      <section
        class="group relative overflow-hidden rounded-2xl bg-white/90 p-4 shadow-sm backdrop-blur transition-all duration-300 hover:shadow-md sm:p-6 dark:bg-slate-900/40 dark:shadow-blue-500/10"
      >
        <div class="pointer-events-none absolute -left-24 -top-24 h-72 w-72 rounded-full bg-gradient-to-tr from-blue-500/20 via-cyan-400/12 to-transparent blur-2xl opacity-80 transition group-hover:opacity-100" />
        <h2 class="text-base font-semibold text-slate-900 dark:text-white">
          Tren sentimen per hari
        </h2>
        <p class="mt-1 text-xs text-slate-500 dark:text-slate-400">
          Per skor per tanggal
        </p>
        <SentimentTrendChart :items="trend" />
      </section>
    </div>
  </div>
</template>
