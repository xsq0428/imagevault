<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import FrontLayout from '../components/FrontLayout.vue'
import Lightbox from '../components/Lightbox.vue'
import SmartImage from '../components/SmartImage.vue'
import { fetchSet, originalUrl, thumbUrl } from '../api'

const route = useRoute()
const router = useRouter()

const detail = ref(null)
const loading = ref(true)
const error = ref('')
const lightboxIndex = ref(-1)

const coverImage = computed(() => {
  if (!detail.value || !detail.value.cover_image_id) return null
  return detail.value.images.find((item) => item.id === detail.value.cover_image_id) || null
})

const coverUrl = computed(() =>
  detail.value && detail.value.cover_image_id
    ? originalUrl(detail.value.cover_image_id)
    : ''
)

const coverPlaceholder = computed(() => coverImage.value?.placeholder || '')

const dateLabel = computed(() => {
  if (!detail.value) return ''
  const date = new Date(detail.value.created_at)
  return `${date.getFullYear()}年${String(date.getMonth() + 1).padStart(2, '0')}月${String(
    date.getDate()
  ).padStart(2, '0')}日`
})

async function load() {
  loading.value = true
  error.value = ''
  try {
    detail.value = await fetchSet(route.params.id)
  } catch (err) {
    error.value = err.message
  } finally {
    loading.value = false
  }
}

function goBack() {
  if (window.history.length > 1) router.back()
  else router.push('/')
}

function openAt(index) {
  lightboxIndex.value = index
}

onMounted(load)
</script>

<template>
  <FrontLayout>
    <div class="set-page">
      <div v-if="loading" class="state-box">加载中…</div>
      <div v-else-if="error" class="state-box">{{ error }}</div>

      <template v-else-if="detail">
        <div class="layout">
          <section class="hero">
        <SmartImage
          v-if="coverUrl"
          class="hero-image"
          :src="coverUrl"
          :placeholder="coverPlaceholder"
          :alt="detail.title"
        />
        <div class="hero-gradient"></div>

        <header class="hero-nav">
          <button class="nav-circle" title="返回" @click="goBack">
            <svg viewBox="0 0 24 24" width="20" height="20">
              <path d="M15 5l-7 7 7 7" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" />
            </svg>
          </button>
          <button
            v-if="detail.cover_image_id"
            class="nav-pill"
            @click="openAt(detail.images.findIndex((item) => item.id === detail.cover_image_id))"
          >
            查看封面
          </button>
        </header>

        <div class="hero-text">
          <h1>{{ detail.title }}</h1>
          <div class="hero-meta">
            <span class="meta-item">
              <svg viewBox="0 0 24 24" width="13" height="13">
                <circle cx="12" cy="12" r="8.5" fill="none" stroke="currentColor" stroke-width="1.5" />
                <path d="M3.5 12h17M12 3.5c2.4 2.4 3.6 5.4 3.6 8.5S14.4 18.1 12 20.5C9.6 18.1 8.4 15.1 8.4 12S9.6 5.9 12 3.5Z" fill="none" stroke="currentColor" stroke-width="1.5" />
              </svg>
              {{ detail.category_name || '未分类' }}
            </span>
            <span class="meta-item">
              <svg viewBox="0 0 24 24" width="13" height="13">
                <rect x="3" y="4" width="18" height="16" rx="3" fill="none" stroke="currentColor" stroke-width="1.5" />
                <path d="M3 9h18" stroke="currentColor" stroke-width="1.5" />
              </svg>
              {{ detail.image_count }} 张
            </span>
          </div>
        </div>
      </section>

      <section class="sheet">
        <p class="date">{{ dateLabel }}</p>
        <p v-if="detail.description" class="description">{{ detail.description }}</p>
        <div v-if="detail.tags.length" class="tag-row">
          <span v-for="tag in detail.tags" :key="tag" class="tag">{{ tag }}</span>
        </div>

        <div class="member-grid">
          <button
            v-for="(image, index) in detail.images"
            :key="image.id"
            class="member-cell"
            :title="image.filename"
            @click="openAt(index)"
          >
            <SmartImage
              :src="thumbUrl(image.id)"
              :placeholder="image.placeholder"
              :alt="image.filename"
            />
          </button>
        </div>
      </section>
        </div>

        <Lightbox
          :images="detail.images"
          :index="lightboxIndex"
          @close="lightboxIndex = -1"
          @change="lightboxIndex = $event"
        />
      </template>
    </div>
  </FrontLayout>
</template>

<style scoped>
.set-page {
  min-height: 100dvh;
  background: var(--white);
}

.layout {
  display: block;
}

.state-box {
  padding: 80px 20px;
  text-align: center;
  color: var(--ink-500);
}

.hero {
  position: relative;
  height: 42vh;
  min-height: 280px;
  max-height: 460px;
  overflow: hidden;
  background: #18181b;
}

.hero-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
  display: block;
}

.hero-gradient {
  position: absolute;
  inset: 0;
  background: linear-gradient(
    to top,
    rgba(0, 0, 0, 0.68) 0%,
    rgba(0, 0, 0, 0.28) 42%,
    rgba(0, 0, 0, 0.06) 72%,
    transparent 100%
  );
}

.hero-nav {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 14px 16px;
}

.nav-circle {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  display: grid;
  place-items: center;
  color: #fff;
  background: rgba(0, 0, 0, 0.28);
  backdrop-filter: blur(6px);
}

.nav-circle:hover {
  background: rgba(0, 0, 0, 0.42);
}

.nav-pill {
  height: 34px;
  padding: 0 16px;
  border-radius: 17px;
  font-size: 13px;
  color: #fff;
  background: rgba(0, 0, 0, 0.28);
  border: 1px solid rgba(255, 255, 255, 0.4);
  backdrop-filter: blur(6px);
}

.hero-text {
  position: absolute;
  left: 18px;
  right: 18px;
  bottom: 30px;
  color: #fff;
}

.hero-text h1 {
  margin: 0 0 8px;
  font-size: 27px;
  font-weight: 600;
  line-height: 1.25;
  text-shadow: 0 1px 6px rgba(0, 0, 0, 0.5);
}

.hero-meta {
  display: flex;
  align-items: center;
  gap: 14px;
  font-size: 12px;
  color: rgba(255, 255, 255, 0.88);
}

.meta-item {
  display: inline-flex;
  align-items: center;
  gap: 5px;
}

.sheet {
  position: relative;
  margin-top: -20px;
  padding: 18px 16px 40px;
  background: var(--mint-50);
  border-radius: 20px 20px 0 0;
  box-shadow: 0 -2px 14px rgba(0, 0, 0, 0.06);
}

.date {
  margin: 0 0 10px;
  font-size: 16px;
  font-weight: 500;
  color: var(--ink-900);
}

.description {
  margin: 0 0 10px;
  font-size: 13px;
  line-height: 1.6;
  color: var(--ink-500);
}

.tag-row {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  margin-bottom: 14px;
}

.tag {
  padding: 3px 12px;
  border-radius: 999px;
  font-size: 11px;
  background: var(--mint-100);
  color: var(--mint-600);
}

.member-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 5px;
}

.member-cell {
  padding: 0;
  border-radius: 6px;
  overflow: hidden;
  aspect-ratio: 3 / 4;
  background: var(--mint-100);
}

.member-cell img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  display: block;
  transition: transform 0.18s ease;
}

.member-cell:hover img {
  transform: scale(1.04);
}

/* 平板 */
@media (min-width: 768px) {
  .hero {
    height: 46vh;
    max-height: 520px;
  }
  .member-grid {
    grid-template-columns: repeat(4, minmax(0, 1fr));
    gap: 7px;
  }
  .member-cell {
    border-radius: 8px;
  }
  .sheet {
    padding: 24px 24px 48px;
  }
}

/* 电脑：封面与内容左右分栏 */
@media (min-width: 1024px) {
  .layout {
    display: grid;
    grid-template-columns: minmax(0, 1.05fr) minmax(0, 1fr);
    gap: 28px;
    align-items: start;
    padding: 28px 32px 48px;
  }
  .hero {
    position: sticky;
    top: 28px;
    height: 74vh;
    max-height: 640px;
    border-radius: 18px;
  }
  .sheet {
    margin-top: 0;
    padding: 24px;
    border-radius: 18px;
    background: var(--white);
    box-shadow: var(--shadow-card);
    border: 1px solid var(--line);
  }
  .member-grid {
    grid-template-columns: repeat(4, minmax(0, 1fr));
    gap: 8px;
  }
}

@media (min-width: 1360px) {
  .member-grid {
    grid-template-columns: repeat(5, minmax(0, 1fr));
  }
}
</style>
