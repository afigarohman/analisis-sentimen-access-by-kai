import type { Chart, Plugin } from 'chart.js'

/**
 * Draws a bright hover disc + soft outer bloom on the active point(s) for line charts.
 */
export const linePointGlowPlugin: Plugin<'line'> = {
  id: 'linePointGlow',
  afterDatasetsDraw(chart: Chart) {
    const actives = chart.getActiveElements()
    if (!actives.length) return

    const ctx = chart.ctx
    ctx.save()

    for (const a of actives) {
      const meta = chart.getDatasetMeta(a.datasetIndex)
      const el = meta.data[a.index] as { x: number; y: number } | undefined
      if (!el) continue
      const x = el.x
      const y = el.y

      ctx.shadowColor = 'rgba(192, 252, 255, 0.55)'
      ctx.shadowBlur = 28
      ctx.fillStyle = 'rgba(255,255,255,0.12)'
      ctx.beginPath()
      ctx.arc(x, y, 14, 0, Math.PI * 2)
      ctx.fill()

      ctx.shadowColor = 'rgba(168,85,247,0.45)'
      ctx.shadowBlur = 18
      ctx.fillStyle = 'rgba(217,70,239,0.20)'
      ctx.beginPath()
      ctx.arc(x, y, 10, 0, Math.PI * 2)
      ctx.fill()

      ctx.shadowBlur = 0
      ctx.fillStyle = 'rgba(255,255,255,0.95)'
      ctx.strokeStyle = 'rgba(147,197,253,0.95)'
      ctx.lineWidth = 2
      ctx.beginPath()
      ctx.arc(x, y, 5, 0, Math.PI * 2)
      ctx.fill()
      ctx.stroke()
    }

    ctx.restore()
  },
}
