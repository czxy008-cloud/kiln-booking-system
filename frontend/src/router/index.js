import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  {
    path: '/',
    name: 'Home',
    component: () => import('@/views/HomeView.vue'),
    meta: { title: '窑位日历' }
  },
  {
    path: '/bookings',
    name: 'Bookings',
    component: () => import('@/views/BookingCalendar.vue'),
    meta: { title: '窑位预约' }
  },
  {
    path: '/kilns',
    name: 'Kilns',
    component: () => import('@/views/KilnManage.vue'),
    meta: { title: '窑炉管理' }
  },
  {
    path: '/curves',
    name: 'FiringCurves',
    component: () => import('@/views/FiringCurves.vue'),
    meta: { title: '烧制曲线' }
  },
  {
    path: '/artworks',
    name: 'Artworks',
    component: () => import('@/views/ArtworkList.vue'),
    meta: { title: '作品追踪' }
  },
  {
    path: '/artworks/:qrCode',
    name: 'ArtworkDetail',
    component: () => import('@/views/ArtworkDetail.vue'),
    meta: { title: '作品进度' }
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes,
  scrollBehavior() {
    return { top: 0 }
  }
})

router.beforeEach((to, _from, next) => {
  document.title = to.meta.title ? `${to.meta.title} · 陶艺工作室` : '陶艺工作室'
  next()
})

export default router
