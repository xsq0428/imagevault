<script setup>
import { onMounted, ref } from 'vue'
import Pagination from '../../components/Pagination.vue'
import {
  emptyTrash,
  fetchTrash,
  fetchTrashSets,
  purgeImage,
  purgeSet,
  restoreImage,
  restoreSet,
  thumbUrl
} from '../../api'

const PAGE_SIZE = 12

const images = ref([])
const sets = ref([])
const total = ref(0)
const page = ref(1)
const loading = ref(false)
const error = ref('')
const success = ref('')

async function load() {
  loading.value = true
  error.value = ''
  try {
    const [data, setList] = await Promise.all([
      fetchTrash({ page: page.value, limit: PAGE_SIZE }),
      fetchTrashSets()
    ])
    images.value = data.items
    total.value = data.total
    sets.value = setList
  } catch (err) {
    error.value = err.message
  } finally {
    loading.value = false
  }
}

function changePage(next) {
  page.value = next
  load()
}

async function restore(id) {
  try {
    await restoreImage(id)
    success.value = '已恢复'
    await load()
  } catch (err) {
    error.value = err.message
  }
}

async function purge(id) {
  if (!window.confirm('彻底删除后无法恢复，确定继续？')) return
  try {
    await purgeImage(id)
    success.value = '已彻底删除'
    await load()
  } catch (err) {
    error.value = err.message
  }
}

async function restoreSetItem(id) {
  try {
    await restoreSet(id)
    success.value = '套图已恢复'
    await load()
  } catch (err) {
    error.value = err.message
  }
}

async function purgeSetItem(item) {
  if (!window.confirm(`彻底删除套图「${item.title}」及其所有图片？该操作不可恢复。`)) return
  try {
    await purgeSet(item.id)
    success.value = '套图已彻底删除'
    await load()
  } catch (err) {
    error.value = err.message
  }
}

async function clearAll() {
  if (!total.value && !sets.value.length) return
  if (!window.confirm('确定清空回收站？该操作不可恢复。')) return
  try {
    await emptyTrash()
    page.value = 1
    success.value = '回收站已清空'
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
        <h3>回收站（{{ total + sets.length }}）</h3>
        <button class="btn danger" :disabled="!total && !sets.length" @click="clearAll">
          清空回收站
        </button>
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
              <th>图片数</th>
              <th>删除时间</th>
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
              <td data-label="图片数">{{ item.image_count }} 张</td>
              <td data-label="删除时间">{{ new Date(item.deleted_at).toLocaleString('zh-CN') }}</td>
              <td data-label="操作">
                <div class="row-actions">
                  <button class="mini-btn" @click="restoreSetItem(item.id)">恢复</button>
                  <button class="mini-btn danger" @click="purgeSetItem(item)">彻底删除</button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <div class="panel">
      <div class="panel-head">
        <h3>单图（{{ total }}）</h3>
      </div>
      <div class="table-wrap">
        <table class="data-table">
          <thead>
            <tr>
              <th>缩略图</th>
              <th>文件名</th>
              <th>分类</th>
              <th>删除时间</th>
              <th>操作</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="image in images" :key="image.id">
              <td data-label="缩略图">
                <img class="table-thumb" :src="thumbUrl(image.id)" :alt="image.filename" />
              </td>
              <td data-label="文件名">{{ image.filename }}</td>
              <td data-label="分类">{{ image.category_name || '未分类' }}</td>
              <td data-label="删除时间">{{ new Date(image.deleted_at).toLocaleString('zh-CN') }}</td>
              <td data-label="操作">
                <div class="row-actions">
                  <button class="mini-btn" @click="restore(image.id)">恢复</button>
                  <button class="mini-btn danger" @click="purge(image.id)">彻底删除</button>
                </div>
              </td>
            </tr>
            <tr v-if="!images.length && !loading">
              <td colspan="5">没有待处理的单图。</td>
            </tr>
            <tr v-if="loading">
              <td colspan="5">加载中…</td>
            </tr>
          </tbody>
        </table>
      </div>

      <Pagination :page="page" :total="total" :limit="PAGE_SIZE" @change="changePage" />
    </div>
  </div>
</template>
