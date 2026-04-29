<script setup lang="ts">
import { computed } from 'vue'
import { Doughnut } from 'vue-chartjs'
import type { ScriptableContext } from 'chart.js'

import type { SentimentDistributionItem } from '@/api/dashboard'

const SCORE_LABELS: Record<number, string> = {
  1: 'Jelek sekali',
  2: 'Jelek',
  3: 'Netral',
  4: 'Baik',
  5: 'Baik sekali',
}

// Requested mapping (with glow):
// 1 jelek sekali: merah
// 2 jelek: ungu
// 3 netral: ungu gradasi biru
// 4 baik: biru muda
// 5 baik sekali: biru
const COLOR = {
  red: '#ef4444',
  purple: '#a855f7',
  blueLight: '#60a5fa',
  blue: '#3b82f6',
}

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
        backgroundColor: (ctx: ScriptableContext<'doughnut'>) => {
          const score = sorted[ctx.dataIndex]?.score ?? 3
          const c = ctx.chart.ctx
          if (score === 3) {
            const g = c.createLinearGradient(0, 0, 220, 220)
            g.addColorStop(0, COLOR.purple)
            g.addColorStop(1, COLOR.blue)
            return g
          }
          if (score === 1) return COLOR.red
          if (score === 2) return COLOR.purple
          if (score === 4) return COLOR.blueLight
          if (score === 5) return COLOR.blue
          return COLOR.blueLight
        },
        borderWidth: 0,
      },
    ],
  }
})

const options = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    // Soft glow around segments
    glow: { color: 'rgba(168,85,247,0.45)', blur: 26 },
    legend: {
      position: 'bottom' as const,
      labels: { boxWidth: 12, padding: 14, font: { size: 11 }, color: '#94a3b8' },
    },
  },
  cutout: '65%',
}

// Chart.js plugin: apply shadow glow when drawing arcs
const glowPlugin = {
  id: 'glow',
  beforeDatasetDraw(chart: any) {
    const ctx = chart.ctx as CanvasRenderingContext2D
    const opts = chart?.config?.options?.plugins?.glow
    if (!opts) return
    ctx.save()
    ctx.shadowColor = opts.color
    ctx.shadowBlur = opts.blur
  },
  afterDatasetDraw(chart: any) {
    chart.ctx.restore()
  },
}
</script>

<template>
  <div class="relative h-72 w-full">
    <Doughnut
      v-if="items.length"
      :data="chartData"
      :options="options"
      :plugins="[glowPlugin]"
    />
    <p
      v-else
      class="flex h-full items-center justify-center text-sm text-slate-500"
    >
      Belum ada data
    </p>
  </div>
</template>
