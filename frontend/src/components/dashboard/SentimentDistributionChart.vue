<script setup lang="ts">
import { computed } from 'vue'
import { Doughnut } from 'vue-chartjs'

import type { SentimentDistributionItem } from '@/api/dashboard'

const SCORE_LABELS: Record<number, string> = {
  1: 'Jelek sekali',
  2: 'Jelek',
  3: 'Netral',
  4: 'Baik',
  5: 'Baik sekali',
}

const COLORS = ['#ef4444', '#f97316', '#94a3b8', '#3b82f6', '#22c55e']

const props = defineProps<{
  items: SentimentDistributionItem[]
}>()

const chartData = computed(() => {
  const sorted = [...props.items].sort((a, b) => a.score - b.score)
  return {
    labels: sorted.map((i) => SCORE_LABELS[i.score] ?? `Skor ${i.score}`),
    datasets: [
      {
        data: sorted.map((i) => i.total),
        backgroundColor: sorted.map((i) => COLORS[i.score - 1] ?? '#64748b'),
        borderWidth: 0,
      },
    ],
  }
})

const options = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: {
      position: 'bottom' as const,
      labels: { boxWidth: 12, padding: 14, font: { size: 11 } },
    },
  },
  cutout: '65%',
}
</script>

<template>
  <div class="relative h-72 w-full">
    <Doughnut v-if="items.length" :data="chartData" :options="options" />
    <p
      v-else
      class="flex h-full items-center justify-center text-sm text-slate-500"
    >
      Belum ada data
    </p>
  </div>
</template>
