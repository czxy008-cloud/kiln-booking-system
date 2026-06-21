<template>
  <footer class="app-footer">
    <div class="footer-inner">
      <p class="footer-text">🏺 陶艺工作室窑位预约与烧制记录系统</p>
      <p class="footer-sub">用心烧制每一件作品</p>
    </div>
  </footer>
</template>

<script setup>
</script>

<style lang="scss" scoped>
.app-footer {
  background: $color-surface;
  border-top: 1px solid $color-border;
  padding: $spacing-lg 0;
  margin-top: $spacing-xl;
}

.footer-inner {
  max-width: 1400px;
  margin: 0 auto;
  padding: 0 $spacing-lg;
  text-align: center;
}

.footer-text {
  color: $color-text-secondary;
  font-size: $font-size-sm;
  font-weight: 500;
}

.footer-sub {
  color: $color-text-muted;
  font-size: $font-size-xs;
  margin-top: $spacing-xs;
}
</style>
