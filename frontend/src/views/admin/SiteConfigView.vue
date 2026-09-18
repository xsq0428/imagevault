<script setup>
import { onMounted, ref } from 'vue'

import {
  deleteLogo,
  fetchAdminSiteConfig,
  logoThumbUrl,
  updateAccount,
  updateSiteConfig,
  uploadLogo
} from '../../api'
import { auth, setSiteConfig } from '../../store'

const form = ref({
  site_name: '',
  site_tagline: '',
  site_description: '',
  site_keywords: '',
  footer_text: '',
  icp_number: '',
  page_size: 8,
  announcement_enabled: false,
  announcement_mode: 'topbar',
  announcement_text: ''
})

const hasLogo = ref(false)
const logoPlaceholder = ref('')
const logoInput = ref(null)
const logoBusy = ref(false)
const logoTick = ref(0)

const account = ref({ username: '', current_password: '', new_password: '', confirm: '' })

const busy = ref(false)
const accountBusy = ref(false)
const error = ref('')
const success = ref('')
const accountError = ref('')
const accountSuccess = ref('')

function applyConfig(config) {
    form.value = {
      site_name: config.site_name,
      site_tagline: config.site_tagline,
      site_description: config.site_description,
      site_keywords: config.site_keywords,
      footer_text: config.footer_text,
      icp_number: config.icp_number,
      page_size: config.page_size,
      announcement_enabled: config.announcement_enabled,
      announcement_mode: config.announcement_mode || 'topbar',
      announcement_text: config.announcement_text
    }
  hasLogo.value = config.has_logo
  logoPlaceholder.value = config.logo_placeholder || ''
}

async function load() {
  try {
    applyConfig(await fetchAdminSiteConfig())
  } catch (err) {
    error.value = err.message
  }
}

async function saveConfig() {
  if (busy.value) return
  busy.value = true
  error.value = ''
  success.value = ''
  try {
    const config = await updateSiteConfig({
      ...form.value,
      page_size: Number(form.value.page_size) || 1
    })
    applyConfig(config)
    setSiteConfig(config)
    success.value = '站点配置已保存'
  } catch (err) {
    error.value = err.message
  } finally {
    busy.value = false
  }
}

async function onPickLogo(event) {
  const file = event.target.files?.[0]
  event.target.value = ''
  if (!file) return
  logoBusy.value = true
  error.value = ''
  success.value = ''
  try {
    const config = await uploadLogo(file)
    applyConfig(config)
    setSiteConfig(config)
    logoTick.value += 1
    success.value = 'Logo 已更新'
  } catch (err) {
    error.value = err.message
  } finally {
    logoBusy.value = false
  }
}

async function removeLogo() {
  if (!window.confirm('确定移除当前 Logo？')) return
  logoBusy.value = true
  error.value = ''
  try {
    const config = await deleteLogo()
    applyConfig(config)
    setSiteConfig(config)
    logoTick.value += 1
    success.value = 'Logo 已移除'
  } catch (err) {
    error.value = err.message
  } finally {
    logoBusy.value = false
  }
}

async function saveAccount() {
  accountError.value = ''
  accountSuccess.value = ''
  const payload = {}
  if (account.value.username && account.value.username !== auth.user?.username) {
    payload.username = account.value.username.trim()
  }
  if (account.value.new_password) {
    if (account.value.new_password.length < 6) {
      accountError.value = '新密码至少 6 位'
      return
    }
    if (account.value.new_password !== account.value.confirm) {
      accountError.value = '两次输入的新密码不一致'
      return
    }
    payload.current_password = account.value.current_password
    payload.new_password = account.value.new_password
  }
  if (!Object.keys(payload).length) {
    accountError.value = '没有需要保存的修改'
    return
  }
  accountBusy.value = true
  try {
    const user = await updateAccount(payload)
    auth.user = user
    account.value = { username: user.username, current_password: '', new_password: '', confirm: '' }
    accountSuccess.value = '账号信息已更新'
  } catch (err) {
    accountError.value = err.message
  } finally {
    accountBusy.value = false
  }
}

onMounted(() => {
  account.value.username = auth.user?.username || ''
  load()
})
</script>

<template>
  <div>
    <div class="panel">
      <div class="panel-head">
        <h3>站点信息</h3>
        <span class="hint-text">作用于前台标题、SEO 与页脚</span>
      </div>

      <div class="form-inline">
        <div class="field">
          <label>站点名称</label>
          <input v-model="form.site_name" type="text" maxlength="64" placeholder="ImageVault" />
        </div>
        <div class="field">
          <label>站点标语</label>
          <input v-model="form.site_tagline" type="text" maxlength="128" placeholder="图片素材库" />
        </div>
      </div>

      <div class="field">
        <label>站点描述（SEO description）</label>
        <input v-model="form.site_description" type="text" maxlength="255" placeholder="一句话介绍站点" />
      </div>

      <div class="field">
        <label>关键词（SEO keywords，用英文逗号分隔）</label>
        <input v-model="form.site_keywords" type="text" maxlength="255" placeholder="图片,素材,图库" />
      </div>

      <div class="form-inline">
        <div class="field">
          <label>页脚版权</label>
          <input v-model="form.footer_text" type="text" maxlength="255" placeholder="© 2026 你的站点" />
        </div>
        <div class="field">
          <label>ICP 备案号</label>
          <input v-model="form.icp_number" type="text" maxlength="128" placeholder="京ICP备00000000号" />
        </div>
      </div>

      <div class="form-inline">
        <div class="field">
          <label>前台每页显示数量</label>
          <input v-model.number="form.page_size" type="number" min="1" max="60" />
        </div>
        <div class="field">
          <label>
            <span class="toggle-label">启用首页公告</span>
            <span class="toggle">
              <input v-model="form.announcement_enabled" type="checkbox" />
              <span class="toggle-track"></span>
            </span>
          </label>
        </div>
      </div>

      <div class="field" v-if="form.announcement_enabled">
        <label>公告展示方式</label>
        <select v-model="form.announcement_mode">
          <option value="topbar">顶栏横幅</option>
          <option value="modal">弹窗</option>
          <option value="inbox">站内信</option>
        </select>
      </div>

      <div class="field" v-if="form.announcement_enabled">
        <label>公告内容</label>
        <textarea
          v-model="form.announcement_text"
          rows="2"
          maxlength="500"
          placeholder="显示在首页顶部的通知文字"
        ></textarea>
      </div>

      <p v-if="error" class="error-text">{{ error }}</p>
      <p v-if="success" class="ok-text">{{ success }}</p>

      <div class="panel-head" style="margin: 14px 0 0">
        <span></span>
        <button class="btn primary" :disabled="busy" @click="saveConfig">
          {{ busy ? '保存中…' : '保存配置' }}
        </button>
      </div>
    </div>

    <div class="panel">
      <div class="panel-head">
        <h3>站点 Logo</h3>
        <span class="hint-text">建议使用正方形图片</span>
      </div>

      <div class="logo-row">
        <div class="logo-preview">
          <img
            v-if="hasLogo"
            :src="`${logoThumbUrl()}?t=${logoTick}`"
            alt="站点 Logo"
          />
          <span v-else class="logo-empty">无 Logo</span>
        </div>
        <div class="logo-actions">
          <input ref="logoInput" type="file" accept="image/*" hidden @change="onPickLogo" />
          <button class="btn" :disabled="logoBusy" @click="logoInput.click()">
            {{ logoBusy ? '处理中…' : hasLogo ? '更换 Logo' : '上传 Logo' }}
          </button>
          <button v-if="hasLogo" class="btn danger" :disabled="logoBusy" @click="removeLogo">
            移除
          </button>
        </div>
      </div>
    </div>

    <div class="panel">
      <div class="panel-head">
        <h3>管理员账号</h3>
        <span class="hint-text">留空表示不修改</span>
      </div>

      <div class="field">
        <label>用户名</label>
        <input v-model="account.username" type="text" maxlength="64" autocomplete="username" />
      </div>

      <div class="form-inline">
        <div class="field">
          <label>当前密码</label>
          <input
            v-model="account.current_password"
            type="password"
            autocomplete="current-password"
            placeholder="修改密码时必填"
          />
        </div>
        <div class="field">
          <label>新密码</label>
          <input
            v-model="account.new_password"
            type="password"
            autocomplete="new-password"
            placeholder="至少 6 位"
          />
        </div>
        <div class="field">
          <label>确认新密码</label>
          <input
            v-model="account.confirm"
            type="password"
            autocomplete="new-password"
            placeholder="再次输入新密码"
          />
        </div>
      </div>

      <p v-if="accountError" class="error-text">{{ accountError }}</p>
      <p v-if="accountSuccess" class="ok-text">{{ accountSuccess }}</p>

      <div class="panel-head" style="margin: 14px 0 0">
        <span></span>
        <button class="btn primary" :disabled="accountBusy" @click="saveAccount">
          {{ accountBusy ? '保存中…' : '保存账号' }}
        </button>
      </div>
    </div>
  </div>
</template>

<style scoped>
.logo-row {
  display: flex;
  align-items: center;
  gap: 18px;
  flex-wrap: wrap;
}

.logo-preview {
  width: 84px;
  height: 84px;
  border: 1px solid var(--line);
  border-radius: 12px;
  display: grid;
  place-items: center;
  overflow: hidden;
  background: var(--mint-50);
}

.logo-preview img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.logo-empty {
  font-size: 12px;
  color: var(--ink-300);
}

.logo-actions {
  display: flex;
  gap: 10px;
}

.ok-text {
  color: var(--mint-600);
  font-size: 13px;
  margin-top: 10px;
}

.toggle-label {
  margin-left: 8px;
  font-size: 13px;
  color: var(--ink-700);
}

.toggle {
  position: relative;
  display: inline-block;
  width: 36px;
  height: 20px;
  flex-shrink: 0;
}

.toggle input {
  opacity: 0;
  width: 0;
  height: 0;
  position: absolute;
}

.toggle-track {
  position: absolute;
  inset: 0;
  border-radius: 999px;
  background: var(--line);
  border: 1px solid var(--line);
  transition: background 0.15s ease, border-color 0.15s ease;
  cursor: pointer;
}

.toggle input:checked + .toggle-track {
  background: var(--mint-500);
  border-color: var(--mint-500);
}

.toggle-track::after {
  content: '';
  position: absolute;
  top: 2px;
  left: 2px;
  width: 14px;
  height: 14px;
  border-radius: 50%;
  background: var(--white);
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.15);
  transition: transform 0.15s ease;
  pointer-events: none;
}

.toggle input:checked + .toggle-track::after {
  transform: translateX(16px);
}

.toggle:hover .toggle-track {
  border-color: var(--mint-400);
}

.toggle input:focus-visible + .toggle-track {
  outline: 2px solid var(--mint-500);
  outline-offset: 2px;
}
</style>
