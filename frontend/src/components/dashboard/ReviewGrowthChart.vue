<script setup lang="ts">
import { computed } from 'vue'
import { Line } from 'vue-chartjs'
import type { ChartOptions, ScriptableContext } from 'chart.js'

import type { ReviewGrowthItem } from '@/api/dashboard'
import { linePointGlowPlugin } from '@/charts/linePointGlowPlugin'

const props = defineProps<{
  items: ReviewGrowthItem[]
}>()

const sorted = computed(() =>
  [...props.items].sort((a, b) => a.date.localeCompare(b.date)),
)

const headline = computed(() => {
  const s = sorted.value
  if (!s.length) return '0'
  const last = s[s.length - 1]
  return Number(last?.total ?? 0).toLocaleString()
})

const subline = computed(() => {
  const s = sorted.value
  if (!s.length) return '—'
  const first = s[0]?.date ?? ''
  const last = s[s.length - 1]?.date ?? ''
  if (first && last && first !== last) return `${first} → ${last}`
  return last || '—'
})

const lag = computed(() => {
  const n = sorted.value.length
  if (n <= 1) return 1
  return Math.min(7, Math.max(1, Math.floor(n / 2)))
})

const chartData = computed(() => {
  const labels = sorted.value.map((i) => i.date)
  const data = sorted.value.map((i) => i.total)
  const k = lag.value
  const compare = data.map((_, i) => data[Math.max(0, i - k)] ?? 0)

  return {
    labels,
    datasets: [
      {
        label: 'Ulasan',
        data,
        borderColor: 'rgba(167, 139, 250, 0.95)',
        backgroundColor: (ctx: ScriptableContext<'line'>) => {
          const { chart } = ctx
          const { ctx: c } = chart
          const area = chart.chartArea
          if (!area) return 'rgba(139, 92, 246, 0.08)'
          const g = c.createLinearGradient(0, area.top, 0, area.bottom)
          g.addColorStop(0, 'rgba(167, 139, 250, 0.36)')
          g.addColorStop(0.42, 'rgba(139, 92, 246, 0.14)')
          g.addColorStop(1, 'rgba(10, 10, 12, 0)')
          return g
        },
        fill: true,
        tension: 0.42,
        borderWidth: 2.5,
        pointRadius: 0,
        pointHoverRadius: 0,
        order: 1,
      },
      {
        label: 'Periode sebelumnya',
        data: compare,
        borderColor: 'rgba(226, 232, 240, 0.35)',
        borderDash: [5, 6],
        borderWidth: 2,
        fill: false,
        tension: 0.35,
        pointRadius: 0,
        order: 2,
      },
    ],
  }
})

const options = computed<ChartOptions<'line'>>(() => ({
  responsive: true,
  maintainAspectRatio: false,
  interaction: { intersect: false, mode: 'index' },
  plugins: {
    legend: {
      display: false,
    },
    tooltip: {
      enabled: true,
      backgroundColor: 'rgba(15, 23, 42, 0.92)',
      titleColor: 'rgba(248, 250, 252, 0.95)',
      bodyColor: 'rgba(226, 232, 240, 0.90)',
      borderColor: 'rgba(255,255,255,0.10)',
      borderWidth: 1,
      padding: 12,
      displayColors: false,
      callbacks: {
        title(ctx) {
          return String(ctx[0]?.label ?? '')
        },
        label(ctx) {
          const v = ctx.parsed.y
          if (ctx.datasetIndex === 0) return `Ulasan: ${v?.toLocaleString?.() ?? v}`
          return `Perbandingan: ${v?.toLocaleString?.() ?? v}`
        },
      },
    },
  },
  scales: {
    x: {
      grid: { display: false, drawBorder: false },
      ticks: {
        color: 'rgba(226,232,240,0.45)',
        maxRotation: 0,
        autoSkip: true,
        maxTicksLimit: 7,
        font: { size: 11 },
      },
    },
    y: {
      beginAtZero: true,
      grid: { color: 'rgba(255,255,255,0.06)', drawBorder: false },
      ticks: {
        color: 'rgba(226,232,240,0.35)',
        precision: 0,
        font: { size: 11 },
      },
    },
  },
}))
</script>

<template>
  <div class="flex flex-col gap-4">
    <div class="flex flex-wrap items-start justify-between gap-3">
      <div class="min-w-0">
        <p class="text-sm font-semibold tracking-tight text-white">
          Pertumbuhan ulasan
        </p>
        <p class="mt-1 text-3xl font-extrabold tracking-tight text-white tabular-nums">
          {{ headline }}
        </p>
        <p class="mt-1 text-xs text-slate-400">
          Per hari menurut
          <span class="text-slate-300">tanggal ulasan masuk · {{ subline }}</span>
        </p>
      </div>
      <div
        class="rounded-full border border-white/10 bg-white/[0.04] px-3 py-1 text-[11px] font-semibold text-slate-300"
      >
        Garis putus: periode sebelumnya (geser {{ lag }} titik)
      </div>
    </div>

    <div class="relative h-64 w-full sm:h-72">
      <Line
        v-if="items.length"
        :data="chartData"
        :options="options"
        :plugins="[linePointGlowPlugin]"
      />
      <p
        v-else
        class="flex h-full items-center justify-center text-sm text-slate-500"
      >
        Belum ada data tanggal
      </p>
    </div>
  </div>
</template>
