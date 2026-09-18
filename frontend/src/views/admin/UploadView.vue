<script setup>
import { onMounted, ref } from 'vue'
import { createSet, fetchCategories, uploadImages } from '../../api'

const categories = ref([])
const files = ref([])
const kind = ref('single')
const setTitle = ref('')
const categoryId = ref('')
const tagsInput = ref('')
const description = ref('')
const dragOver = ref(false)
const busy = ref(false)
const error = ref('')
const success = ref('')
const inputRef = ref(null)

async function load() {
  try {
    categories.value = await fetchCategories()
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

function resetForm() {
  files.value = []
  tagsInput.value = ''
  description.value = ''
  setTitle.value = ''
}

async function submit() {
  if (!files.value.length || busy.value) return
  busy.value = true
  error.value = ''
  success.value = ''
  const count = files.value.length
  const tags = tagsInput.value
    .split(',')
    .map((item) => item.trim())
    .filter(Boolean)
  const category = categoryId.value === '' ? null : Number(categoryId.value)
  try {
    if (kind.value === 'set') {
      await createSet(files.value, {
        title: setTitle.value,
        description: description.value,
        categoryId: category,
        tags
      })
      success.value = `成功创建套图，共 ${count} 张，第一张已设为封面`
    } else {
      await uploadImages(files.value, {
        tags,
        categoryId: category,
        description: description.value
      })
      success.value = `成功上传 ${count} 张单图`
    }
    resetForm()
  } catch (err) {
    error.value = err.message
  } finally {
    busy.value = false
  }
}

onMounted(load)
</script>

<template>
  <div class="panel">
    <div class="panel-head">
      <h3>上传素材</h3>
      <router-link class="icon-link" to="/admin/assets">去素材管理 →</router-link>
    </div>

    <div class="kind-switch">
      <button
        class="kind-option"
        :class="{ active: kind === 'single' }"
        @click="kind = 'single'"
      >
        <svg viewBox="0 0 24 24" width="18" height="18">
          <rect x="4" y="4" width="16" height="16" rx="3" fill="none" stroke="currentColor" stroke-width="1.7" />
          <circle cx="9" cy="10" r="1.6" fill="currentColor" />
          <path d="M6 18l4-4.5 3 3 3.5-3.5L20 18" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linejoin="round" />
        </svg>
        <span class="kind-title">单图</span>
        <span class="kind-hint">每张图片独立展示</span>
      </button>

      <button class="kind-option" :class="{ active: kind === 'set' }" @click="kind = 'set'">
        <svg viewBox="0 0 24 24" width="18" height="18">
          <rect x="3" y="3" width="12" height="12" rx="2.5" fill="none" stroke="currentColor" stroke-width="1.7" />
          <path d="M8 21h10a3 3 0 0 0 3-3V8" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" />
        </svg>
        <span class="kind-title">套图</span>
        <span class="kind-hint">多张成组，第一张为封面</span>
      </button>
    </div>

    <div
      class="dropzone"
      :class="{ over: dragOver }"
      @dragover.prevent="dragOver = true"
      @dragleave.prevent="dragOver = false"
      @drop.prevent="onDrop"
      @click="inputRef.click()"
    >
      <svg viewBox="0 0 24 24" width="32" height="32">
        <path d="M12 16V5m0 0L8 9m4-4l4 4" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" />
        <path d="M4 17v1.5A1.5 1.5 0 0 0 5.5 20h13a1.5 1.5 0 0 0 1.5-1.5V17" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" />
      </svg>
      <p>点击选择或拖拽图片到此处，可多选</p>
      <small>支持 JPG / PNG / WEBP / GIF / BMP，单张最大 20MB</small>
      <input ref="inputRef" type="file" accept="image/*" multiple hidden @change="onPick" />
    </div>

    <div class="form-inline" style="margin-top: 16px">
      <div v-if="kind === 'set'" class="field">
        <label>套图标题</label>
        <input v-model="setTitle" type="text" placeholder="例如：夏日海边系列" />
      </div>
      <div class="field">
        <label>归属分类</label>
        <select v-model="categoryId">
          <option value="">未分类</option>
          <option v-for="category in categories" :key="category.id" :value="category.id">
            {{ category.name }}
          </option>
        </select>
      </div>
      <div class="field">
        <label>标签（逗号分隔）</label>
        <input v-model="tagsInput" type="text" placeholder="例如：旅行, 晚霞" />
      </div>
      <div class="field">
        <label>描述</label>
        <input v-model="description" type="text" placeholder="可留空" />
      </div>
    </div>

    <ul v-if="files.length" class="file-list">
      <li v-for="(file, index) in files" :key="`${file.name}-${index}`">
        <span class="file-name">{{ file.name }}</span>
        <span v-if="kind === 'set' && index === 0" class="cover-flag">封面</span>
        <span class="file-size">{{ humanSize(file.size) }}</span>
        <button class="mini-btn danger" @click="files.splice(index, 1)">移除</button>
      </li>
    </ul>

    <p v-if="error" class="error-text">{{ error }}</p>
    <p v-if="success" style="color: var(--mint-600); font-size: 13px; margin-top: 10px">{{ success }}</p>

    <div class="panel-head" style="margin: 18px 0 0">
      <span v-if="kind === 'set' && files.length" class="cover-tip">
        将使用第一张图片作为套图封面
      </span>
      <span v-else></span>
      <button class="btn primary" :disabled="!files.length || busy" @click="submit">
        {{
          busy
            ? '处理中…'
            : kind === 'set'
              ? `创建套图${files.length ? `（${files.length}）` : ''}`
              : `开始上传${files.length ? `（${files.length}）` : ''}`
        }}
      </button>
    </div>
  </div>
</template>

<style scoped>
.kind-switch {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 12px;
  margin-bottom: 16px;
  max-width: 560px;
}

.kind-option {
  display: grid;
  grid-template-columns: auto 1fr;
  grid-template-rows: auto auto;
  column-gap: 10px;
  align-items: center;
  padding: 12px 14px;
  border-radius: 12px;
  border: 2px solid var(--line);
  background: var(--white);
  color: var(--ink-500);
  text-align: left;
  transition: border-color 0.15s ease, background 0.15s ease, color 0.15s ease;
}

.kind-option svg {
  grid-row: span 2;
}

.kind-option.active {
  border-color: var(--mint-500);
  background: var(--mint-50);
  color: var(--mint-600);
}

.kind-title {
  font-size: 14px;
  font-weight: 600;
}

.kind-hint {
  font-size: 11px;
  color: var(--ink-300);
}

.cover-flag {
  padding: 2px 8px;
  border-radius: 999px;
  font-size: 10px;
  background: var(--mint-500);
  color: var(--white);
}

.cover-tip {
  font-size: 12px;
  color: var(--ink-300);
}
</style>
