import { ref } from 'vue'

const isDark = ref(false)
let initialized = false

function applyDarkClass(next: boolean) {
  const root = document.documentElement
  root.classList.toggle('dark', next)
  isDark.value = next
}

export function useDarkMode() {
  if (initialized) {
    return {
      isDark,
      setDark: applyDarkClass,
      toggle: () => applyDarkClass(!isDark.value),
    }
  }
  initialized = true

  const mql = window.matchMedia?.('(prefers-color-scheme: dark)')
  const setFromSystem = () => applyDarkClass(Boolean(mql?.matches))
  setFromSystem()

  mql?.addEventListener?.('change', setFromSystem)

  return {
    isDark,
    setDark: applyDarkClass,
    toggle: () => applyDarkClass(!isDark.value),
  }
}

