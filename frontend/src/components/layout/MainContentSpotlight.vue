<script setup lang="ts">
import { computed } from 'vue'
import type { SpotlightMode } from '@/composables/useMainSpotlightMode'

/**
 * Cahaya ambiens lembut: elips + blur besar, tanpa clip-path.
 * Referensi utama: kusut ungu dari kiri atas dashboard; Review atas tengah; AI Pipeline bawah tengah.
 */
const props = defineProps<{
  mode: SpotlightMode
}>()

const isBottom = computed(() => props.mode === 'bottom-center')
const isTopCenter = computed(() => props.mode === 'top-center')
</script>

<template>
  <!-- fixed = tidak ikut konten utama saat scroll (seperti sidebar tetap pada viewport) -->
  <div
    class="pointer-events-none fixed inset-0 z-0 hidden overflow-hidden md:left-64 dark:block"
    aria-hidden="true"
  >
    <!-- Kiri atas: Dashboard & halaman default -->
    <template v-if="!isBottom && !isTopCenter">
      <div
        class="absolute left-0 top-0 h-[min(580px,62vw)] w-[min(920px,130vw)] -translate-x-[8%] -translate-y-[38%] rounded-full bg-violet-500/[0.19] blur-[190px]"
      />
      <div
        class="absolute -top-36 left-[10%] h-[440px] w-[min(720px,94vw)] -translate-x-[20%] rounded-full bg-purple-500/[0.32] blur-[150px]"
      />
    </template>

    <!-- Atas tengah: Review Ulasan -->
    <template v-else-if="!isBottom && isTopCenter">
      <div
        class="absolute left-1/2 top-0 h-[min(560px,58vw)] w-[min(960px,125vw)] -translate-x-1/2 -translate-y-[38%] rounded-full bg-violet-500/[0.18] blur-[185px]"
      />
      <div
        class="absolute -top-32 left-1/2 h-[400px] w-[700px] max-w-[92vw] -translate-x-1/2 rounded-full bg-purple-500/30 blur-[140px]"
      />
    </template>

    <!-- Bawah tengah: AI Pipeline (sorotan lebih kuat + aksen fuchsia) -->
    <template v-else>
      <div
        class="absolute bottom-0 left-1/2 h-[min(680px,72vw)] w-[min(1040px,140vw)] -translate-x-1/2 translate-y-[32%] rounded-full bg-violet-500/[0.32] blur-[210px]"
      />
      <div
        class="absolute bottom-0 left-1/2 h-[min(520px,56vw)] w-[min(880px,118vw)] max-w-[94vw] -translate-x-1/2 translate-y-[22%] rounded-full bg-purple-500/[0.44] blur-[175px]"
      />
      <div
        class="absolute bottom-0 left-1/2 h-[360px] w-[min(760px,92vw)] max-w-[90vw] -translate-x-1/2 translate-y-32 rounded-full bg-fuchsia-500/[0.26] blur-[150px]"
      />
      <div
        class="absolute bottom-[8%] left-1/2 h-[240px] w-[min(560px,85vw)] max-w-[82vw] -translate-x-1/2 rounded-full bg-purple-300/[0.08] blur-[95px]"
      />
    </template>
  </div>
</template>
