<script setup lang="ts">
import { computed, ref } from 'vue'
import { Line } from 'vue-chartjs'
import type { ChartOptions } from 'chart.js'

import type { SentimentTrendItem } from '@/api/dashboard'
import { linePointGlowPlugin } from '@/charts/linePointGlowPlugin'

type RangeKey = 'day' | 'week' | 'month' | 'year'
const range = ref<RangeKey>('day')

const props = defineProps<{
  items: SentimentTrendItem[]
}>()

function toDate(d: string) {
  const parts = d.split('-')
  const y = Number(parts[0] ?? 1970)
  const m = Number(parts[1] ?? 1)
  const day = Number(parts[2] ?? 1)
  return new Date(y, m - 1, day)
}

function fmtYMD(dt: Date) {
  const y = dt.getFullYear()
  const m = String(dt.getMonth() + 1).padStart(2, '0')
  const d = String(dt.getDate()).padStart(2, '0')
  return `${y}-${m}-${d}`
}

function startOfWeekMonday(dt: Date) {
  const d = new Date(dt)
  const day = d.getDay()
  const diff = (day === 0 ? -6 : 1) - day
  d.setDate(d.getDate() + diff)
  d.setHours(0, 0, 0, 0)
  return d
}

/** Agregasi per bucket: volumen tidak digabung jadi satu seri mentah seperti review-growth. */
type BucketTotals = { pos: number; neu: number; neg: number }

const buckets = computed(() => {
  const map = new Map<string, BucketTotals>()
  for (const it of props.items) {
    const dt = toDate(it.date)
    let key = it.date
    if (range.value === 'week') key = fmtYMD(startOfWeekMonday(dt))
    else if (range.value === 'month')
      key = `${dt.getFullYear()}-${String(dt.getMonth() + 1).padStart(2, '0')}`
    else if (range.value === 'year') key = String(dt.getFullYear())

    const cur = map.get(key) ?? { pos: 0, neu: 0, neg: 0 }
    const t = Number(it.total ?? 0)
    if ([4, 5].includes(Number(it.score))) cur.pos += t
    else if (Number(it.score) === 3) cur.neu += t
    else cur.neg += t
    map.set(key, cur)
  }
  const keys = [...map.keys()].sort()
  const posArr = keys.map((k) => map.get(k)!.pos)
  const neuArr = keys.map((k) => map.get(k)!.neu)
  const negArr = keys.map((k) => map.get(k)!.neg)
  return { labels: keys, posArr, neuArr, negArr }
})

const headline = computed(() => {
  const n = buckets.value.labels.length
  if (!n) return '—'
  const i = n - 1
  const t =
    buckets.value.negArr[i]! +
    buckets.value.neuArr[i]! +
    buckets.value.posArr[i]!
  return `${t.toLocaleString('id-ID')} ulasan`
})

const pctLine = computed(() => {
  const n = buckets.value.labels.length
  if (!n) return ''
  const i = n - 1
  const pos = buckets.value.posArr[i] ?? 0
  const neu = buckets.value.neuArr[i] ?? 0
  const neg = buckets.value.negArr[i] ?? 0
  const tot = pos + neu + neg
  if (!tot) return ''
  const pPos = Math.round((pos / tot) * 1000) / 10
  const pNeu = Math.round((neu / tot) * 1000) / 10
  const pNeg = Math.round((neg / tot) * 1000) / 10
  return `Periode akhir · ${pPos}% pos · ${pNeu}% net · ${pNeg}% neg`
})

const chartData = computed(() => {
  const { labels, negArr, neuArr, posArr } = buckets.value
  return {
    labels,
    datasets: [
      {
        label: 'Negatif (1–2)',
        data: negArr,
        stack: 'vol',
        borderColor: 'rgba(251, 113, 133, 0.95)',
        backgroundColor: 'rgba(251, 113, 133, 0.24)',
        fill: true,
        tension: 0.38,
        borderWidth: 1.5,
        pointRadius: 0,
      },
      {
        label: 'Netral (3)',
        data: neuArr,
        stack: 'vol',
        borderColor: 'rgba(148, 163, 184, 0.9)',
        backgroundColor: 'rgba(148, 163, 184, 0.22)',
        fill: true,
        tension: 0.38,
        borderWidth: 1.5,
        pointRadius: 0,
      },
      {
        label: 'Positif (4–5)',
        data: posArr,
        stack: 'vol',
        borderColor: 'rgba(139, 92, 246, 0.98)',
        backgroundColor: 'rgba(139, 92, 246, 0.32)',
        fill: true,
        tension: 0.38,
        borderWidth: 1.5,
        pointRadius: 0,
      },
    ],
  }
})

const rangeLabel = computed(() => {
  if (range.value === 'day') return 'Per hari'
  if (range.value === 'week') return 'Per minggu'
  if (range.value === 'month') return 'Per bulan'
  return 'Per tahun'
})

const options = computed<ChartOptions<'line'>>(() => ({
  responsive: true,
  maintainAspectRatio: false,
  interaction: { intersect: false, mode: 'index' },
  plugins: {
    legend: {
      display: true,
      position: 'bottom',
      labels: {
        boxWidth: 10,
        boxHeight: 10,
        usePointStyle: true,
        pointStyle: 'rectRounded',
        padding: 16,
        color: 'rgba(226,232,240,0.82)',
        font: { family: "'Inter', system-ui, sans-serif", size: 11 },
      },
    },
    tooltip: {
      enabled: true,
      backgroundColor: 'rgba(15, 23, 42, 0.94)',
      titleColor: 'rgba(248, 250, 252, 0.96)',
      bodyColor: 'rgba(226, 232, 240, 0.92)',
      borderColor: 'rgba(255,255,255,0.08)',
      borderWidth: 1,
      padding: 12,
      callbacks: {
        title(ctx) {
          return String(ctx[0]?.label ?? '')
        },
        footer(ctxItems) {
          const items = [...ctxItems]
          const neg = Number(items.find((x) => x.datasetIndex === 0)?.parsed.y ?? 0)
          const neu = Number(items.find((x) => x.datasetIndex === 1)?.parsed.y ?? 0)
          const pos = Number(items.find((x) => x.datasetIndex === 2)?.parsed.y ?? 0)
          const sum = neg + neu + pos
          return [`Total periode: ${sum.toLocaleString('id-ID')}`]
        },
        label(ctx) {
          const v = ctx.parsed.y
          return ` ${ctx.dataset.label}: ${Number(v).toLocaleString('id-ID')}`
        },
      },
    },
  },
  scales: {
    x: {
      stacked: true,
      grid: { display: false, drawBorder: false },
      ticks: {
        color: 'rgba(226,232,240,0.45)',
        maxRotation: 0,
        autoSkip: true,
        maxTicksLimit: 10,
        font: { family: "'Inter', system-ui, sans-serif", size: 11 },
      },
    },
    y: {
      stacked: true,
      beginAtZero: true,
      grid: { color: 'rgba(255,255,255,0.06)', drawBorder: false },
      ticks: {
        color: 'rgba(226,232,240,0.38)',
        precision: 0,
        font: { family: "'Inter', system-ui, sans-serif", size: 11 },
      },
    },
  },
}))

function rangeBtn(active: boolean) {
  return active
    ? 'border-[#8b5cf6]/35 bg-white/[0.08] text-white shadow-[0_0_22px_-8px_rgba(139,92,246,0.35)]'
    : 'border-white/[0.07] bg-white/[0.03] text-slate-300 hover:border-white/[0.12] hover:bg-white/[0.05]'
}
</script>

<template>
  <div class="flex flex-col gap-4">
    <div class="flex flex-wrap items-start justify-between gap-3">
      <div class="min-w-0">
        <p class="text-sm font-semibold tracking-tight text-white">
          Tren volume per sentimen
        </p>
        <p
          class="mt-1 text-3xl font-extrabold tracking-tight text-white tabular-nums"
        >
          {{ headline }}
        </p>
        <p class="mt-1 text-xs leading-relaxed text-slate-400">
          Area bertumpuk: volume ulasan negatif, netral, dan positif per
          {{ rangeLabel }}.
        </p>
        <p v-if="pctLine" class="mt-0.5 text-xs font-medium text-slate-300">
          {{ pctLine }}
        </p>
      </div>

      <div class="flex flex-wrap gap-2">
        <button
          type="button"
          class="rounded-full border px-3 py-1.5 text-[11px] font-semibold tracking-tight transition"
          :class="rangeBtn(range === 'day')"
          @click="range = 'day'"
        >
          Hari
        </button>
        <button
          type="button"
          class="rounded-full border px-3 py-1.5 text-[11px] font-semibold tracking-tight transition"
          :class="rangeBtn(range === 'week')"
          @click="range = 'week'"
        >
          Minggu
        </button>
        <button
          type="button"
          class="rounded-full border px-3 py-1.5 text-[11px] font-semibold tracking-tight transition"
          :class="rangeBtn(range === 'month')"
          @click="range = 'month'"
        >
          Bulan
        </button>
        <button
          type="button"
          class="rounded-full border px-3 py-1.5 text-[11px] font-semibold tracking-tight transition"
          :class="rangeBtn(range === 'year')"
          @click="range = 'year'"
        >
          Tahun
        </button>
      </div>
    </div>

    <div class="relative h-72 w-full sm:h-80">
      <Line
        v-if="props.items.length"
        :data="chartData"
        :options="options"
        :plugins="[linePointGlowPlugin]"
      />
      <p
        v-else
        class="flex h-full items-center justify-center text-sm text-slate-500"
      >
        Belum ada data tren
      </p>
    </div>
  </div>
</template>
