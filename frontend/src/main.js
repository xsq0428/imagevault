import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import { setUnauthorizedHandler } from './api'
import { loadSiteConfig, markUnauthorized } from './store'
import './styles.css'
import './admin.css'

setUnauthorizedHandler(() => {
  markUnauthorized()
  const current = router.currentRoute.value
  if (
    current.matched.some((record) => record.meta.requiresAuth) &&
    current.name !== 'admin-login'
  ) {
    router.push({ name: 'admin-login', query: { redirect: current.fullPath } })
  }
})

createApp(App).use(router).mount('#app')

loadSiteConfig()
