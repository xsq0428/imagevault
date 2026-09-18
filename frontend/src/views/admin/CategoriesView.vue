<script setup>
import { onMounted, ref } from 'vue'
import {
  categoryCoverUrl,
  createCategory,
  deleteCategory,
  deleteCategoryCover,
  fetchCategories,
  thumbUrl,
  updateCategory,
  uploadCategoryCover
} from '../../api'

const categories = ref([])
const error = ref('')
const success = ref('')

const dialogOpen = ref(false)
const editingId = ref(null)
const form = ref({ name: '', description: '', sort_order: 0 })
const coverFile = ref(null)
const coverPreview = ref('')
const coverRemoved = ref(false)
const busy = ref(false)
const fileInput = ref(null)

async function load() {
  try {
    categories.value = await fetchCategories()
  } catch (err) {
    error.value = err.message
  }
}

function resetDialog() {
  editingId.value = null
  form.value = { name: '', description: '', sort_order: 0 }
  coverFile.value = null
  coverPreview.value = ''
  coverRemoved.value = false
  error.value = ''
}

function openCreate() {
  resetDialog()
  dialogOpen.value = true
}

function openEdit(category) {
  resetDialog()
  editingId.value = category.id
  form.value = {
    name: category.name,
    description: category.description,
    sort_order: category.sort_order
  }
  if (category.cover_source === 'upload') {
    coverPreview.value = categoryCoverUrl(category.id)
  } else if (category.cover_source === 'image' && category.cover_image_id) {
    coverPreview.value = thumbUrl(category.cover_image_id)
  }
  dialogOpen.value = true
}

function onPickCover(event) {
  const file = event.target.files?.[0]
  event.target.value = ''
  if (!file) return
  coverFile.value = file
  coverRemoved.value = false
  coverPreview.value = URL.createObjectURL(file)
}

function removeCover() {
  coverFile.value = null
  coverRemoved.value = !!editingId.value
  coverPreview.value = ''
}

function closeDialog() {
  if (coverPreview.value.startsWith('blob:')) URL.revokeObjectURL(coverPreview.value)
  dialogOpen.value = false
}

async function submit() {
  if (!form.value.name.trim()) {
    error.value = '请输入分类名称'
    return
  }
  if (busy.value) return
  busy.value = true
  error.value = ''
  success.value = ''
  const payload = {
    name: form.value.name.trim(),
    description: form.value.description.trim(),
    sort_order: Number(form.value.sort_order) || 0
  }
  try {
    let category
    if (editingId.value) {
      category = await updateCategory(editingId.value, payload)
    } else {
      category = await createCategory(payload)
    }
    if (coverFile.value) {
      await uploadCategoryCover(category.id, coverFile.value)
    } else if (coverRemoved.value) {
      await deleteCategoryCover(category.id)
    }
    closeDialog()
    success.value = '已保存'
    await load()
  } catch (err) {
    error.value = err.message
  } finally {
    busy.value = false
  }
}

async function remove(category) {
  if (!window.confirm(`确定删除分类「${category.name}」？该分类下的素材会变为未分类。`)) return
  try {
    await deleteCategory(category.id)
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
        <h3>分类列表（{{ categories.length }}）</h3>
        <button class="btn primary" @click="openCreate">新增分类</button>
      </div>

      <p v-if="error" class="error-text">{{ error }}</p>
      <p v-if="success" style="color: var(--mint-600); font-size: 13px">{{ success }}</p>

      <div class="table-wrap">
        <table class="data-table">
          <thead>
            <tr>
              <th>封面</th>
              <th>名称</th>
              <th>描述</th>
              <th>素材数</th>
              <th>排序</th>
              <th>操作</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="category in categories" :key="category.id">
              <td data-label="封面">
                <img
                  v-if="category.cover_source === 'upload'"
                  class="table-thumb"
                  :src="categoryCoverUrl(category.id)"
                  :alt="category.name"
                />
                <img
                  v-else-if="category.cover_source === 'image' && category.cover_image_id"
                  class="table-thumb"
                  :src="thumbUrl(category.cover_image_id)"
                  :alt="category.name"
                />
                <span v-else class="table-thumb"></span>
              </td>
              <td data-label="名称">{{ category.name }}</td>
              <td data-label="描述">{{ category.description || '—' }}</td>
              <td data-label="素材数">{{ category.image_count }}</td>
              <td data-label="排序">{{ category.sort_order }}</td>
              <td data-label="操作">
                <div class="row-actions">
                  <button class="mini-btn" @click="openEdit(category)">编辑</button>
                  <button class="mini-btn danger" @click="remove(category)">删除</button>
                </div>
              </td>
            </tr>
            <tr v-if="!categories.length">
              <td colspan="6">还没有分类，点击右上角「新增分类」创建。</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <div v-if="dialogOpen" class="overlay" @click.self="closeDialog">
      <div class="dialog">
        <div class="panel-head">
          <h3>{{ editingId ? '编辑分类' : '新增分类' }}</h3>
          <button class="mini-btn" @click="closeDialog">关闭</button>
        </div>

        <div class="field">
          <label>分类封面</label>
          <div class="cover-picker">
            <button class="cover-preview" type="button" @click="fileInput.click()">
              <img v-if="coverPreview" :src="coverPreview" alt="分类封面" />
              <span v-else class="cover-empty">
                <svg viewBox="0 0 24 24" width="24" height="24">
                  <path d="M12 16V5m0 0L8 9m4-4l4 4" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" />
                  <path d="M4 17v1.5A1.5 1.5 0 0 0 5.5 20h13a1.5 1.5 0 0 0 1.5-1.5V17" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" />
                </svg>
                上传封面
              </span>
            </button>
            <div class="cover-actions">
              <button class="mini-btn" type="button" @click="fileInput.click()">
                {{ coverPreview ? '更换图片' : '选择图片' }}
              </button>
              <button v-if="coverPreview" class="mini-btn danger" type="button" @click="removeCover">
                移除封面
              </button>
              <p class="cover-hint">
                不设置封面时，自动使用该分类下最新素材的缩略图
              </p>
            </div>
          </div>
          <input ref="fileInput" type="file" accept="image/*" hidden @change="onPickCover" />
        </div>

        <div class="field">
          <label>分类名称</label>
          <input v-model="form.name" type="text" placeholder="例如：风景、人像、素材" />
        </div>

        <div class="field">
          <label>描述</label>
          <input v-model="form.description" type="text" placeholder="可留空" />
        </div>

        <div class="field">
          <label>排序（越小越前）</label>
          <input v-model="form.sort_order" type="number" />
        </div>

        <p v-if="error" class="error-text">{{ error }}</p>

        <div class="panel-head" style="margin: 4px 0 0">
          <span></span>
          <div class="row-actions">
            <button class="btn" @click="closeDialog">取消</button>
            <button class="btn primary" :disabled="busy" @click="submit">
              {{ busy ? '保存中…' : '保存' }}
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.overlay {
  position: fixed;
  inset: 0;
  z-index: 50;
  display: grid;
  place-items: center;
  padding: 18px;
  background: rgba(9, 9, 11, 0.45);
  overflow-y: auto;
}

.dialog {
  width: min(460px, 100%);
  max-height: 90vh;
  overflow-y: auto;
  background: var(--white);
  border-radius: var(--radius-lg);
  padding: 20px;
  box-shadow: var(--shadow-soft);
}

.cover-picker {
  display: flex;
  gap: 14px;
  align-items: flex-start;
}

.cover-preview {
  flex: 0 0 auto;
  width: 108px;
  height: 108px;
  border-radius: 12px;
  overflow: hidden;
  border: 1px dashed var(--line);
  background: var(--mint-50);
  display: grid;
  place-items: center;
  padding: 0;
}

.cover-preview img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  display: block;
}

.cover-empty {
  display: grid;
  justify-items: center;
  gap: 6px;
  font-size: 11px;
  color: var(--mint-600);
}

.cover-actions {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  gap: 8px;
  min-width: 0;
}

.cover-actions .mini-btn {
  min-height: 32px;
  padding: 0 14px;
}

.cover-hint {
  margin: 0;
  font-size: 11px;
  line-height: 1.5;
  color: var(--ink-300);
}
</style>
