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
    class="rounded-2xl bg-white p-4 shadow-md ring-1 ring-slate-200/80 transition hover:shadow-lg sm:p-6"
  >
    <p class="text-xs font-semibold text-slate-500 sm:text-sm">{{ title }}</p>
    <p
      class="mt-2 text-2xl font-extrabold tracking-tight sm:mt-3 sm:text-3xl"
      :class="accent ?? 'text-slate-900'"
    >
      {{ formatNumber(value) }}
    </p>
  </div>
</template>
