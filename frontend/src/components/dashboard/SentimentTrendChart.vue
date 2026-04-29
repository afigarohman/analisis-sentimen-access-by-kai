<script setup lang="ts">
import { computed, ref } from 'vue'
import { Line } from 'vue-chartjs'

import type { SentimentTrendItem } from '@/api/dashboard'

const SCORE_LABELS: Record<number, string> = {
  1: 'Jelek sekali',
  2: 'Jelek',
  3: 'Netral',
  4: 'Baik',
  5: 'Baik sekali',
}

// Brand-ish colors (no pink neon)
const COLORS: Record<number, string> = {
  1: '#ef4444', // red
  2: '#a855f7', // purple
  3: '#94a3b8', // slate
  4: '#3b82f6', // blue
  5: '#60a5fa', // light blue
}

const props = defineProps<{
  items: SentimentTrendItem[]
}>()

type RangeKey = 'day' | 'week' | 'month' | 'year'
const range = ref<RangeKey>('day')

function toDate(d: string) {
  // input is YYYY-MM-DD
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
  const day = d.getDay() // 0..6 (Sun..Sat)
  const diff = (day === 0 ? -6 : 1) - day
  d.setDate(d.getDate() + diff)
  d.setHours(0, 0, 0, 0)
  return d
}

const normalized = computed(() => {
  const items = props.items
  const out: { key: string; score: number; total: number }[] = []
  for (const it of items) {
    const dt = toDate(it.date)
    let key = it.date
    if (range.value === 'week') key = fmtYMD(startOfWeekMonday(dt))
    else if (range.value === 'month')
      key = `${dt.getFullYear()}-${String(dt.getMonth() + 1).padStart(2, '0')}`
    else if (range.value === 'year') key = String(dt.getFullYear())
    out.push({ key, score: it.score, total: it.total })
  }
  // aggregate
  const map = new Map<string, number>()
  for (const r of out) {
    const k = `${r.key}__${r.score}`
    map.set(k, (map.get(k) ?? 0) + r.total)
  }
  return { map, keys: [...new Set(out.map((r) => r.key))].sort() }
})

const chartData = computed(() => {
  const dates = normalized.value.keys
  const scores = [1, 2, 3, 4, 5]
  return {
    labels: dates,
    datasets: scores.map((score) => ({
      label: SCORE_LABELS[score],
      data: dates.map((d) => normalized.value.map.get(`${d}__${score}`) ?? 0),
      borderColor: COLORS[score],
      backgroundColor: 'transparent',
      tension: 0.25,
      pointRadius: 2,
      borderWidth: 2,
    })),
  }
})

const options = {
  responsive: true,
  maintainAspectRatio: false,
  interaction: { intersect: false, mode: 'index' as const },
  plugins: {
    legend: {
      position: 'top' as const,
      labels: { boxWidth: 10, padding: 12, font: { size: 11 } },
    },
  },
  scales: {
    x: {
      grid: { display: false },
      ticks: { maxRotation: 45, font: { size: 11 } },
    },
    y: {
      beginAtZero: true,
      grid: { color: 'rgba(148,163,184,0.18)' },
      ticks: { precision: 0 },
    },
  },
}
</script>

<template>
  <div class="relative h-80 w-full">
    <div class="mb-3 flex flex-wrap gap-2">
      <button
        type="button"
        class="rounded-xl px-3 py-1.5 text-xs font-semibold shadow-sm transition"
        :class="range === 'day' ? 'bg-blue-500 text-white' : 'bg-slate-100 text-slate-700 dark:bg-slate-950/35 dark:text-slate-200'"
        @click="range = 'day'"
      >
        Hari
      </button>
      <button
        type="button"
        class="rounded-xl px-3 py-1.5 text-xs font-semibold shadow-sm transition"
        :class="range === 'week' ? 'bg-blue-500 text-white' : 'bg-slate-100 text-slate-700 dark:bg-slate-950/35 dark:text-slate-200'"
        @click="range = 'week'"
      >
        Minggu
      </button>
      <button
        type="button"
        class="rounded-xl px-3 py-1.5 text-xs font-semibold shadow-sm transition"
        :class="range === 'month' ? 'bg-blue-500 text-white' : 'bg-slate-100 text-slate-700 dark:bg-slate-950/35 dark:text-slate-200'"
        @click="range = 'month'"
      >
        Bulan
      </button>
      <button
        type="button"
        class="rounded-xl px-3 py-1.5 text-xs font-semibold shadow-sm transition"
        :class="range === 'year' ? 'bg-blue-500 text-white' : 'bg-slate-100 text-slate-700 dark:bg-slate-950/35 dark:text-slate-200'"
        @click="range = 'year'"
      >
        Tahun
      </button>
    </div>
    <Line v-if="items.length" :data="chartData" :options="options" />
    <p
      v-else
      class="flex h-full items-center justify-center text-sm text-slate-500"
    >
      Belum ada data tren
    </p>
  </div>
</template>
