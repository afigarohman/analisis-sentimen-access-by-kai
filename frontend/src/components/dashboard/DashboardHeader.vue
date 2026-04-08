<script setup lang="ts">
defineProps<{
  title?: string
  breadcrumb?: string
}>()

const emit = defineEmits<{
  (e: 'toggleSidebar'): void
}>()
</script>

<template>
  <header
    class="flex h-16 shrink-0 items-center justify-between border-b border-slate-200 bg-white px-4 sm:px-6"
  >
    <div class="flex min-w-0 items-center gap-3">
      <button
        class="rounded-lg p-2 text-slate-600 hover:bg-slate-100 md:hidden"
        aria-label="Buka sidebar"
        @click="emit('toggleSidebar')"
      >
        <svg viewBox="0 0 24 24" class="h-5 w-5" fill="none" stroke="currentColor" stroke-width="2">
          <path stroke-linecap="round" stroke-linejoin="round" d="M4 6h16M4 12h16M4 18h16" />
        </svg>
      </button>

      <div class="min-w-0">
        <h1 class="truncate text-base font-semibold text-slate-900 sm:text-lg">
          {{ title ?? 'Dashboard' }}
        </h1>
        <p v-if="breadcrumb" class="mt-0.5 truncate text-xs text-slate-400">
          {{ breadcrumb }}
        </p>
      </div>
    </div>
    <div class="flex items-center gap-3">
      <div
        class="hidden rounded-full border border-slate-200 bg-slate-50 px-3 py-1.5 text-sm text-slate-400 sm:block"
      >
        <span class="text-slate-500">Cari…</span>
      </div>
      <div
        class="flex h-9 w-9 items-center justify-center rounded-full bg-gradient-to-br from-blue-500 to-indigo-600 text-xs font-semibold text-white"
      >
        AK
      </div>
    </div>
  </header>
</template>
