<script setup lang="ts">
import { computed } from 'vue'
import { Line } from 'vue-chartjs'

import type { SentimentTrendItem } from '@/api/dashboard'

const SCORE_LABELS: Record<number, string> = {
  1: 'Jelek sekali',
  2: 'Jelek',
  3: 'Netral',
  4: 'Baik',
  5: 'Baik sekali',
}

const COLORS: Record<number, string> = {
  1: '#ef4444',
  2: '#f97316',
  3: '#94a3b8',
  4: '#3b82f6',
  5: '#ec4899',
}

const props = defineProps<{
  items: SentimentTrendItem[]
}>()

const chartData = computed(() => {
  const items = props.items
  const dates = [...new Set(items.map((i) => i.date))].sort()
  const scores = [1, 2, 3, 4, 5]
  return {
    labels: dates,
    datasets: scores.map((score) => ({
      label: SCORE_LABELS[score],
      data: dates.map((d) => {
        const row = items.find((x) => x.date === d && x.score === score)
        return row ? row.total : 0
      }),
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
      grid: { color: '#f1f5f9' },
      ticks: { precision: 0 },
    },
  },
}
</script>

<template>
  <div class="relative h-80 w-full">
    <Line v-if="items.length" :data="chartData" :options="options" />
    <p
      v-else
      class="flex h-full items-center justify-center text-sm text-slate-500"
    >
      Belum ada data tren
    </p>
  </div>
</template>
