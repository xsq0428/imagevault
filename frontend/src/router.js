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

const routes = [
  { path: '/', name: 'home', component: HomeView },
  { path: '/categories', name: 'categories', component: GalleryView },
  { path: '/set/:id', name: 'set-detail', component: SetDetailView },
  {
    path: '/admin',
    component: AdminLayout,
    children: [
      { path: '', redirect: '/admin/dashboard' },
      { path: 'dashboard', name: 'admin-dashboard', component: DashboardView },
      { path: 'banners', name: 'admin-banners', component: BannersView },
      { path: 'categories', name: 'admin-categories', component: CategoriesView },
      { path: 'upload', name: 'admin-upload', component: UploadView },
      { path: 'assets', name: 'admin-assets', component: AssetsView },
      { path: 'trash', name: 'admin-trash', component: TrashView }
    ]
  }
]

export default createRouter({
  history: createWebHistory(),
  routes
})
