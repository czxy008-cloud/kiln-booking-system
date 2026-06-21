<template>
  <div class="page-container">
    <div class="page-header">
      <div>
        <h1>🏺 窑位日历</h1>
        <p class="subtitle">可视化查看各窑炉本周预约情况，支持拖拽调整</p>
      </div>
      <div class="header-actions">
        <button class="btn btn-outline btn-sm" @click="changeWeek(-1)">← 上周</button>
        <button class="btn btn-secondary btn-sm" @click="goToday">今天</button>
        <button class="btn btn-outline btn-sm" @click="changeWeek(1)">下周 →</button>
        <button class="btn btn-primary" @click="openCreateBooking">
          <span>+</span> 新建预约
        </button>
      </div>
    </div>

    <div class="week-nav">
      <h2 class="week-title">{{ weekTitle }}</h2>
    </div>

    <div v-if="loading" class="empty-state">
      <div class="empty-icon">⏳</div>
      <div class="empty-text">加载中...</div>
    </div>
    <div v-else-if="kilns.length === 0" class="empty-state">
      <div class="empty-icon">🏚️</div>
      <div class="empty-text">暂无窑炉，请先在窑炉管理中添加</div>
    </div>
    <div v-else class="calendar-grid">
      <div class="calendar-header">
        <div class="time-label">窑炉 \ 时间</div>
        <div v-for="(day, idx) in weekDays" :key="idx" class="day-header" :class="{ today: isToday(day.date) }">
          <div class="day-name">{{ day.weekday }}</div>
          <div class="day-date">{{ day.dateStr }}</div>
        </div>
      </div>
      <div v-for="kiln in kilns" :key="kiln.id" class="calendar-row">
        <div class="kiln-label">
          <div class="kiln-name">{{ kiln.name }}</div>
          <div class="kiln-capacity">{{ kiln.capacity || '—' }}</div>
        </div>
        <div v-for="(day, dayIdx) in weekDays" :key="dayIdx" class="day-cell" @click="handleCellClick(kiln, day)">
          <div
            v-for="booking in getDayBookings(kiln.id, day.date)"
            :key="booking.id"
            class="booking-block"
            :class="getStatusClass(booking.status)"
            draggable="true"
            @dragstart="onDragStart($event, booking)"
            @dragover.prevent
            @drop="onDrop($event, kiln, day)"
            @click.stop="openEditBooking(booking)"
            :style="getBookingStyle(booking, day)"
          >
            <div class="booking-title">{{ booking.title }}</div>
            <div class="booking-time">{{ formatTime(booking.start_time) }} - {{ formatTime(booking.end_time) }}</div>
            <div class="booking-booker">{{ booking.booker_name }}</div>
          </div>
        </div>
      </div>
    </div>

    <BookingModal
      v-if="showBookingModal"
      :booking="editingBooking"
      :kilns="kilns"
      :curves="firingCurves"
      @close="showBookingModal = false"
      @saved="onBookingSaved"
      @conflict="showConflictMessage"
    />

    <div v-if="conflictMessage" class="conflict-toast" @click="conflictMessage = ''">
      <span>⚠️ {{ conflictMessage }}</span>
      <button class="toast-close">×</button>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import dayjs from 'dayjs'
import 'dayjs/locale/zh-cn'
import api from '@/api'
import BookingModal from '@/components/BookingModal.vue'

dayjs.locale('zh-cn')

const loading = ref(true)
const weekData = ref({})
const kilns = ref([])
const firingCurves = ref([])
const currentWeekStart = ref(dayjs().startOf('week'))
const showBookingModal = ref(false)
const editingBooking = ref(null)
const dragBooking = ref(null)
const conflictMessage = ref('')

const weekDays = computed(() => {
  const days = []
  for (let i = 0; i < 7; i++) {
    const d = currentWeekStart.value.add(i, 'day')
    days.push({
      date: d,
      dateStr: d.format('MM/DD'),
      weekday: d.format('dddd').replace('星期', '周')
    })
  }
  return days
})

const weekTitle = computed(() => {
  const start = currentWeekStart.value
  const end = currentWeekStart.value.add(6, 'day')
  return `${start.format('YYYY年MM月DD日')} - ${end.format('MM月DD日')}`
})

function isToday(date) {
  return dayjs().isSame(date, 'day')
}

function formatTime(isoStr) {
  return dayjs(isoStr).format('HH:mm')
}

function getStatusClass(status) {
  const map = {
    pending: 'status-pending',
    confirmed: 'status-confirmed',
    in_progress: 'status-progress',
    completed: 'status-completed',
    cancelled: 'status-cancelled'
  }
  return map[status] || 'status-pending'
}

function getDayBookings(kilnId, dayDate) {
  const kilnData = weekData.value[String(kilnId)]
  if (!kilnData) return []
  const dayStart = dayDate.startOf('day')
  const dayEnd = dayDate.endOf('day')
  return kilnData.bookings.filter(b => {
    const s = dayjs(b.start_time)
    const e = dayjs(b.end_time)
    return s.isBefore(dayEnd) && e.isAfter(dayStart)
  })
}

function getBookingStyle(booking, day) {
  const dayStart = day.date.startOf('day')
  const dayEnd = day.date.endOf('day')
  const bStart = dayjs(booking.start_time)
  const bEnd = dayjs(booking.end_time)

  const effectiveStart = bStart.isAfter(dayStart) ? bStart : dayStart
  const effectiveEnd = bEnd.isBefore(dayEnd) ? bEnd : dayEnd

  const startMinutes = effectiveStart.diff(dayStart, 'minute')
  const durationMinutes = effectiveEnd.diff(effectiveStart, 'minute')

  const topPct = (startMinutes / (24 * 60)) * 100
  const heightPct = (durationMinutes / (24 * 60)) * 100

  return {
    top: `${topPct}%`,
    height: `${Math.max(heightPct, 6)}%`
  }
}

async function fetchWeekData() {
  loading.value = true
  try {
    const params = { date: currentWeekStart.value.toISOString() }
    const res = await api.get('/bookings/week', { params })
    weekData.value = res.data
    kilns.value = Object.values(res.data).map(v => v.kiln)
  } catch (e) {
    console.error(e)
  } finally {
    loading.value = false
  }
}

async function fetchCurves() {
  try {
    const res = await api.get('/firing-curves')
    firingCurves.value = res.data
  } catch (e) {
    console.error(e)
  }
}

function changeWeek(delta) {
  currentWeekStart.value = currentWeekStart.value.add(delta, 'week')
  fetchWeekData()
}

function goToday() {
  currentWeekStart.value = dayjs().startOf('week')
  fetchWeekData()
}

function openCreateBooking() {
  editingBooking.value = null
  showBookingModal.value = true
}

function openEditBooking(booking) {
  editingBooking.value = { ...booking }
  showBookingModal.value = true
}

function handleCellClick(kiln, day) {
  editingBooking.value = {
    kiln_id: kiln.id,
    start_time: day.date.hour(9).minute(0).toISOString(),
    end_time: day.date.hour(18).minute(0).toISOString()
  }
  showBookingModal.value = true
}

function onDragStart(e, booking) {
  dragBooking.value = booking
  e.dataTransfer.effectAllowed = 'move'
}

async function onDrop(e, kiln, day) {
  if (!dragBooking.value) return
  const booking = dragBooking.value
  const originalStart = dayjs(booking.start_time)
  const originalEnd = dayjs(booking.end_time)
  const duration = originalEnd.diff(originalStart, 'minute')

  const newStart = day.date.hour(originalStart.hour()).minute(originalStart.minute())
  const newEnd = newStart.add(duration, 'minute')

  try {
    await api.put(`/bookings/${booking.id}`, {
      kiln_id: kiln.id,
      start_time: newStart.toISOString(),
      end_time: newEnd.toISOString()
    })
    await fetchWeekData()
  } catch (e) {
    const msg = e.response?.data?.detail || '更新预约失败'
    showConflictMessage(msg)
  }
  dragBooking.value = null
}

function onBookingSaved() {
  showBookingModal.value = false
  fetchWeekData()
}

function showConflictMessage(msg) {
  conflictMessage.value = msg
  setTimeout(() => { conflictMessage.value = '' }, 5000)
}

onMounted(() => {
  fetchWeekData()
  fetchCurves()
})
</script>

<style lang="scss" scoped>
.header-actions {
  display: flex;
  gap: $spacing-sm;
  align-items: center;
}

.week-nav {
  margin-bottom: $spacing-md;
  text-align: center;
}
.week-title {
  font-size: $font-size-lg;
  font-weight: 500;
  color: $color-text-secondary;
}

.calendar-grid {
  background: $color-surface;
  border-radius: $radius-lg;
  box-shadow: $shadow-sm;
  overflow: auto;
}

.calendar-header {
  display: grid;
  grid-template-columns: 140px repeat(7, 1fr);
  background: $color-surface-alt;
  border-bottom: 1px solid $color-border;
  position: sticky;
  top: 0;
  z-index: 10;
}

.time-label, .day-header, .kiln-label {
  padding: $spacing-md;
  border-right: 1px solid $color-border;
  text-align: center;
}

.time-label {
  font-weight: 600;
  color: $color-text-secondary;
  font-size: $font-size-sm;
  display: flex;
  align-items: center;
  justify-content: center;
}

.day-header {
  .day-name {
    font-size: $font-size-sm;
    font-weight: 600;
    color: $color-text-secondary;
  }
  .day-date {
    font-size: $font-size-xs;
    color: $color-text-muted;
    margin-top: 2px;
  }
  &.today {
    background: rgba($color-primary, 0.08);
    .day-name, .day-date {
      color: $color-primary;
      font-weight: 600;
    }
  }
}

.calendar-row {
  display: grid;
  grid-template-columns: 140px repeat(7, 1fr);
  border-bottom: 1px solid $color-border;
  &:last-child {
    border-bottom: none;
  }
}

.kiln-label {
  background: $color-surface-alt;
  text-align: left;
  position: sticky;
  left: 0;
  z-index: 5;
  .kiln-name {
    font-weight: 600;
    color: $color-text;
    font-size: $font-size-sm;
  }
  .kiln-capacity {
    font-size: $font-size-xs;
    color: $color-text-muted;
    margin-top: 2px;
  }
}

.day-cell {
  position: relative;
  min-height: 200px;
  border-right: 1px solid $color-border;
  padding: 2px;
  background: linear-gradient(180deg, transparent 0%, transparent calc(100% / 24 - 1px), rgba(0,0,0,0.03) calc(100% / 24));
  background-size: 100% calc(100% / 24);
  cursor: pointer;
  transition: background $transition-fast;
  &:hover {
    background-color: rgba($color-primary, 0.04);
  }
  &:last-child {
    border-right: none;
  }
}

.booking-block {
  position: absolute;
  left: 4px;
  right: 4px;
  border-radius: $radius-sm;
  padding: $spacing-xs $spacing-sm;
  overflow: hidden;
  cursor: grab;
  font-size: $font-size-xs;
  transition: transform $transition-fast, box-shadow $transition-fast;

  &:hover {
    transform: translateY(-1px);
    box-shadow: $shadow-md;
    z-index: 2;
  }
  &:active {
    cursor: grabbing;
  }

  .booking-title {
    font-weight: 600;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
    color: #fff;
  }
  .booking-time {
    font-size: 11px;
    opacity: 0.9;
    color: #fff;
    margin-top: 1px;
  }
  .booking-booker {
    font-size: 11px;
    opacity: 0.85;
    color: #fff;
  }

  &.status-pending {
    background: linear-gradient(135deg, $color-warning, darken($color-warning, 10%));
  }
  &.status-confirmed {
    background: linear-gradient(135deg, $color-primary, $color-primary-dark);
  }
  &.status-progress {
    background: linear-gradient(135deg, $color-info, darken($color-info, 10%));
  }
  &.status-completed {
    background: linear-gradient(135deg, $color-success, darken($color-success, 10%));
  }
  &.status-cancelled {
    background: linear-gradient(135deg, $color-text-muted, darken($color-text-muted, 15%));
    opacity: 0.7;
  }
}

.conflict-toast {
  position: fixed;
  top: 80px;
  right: $spacing-lg;
  background: $color-danger;
  color: #fff;
  padding: $spacing-md $spacing-lg;
  border-radius: $radius-md;
  box-shadow: $shadow-lg;
  z-index: 1000;
  display: flex;
  align-items: center;
  gap: $spacing-md;
  max-width: 400px;
  animation: slideIn 0.3s ease;

  .toast-close {
    background: none;
    color: #fff;
    font-size: 20px;
    line-height: 1;
    opacity: 0.8;
    &:hover { opacity: 1; }
  }
}

@keyframes slideIn {
  from { transform: translateX(100%); opacity: 0; }
  to { transform: translateX(0); opacity: 1; }
}

@media (max-width: 768px) {
  .calendar-grid {
    font-size: $font-size-xs;
  }
  .calendar-header, .calendar-row {
    grid-template-columns: 80px repeat(7, 1fr);
  }
  .time-label, .day-header, .kiln-label {
    padding: $spacing-sm $spacing-xs;
  }
  .kiln-name {
    font-size: $font-size-xs;
  }
  .booking-block {
    padding: 2px 4px;
    .booking-booker { display: none; }
    .booking-time { display: none; }
  }
}
</style>
