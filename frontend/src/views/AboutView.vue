<script setup lang="ts">
import DashboardCardShell from '@/components/dashboard/DashboardCardShell.vue'
</script>

<template>
  <div class="mx-auto flex min-h-[50vh] w-full max-w-6xl flex-col justify-center px-4 sm:min-h-[60vh]">
    <DashboardCardShell tag="section" variant="tm" class="p-8">
      <div class="space-y-2">
        <h1 class="text-xl font-semibold text-white sm:text-2xl">
          <span
            class="bg-gradient-to-r from-purple-200 via-fuchsia-200 to-purple-100 bg-clip-text text-transparent"
          >
            Tentang aplikasi
          </span>
        </h1>
        <p class="max-w-2xl text-sm leading-relaxed text-slate-300/85">
          Panel analisis sentimen ulasan untuk Access by KAI. Halaman ini memuat konten
          statis pengantar dan dapat Anda sesuaikan sesuai kebutuhan dokumentasi tugas akhir.
        </p>
      </div>
    </DashboardCardShell>
  </div>
</template>
