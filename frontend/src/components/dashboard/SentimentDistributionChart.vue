<script setup lang="ts">
import { computed } from 'vue'
import { Bar } from 'vue-chartjs'
import type { ChartOptions, ScriptableContext } from 'chart.js'

import type { SentimentDistributionItem } from '@/api/dashboard'

const SCORE_LABELS: Record<number, string> = {
  1: 'Jelek sekali',
  2: 'Jelek',
  3: 'Netral',
  4: 'Baik',
  5: 'Baik sekali',
}

const COLOR = {
  purple: '#a855f7',
  purple2: '#d946ef',
  grid: 'rgba(255,255,255,0.08)',
  tick: 'rgba(226,232,240,0.55)',
}

const props = defineProps<{
  items: SentimentDistributionItem[]
}>()

const chartData = computed(() => {
  const sorted = [...props.items].sort((a, b) => a.score - b.score)
  const labels = sorted.map((i) => SCORE_LABELS[i.score] ?? `Skor ${i.score}`)
  const values = sorted.map((i) => i.total)
  return {
    labels,
    datasets: [
      {
        label: 'Jumlah',
        data: values,
        borderRadius: 10,
        borderSkipped: false,
        backgroundColor: (ctx: ScriptableContext<'bar'>) => {
          const c = ctx.chart.ctx
          const area = ctx.chart.chartArea
          // chartArea not ready on first pass
          if (!area) return 'rgba(168,85,247,0.55)'

          const g = c.createLinearGradient(0, area.top, 0, area.bottom)
          // hovered bar becomes brighter
          if (ctx.active) {
            g.addColorStop(0, 'rgba(217,70,239,0.95)')
            g.addColorStop(1, 'rgba(168,85,247,0.55)')
            return g
          }
          g.addColorStop(0, 'rgba(168,85,247,0.85)')
          g.addColorStop(1, 'rgba(88,28,135,0.25)')
          return g
        },
        hoverBackgroundColor: 'rgba(217,70,239,0.9)',
        borderWidth: 0,
      },
    ],
  }
})

const options: ChartOptions<'bar'> = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: {
      display: false,
    },
    tooltip: {
      enabled: true,
      backgroundColor: 'rgba(15, 23, 42, 0.92)',
      titleColor: 'rgba(226,232,240,0.95)',
      bodyColor: 'rgba(226,232,240,0.85)',
      borderColor: 'rgba(255,255,255,0.10)',
      borderWidth: 1,
      padding: 10,
      displayColors: false,
    },
  },
  interaction: { intersect: true, mode: 'nearest' as const },
  scales: {
    x: {
      grid: { display: false },
      ticks: { color: COLOR.tick, font: { size: 11 } },
    },
    y: {
      beginAtZero: true,
      grid: { color: COLOR.grid },
      ticks: { color: 'rgba(226,232,240,0.35)', font: { size: 11 } },
    },
  },
}

function roundRectPath(
  ctx: CanvasRenderingContext2D,
  x: number,
  y: number,
  w: number,
  h: number,
  r: number,
) {
  const rr = Math.min(r, Math.abs(w) / 2, Math.abs(h) / 2)
  ctx.beginPath()
  ctx.moveTo(x + rr, y)
  ctx.lineTo(x + w - rr, y)
  ctx.quadraticCurveTo(x + w, y, x + w, y + rr)
  ctx.lineTo(x + w, y + h - rr)
  ctx.quadraticCurveTo(x + w, y + h, x + w - rr, y + h)
  ctx.lineTo(x + rr, y + h)
  ctx.quadraticCurveTo(x, y + h, x, y + h - rr)
  ctx.lineTo(x, y + rr)
  ctx.quadraticCurveTo(x, y, x + rr, y)
  ctx.closePath()
}

// Glow on hovered bar (matches reference "bar lights up")
const hoverGlowPlugin = {
  id: 'hoverGlow',
  afterDatasetsDraw(chart: any) {
    const ctx = chart.ctx as CanvasRenderingContext2D
    const actives = chart.getActiveElements?.() ?? []
    if (!actives.length) return

    ctx.save()
    for (const a of actives) {
      const meta = chart.getDatasetMeta(a.datasetIndex)
      const el = meta?.data?.[a.index]
      if (!el) continue

      const p = el.getProps(['x', 'y', 'base', 'width'], true)
      const left = p.x - p.width / 2
      const top = Math.min(p.y, p.base)
      const height = Math.abs(p.base - p.y)

      // Wide bloom (spread blur)
      ctx.shadowColor = 'rgba(217,70,239,0.55)'
      ctx.shadowBlur = 72
      ctx.fillStyle = 'rgba(217,70,239,0.18)'
      roundRectPath(ctx, left - 6, top - 6, p.width + 12, height + 12, 16)
      ctx.fill()

      // Secondary bloom layer for depth
      ctx.shadowColor = 'rgba(168,85,247,0.6)'
      ctx.shadowBlur = 44
      ctx.fillStyle = 'rgba(168,85,247,0.16)'
      roundRectPath(ctx, left - 3, top - 3, p.width + 6, height + 6, 14)
      ctx.fill()

      // Soft inner glow (no sharp lines)
      ctx.shadowColor = 'rgba(217,70,239,0.45)'
      ctx.shadowBlur = 22
      ctx.fillStyle = 'rgba(217,70,239,0.10)'
      roundRectPath(ctx, left, top, p.width, height, 10)
      ctx.fill()
    }
    ctx.restore()
  },
}
</script>

<template>
  <div class="relative h-72 w-full">
    <Bar v-if="items.length" :data="chartData" :options="options" :plugins="[hoverGlowPlugin]" />
    <p
      v-else
      class="flex h-full items-center justify-center text-sm text-slate-500"
    >
      Belum ada data
    </p>
  </div>
</template>
