const BASE = '/api'

async function request(url, options = {}) {
  const response = await fetch(`${BASE}${url}`, options)
  if (!response.ok) {
    let detail = `请求失败 (${response.status})`
    try {
      const body = await response.json()
      if (body.detail) detail = body.detail
    } catch {
      /* keep default message */
    }
    throw new Error(detail)
  }
  if (response.status === 204) return null
  return response.json()
}

export function fetchImages({ q = '', tag = '', categoryId = null, page = 1, limit = 8 } = {}) {
  const params = new URLSearchParams()
  if (q) params.set('q', q)
  if (tag) params.set('tag', tag)
  if (categoryId !== null && categoryId !== undefined && categoryId !== '') {
    params.set('category_id', categoryId)
  }
  params.set('page', page)
  params.set('limit', limit)
  return request(`/images?${params.toString()}`)
}

export function fetchFeed({ q = '', categoryId = null, page = 1, limit = 8 } = {}) {
  const params = new URLSearchParams()
  if (q) params.set('q', q)
  if (categoryId !== null && categoryId !== undefined && categoryId !== '') {
    params.set('category_id', categoryId)
  }
  params.set('page', page)
  params.set('limit', limit)
  return request(`/feed?${params.toString()}`)
}

export function fetchTags() {
  return request('/tags')
}

export function fetchStats() {
  return request('/stats')
}

export function fetchCategories() {
  return request('/categories')
}

export function createCategory(payload) {
  return request('/categories', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload)
  })
}

export function updateCategory(id, payload) {
  return request(`/categories/${id}`, {
    method: 'PATCH',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload)
  })
}

export function deleteCategory(id) {
  return request(`/categories/${id}`, { method: 'DELETE' })
}

export function uploadCategoryCover(id, file) {
  const form = new FormData()
  form.append('file', file)
  return request(`/categories/${id}/cover`, { method: 'POST', body: form })
}

export function deleteCategoryCover(id) {
  return request(`/categories/${id}/cover`, { method: 'DELETE' })
}

export function categoryCoverThumbUrl(id) {
  return `${BASE}/categories/${id}/cover-thumb`
}

export function categoryCoverUrl(id) {
  return `${BASE}/categories/${id}/cover`
}

export function fetchSets() {
  return request('/sets')
}

export function fetchSet(id) {
  return request(`/sets/${id}`)
}

export function createSet(files, { title = '', description = '', categoryId = null, tags = [] } = {}) {
  const form = new FormData()
  for (const file of files) form.append('files', file)
  form.append('title', title)
  form.append('description', description)
  form.append('tags', tags.join(','))
  if (categoryId !== null && categoryId !== undefined && categoryId !== '') {
    form.append('category_id', categoryId)
  }
  return request('/sets', { method: 'POST', body: form })
}

export function updateSet(id, payload) {
  return request(`/sets/${id}`, {
    method: 'PATCH',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload)
  })
}

export function deleteSet(id) {
  return request(`/sets/${id}`, { method: 'DELETE' })
}

export function restoreSet(id) {
  return request(`/sets/${id}/restore`, { method: 'POST' })
}

export function purgeSet(id) {
  return request(`/sets/${id}/purge`, { method: 'DELETE' })
}

export function fetchTrashSets() {
  return request('/sets/trash')
}

export function fetchBanners({ includeInactive = false } = {}) {
  return request(`/banners?include_inactive=${includeInactive}`)
}

export function uploadBanners(files, { title = '', link = '' } = {}) {
  const form = new FormData()
  for (const file of files) form.append('files', file)
  form.append('title', title)
  form.append('link', link)
  return request('/banners', { method: 'POST', body: form })
}

export function updateBanner(id, payload) {
  return request(`/banners/${id}`, {
    method: 'PATCH',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload)
  })
}

export function deleteBanner(id) {
  return request(`/banners/${id}`, { method: 'DELETE' })
}

export function fetchTrash({ page = 1, limit = 12 } = {}) {
  return request(`/images/trash?page=${page}&limit=${limit}`)
}

export function uploadImages(files, { tags = [], categoryId = null, description = '' } = {}) {
  const form = new FormData()
  for (const file of files) form.append('files', file)
  form.append('tags', tags.join(','))
  if (categoryId !== null && categoryId !== undefined && categoryId !== '') {
    form.append('category_id', categoryId)
  }
  form.append('description', description)
  return request('/images', { method: 'POST', body: form })
}

export function updateImage(id, payload) {
  return request(`/images/${id}`, {
    method: 'PATCH',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload)
  })
}

export function deleteImage(id) {
  return request(`/images/${id}`, { method: 'DELETE' })
}

export function deleteImages(ids) {
  return request('/images/batch-delete', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ ids })
  })
}

export function moveImages(ids, categoryId) {
  return request('/images/batch-move', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ ids, category_id: categoryId })
  })
}

export function restoreImage(id) {
  return request(`/images/${id}/restore`, { method: 'POST' })
}

export function purgeImage(id) {
  return request(`/images/${id}/purge`, { method: 'DELETE' })
}

export function emptyTrash() {
  return request('/trash/empty', { method: 'POST' })
}

export const originalUrl = (id) => `${BASE}/media/original/${id}`
export const thumbUrl = (id) => `${BASE}/media/thumb/${id}`
export const bannerUrl = (id) => `${BASE}/media/banner/${id}`
export const bannerThumbUrl = (id) => `${BASE}/media/banner-thumb/${id}`
