<script setup lang="ts">
import { computed } from 'vue'

import type { AspectDistributionItem } from '@/api/dashboard'

const props = defineProps<{
  items: AspectDistributionItem[]
}>()

const uid = Math.random().toString(16).slice(2)
const orbGradId = `orbGrad-${uid}`
const orbGlowId = `orbGlow-${uid}`

const ordered = computed(() => {
  const out = [...props.items]
    .map((x) => ({ aspect: x.aspect, total: Number(x.total ?? 0) }))
    .filter((x) => x.total > 0)
    .sort((a, b) => b.total - a.total)
  return out
})

const total = computed(() =>
  ordered.value.reduce((acc, x) => acc + x.total, 0),
)

function pct(v: number): number {
  const t = total.value
  if (!t) return 0
  return Math.round((v / t) * 100)
}

const topAspect = computed(() => {
  const first = ordered.value[0]
  if (!first) return null
  return { aspect: first.aspect, percent: pct(first.total) }
})

const barColor = (aspect: string) => {
  // keep consistent purple palette; subtle variation per aspect
  if (aspect === 'Sistem') return 'bg-purple-300'
  if (aspect === 'Login') return 'bg-fuchsia-300'
  if (aspect === 'Pembayaran') return 'bg-indigo-300'
  if (aspect === 'UI/UX') return 'bg-violet-300'
  if (aspect === 'Performa') return 'bg-purple-200'
  return 'bg-slate-300'
}

const orbTone = computed(() => {
  const a = topAspect.value?.aspect
  if (a === 'Sistem') return { from: '#a855f7', to: '#ef4444' } // purple -> red
  if (a === 'Login') return { from: '#a855f7', to: '#22d3ee' } // purple -> cyan
  if (a === 'Pembayaran') return { from: '#6366f1', to: '#a855f7' } // indigo -> purple
  if (a === 'UI/UX') return { from: '#8b5cf6', to: '#3b82f6' } // violet -> blue
  if (a === 'Performa') return { from: '#a855f7', to: '#f59e0b' } // purple -> amber
  return { from: '#a855f7', to: '#60a5fa' } // purple -> blueLight
})

const orbRing = computed(() => {
  // 0..100
  const p = Math.min(100, Math.max(0, topAspect.value?.percent ?? 0))
  const r = 18
  const c = 2 * Math.PI * r
  const dash = (p / 100) * c
  return {
    percent: p,
    r,
    c,
    dash,
  }
})
</script>

<template>
  <section
    class="group relative overflow-hidden rounded-2xl border border-white/10 bg-gradient-to-br from-purple-900 via-purple-800 to-purple-700 p-6 shadow-lg shadow-purple-500/30 backdrop-blur transition duration-300 hover:scale-[1.01]"
  >
    <div
      class="pointer-events-none absolute -right-24 -top-24 h-72 w-72 rounded-full bg-purple-500/25 blur-3xl opacity-80 transition group-hover:opacity-100"
    />
    <div
      class="pointer-events-none absolute -left-24 -bottom-28 h-72 w-72 rounded-full bg-fuchsia-400/10 blur-3xl"
    />
    <div
      class="pointer-events-none absolute inset-0 bg-[radial-gradient(circle_at_20%_20%,rgba(255,255,255,0.08),transparent_55%)] opacity-80"
    />

    <div class="relative">
      <div class="flex items-start justify-between gap-4">
        <div class="min-w-0">
          <h2 class="text-base font-semibold text-white">Distribusi Aspek</h2>
          <p class="mt-1 text-xs text-slate-300/85">
            Kategori masalah dari ulasan pengguna
          </p>
        </div>

        <!-- Orb (data-driven) -->
        <div class="shrink-0">
          <div class="relative h-16 w-16">
            <svg
              viewBox="0 0 64 64"
              class="h-16 w-16"
              aria-hidden="true"
            >
              <defs>
                <radialGradient :id="orbGradId" cx="30%" cy="25%" r="75%">
                  <stop offset="0%" stop-color="rgba(255,255,255,0.55)" />
                  <stop offset="35%" :stop-color="orbTone.from" stop-opacity="0.95" />
                  <stop offset="100%" :stop-color="orbTone.to" stop-opacity="0.85" />
                </radialGradient>
                <filter :id="orbGlowId" x="-50%" y="-50%" width="200%" height="200%">
                  <feGaussianBlur stdDeviation="6" result="blur" />
                  <feColorMatrix
                    in="blur"
                    type="matrix"
                    values="1 0 0 0 0  0 1 0 0 0  0 0 1 0 0  0 0 0 0.9 0"
                    result="glow"
                  />
                  <feMerge>
                    <feMergeNode in="glow" />
                    <feMergeNode in="SourceGraphic" />
                  </feMerge>
                </filter>
              </defs>

              <!-- glow blob -->
              <circle
                cx="32"
                cy="32"
                r="22"
                :fill="`url(#${orbGradId})`"
                opacity="0.35"
                :filter="`url(#${orbGlowId})`"
              />

              <!-- orb -->
              <circle
                cx="32"
                cy="32"
                r="20"
                :fill="`url(#${orbGradId})`"
                stroke="rgba(255,255,255,0.16)"
                stroke-width="1"
              />

              <!-- highlight -->
              <circle cx="25" cy="22" r="6" fill="rgba(255,255,255,0.25)" />

              <!-- progress ring -->
              <g transform="rotate(-90 32 32)">
                <circle
                  cx="32"
                  cy="32"
                  :r="orbRing.r"
                  fill="none"
                  stroke="rgba(255,255,255,0.16)"
                  stroke-width="3.5"
                />
                <circle
                  cx="32"
                  cy="32"
                  :r="orbRing.r"
                  fill="none"
                  stroke="rgba(255,255,255,0.85)"
                  stroke-linecap="round"
                  stroke-width="3.5"
                  :stroke-dasharray="`${orbRing.dash} ${orbRing.c}`"
                />
              </g>
            </svg>

            <div
              class="absolute inset-0 flex items-center justify-center text-[11px] font-extrabold text-white drop-shadow"
            >
              {{ orbRing.percent }}%
            </div>
          </div>

          <p class="mt-2 text-right text-[11px] font-semibold text-slate-300/90">
            Top aspect
          </p>
          <p v-if="topAspect" class="text-right text-xs font-bold text-white">
            {{ topAspect.aspect }}
          </p>
        </div>
      </div>

      <div class="mt-6 space-y-4">
        <div
          v-for="row in ordered"
          :key="row.aspect"
          class="grid grid-cols-[1fr_auto] gap-3"
        >
          <div class="min-w-0">
            <div class="flex items-center justify-between gap-3">
              <p class="truncate text-sm font-semibold text-white">
                {{ row.aspect }}
              </p>
              <p class="text-xs font-semibold text-slate-300/90">
                {{ pct(row.total) }}%
              </p>
            </div>
            <div
              class="mt-2 h-2.5 w-full overflow-hidden rounded-full bg-white/10 ring-1 ring-white/10"
            >
              <div
                class="h-full rounded-full shadow-[0_0_18px_rgba(168,85,247,0.35)] transition-[width] duration-500"
                :class="barColor(row.aspect)"
                :style="{ width: `${pct(row.total)}%` }"
              />
            </div>
          </div>

          <div class="flex items-end pb-0.5">
            <p class="text-xs font-semibold text-slate-300/85">
              {{ row.total }}
            </p>
          </div>
        </div>

        <div
          v-if="ordered.length === 0"
          class="rounded-xl bg-black/15 p-4 text-center text-sm text-slate-300/80 ring-1 ring-white/10"
        >
          Belum ada data
        </div>
      </div>
    </div>
  </section>
</template>

