<template>
  <header class="app-header">
    <div class="header-inner">
      <router-link to="/" class="logo">
        <span class="logo-icon">🏺</span>
        <span class="logo-text">陶艺工作室</span>
      </router-link>
      <nav v-if="authStore.isLoggedIn" class="nav">
        <router-link to="/" class="nav-item" exact-active-class="active">
          <span>窑位日历</span>
        </router-link>
        <router-link to="/kilns" class="nav-item" active-class="active">
          <span>窑炉管理</span>
        </router-link>
        <router-link to="/curves" class="nav-item" active-class="active">
          <span>烧制曲线</span>
        </router-link>
        <router-link to="/artworks" class="nav-item" active-class="active">
          <span>作品追踪</span>
        </router-link>
      </nav>
      <div class="header-right">
        <div v-if="authStore.isLoggedIn" class="user-info">
          <span class="user-name">{{ authStore.userInfo?.full_name || authStore.userInfo?.username }}</span>
          <button class="btn btn-outline btn-sm logout-btn" @click="handleLogout">
            退出
          </button>
        </div>
        <router-link v-else to="/login" class="btn btn-primary btn-sm">
          登录
        </router-link>
        <button class="menu-toggle" @click="menuOpen = !menuOpen">
          <span v-if="!menuOpen">☰</span>
          <span v-else>✕</span>
        </button>
      </div>
    </div>
    <nav v-if="menuOpen && authStore.isLoggedIn" class="mobile-nav">
      <router-link to="/" class="nav-item" @click="menuOpen = false">窑位日历</router-link>
      <router-link to="/kilns" class="nav-item" @click="menuOpen = false">窑炉管理</router-link>
      <router-link to="/curves" class="nav-item" @click="menuOpen = false">烧制曲线</router-link>
      <router-link to="/artworks" class="nav-item" @click="menuOpen = false">作品追踪</router-link>
      <div class="mobile-user">
        <span>{{ authStore.userInfo?.full_name || authStore.userInfo?.username }}</span>
        <button class="btn btn-outline btn-sm" @click="handleLogout">退出登录</button>
      </div>
    </nav>
  </header>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const authStore = useAuthStore()
const menuOpen = ref(false)

function handleLogout() {
  authStore.logout()
  menuOpen.value = false
  router.push('/login')
}
</script>

<style lang="scss" scoped>
.app-header {
  background: $color-surface;
  border-bottom: 1px solid $color-border;
  position: sticky;
  top: 0;
  z-index: 100;
}

.header-inner {
  max-width: 1400px;
  margin: 0 auto;
  padding: 0 $spacing-lg;
  height: 64px;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.header-right {
  display: flex;
  align-items: center;
  gap: $spacing-sm;
}

.user-info {
  display: flex;
  align-items: center;
  gap: $spacing-sm;
}

.user-name {
  font-size: $font-size-sm;
  color: $color-text-secondary;
}

.logout-btn {
  margin-left: $spacing-xs;
}

.mobile-user {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: $spacing-md;
  border-top: 1px solid $color-border;
  margin-top: $spacing-sm;
  color: $color-text-secondary;
  font-size: $font-size-sm;
}

.logo {
  display: flex;
  align-items: center;
  gap: $spacing-sm;
  font-size: $font-size-xl;
  font-weight: 600;
  color: $color-text;

  &:hover {
    color: $color-primary;
  }
}

.logo-icon {
  font-size: 28px;
}

.nav {
  display: flex;
  gap: $spacing-xs;

  .nav-item {
    padding: $spacing-sm $spacing-md;
    color: $color-text-secondary;
    font-size: $font-size-sm;
    font-weight: 500;
    border-radius: $radius-md;
    transition: all $transition-fast;

    &:hover {
      background: $color-surface-alt;
      color: $color-primary;
    }
    &.active {
      background: rgba($color-primary, 0.1);
      color: $color-primary;
    }
  }
}

.menu-toggle {
  display: none;
  width: 40px;
  height: 40px;
  align-items: center;
  justify-content: center;
  font-size: 20px;
  color: $color-text;
  border-radius: $radius-md;

  &:hover {
    background: $color-surface-alt;
  }
}

.mobile-nav {
  display: none;
  flex-direction: column;
  padding: $spacing-sm;
  border-top: 1px solid $color-border;
  background: $color-surface;

  .nav-item {
    padding: $spacing-md;
    color: $color-text-secondary;
    border-radius: $radius-md;

    &:hover {
      background: $color-surface-alt;
      color: $color-primary;
    }
  }
}

@media (max-width: 768px) {
  .header-inner {
    padding: 0 $spacing-md;
  }
  .nav {
    display: none;
  }
  .user-info .user-name {
    display: none;
  }
  .menu-toggle {
    display: flex;
  }
  .mobile-nav {
    display: flex;
  }
}
</style>
