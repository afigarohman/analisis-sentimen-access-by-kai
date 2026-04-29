import './charts/register'
import './assets/main.css'

import { createApp } from 'vue'
import { createPinia } from 'pinia'

import App from './App.vue'
import router from './router'

// Dark mode: auto-follow system preference (class-based)
const mql = window.matchMedia?.('(prefers-color-scheme: dark)')
const applySystemTheme = () => {
  const dark = Boolean(mql?.matches)
  document.documentElement.classList.toggle('dark', dark)
}
applySystemTheme()
mql?.addEventListener?.('change', applySystemTheme)

const app = createApp(App)

app.use(createPinia())
app.use(router)

app.mount('#app')
