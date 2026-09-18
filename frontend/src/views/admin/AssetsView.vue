<script setup>
import { computed, onMounted, ref } from 'vue'
import Pagination from '../../components/Pagination.vue'
import {
  deleteImages,
  deleteSet,
  fetchCategories,
  fetchImages,
  fetchSets,
  moveImages,
  thumbUrl,
  updateImage
} from '../../api'

const PAGE_SIZE = 10

const images = ref([])
const sets = ref([])
const categories = ref([])
const total = ref(0)
const page = ref(1)
const keyword = ref('')
const categoryFilter = ref('')
const loading = ref(false)
const error = ref('')
const success = ref('')
const selectedIds = ref([])

const moveTarget = ref('')
const editing = ref(null)
const editForm = ref({ filename: '', description: '', category_id: '', tags: '' })
const busy = ref(false)

const allChecked = computed(
  () => images.value.length > 0 && selectedIds.value.length === images.value.length
)

async function load() {
  loading.value = true
  error.value = ''
  try {
    const [list, categoryList, setList] = await Promise.all([
      fetchImages({
        q: keyword.value,
        categoryId: categoryFilter.value === '' ? null : categoryFilter.value,
        page: page.value,
        limit: PAGE_SIZE
      }),
      fetchCategories(),
      fetchSets()
    ])
    images.value = list.items
    total.value = list.total
    categories.value = categoryList
    sets.value = setList
    selectedIds.value = selectedIds.value.filter((id) =>
      list.items.some((image) => image.id === id)
    )
  } catch (err) {
    error.value = err.message
  } finally {
    loading.value = false
  }
}

function applyFilter() {
  page.value = 1
  load()
}

function changePage(next) {
  page.value = next
  load()
}

function toggleAll() {
  selectedIds.value = allChecked.value ? [] : images.value.map((image) => image.id)
}

function toggleOne(id) {
  const index = selectedIds.value.indexOf(id)
  if (index >= 0) selectedIds.value.splice(index, 1)
  else selectedIds.value.push(id)
}

function startEdit(image) {
  editing.value = image
  editForm.value = {
    filename: image.filename,
    description: image.description,
    category_id: image.category_id === null ? '' : image.category_id,
    tags: image.tags.join(', ')
  }
}

async function saveEdit() {
  if (!editing.value || busy.value) return
  busy.value = true
  error.value = ''
  try {
    await updateImage(editing.value.id, {
      filename: editForm.value.filename,
      description: editForm.value.description,
      category_id:
        editForm.value.category_id === '' ? null : Number(editForm.value.category_id),
      tags: editForm.value.tags
        .split(',')
        .map((item) => item.trim())
        .filter(Boolean)
    })
    editing.value = null
    success.value = '已保存修改'
    await load()
  } catch (err) {
    error.value = err.message
  } finally {
    busy.value = false
  }
}

async function removeSelected() {
  if (!selectedIds.value.length) return
  if (!window.confirm(`确定将选中的 ${selectedIds.value.length} 张图片移入回收站？`)) return
  try {
    await deleteImages([...selectedIds.value])
    selectedIds.value = []
    success.value = '已移入回收站'
    await load()
  } catch (err) {
    error.value = err.message
  }
}

async function removeSet(item) {
  if (
    !window.confirm(
      `确定将套图「${item.title}」及其 ${item.image_count} 张图片移入回收站？`
    )
  ) {
    return
  }
  try {
    await deleteSet(item.id)
    success.value = '套图已移入回收站'
    await load()
  } catch (err) {
    error.value = err.message
  }
}

async function moveSelected() {
  if (!selectedIds.value.length) return
  if (moveTarget.value === '') {
    error.value = '请先选择目标分类'
    return
  }
  try {
    await moveImages(
      [...selectedIds.value],
      moveTarget.value === 'none' ? null : Number(moveTarget.value)
    )
    selectedIds.value = []
    moveTarget.value = ''
    success.value = '已移动分类'
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
      <div class="toolbar">
        <div class="field" style="flex: 1; min-width: 180px">
          <label>搜索文件名</label>
          <input v-model="keyword" type="text" placeholder="输入关键词后回车" @keyup.enter="applyFilter" />
        </div>
        <div class="field" style="min-width: 150px">
          <label>分类筛选</label>
          <select v-model="categoryFilter" @change="applyFilter">
            <option value="">全部分类</option>
            <option v-for="category in categories" :key="category.id" :value="category.id">
              {{ category.name }}
            </option>
          </select>
        </div>
        <button class="btn" @click="applyFilter">查询</button>
      </div>

      <div v-if="selectedIds.length" class="toolbar">
        <span style="font-size: 13px; color: var(--ink-700)">已选 {{ selectedIds.length }} 张</span>
        <div class="field" style="margin: 0">
          <select v-model="moveTarget">
            <option value="">移动到分类…</option>
            <option value="none">未分类</option>
            <option v-for="category in categories" :key="category.id" :value="category.id">
              {{ category.name }}
            </option>
          </select>
        </div>
        <button class="btn" @click="moveSelected">批量移动</button>
        <button class="btn danger" @click="removeSelected">移入回收站</button>
        <button class="btn" @click="selectedIds = []">取消选择</button>
      </div>

      <p v-if="error" class="error-text">{{ error }}</p>
      <p v-if="success" style="color: var(--mint-600); font-size: 13px">{{ success }}</p>
    </div>

    <div v-if="sets.length" class="panel">
      <div class="panel-head">
        <h3>套图（{{ sets.length }}）</h3>
      </div>
      <div class="table-wrap">
        <table class="data-table">
          <thead>
            <tr>
              <th>封面</th>
              <th>标题</th>
              <th>分类</th>
              <th>图片数</th>
              <th>创建时间</th>
              <th>操作</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="item in sets" :key="item.id">
              <td data-label="封面">
                <img
                  v-if="item.cover_image_id"
                  class="table-thumb"
                  :src="thumbUrl(item.cover_image_id)"
                  :alt="item.title"
                />
                <span v-else class="table-thumb"></span>
              </td>
              <td data-label="标题">{{ item.title }}</td>
              <td data-label="分类">{{ item.category_name || '未分类' }}</td>
              <td data-label="图片数">{{ item.image_count }} 张</td>
              <td data-label="创建时间">{{ new Date(item.created_at).toLocaleString('zh-CN') }}</td>
              <td data-label="操作">
                <div class="row-actions">
                  <router-link class="mini-btn" :to="`/set/${item.id}`" target="_blank">
                    预览
                  </router-link>
                  <button class="mini-btn danger" @click="removeSet(item)">删除</button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <div class="panel">
      <div class="panel-head">
        <h3>素材列表（{{ total }}）</h3>
      </div>
      <div class="table-wrap">
        <table class="data-table">
          <thead>
            <tr>
              <th style="width: 40px">
                <input class="checkbox" type="checkbox" :checked="allChecked" @change="toggleAll" />
              </th>
              <th>缩略图</th>
              <th>文件名</th>
              <th>分类</th>
              <th>标签</th>
              <th>尺寸</th>
              <th>操作</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="image in images" :key="image.id">
              <td data-label="选择">
                <input
                  class="checkbox"
                  type="checkbox"
                  :checked="selectedIds.includes(image.id)"
                  @change="toggleOne(image.id)"
                />
              </td>
              <td data-label="缩略图">
                <img class="table-thumb" :src="thumbUrl(image.id)" :alt="image.filename" />
              </td>
              <td data-label="文件名">
                {{ image.filename }}
                <span v-if="image.set_id" class="set-flag">套图 #{{ image.set_id }}</span>
              </td>
              <td data-label="分类">{{ image.category_name || '未分类' }}</td>
              <td data-label="标签">
                <span v-for="tag in image.tags" :key="tag" class="tag-chip">{{ tag }}</span>
                <span v-if="!image.tags.length">—</span>
              </td>
              <td data-label="尺寸">{{ image.width }} × {{ image.height }}</td>
              <td data-label="操作">
                <div class="row-actions">
                  <button class="mini-btn" @click="startEdit(image)">编辑</button>
                  <button
                    class="mini-btn danger"
                    @click="selectedIds = [image.id]; removeSelected()"
                  >
                    删除
                  </button>
                </div>
              </td>
            </tr>
            <tr v-if="!images.length && !loading">
              <td colspan="7">没有符合条件的素材。</td>
            </tr>
            <tr v-if="loading">
              <td colspan="7">加载中…</td>
            </tr>
          </tbody>
        </table>
      </div>

      <Pagination :page="page" :total="total" :limit="PAGE_SIZE" @change="changePage" />
    </div>

    <div v-if="editing" class="overlay" @click.self="editing = null">
      <div class="dialog">
        <div class="panel-head">
          <h3>编辑素材</h3>
          <button class="mini-btn" @click="editing = null">关闭</button>
        </div>
        <div class="field">
          <label>文件名</label>
          <input v-model="editForm.filename" type="text" />
        </div>
        <div class="field">
          <label>分类</label>
          <select v-model="editForm.category_id">
            <option value="">未分类</option>
            <option v-for="category in categories" :key="category.id" :value="category.id">
              {{ category.name }}
            </option>
          </select>
        </div>
        <div class="field">
          <label>标签（逗号分隔）</label>
          <input v-model="editForm.tags" type="text" />
        </div>
        <div class="field">
          <label>描述</label>
          <textarea v-model="editForm.description" rows="3"></textarea>
        </div>
        <div class="panel-head" style="margin: 0">
          <span></span>
          <button class="btn primary" :disabled="busy" @click="saveEdit">
            {{ busy ? '保存中…' : '保存' }}
          </button>
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
  background: rgba(12, 24, 19, 0.45);
}

.dialog {
  width: min(460px, 100%);
  max-height: 88vh;
  overflow-y: auto;
  background: var(--white);
  border-radius: var(--radius-lg);
  padding: 20px;
  box-shadow: var(--shadow-soft);
}

.set-flag {
  display: inline-block;
  margin-left: 6px;
  padding: 1px 8px;
  border-radius: 999px;
  font-size: 10px;
  background: var(--mint-100);
  color: var(--mint-600);
}
</style>
