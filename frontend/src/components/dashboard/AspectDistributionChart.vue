<script setup lang="ts">
import { computed } from 'vue'
import { Doughnut } from 'vue-chartjs'
import type { ScriptableContext } from 'chart.js'

import type { AspectDistributionItem } from '@/api/dashboard'

const ASPECT_ORDER: string[] = [
  'Sistem',
  'Login',
  'Pembayaran',
  'UI/UX',
  'Performa',
  'Lainnya',
]

const COLORS: Record<string, string> = {
  Sistem: '#ef4444', // red
  Login: '#a855f7', // purple
  Pembayaran: '#60a5fa', // light blue
  'UI/UX': '#3b82f6', // blue
  Performa: '#f59e0b', // amber
  Lainnya: '#94a3b8', // slate
}

const props = defineProps<{
  items: AspectDistributionItem[]
}>()

const ordered = computed(() => {
  const m = new Map(props.items.map((i) => [i.aspect, i.total]))
  return ASPECT_ORDER.map((aspect) => ({
    aspect,
    total: Number(m.get(aspect) ?? 0),
  }))
})

const chartData = computed(() => {
  return {
    labels: ordered.value.map((x) => x.aspect),
    datasets: [
      {
        data: ordered.value.map((x) => x.total),
        backgroundColor: (ctx: ScriptableContext<'doughnut'>) => {
          const idx = ctx.dataIndex
          const aspect = ordered.value[idx]?.aspect
          return COLORS[aspect ?? 'Lainnya'] ?? COLORS.Lainnya
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
    glow: { color: 'rgba(59,130,246,0.45)', blur: 26 },
    legend: {
      position: 'bottom' as const,
      labels: {
        boxWidth: 12,
        padding: 14,
        font: { size: 11 },
        color: '#94a3b8',
      },
    },
  },
  cutout: '65%',
}

// Chart.js plugin: apply shadow glow around segments
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

