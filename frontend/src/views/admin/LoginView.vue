<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'

import { captchaUrl, login, logoUrl } from '../../api'
import { auth, loadSiteConfig, site } from '../../store'

const route = useRoute()
const router = useRouter()

const username = ref('')
const password = ref('')
const captcha = ref('')
const captchaTick = ref(0)
const submitting = ref(false)
const error = ref('')

const captchaSrc = computed(() => `${captchaUrl()}&_=${captchaTick.value}`)

function refreshCaptcha() {
  captchaTick.value += 1
  captcha.value = ''
}

async function submit() {
  if (submitting.value) return
  error.value = ''
  if (!username.value.trim() || !password.value) {
    error.value = '请输入用户名和密码'
    return
  }
  if (!/^\d{4}$/.test(captcha.value.trim())) {
    error.value = '请输入 4 位数字验证码'
    return
  }
  submitting.value = true
  try {
    const user = await login({
      username: username.value.trim(),
      password: password.value,
      captcha: captcha.value.trim()
    })
    auth.user = user
    auth.checked = true
    const redirect = typeof route.query.redirect === 'string' ? route.query.redirect : ''
    router.replace(redirect || '/admin/dashboard')
  } catch (err) {
    error.value = err.message
    refreshCaptcha()
  } finally {
    submitting.value = false
  }
}

onMounted(async () => {
  await loadSiteConfig()
})
</script>

<template>
  <div class="login-page">
    <form class="login-card" @submit.prevent="submit">
      <div class="login-brand">
        <span class="brand-mark">
          <img v-if="site.has_logo" :src="logoUrl()" alt="logo" />
          <svg v-else viewBox="0 0 24 24" width="20" height="20">
            <rect x="3" y="3" width="8" height="8" rx="2" fill="currentColor" />
            <rect x="13" y="3" width="8" height="8" rx="2" fill="currentColor" />
            <rect x="3" y="13" width="8" height="8" rx="2" fill="currentColor" />
            <rect x="13" y="13" width="8" height="8" rx="2" fill="currentColor" />
          </svg>
        </span>
        <div>
          <h1>{{ site.site_name }}</h1>
          <p>后台管理登录</p>
        </div>
      </div>

      <label class="login-field">
        <span>用户名</span>
        <input
          v-model="username"
          type="text"
          autocomplete="username"
          placeholder="请输入用户名"
          autofocus
        />
      </label>

      <label class="login-field">
        <span>密码</span>
        <input
          v-model="password"
          type="password"
          autocomplete="current-password"
          placeholder="请输入密码"
        />
      </label>

      <label class="login-field">
        <span>验证码</span>
        <div class="captcha-row">
          <input
            v-model="captcha"
            type="text"
            inputmode="numeric"
            maxlength="4"
            placeholder="4 位数字"
          />
          <button
            type="button"
            class="captcha-image"
            title="点击刷新验证码"
            @click="refreshCaptcha"
          >
            <img :src="captchaSrc" alt="验证码" />
          </button>
        </div>
      </label>

      <p v-if="error" class="error-text">{{ error }}</p>

      <button class="btn primary login-submit" type="submit" :disabled="submitting">
        {{ submitting ? '登录中…' : '登录' }}
      </button>

      <router-link class="login-back" to="/">返回图库</router-link>
    </form>
  </div>
</template>

<style scoped>
.login-page {
  min-height: 100dvh;
  display: grid;
  place-items: center;
  padding: 24px 18px;
  background: var(--mint-50);
}

.login-card {
  width: 100%;
  max-width: 380px;
  display: flex;
  flex-direction: column;
  gap: 16px;
  padding: 28px 24px 24px;
  background: var(--white);
  border: 1px solid var(--line);
  border-radius: 16px;
  box-shadow: var(--shadow-card);
}

.login-brand {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 4px;
}

.brand-mark {
  width: 42px;
  height: 42px;
  flex: 0 0 auto;
  border-radius: 12px;
  display: grid;
  place-items: center;
  background: var(--mint-500);
  color: #fff;
  overflow: hidden;
}

.brand-mark img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.login-brand h1 {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
  color: var(--ink-900);
}

.login-brand p {
  margin: 2px 0 0;
  font-size: 12px;
  color: var(--ink-300);
}

.login-field {
  display: flex;
  flex-direction: column;
  gap: 6px;
  font-size: 13px;
  color: var(--ink-700);
}

.login-field input {
  height: 42px;
  padding: 0 12px;
  border: 1px solid var(--line);
  border-radius: 10px;
  font-size: 14px;
  color: var(--ink-900);
  background: var(--white);
  transition: border-color 0.15s ease;
}

.login-field input:focus {
  border-color: var(--mint-500);
  outline: none;
}

.captcha-row {
  display: flex;
  gap: 10px;
}

.captcha-row input {
  flex: 1;
  min-width: 0;
  letter-spacing: 4px;
}

.captcha-image {
  flex: 0 0 auto;
  width: 120px;
  height: 42px;
  padding: 0;
  border: 1px solid var(--line);
  border-radius: 10px;
  overflow: hidden;
  background: var(--mint-50);
}

.captcha-image img {
  width: 100%;
  height: 100%;
  display: block;
  object-fit: cover;
}

.login-submit {
  height: 44px;
  margin-top: 4px;
  font-size: 15px;
}

.login-back {
  text-align: center;
  font-size: 13px;
  color: var(--ink-300);
  text-decoration: none;
}

.login-back:hover {
  color: var(--mint-600);
}
</style>
