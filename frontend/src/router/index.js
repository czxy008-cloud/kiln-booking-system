import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const routes = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/LoginView.vue'),
    meta: { title: '登录', public: true }
  },
  {
    path: '/',
    name: 'Home',
    component: () => import('@/views/HomeView.vue'),
    meta: { title: '窑位日历', requiresAuth: true }
  },
  {
    path: '/bookings',
    name: 'Bookings',
    component: () => import('@/views/BookingCalendar.vue'),
    meta: { title: '窑位预约', requiresAuth: true }
  },
  {
    path: '/kilns',
    name: 'Kilns',
    component: () => import('@/views/KilnManage.vue'),
    meta: { title: '窑炉管理', requiresAuth: true }
  },
  {
    path: '/curves',
    name: 'FiringCurves',
    component: () => import('@/views/FiringCurves.vue'),
    meta: { title: '烧制曲线', requiresAuth: true }
  },
  {
    path: '/artworks',
    name: 'Artworks',
    component: () => import('@/views/ArtworkList.vue'),
    meta: { title: '作品追踪', requiresAuth: true }
  },
  {
    path: '/artworks/:qrCode',
    name: 'ArtworkDetail',
    component: () => import('@/views/ArtworkDetail.vue'),
    meta: { title: '作品进度', public: true }
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes,
  scrollBehavior() {
    return { top: 0 }
  }
})

router.beforeEach(async (to, _from, next) => {
  document.title = to.meta.title ? `${to.meta.title} · 陶艺工作室` : '陶艺工作室'

  const authStore = useAuthStore()

  if (to.meta.public) {
    return next()
  }

  if (to.meta.requiresAuth && !authStore.isLoggedIn) {
    return next({
      path: '/login',
      query: { redirect: to.fullPath }
    })
  }

  if (to.path === '/login' && authStore.isLoggedIn) {
    return next('/')
  }

  next()
})

export default router
