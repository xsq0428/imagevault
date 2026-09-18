<script setup>
import { computed, onMounted, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import FrontLayout from '../components/FrontLayout.vue'
import SideNav from '../components/SideNav.vue'
import GalleryGrid from '../components/GalleryGrid.vue'
import Pagination from '../components/Pagination.vue'
import Lightbox from '../components/Lightbox.vue'
import { fetchCategories, fetchFeed } from '../api'

const PAGE_SIZE = 10

const route = useRoute()
const router = useRouter()

const items = ref([])
const categories = ref([])
const total = ref(0)
const page = ref(1)
const query = ref('')
const activeCategory = ref(null)
const loading = ref(false)
const toast = ref('')
const lightboxIndex = ref(-1)

const imageItems = computed(() => items.value.filter((item) => item.item_type === 'image'))
const lightboxImages = computed(() => imageItems.value.map((item) => item.image))

const activeCategoryLabel = computed(() => {
  if (activeCategory.value === null) return '全部'
  const found = categories.value.find((item) => item.id === activeCategory.value)
  return found ? found.name : '全部'
})

let toastTimer = null
function notify(message) {
  toast.value = message
  clearTimeout(toastTimer)
  toastTimer = setTimeout(() => (toast.value = ''), 2200)
}

function parseCategory(value) {
  if (value === undefined || value === null || value === '') return null
  const parsed = Number(value)
  return Number.isNaN(parsed) ? null : parsed
}

async function load() {
  loading.value = true
  try {
    const [feed, categoryList] = await Promise.all([
      fetchFeed({
        q: query.value,
        categoryId: activeCategory.value,
        page: page.value,
        limit: PAGE_SIZE
      }),
      fetchCategories()
    ])
    items.value = feed.items
    total.value = feed.total
    categories.value = categoryList
  } catch (err) {
    notify(err.message)
  } finally {
    loading.value = false
  }
}

function selectCategory(id) {
  activeCategory.value = id
  page.value = 1
  router.replace({ query: id === null ? {} : { category: id } })
  load()
}

let searchTimer = null
function onSearchInput() {
  clearTimeout(searchTimer)
  searchTimer = setTimeout(() => {
    page.value = 1
    load()
  }, 320)
}

function changePage(next) {
  page.value = next
  load()
  window.scrollTo({ top: 0, behavior: 'smooth' })
}

function openImage(image) {
  const index = imageItems.value.findIndex((item) => item.id === image.id)
  if (index >= 0) lightboxIndex.value = index
}

function openSet(item) {
  router.push(`/set/${item.id}`)
}

watch(
  () => route.query.category,
  (value) => {
    if (route.path !== '/categories') return
    const parsed = parseCategory(value)
    if (parsed !== activeCategory.value) {
      activeCategory.value = parsed
      page.value = 1
      load()
    }
  }
)

onMounted(() => {
  activeCategory.value = parseCategory(route.query.category)
  query.value = typeof route.query.q === 'string' ? route.query.q : ''
  load()
})
</script>

<template>
  <FrontLayout>
    <div class="category-page">
      <header class="search-row">
        <div class="search-pill">
          <svg viewBox="0 0 24 24" width="16" height="16">
            <circle cx="11" cy="11" r="6.5" fill="none" stroke="currentColor" stroke-width="1.8" />
            <path d="M16 16l4 4" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" />
          </svg>
          <input
            v-model="query"
            type="search"
            placeholder="搜索名称或文件名"
            @input="onSearchInput"
            @keyup.enter="load"
          />
        </div>
      </header>

      <div class="browse">
        <SideNav
          :categories="categories"
          :active="activeCategory"
          @select="selectCategory"
        />

        <main class="result-pane">
          <div class="pane-head">
            <h2>{{ activeCategoryLabel }}</h2>
            <span>共 {{ total }} 项</span>
          </div>

          <div v-if="loading" class="hint">加载中…</div>
          <div v-else-if="!items.length" class="hint">该分类下还没有内容</div>

          <GalleryGrid
            v-else
            :items="items"
            :selectable="false"
            @open="openImage"
            @open-set="openSet"
          />

          <Pagination :page="page" :total="total" :limit="PAGE_SIZE" @change="changePage" />
        </main>
      </div>

      <Lightbox
        :images="lightboxImages"
        :index="lightboxIndex"
        @close="lightboxIndex = -1"
        @change="lightboxIndex = $event"
      />

      <transition name="fade">
        <div v-if="toast" class="toast">{{ toast }}</div>
      </transition>
    </div>
  </FrontLayout>
</template>

<style scoped>
.category-page {
  --search-h: 62px;
  display: flex;
  flex-direction: column;
  min-height: calc(100dvh - 70px);
}

.search-row {
  position: sticky;
  top: 0;
  z-index: 20;
  display: flex;
  align-items: center;
  gap: 10px;
  height: var(--search-h);
  padding: 0 16px;
  background: var(--white);
}

.search-pill {
  flex: 1;
  display: flex;
  align-items: center;
  gap: 8px;
  height: 38px;
  padding: 0 14px;
  border-radius: 999px;
  background: #f2f3f2;
  color: var(--ink-300);
}

.search-pill input {
  flex: 1;
  min-width: 0;
  border: none;
  outline: none;
  background: transparent;
  font-size: 14px;
  color: var(--ink-900);
}

.browse {
  flex: 1;
  display: flex;
  align-items: flex-start;
  min-height: 0;
  border-top: 1px solid var(--line);
}

.result-pane {
  flex: 1;
  min-width: 0;
  padding: 14px 12px 24px;
  background: var(--white);
}

.pane-head {
  display: flex;
  align-items: baseline;
  justify-content: space-between;
  margin-bottom: 12px;
}

.pane-head h2 {
  margin: 0;
  font-size: 15px;
  font-weight: 600;
  color: var(--ink-900);
}

.pane-head span {
  font-size: 12px;
  color: var(--ink-300);
}

.hint {
  padding: 40px 0;
  text-align: center;
  font-size: 13px;
  color: var(--ink-300);
}

/* 平板 */
@media (min-width: 768px) {
  .search-row {
    padding: 0 24px;
  }
  .result-pane {
    padding: 18px 24px 28px;
  }
  .pane-head h2 {
    font-size: 17px;
  }
}

/* 电脑 */
@media (min-width: 1024px) {
  .category-page {
    min-height: 100dvh;
  }
  .search-row {
    padding: 0 32px;
  }
  .result-pane {
    padding: 22px 32px 40px;
  }
  .pane-head h2 {
    font-size: 18px;
  }
}
</style>
