<script setup>
import { onMounted, ref } from 'vue'
import {
  bannerThumbUrl,
  deleteBanner,
  fetchBanners,
  updateBanner,
  uploadBanners
} from '../../api'

const banners = ref([])
const files = ref([])
const title = ref('')
const link = ref('')
const inputRef = ref(null)
const dragOver = ref(false)
const busy = ref(false)
const error = ref('')
const success = ref('')
const editing = ref(null)
const editForm = ref({ title: '', link: '', sort_order: 0, is_active: true })

async function load() {
  try {
    banners.value = await fetchBanners({ includeInactive: true })
  } catch (err) {
    error.value = err.message
  }
}

function addFiles(list) {
  const incoming = Array.from(list).filter((file) => file.type.startsWith('image/'))
  const seen = new Set(files.value.map((file) => `${file.name}-${file.size}`))
  for (const file of incoming) {
    const key = `${file.name}-${file.size}`
    if (!seen.has(key)) {
      files.value.push(file)
      seen.add(key)
    }
  }
}

function onDrop(event) {
  dragOver.value = false
  addFiles(event.dataTransfer.files)
}

function onPick(event) {
  addFiles(event.target.files)
  event.target.value = ''
}

function humanSize(bytes) {
  return bytes > 1024 * 1024
    ? `${(bytes / 1024 / 1024).toFixed(1)} MB`
    : `${Math.max(1, Math.round(bytes / 1024))} KB`
}

async function submit() {
  if (!files.value.length || busy.value) return
  busy.value = true
  error.value = ''
  success.value = ''
  try {
    await uploadBanners(files.value, { title: title.value, link: link.value })
    success.value = `已添加 ${files.value.length} 张广告图`
    files.value = []
    title.value = ''
    link.value = ''
    await load()
  } catch (err) {
    error.value = err.message
  } finally {
    busy.value = false
  }
}

function startEdit(banner) {
  editing.value = banner
  editForm.value = {
    title: banner.title,
    link: banner.link,
    sort_order: banner.sort_order,
    is_active: banner.is_active
  }
}

async function saveEdit() {
  if (!editing.value) return
  try {
    await updateBanner(editing.value.id, {
      title: editForm.value.title,
      link: editForm.value.link,
      sort_order: Number(editForm.value.sort_order) || 0,
      is_active: editForm.value.is_active
    })
    editing.value = null
    success.value = '已保存'
    await load()
  } catch (err) {
    error.value = err.message
  }
}

async function toggleActive(banner) {
  try {
    await updateBanner(banner.id, { is_active: !banner.is_active })
    await load()
  } catch (err) {
    error.value = err.message
  }
}

async function remove(banner) {
  if (!window.confirm('确定删除这张广告图？')) return
  try {
    await deleteBanner(banner.id)
    success.value = '已删除'
    await load()
  } catch (err) {
    error.value = err.message
  }
}

onMounted(load)
</script>

<template>
  <div>
    <div class="panel">
      <div class="panel-head">
        <h3>新增广告图</h3>
        <span class="hint-text">用于首页顶部轮播</span>
      </div>

      <div
        class="dropzone"
        :class="{ over: dragOver }"
        @dragover.prevent="dragOver = true"
        @dragleave.prevent="dragOver = false"
        @drop.prevent="onDrop"
        @click="inputRef.click()"
      >
        <svg viewBox="0 0 24 24" width="30" height="30">
          <path d="M12 16V5m0 0L8 9m4-4l4 4" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" />
          <path d="M4 17v1.5A1.5 1.5 0 0 0 5.5 20h13a1.5 1.5 0 0 0 1.5-1.5V17" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" />
        </svg>
        <p>点击选择或拖拽广告图到此处，可多选</p>
        <small>建议尺寸 2:1（如 1200×600），单张最大 20MB</small>
        <input ref="inputRef" type="file" accept="image/*" multiple hidden @change="onPick" />
      </div>

      <div class="form-inline" style="margin-top: 16px">
        <div class="field">
          <label>标题</label>
          <input v-model="title" type="text" placeholder="可留空，默认使用文件名" />
        </div>
        <div class="field">
          <label>跳转链接</label>
          <input v-model="link" type="text" placeholder="例如 /set/1 或 https://..." />
        </div>
      </div>

      <ul v-if="files.length" class="file-list">
        <li v-for="(file, index) in files" :key="`${file.name}-${index}`">
          <span class="file-name">{{ file.name }}</span>
          <span class="file-size">{{ humanSize(file.size) }}</span>
          <button class="mini-btn danger" @click="files.splice(index, 1)">移除</button>
        </li>
      </ul>

      <p v-if="error" class="error-text">{{ error }}</p>
      <p v-if="success" style="color: var(--mint-600); font-size: 13px; margin-top: 10px">{{ success }}</p>

      <div class="panel-head" style="margin: 16px 0 0">
        <span></span>
        <button class="btn primary" :disabled="!files.length || busy" @click="submit">
          {{ busy ? '上传中…' : `添加广告图${files.length ? `（${files.length}）` : ''}` }}
        </button>
      </div>
    </div>

    <div class="panel">
      <div class="panel-head">
        <h3>广告图列表（{{ banners.length }}）</h3>
      </div>
      <div class="table-wrap">
        <table class="data-table">
          <thead>
            <tr>
              <th>预览</th>
              <th>标题</th>
              <th>跳转</th>
              <th>排序</th>
              <th>状态</th>
              <th>操作</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="banner in banners" :key="banner.id">
              <td data-label="预览">
                <img class="table-thumb banner-thumb" :src="bannerThumbUrl(banner.id)" :alt="banner.title" />
              </td>
              <td data-label="标题">{{ banner.title || '—' }}</td>
              <td data-label="跳转">{{ banner.link || '—' }}</td>
              <td data-label="排序">{{ banner.sort_order }}</td>
              <td data-label="状态">
                <button class="mini-btn" @click="toggleActive(banner)">
                  {{ banner.is_active ? '已启用' : '已停用' }}
                </button>
              </td>
              <td data-label="操作">
                <div class="row-actions">
                  <button class="mini-btn" @click="startEdit(banner)">编辑</button>
                  <button class="mini-btn danger" @click="remove(banner)">删除</button>
                </div>
              </td>
            </tr>
            <tr v-if="!banners.length">
              <td colspan="6">还没有广告图，使用上方表单添加。</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <div v-if="editing" class="overlay" @click.self="editing = null">
      <div class="dialog">
        <div class="panel-head">
          <h3>编辑广告图</h3>
          <button class="mini-btn" @click="editing = null">关闭</button>
        </div>
        <div class="field">
          <label>标题</label>
          <input v-model="editForm.title" type="text" />
        </div>
        <div class="field">
          <label>跳转链接</label>
          <input v-model="editForm.link" type="text" placeholder="/set/1 或 https://..." />
        </div>
        <div class="field">
          <label>排序（越小越前）</label>
          <input v-model="editForm.sort_order" type="number" />
        </div>
        <div class="field">
          <label>状态</label>
          <select v-model="editForm.is_active">
            <option :value="true">启用</option>
            <option :value="false">停用</option>
          </select>
        </div>
        <div class="panel-head" style="margin: 0">
          <span></span>
          <button class="btn primary" @click="saveEdit">保存</button>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.hint-text {
  font-size: 12px;
  color: var(--ink-300);
}

.banner-thumb {
  width: 84px;
  height: 48px;
  border-radius: 8px;
  object-fit: cover;
}

.overlay {
  position: fixed;
  inset: 0;
  z-index: 50;
  display: grid;
  place-items: center;
  padding: 18px;
  background: rgba(12, 24, 19, 0.45);
}

.dialog {
  width: min(440px, 100%);
  max-height: 88vh;
  overflow-y: auto;
  background: var(--white);
  border-radius: var(--radius-lg);
  padding: 20px;
  box-shadow: var(--shadow-soft);
}
</style>
