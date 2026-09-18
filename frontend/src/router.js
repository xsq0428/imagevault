import { createRouter, createWebHistory } from 'vue-router'
import HomeView from './views/HomeView.vue'
import GalleryView from './views/GalleryView.vue'
import SetDetailView from './views/SetDetailView.vue'
import AdminLayout from './views/admin/AdminLayout.vue'
import DashboardView from './views/admin/DashboardView.vue'
import CategoriesView from './views/admin/CategoriesView.vue'
import BannersView from './views/admin/BannersView.vue'
import UploadView from './views/admin/UploadView.vue'
import AssetsView from './views/admin/AssetsView.vue'
import TrashView from './views/admin/TrashView.vue'
import SiteConfigView from './views/admin/SiteConfigView.vue'
import LoginView from './views/admin/LoginView.vue'
import { ensureAuth } from './store'

const routes = [
  { path: '/', name: 'home', component: HomeView },
  { path: '/categories', name: 'categories', component: GalleryView },
  { path: '/set/:id', name: 'set-detail', component: SetDetailView },
  {
    path: '/admin/login',
    name: 'admin-login',
    component: LoginView,
    meta: { public: true }
  },
  {
    path: '/admin',
    component: AdminLayout,
    meta: { requiresAuth: true },
    children: [
      { path: '', redirect: '/admin/dashboard' },
      { path: 'dashboard', name: 'admin-dashboard', component: DashboardView },
      { path: 'banners', name: 'admin-banners', component: BannersView },
      { path: 'categories', name: 'admin-categories', component: CategoriesView },
      { path: 'upload', name: 'admin-upload', component: UploadView },
      { path: 'assets', name: 'admin-assets', component: AssetsView },
      { path: 'trash', name: 'admin-trash', component: TrashView },
      { path: 'site', name: 'admin-site', component: SiteConfigView }
    ]
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

router.beforeEach(async (to) => {
  if (to.matched.some((record) => record.meta.requiresAuth)) {
    const user = await ensureAuth()
    if (!user) {
      return { name: 'admin-login', query: { redirect: to.fullPath } }
    }
    return true
  }

  if (to.name === 'admin-login') {
    const user = await ensureAuth()
    if (user) return { path: '/admin/dashboard' }
  }

  return true
})

export default router
