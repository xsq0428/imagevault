<script setup>
import { computed, onMounted, ref } from 'vue'
import { fetchStats, thumbUrl } from '../../api'

const stats = ref(null)
const loading = ref(true)
const error = ref('')

const totalSize = computed(() => {
  if (!stats.value) return '0 KB'
  const bytes = stats.value.total_bytes
  if (bytes >= 1024 * 1024 * 1024) return `${(bytes / 1024 / 1024 / 1024).toFixed(2)} GB`
  if (bytes >= 1024 * 1024) return `${(bytes / 1024 / 1024).toFixed(1)} MB`
  return `${Math.max(0, Math.round(bytes / 1024))} KB`
})

const maxUsage = computed(() => {
  if (!stats.value || !stats.value.category_usage.length) return 1
  return Math.max(...stats.value.category_usage.map((item) => item.image_count), 1)
})

async function load() {
  loading.value = true
  try {
    stats.value = await fetchStats()
  } catch (err) {
    error.value = err.message
  } finally {
    loading.value = false
  }
}

onMounted(load)
</script>

<template>
  <div>
    <p v-if="error" class="error-text">{{ error }}</p>

    <div v-if="stats" class="stat-grid">
      <div class="stat-card">
        <div class="label">单图总数</div>
        <div class="value">{{ stats.total_images }}<span class="unit">张</span></div>
      </div>
      <div class="stat-card">
        <div class="label">套图数量</div>
        <div class="value">{{ stats.total_sets }}<span class="unit">组</span></div>
      </div>
      <div class="stat-card">
        <div class="label">分类数量</div>
        <div class="value">{{ stats.total_categories }}<span class="unit">个</span></div>
      </div>
      <div class="stat-card">
        <div class="label">标签数量</div>
        <div class="value">{{ stats.total_tags }}<span class="unit">个</span></div>
      </div>
      <div class="stat-card">
        <div class="label">存储占用</div>
        <div class="value">{{ totalSize }}</div>
      </div>
      <div class="stat-card">
        <div class="label">回收站</div>
        <div class="value">{{ stats.trash_count }}<span class="unit">张</span></div>
      </div>
    </div>

    <div v-if="stats" class="panel">
      <div class="panel-head">
        <h3>分类分布</h3>
        <router-link class="icon-link" to="/admin/categories">管理分类 →</router-link>
      </div>
      <p v-if="!stats.category_usage.length" class="error-text">还没有分类，先到分类管理新建一个。</p>
      <div v-for="item in stats.category_usage" :key="item.id" class="bar-row">
        <span>{{ item.name }}</span>
        <span class="bar-track">
          <span class="bar-fill" :style="{ width: `${(item.image_count / maxUsage) * 100}%` }"></span>
        </span>
        <span>{{ item.image_count }} 张</span>
      </div>
    </div>

    <div v-if="stats" class="panel">
      <div class="panel-head">
        <h3>最近上传</h3>
        <router-link class="icon-link" to="/admin/assets">全部素材 →</router-link>
      </div>
      <div v-if="stats.recent.length" class="recent-grid">
        <div v-for="image in stats.recent" :key="image.id" class="recent-item" :title="image.filename">
          <img :src="thumbUrl(image.id)" :alt="image.filename" />
        </div>
      </div>
      <p v-else class="error-text">暂无素材，去素材上传添加第一张。</p>
    </div>

    <div v-if="loading" class="panel">加载中…</div>
  </div>
</template>
