<script setup lang="ts">
import { computed } from 'vue'

function formatNumber(value: number | string) {
  if (typeof value === 'number') return value.toLocaleString()
  return value
}

const props = defineProps<{
  title: string
  value: number | string
  note?: string
  pill?: {
    label: string
    tone?: 'good' | 'bad' | 'neutral'
  }
  spark?: number[] // simple mini bar chart (dummy OK)
  icon?: string // optional single letter/icon
}>()

const pillClass = computed(() => {
  const tone = props.pill?.tone ?? 'neutral'
  if (tone === 'good') return 'bg-emerald-500/15 text-emerald-200 ring-emerald-400/20'
  if (tone === 'bad') return 'bg-rose-500/15 text-rose-200 ring-rose-400/20'
  return 'bg-white/10 text-slate-200 ring-white/10'
})

const sparkBars = computed(() => {
  const s = props.spark ?? [20, 55, 38, 70, 44, 62]
  const max = Math.max(...s, 1)
  return s.map((x) => Math.max(8, Math.round((x / max) * 44)))
})
</script>

<template>
  <div
    class="group relative overflow-hidden rounded-2xl border border-white/10 bg-gradient-to-br from-purple-900 via-purple-800 to-purple-700 p-5 shadow-lg backdrop-blur transition duration-300 hover:scale-[1.02]"
  >
    <div
      class="pointer-events-none absolute -right-24 -top-24 h-56 w-56 rounded-full bg-purple-500/20 blur-3xl opacity-70 transition group-hover:opacity-100"
    />
    <div
      class="pointer-events-none absolute -left-20 -bottom-20 h-56 w-56 rounded-full bg-fuchsia-400/10 blur-3xl"
    />

    <div class="relative flex items-start justify-between gap-4">
      <div class="min-w-0">
        <p class="text-xs font-semibold tracking-wide text-slate-300/90">
          {{ title }}
        </p>
        <p class="mt-2 text-3xl font-extrabold tracking-tight text-white">
          {{ formatNumber(value) }}
        </p>
        <div class="mt-2 flex items-center gap-2">
          <span
            v-if="pill"
            class="inline-flex items-center rounded-full px-2.5 py-1 text-[11px] font-semibold ring-1"
            :class="pillClass"
          >
            {{ pill.label }}
          </span>
          <p v-if="note" class="text-xs text-slate-300/80">
            {{ note }}
          </p>
        </div>
      </div>

      <div class="flex shrink-0 flex-col items-end gap-3">
        <div
          v-if="icon"
          class="flex h-10 w-10 items-center justify-center rounded-full bg-purple-500/20 text-sm font-bold text-white ring-1 ring-white/10"
        >
          {{ icon }}
        </div>
        <div
          v-else
          class="flex items-end gap-1.5 rounded-xl bg-black/15 p-2 ring-1 ring-white/10"
        >
          <div
            v-for="(h, idx) in sparkBars"
            :key="idx"
            class="w-2 rounded-md bg-white/15"
            :style="{ height: `${h}px` }"
          />
          <div
            class="w-2 rounded-md bg-purple-200/60"
            :style="{ height: `${sparkBars[sparkBars.length - 1] ?? 18}px` }"
          />
        </div>
      </div>
    </div>
  </div>
</template>

