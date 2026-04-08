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
import DashboardHeader from '@/components/dashboard/DashboardHeader.vue'
import DashboardSidebar from '@/components/dashboard/DashboardSidebar.vue'
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
const sidebarOpen = ref(false)

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
  <div class="flex min-h-screen overflow-x-hidden bg-slate-100">
    <DashboardSidebar :open="sidebarOpen" @close="sidebarOpen = false" />
    <div class="flex min-w-0 flex-1 flex-col">
      <DashboardHeader
        title="Dashboard"
        breadcrumb="Dashboard / Ringkasan ulasan"
        @toggleSidebar="sidebarOpen = true"
      />
      <main class="flex-1 overflow-auto p-3 sm:p-6">
        <div
          v-if="loading"
          class="flex h-64 items-center justify-center text-slate-500"
        >
          Memuat data…
        </div>
        <div
          v-else-if="error"
          class="rounded-xl bg-red-50 p-4 text-red-700 ring-1 ring-red-200"
        >
          {{ error }}
        </div>
        <div v-else class="space-y-4 sm:space-y-6">
          <div class="grid grid-cols-1 gap-4 sm:grid-cols-2 xl:grid-cols-5">
            <KpiCard title="Total ulasan" :value="stats?.total_reviews ?? 0" />
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
              class="rounded-2xl bg-white p-4 shadow-sm ring-1 ring-slate-200/80 sm:p-6"
            >
              <h2 class="text-base font-semibold text-slate-900">
                Distribusi sentimen (skor)
              </h2>
              <p class="mt-1 text-xs text-slate-500">
                Proporsi ulasan per star rating
              </p>
              <SentimentDistributionChart :items="distribution" />
            </section>
            <section
              class="rounded-2xl bg-white p-4 shadow-sm ring-1 ring-slate-200/80 sm:p-6"
            >
              <h2 class="text-base font-semibold text-slate-900">
                Pertumbuhan ulasan
              </h2>
              <p class="mt-1 text-xs text-slate-500">
                Jumlah ulasan per tanggal
              </p>
              <ReviewGrowthChart :items="growth" />
            </section>
          </div>

          <section
            class="rounded-2xl bg-white p-4 shadow-sm ring-1 ring-slate-200/80 sm:p-6"
          >
            <h2 class="text-base font-semibold text-slate-900">
              Tren sentimen per hari
            </h2>
            <p class="mt-1 text-xs text-slate-500">Per skor per tanggal</p>
            <SentimentTrendChart :items="trend" />
          </section>
        </div>
      </main>
    </div>
  </div>
</template>
