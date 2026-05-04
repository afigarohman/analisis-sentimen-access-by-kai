<script lang="ts">
/** Hover glow untuk kartu glass (dipakai di daftar/tombol luar shell agar sama dengan dashboard) */
export const dashboardCardHoverClasses =
  'transition duration-300 hover:-translate-y-0.5 hover:border-white/[0.13] hover:shadow-[0_28px_65px_-24px_rgba(168,85,247,0.42),0_18px_50px_-18px_rgba(217,70,239,0.16)]'
</script>

<script setup lang="ts">
import { computed } from 'vue'

/**
 * Kartu dashboard: alas semi-transparan + blur + hover glow (border & bayangan violet) sama di semua halaman.
 */
export type DashboardSpotlight = 'tl' | 'tr' | 'bl' | 'br' | 'tm' | 'offset'

const props = withDefaults(
  defineProps<{
    variant?: DashboardSpotlight
    /** Root tag, mis. section atau div */
    tag?: string
    /** Radius & orbs lebih kecil untuk item dalam daftar / panel sekunder */
    compact?: boolean
  }>(),
  {
    variant: 'tl',
    tag: 'div',
    compact: false,
  },
)

const rounded = computed(() => (props.compact ? 'rounded-xl' : 'rounded-[1.75rem]'))

const shellClass = computed(() => [
  rounded.value,
  'group relative overflow-hidden border border-white/[0.06] bg-white/[0.04] shadow-[0_20px_50px_-20px_rgba(0,0,0,0.65)] backdrop-blur-xl',
  dashboardCardHoverClasses,
  'dark:border-white/[0.08] dark:bg-[rgba(255,255,255,0.045)] dark:hover:border-white/[0.16]',
])

const orbTopClass = computed(() =>
  props.compact
    ? 'pointer-events-none absolute -right-16 -top-16 h-40 w-40 rounded-full bg-purple-500/16 blur-2xl opacity-50 transition-opacity duration-300 group-hover:opacity-95'
    : 'pointer-events-none absolute -right-28 -top-28 h-72 w-72 rounded-full bg-purple-500/14 blur-3xl opacity-55 transition-opacity duration-300 group-hover:opacity-95',
)

const orbBottomClass = computed(() =>
  props.compact
    ? 'pointer-events-none absolute -bottom-14 -left-14 h-36 w-36 rounded-full bg-fuchsia-500/11 blur-2xl opacity-45 transition-opacity duration-300 group-hover:opacity-90'
    : 'pointer-events-none absolute -bottom-28 -left-28 h-72 w-72 rounded-full bg-fuchsia-500/11 blur-3xl opacity-50 transition-opacity duration-300 group-hover:opacity-92',
)
</script>

<template>
  <component :is="tag" :class="shellClass">
    <div class="pointer-events-none absolute inset-0" aria-hidden="true">
      <div :class="orbTopClass" />
      <div :class="orbBottomClass" />
    </div>
    <!-- min-h-0 + flex-col: rantai tinggi sampai konten bermakna (mis. overflow-y-auto di slot) -->
    <div class="relative z-10 flex min-h-0 w-full flex-1 flex-col">
      <slot />
    </div>
  </component>
</template>
