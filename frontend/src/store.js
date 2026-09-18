import { reactive } from 'vue'

import { fetchMe, fetchSiteConfig, logout as apiLogout } from './api'

export const auth = reactive({
  user: null,
  checked: false
})

export async function ensureAuth(force = false) {
  if (auth.checked && !force) return auth.user
  try {
    auth.user = await fetchMe()
  } catch {
    auth.user = null
  }
  auth.checked = true
  return auth.user
}

export function markUnauthorized() {
  auth.user = null
  auth.checked = true
}

export async function signOut() {
  try {
    await apiLogout()
  } catch {
    /* ignore network errors on logout */
  }
  auth.user = null
  auth.checked = true
}

const DEFAULTS = {
  site_name: 'ImageVault',
  site_tagline: '图片素材库',
  site_description: '',
  site_keywords: '',
  footer_text: '',
  icp_number: '',
  logo_placeholder: '',
  has_logo: false,
  page_size: 8,
  announcement_enabled: false,
  announcement_mode: 'topbar',
  announcement_text: ''
}

export const site = reactive({ ...DEFAULTS, loaded: false })

function applyDocumentMeta() {
  if (typeof document === 'undefined') return
  document.title = site.site_tagline
    ? `${site.site_name} · ${site.site_tagline}`
    : site.site_name

  const setMeta = (name, content) => {
    if (content) {
      let tag = document.querySelector(`meta[name="${name}"]`)
      if (!tag) {
        tag = document.createElement('meta')
        tag.setAttribute('name', name)
        document.head.appendChild(tag)
      }
      tag.setAttribute('content', content)
    }
  }
  setMeta('description', site.site_description)
  setMeta('keywords', site.site_keywords)
}

export async function loadSiteConfig(force = false) {
  if (site.loaded && !force) return site
  try {
    Object.assign(site, await fetchSiteConfig())
  } catch {
    /* keep defaults when backend is unavailable */
  }
  site.loaded = true
  applyDocumentMeta()
  return site
}

export function setSiteConfig(data) {
  Object.assign(site, data)
  applyDocumentMeta()
}

export const notif = reactive({ open: false })

export function setNotifOpen(open) {
  notif.open = open
}
