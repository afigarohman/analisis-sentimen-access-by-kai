<script setup lang="ts">
import { computed } from 'vue'
import { Line } from 'vue-chartjs'

import type { ReviewGrowthItem } from '@/api/dashboard'

const props = defineProps<{
  items: ReviewGrowthItem[]
}>()

const chartData = computed(() => ({
  labels: props.items.map((i) => i.date),
  datasets: [
    {
      label: 'Jumlah ulasan',
      data: props.items.map((i) => i.total),
      borderColor: '#3b82f6',
      backgroundColor: 'rgba(59, 130, 246, 0.12)',
      fill: true,
      tension: 0.35,
      pointRadius: 3,
      pointBackgroundColor: '#3b82f6',
      borderWidth: 2,
    },
  ],
}))

const options = {
  responsive: true,
  maintainAspectRatio: false,
  interaction: { intersect: false, mode: 'index' as const },
  plugins: {
    legend: { display: false },
    tooltip: { enabled: true },
  },
  scales: {
    x: {
      grid: { display: false },
      ticks: { maxRotation: 45, minRotation: 0, font: { size: 11 } },
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
  <div class="relative h-72 w-full">
    <Line v-if="items.length" :data="chartData" :options="options" />
    <p
      v-else
      class="flex h-full items-center justify-center text-sm text-slate-500"
    >
      Belum ada data tanggal
    </p>
  </div>
</template>
