<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'

import { formatHttpClientError } from '@/api/httpErrors'
import {
  fetchDashboardStats,
  fetchAspectDistribution,
  fetchReviewGrowth,
  fetchSentimentDistribution,
  fetchSentimentTrend,
  type DashboardStats,
  type AspectDistributionItem,
  type ReviewGrowthItem,
  type SentimentDistributionItem,
  type SentimentTrendItem,
} from '@/api/dashboard'
import DashboardCardShell, {
  type DashboardSpotlight,
} from '@/components/dashboard/DashboardCardShell.vue'
import KpiCardModern from '@/components/dashboard/KpiCardModern.vue'
import AspectOverviewCard from '@/components/dashboard/AspectOverviewCard.vue'
import ReviewGrowthChart from '@/components/dashboard/ReviewGrowthChart.vue'
import SentimentDistributionChart from '@/components/dashboard/SentimentDistributionChart.vue'
import SentimentTrendChart from '@/components/dashboard/SentimentTrendChart.vue'

function padFour(values: number[]): number[] {
  const v = values.map((x) => (Number.isFinite(x) ? x : 0))
  const out = [...v]
  while (out.length < 4) out.unshift(0)
  return out.slice(-4)
}

function candlesFromGrowth(items: ReviewGrowthItem[]): number[] {
  const s = [...items].sort((a, b) => a.date.localeCompare(b.date)).slice(-4)
  return padFour(s.map((x) => Number(x.total ?? 0)))
}

function sumTrend(
  items: SentimentTrendItem[],
  date: string,
  scores: number[] | null,
): number {
  if (!date) return 0
  let s = 0
  for (const it of items) {
    if (it.date !== date) continue
    if (scores === null) s += Number(it.total ?? 0)
    else if (scores.includes(it.score)) s += Number(it.total ?? 0)
  }
  return s
}

function candlesFromTrend(
  items: SentimentTrendItem[],
  mode: 'pos' | 'neu' | 'neg' | 'all' | 'avg',
): number[] {
  const dates = [...new Set(items.map((i) => i.date))].sort().slice(-4)
  const vals = dates.map((d) => {
    if (mode === 'pos') return sumTrend(items, d, [4, 5])
    if (mode === 'neu') return sumTrend(items, d, [3])
    if (mode === 'neg') return sumTrend(items, d, [1, 2])
    if (mode === 'all') return sumTrend(items, d, null)
    let w = 0
    let c = 0
    for (const it of items) {
      if (it.date !== d) continue
      w += Number(it.score) * Number(it.total ?? 0)
      c += Number(it.total ?? 0)
    }
    if (!c) return 0
    return Math.round((w / c) * 20)
  })
  return padFour(vals)
}

/** Variasi sorot pojok untuk KPI (berputar tiap kartu). */
function kpiSpotlight(index: number): DashboardSpotlight {
  const spots: DashboardSpotlight[] = ['tl', 'tr', 'bl', 'br', 'tm', 'offset']
  return spots[index % spots.length]!
}

const loading = ref(true)
const error = ref<string | null>(null)
const stats = ref<DashboardStats | null>(null)
const distribution = ref<SentimentDistributionItem[]>([])
const aspects = ref<AspectDistributionItem[]>([])
const growth = ref<ReviewGrowthItem[]>([])
const trend = ref<SentimentTrendItem[]>([])

const aspectCardSpot: DashboardSpotlight = 'bl'

const kpiItems = computed(() => {
  const s = stats.value
  if (!s) return []

  const total = s.total_reviews || 0
  const pct = (n: number) => (total > 0 ? (n / total) * 100 : 0)

  const g = growth.value
  const tr = trend.value

  const candlesTotal =
    g.length > 0 ? candlesFromGrowth(g) : candlesFromTrend(tr, 'all')
  const candlesPos = candlesFromTrend(tr, 'pos')
  const candlesNeu = candlesFromTrend(tr, 'neu')
  const candlesNeg = candlesFromTrend(tr, 'neg')
  const candlesRating = candlesFromTrend(tr, 'avg')

  return [
    {
      title: 'Total ulasan',
      value: s.total_reviews,
      percent: null as number | null,
      trend: 'neutral' as const,
      subtitle: 'Total ulasan tersimpan di database',
      candles: candlesTotal,
      icon: 'total' as const,
    },
    {
      title: 'Positif (4–5)',
      value: s.total_positive,
      percent: pct(s.total_positive),
      trend: 'up' as const,
      subtitle: 'Ulasan dengan skor 4–5',
      candles: candlesPos,
      icon: 'positive' as const,
    },
    {
      title: 'Netral (3)',
      value: s.total_neutral,
      percent: pct(s.total_neutral),
      trend: 'neutral' as const,
      subtitle: 'Ulasan dengan skor 3',
      candles: candlesNeu,
      icon: 'neutral' as const,
    },
    {
      title: 'Negatif (1–2)',
      value: s.total_negative,
      percent: pct(s.total_negative),
      trend: 'down' as const,
      subtitle: 'Ulasan dengan skor 1–2',
      candles: candlesNeg,
      icon: 'negative' as const,
    },
    {
      title: 'Rata-rata Rating',
      value: s.average_score?.toFixed(1) ?? 0,
      percent: null as number | null,
      trend: 'neutral' as const,
      subtitle: 'Rata-rata skor ulasan (1–5)',
      candles: candlesRating,
      icon: 'rating' as const,
    },
  ]
})

async function load() {
  loading.value = true
  error.value = null
  try {
    const [s, d, a, g, t] = await Promise.all([
      fetchDashboardStats(),
      fetchSentimentDistribution(),
      fetchAspectDistribution(),
      fetchReviewGrowth(),
      fetchSentimentTrend(),
    ])
    stats.value = s
    distribution.value = d
    aspects.value = a
    growth.value = g
    trend.value = t
  } catch (e) {
    error.value = formatHttpClientError(e)
  } finally {
    loading.value = false
  }
}

onMounted(load)
</script>

<template>
  <div class="mx-auto w-full max-w-6xl space-y-4 sm:space-y-6">
    <DashboardCardShell
      v-if="loading"
      variant="offset"
      tag="div"
      class="flex h-64 items-center justify-center p-6 text-slate-300/85"
    >
      Memuat data…
    </DashboardCardShell>
    <div
      v-else-if="error"
      class="rounded-[1.75rem] border border-red-400/35 bg-red-950/45 p-4 text-red-100 shadow-[0_18px_55px_-24px_rgba(239,68,68,0.25)] backdrop-blur-xl transition duration-300 hover:-translate-y-0.5 hover:border-red-300/45 hover:shadow-[0_28px_60px_-22px_rgba(239,68,68,0.35),0_14px_40px_-14px_rgba(248,113,113,0.12)]"
    >
      {{ error }}
    </div>
    <div v-else class="space-y-4 sm:space-y-6">
      <section class="relative">
        <div class="-mx-1 overflow-x-auto pb-2">
          <div class="flex min-w-max gap-4 px-1">
            <div
              v-for="(k, kpiIdx) in kpiItems"
              :key="k.title"
              class="w-[280px] shrink-0"
            >
              <KpiCardModern
                :title="k.title"
                :value="k.value"
                :percent="k.percent"
                :trend="k.trend"
                :subtitle="k.subtitle"
                :candles="k.candles"
                :icon="k.icon"
                :spotlight="kpiSpotlight(kpiIdx)"
              />
            </div>
          </div>
        </div>
        <p class="mt-1 text-xs text-slate-400/80">
          Geser ke samping untuk melihat KPI lainnya.
        </p>
      </section>

      <!-- Row 1: Aspect (dominant) + Sentiment distribution -->
      <div class="grid grid-cols-1 gap-6 lg:grid-cols-3">
        <DashboardCardShell tag="section" variant="tr" class="p-6">
          <h2 class="text-base font-semibold text-white">
            Distribusi sentimen (skor)
          </h2>
          <p class="mt-1 text-xs text-slate-300/85">
            Proporsi ulasan per star rating
          </p>
          <SentimentDistributionChart :items="distribution" />
        </DashboardCardShell>

        <div class="lg:col-span-2 lg:order-first">
          <AspectOverviewCard :items="aspects" :spotlight="aspectCardSpot" />
        </div>
      </div>

      <!-- Row 2: Review growth (moved below) -->
      <DashboardCardShell tag="section" variant="br" class="p-6">
        <ReviewGrowthChart :items="growth" />
      </DashboardCardShell>

      <DashboardCardShell tag="section" variant="tm" class="p-6">
        <SentimentTrendChart :items="trend" />
      </DashboardCardShell>
    </div>
  </div>
</template>
