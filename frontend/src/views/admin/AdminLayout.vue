<script setup>
import { computed, onMounted, ref } from 'vue'
import { fetchStats } from '../../api'

const collapsed = ref(typeof window !== 'undefined' && window.innerWidth <= 720)
const trashCount = ref(0)

const menu = [
  { to: '/admin/dashboard', label: '数据看板', icon: 'chart' },
  { to: '/admin/banners', label: '广告图管理', icon: 'banner' },
  { to: '/admin/categories', label: '分类管理', icon: 'folder' },
  { to: '/admin/upload', label: '素材上传', icon: 'upload' },
  { to: '/admin/assets', label: '素材管理', icon: 'image' },
  { to: '/admin/trash', label: '回收站', icon: 'trash', badge: true }
]

const pageTitle = computed(() => '素材上传后台')

async function loadBadge() {
  try {
    const data = await fetchStats()
    trashCount.value = data.trash_count
  } catch {
    trashCount.value = 0
  }
}

onMounted(loadBadge)
</script>

<template>
  <div class="admin-shell">
    <aside class="admin-sidebar" :class="{ collapsed }">
      <div class="admin-brand">
        <span class="brand-mark">
          <svg viewBox="0 0 24 24" width="18" height="18">
            <rect x="3" y="3" width="8" height="8" rx="2" fill="currentColor" />
            <rect x="13" y="3" width="8" height="8" rx="2" fill="currentColor" />
            <rect x="3" y="13" width="8" height="8" rx="2" fill="currentColor" />
            <rect x="13" y="13" width="8" height="8" rx="2" fill="currentColor" />
          </svg>
        </span>
        <span v-show="!collapsed" class="brand-text">素材上传后台</span>
      </div>

      <nav class="admin-menu">
        <router-link
          v-for="item in menu"
          :key="item.to"
          :to="item.to"
          class="menu-item"
          :title="item.label"
        >
          <svg v-if="item.icon === 'chart'" viewBox="0 0 24 24" width="18" height="18">
            <path d="M4 20V10M10 20V4M16 20v-7M22 20H2" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" />
          </svg>
          <svg v-else-if="item.icon === 'banner'" viewBox="0 0 24 24" width="18" height="18">
            <rect x="3" y="5" width="18" height="14" rx="3" fill="none" stroke="currentColor" stroke-width="1.7" />
            <path d="M3 15l4.5-4 3.5 3 3-2.5L21 15" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linejoin="round" />
            <circle cx="8.5" cy="9.5" r="1.4" fill="currentColor" />
          </svg>
          <svg v-else-if="item.icon === 'folder'" viewBox="0 0 24 24" width="18" height="18">
            <path d="M3 7a2 2 0 0 1 2-2h4l2 2h8a2 2 0 0 1 2 2v8a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V7Z" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linejoin="round" />
          </svg>
          <svg v-else-if="item.icon === 'upload'" viewBox="0 0 24 24" width="18" height="18">
            <path d="M12 16V5m0 0L8 9m4-4l4 4" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" />
            <path d="M4 17v1.5A1.5 1.5 0 0 0 5.5 20h13a1.5 1.5 0 0 0 1.5-1.5V17" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" />
          </svg>
          <svg v-else-if="item.icon === 'image'" viewBox="0 0 24 24" width="18" height="18">
            <rect x="3" y="4" width="18" height="16" rx="3" fill="none" stroke="currentColor" stroke-width="1.7" />
            <circle cx="9" cy="10" r="1.8" fill="currentColor" />
            <path d="M5 18l4.5-5 3.5 3.5L16 13l3 5" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linejoin="round" />
          </svg>
          <svg v-else viewBox="0 0 24 24" width="18" height="18">
            <path d="M5 7h14M9 7V5h6v2M6 7l1 13h10l1-13" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round" />
          </svg>
          <span v-show="!collapsed" class="menu-label">{{ item.label }}</span>
          <span
            v-if="item.badge && trashCount"
            v-show="!collapsed"
            class="menu-badge"
          >{{ trashCount }}</span>
        </router-link>
      </nav>

      <div class="sidebar-footer">
        <router-link to="/" class="menu-item" title="返回图库">
          <svg viewBox="0 0 24 24" width="18" height="18">
            <path d="M15 5l-7 7 7 7" fill="none" stroke="currentColor" stroke-width="1.9" stroke-linecap="round" stroke-linejoin="round" />
          </svg>
          <span v-show="!collapsed" class="menu-label">返回图库</span>
        </router-link>
      </div>
    </aside>

    <div v-if="!collapsed" class="sidebar-backdrop" @click="collapsed = true"></div>

    <div class="admin-main">
      <header class="admin-topbar">
        <button class="hamburger" title="切换菜单" @click="collapsed = !collapsed">
          <svg viewBox="0 0 24 24" width="20" height="20">
            <path d="M4 6h16M4 12h16M4 18h16" stroke="currentColor" stroke-width="2" stroke-linecap="round" />
          </svg>
        </button>
        <div>
          <div class="admin-title">{{ pageTitle }}</div>
          <div class="admin-subtitle">图片分类、上传与素材管理</div>
        </div>
        <div class="topbar-spacer"></div>
        <router-link class="icon-link" to="/">查看前台图库 →</router-link>
      </header>

      <section class="admin-content">
        <router-view />
      </section>
    </div>
  </div>
</template>

<style scoped>
.icon-link:hover {
  text-decoration: underline;
}
</style>
