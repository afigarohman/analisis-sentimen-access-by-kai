<script setup lang="ts">
function formatNumber(value: number | string) {
  if (typeof value === 'number') {
    return value.toLocaleString()
  }
  return value
}
defineProps<{
  title: string
  value: number | string
  accent?: string
}>()
</script>

<template>
  <div
    class="group relative overflow-hidden rounded-2xl bg-white/90 p-4 shadow-md backdrop-blur transition-all duration-300 hover:shadow-lg sm:p-6 dark:bg-slate-900/40 dark:shadow-blue-500/10"
  >
    <div
      class="pointer-events-none absolute -right-24 -top-24 h-56 w-56 rounded-full bg-gradient-to-tr from-blue-500/22 via-cyan-400/12 to-transparent blur-2xl opacity-80 transition group-hover:opacity-100"
    />
    <p class="relative text-xs font-semibold text-slate-600 sm:text-sm dark:text-slate-300">
      {{ title }}
    </p>
    <p
      class="relative mt-2 text-2xl font-extrabold tracking-tight sm:mt-3 sm:text-3xl"
      :class="accent ?? 'text-slate-900 dark:text-slate-100'"
    >
      {{ formatNumber(value) }}
    </p>
  </div>
</template>
