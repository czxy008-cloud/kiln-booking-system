<template>
  <header class="app-header">
    <div class="header-inner">
      <router-link to="/" class="logo">
        <span class="logo-icon">🏺</span>
        <span class="logo-text">陶艺工作室</span>
      </router-link>
      <nav class="nav">
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
      <button class="menu-toggle" @click="menuOpen = !menuOpen">
        <span v-if="!menuOpen">☰</span>
        <span v-else>✕</span>
      </button>
    </div>
    <nav v-if="menuOpen" class="mobile-nav">
      <router-link to="/" class="nav-item" @click="menuOpen = false">窑位日历</router-link>
      <router-link to="/kilns" class="nav-item" @click="menuOpen = false">窑炉管理</router-link>
      <router-link to="/curves" class="nav-item" @click="menuOpen = false">烧制曲线</router-link>
      <router-link to="/artworks" class="nav-item" @click="menuOpen = false">作品追踪</router-link>
    </nav>
  </header>
</template>

<script setup>
import { ref } from 'vue'
const menuOpen = ref(false)
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
  .menu-toggle {
    display: flex;
  }
  .mobile-nav {
    display: flex;
  }
}
</style>
