<script setup>
import { onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import FrontLayout from '../components/FrontLayout.vue'
import BannerCarousel from '../components/BannerCarousel.vue'
import SmartImage from '../components/SmartImage.vue'
import { categoryCoverThumbUrl, fetchBanners, fetchCategories, thumbUrl } from '../api'

const router = useRouter()

const banners = ref([])
const categories = ref([])
const loading = ref(true)
const error = ref('')

async function load() {
  loading.value = true
  error.value = ''
  try {
    const [bannerList, categoryList] = await Promise.all([
      fetchBanners(),
      fetchCategories()
    ])
    banners.value = bannerList
    categories.value = categoryList
  } catch (err) {
    error.value = err.message
  } finally {
    loading.value = false
  }
}

function openBanner(banner) {
  if (!banner.link) return
  if (/^https?:\/\//.test(banner.link)) window.open(banner.link, '_blank')
  else router.push(banner.link)
}

function openCategory(category) {
  router.push({ path: '/categories', query: { category: category.id } })
}

function coverSrc(category) {
  if (category.cover_source === 'upload') return categoryCoverThumbUrl(category.id)
  if (category.cover_source === 'image' && category.cover_image_id) {
    return thumbUrl(category.cover_image_id)
  }
  return ''
}

onMounted(load)
</script>

<template>
  <FrontLayout>
    <BannerCarousel :banners="banners" @open="openBanner" />

    <section class="section">
      <div class="section-head">
        <h2>分类</h2>
      </div>

      <div v-if="loading" class="hint">加载中…</div>
      <div v-else-if="error" class="hint">{{ error }}</div>
      <div v-else-if="!categories.length" class="hint">还没有分类，请到后台创建</div>

      <div v-else class="category-grid">
        <button
          v-for="category in categories"
          :key="category.id"
          class="category-card"
          @click="openCategory(category)"
        >
          <span class="category-cover">
            <SmartImage
              v-if="coverSrc(category)"
              :src="coverSrc(category)"
              :placeholder="category.cover_placeholder"
              :alt="category.name"
            />
            <span v-else class="category-cover-empty">
              <svg viewBox="0 0 24 24" width="22" height="22">
                <rect x="3" y="4" width="18" height="16" rx="3" fill="none" stroke="currentColor" stroke-width="1.7" />
                <circle cx="9" cy="10" r="1.8" fill="currentColor" />
                <path d="M5 18l4.5-5 3.5 3.5L16 13l3 5" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linejoin="round" />
              </svg>
            </span>
          </span>
          <span class="category-name">{{ category.name }}</span>
          <span class="category-count">{{ category.image_count }} 张</span>
        </button>
      </div>
    </section>
  </FrontLayout>
</template>

<style scoped>
.section {
  padding: 24px 16px 0;
}

.section-head {
  display: flex;
  justify-content: center;
  margin-bottom: 18px;
}

.section-head h2 {
  margin: 0;
  font-size: 19px;
  font-weight: 600;
  color: var(--ink-900);
}

.hint {
  padding: 30px 0;
  text-align: center;
  font-size: 13px;
  color: var(--ink-300);
}

.category-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 20px 11px;
}

.category-card {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 0;
  border-radius: 0;
  overflow: visible;
  background: transparent;
  box-shadow: none;
  text-align: center;
  transition: transform 0.15s ease;
}

.category-card:hover {
  transform: translateY(-2px);
}

.category-cover {
  display: block;
  width: 100%;
  aspect-ratio: 6 / 5;
  border-radius: 8px;
  background: var(--mint-100);
  overflow: hidden;
}

.category-cover img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  display: block;
}

.category-cover-empty {
  width: 100%;
  height: 100%;
  display: grid;
  place-items: center;
  color: var(--mint-400);
}

.category-name {
  margin-top: 9px;
  max-width: 100%;
  font-size: 13px;
  font-weight: 400;
  color: var(--ink-900);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.category-count {
  margin-top: 2px;
  font-size: 11px;
  color: var(--ink-300);
}

/* 平板 */
@media (min-width: 768px) {
  .section {
    padding: 28px 24px 0;
  }
  .section-head h2 {
    font-size: 21px;
  }
  .category-grid {
    grid-template-columns: repeat(4, minmax(0, 1fr));
    gap: 22px 16px;
  }
  .category-name {
    font-size: 14px;
  }
}

/* 电脑 */
@media (min-width: 1024px) {
  .section {
    padding: 32px 32px 0;
  }
  .category-grid {
    grid-template-columns: repeat(5, minmax(0, 1fr));
    gap: 24px 20px;
  }
  .category-card:hover {
    transform: translateY(-3px);
  }
  .category-cover {
    border-radius: 10px;
  }
}

@media (min-width: 1360px) {
  .category-grid {
    grid-template-columns: repeat(6, minmax(0, 1fr));
  }
}
</style>
