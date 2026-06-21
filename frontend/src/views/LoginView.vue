<template>
  <div class="login-page">
    <div class="login-card">
      <div class="login-header">
        <div class="logo-icon">🏺</div>
        <h1 class="login-title">陶艺工作室</h1>
        <p class="login-subtitle">窑位预约与烧制记录系统</p>
      </div>

      <form class="login-form" @submit.prevent="handleLogin">
        <div class="form-group">
          <label>用户名</label>
          <input
            v-model="form.username"
            type="text"
            placeholder="请输入用户名"
            autocomplete="username"
          />
        </div>
        <div class="form-group">
          <label>密码</label>
          <input
            v-model="form.password"
            type="password"
            placeholder="请输入密码"
            autocomplete="current-password"
            @keyup.enter="handleLogin"
          />
        </div>

        <div v-if="errorMsg" class="error-box">
          ⚠️ {{ errorMsg }}
        </div>

        <button
          type="submit"
          class="btn btn-primary btn-lg login-btn"
          :disabled="loggingIn"
        >
          {{ loggingIn ? '登录中...' : '登 录' }}
        </button>
      </form>

      <div class="login-footer">
        <p>默认账号：<code>admin</code> / <code>admin123</code></p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()

const loggingIn = ref(false)
const errorMsg = ref('')

const form = ref({
  username: '',
  password: ''
})

onMounted(() => {
  if (authStore.isLoggedIn) {
    redirect()
  }
})

async function handleLogin() {
  errorMsg.value = ''
  if (!form.value.username.trim()) {
    errorMsg.value = '请输入用户名'
    return
  }
  if (!form.value.password.trim()) {
    errorMsg.value = '请输入密码'
    return
  }

  loggingIn.value = true
  try {
    await authStore.login(form.value.username, form.value.password)
    redirect()
  } catch (e) {
    errorMsg.value = e.response?.data?.detail || '登录失败，请检查用户名和密码'
  } finally {
    loggingIn.value = false
  }
}

function redirect() {
  const redirect = route.query.redirect || '/'
  router.replace(redirect)
}
</script>

<style lang="scss" scoped>
.login-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, $color-background 0%, $color-secondary 100%);
  padding: $spacing-lg;
}

.login-card {
  width: 100%;
  max-width: 400px;
  background: $color-surface;
  border-radius: $radius-xl;
  box-shadow: $shadow-lg;
  padding: $spacing-xxl $spacing-xl;
}

.login-header {
  text-align: center;
  margin-bottom: $spacing-xl;
}

.logo-icon {
  font-size: 56px;
  margin-bottom: $spacing-sm;
}

.login-title {
  font-size: $font-size-xxl;
  font-weight: 600;
  color: $color-text;
  margin-bottom: $spacing-xs;
}

.login-subtitle {
  font-size: $font-size-sm;
  color: $color-text-muted;
}

.login-form {
  margin-bottom: $spacing-lg;
}

.login-btn {
  width: 100%;
  margin-top: $spacing-md;
}

.login-footer {
  text-align: center;
  padding-top: $spacing-lg;
  border-top: 1px solid $color-border;

  p {
    font-size: $font-size-xs;
    color: $color-text-muted;

    code {
      background: $color-surface-alt;
      padding: 2px 6px;
      border-radius: $radius-sm;
      font-family: monospace;
    }
  }
}

.error-box {
  background: rgba($color-danger, 0.1);
  color: $color-danger;
  padding: $spacing-sm $spacing-md;
  border-radius: $radius-md;
  font-size: $font-size-sm;
  margin-bottom: $spacing-md;
}
</style>
