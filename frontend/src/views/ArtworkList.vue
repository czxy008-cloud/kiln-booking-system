<template>
  <div class="page-container">
    <div class="page-header">
      <div>
        <h1>🎨 作品追踪</h1>
        <p class="subtitle">追踪每件作品从入窑到出窑的完整生命周期</p>
      </div>
      <div class="header-actions">
        <button class="btn btn-primary" @click="openCreate">
          <span>+</span> 登记作品
        </button>
      </div>
    </div>

    <div class="filter-bar">
      <div class="filter-item">
        <input v-model="searchName" type="text" placeholder="搜索学员姓名..." class="filter-input" />
      </div>
      <div class="filter-item">
        <select v-model="stageFilter" class="filter-select">
          <option value="">全部阶段</option>
          <option v-for="s in stageOptions" :key="s.key" :value="s.key">{{ s.name }}</option>
        </select>
      </div>
    </div>

    <div v-if="loading" class="empty-state">
      <div class="empty-icon">⏳</div>
      <div class="empty-text">加载中...</div>
    </div>
    <div v-else-if="filteredArtworks.length === 0" class="empty-state">
      <div class="empty-icon">🖼️</div>
      <div class="empty-text">暂无作品记录</div>
    </div>
    <div v-else class="artwork-grid">
      <div
        v-for="art in filteredArtworks"
        :key="art.id"
        class="artwork-card card"
        @click="openDetail(art)"
      >
        <div class="artwork-header">
          <h3 class="artwork-title">{{ art.title }}</h3>
          <span class="badge" :class="stageBadgeClass(art.current_stage)">
            {{ getStageName(art.current_stage) }}
          </span>
        </div>
        <div class="artwork-info">
          <div class="info-row">
            <span class="label">学员</span>
            <span class="value">{{ art.student_name }}</span>
          </div>
          <div class="info-row" v-if="art.clay_type">
            <span class="label">泥料</span>
            <span class="value tag">{{ art.clay_type }}</span>
          </div>
          <div class="info-row">
            <span class="label">编号</span>
            <span class="value code">{{ art.qr_code }}</span>
          </div>
        </div>

        <div class="progress-bar">
          <div
            v-for="(s, idx) in stageOptions"
            :key="s.key"
            class="progress-step"
            :class="getStepClass(art, s.key, idx)"
          >
            <div class="step-dot"></div>
          </div>
        </div>
        <div class="progress-labels">
          <span>{{ getStageName(art.current_stage) }}</span>
          <span>{{ calculateProgress(art) }}%</span>
        </div>

        <div class="artwork-footer">
          <span class="update-time">{{ formatDate(art.updated_at) }}</span>
          <button
            class="btn btn-outline btn-sm"
            @click.stop="showQR(art)"
          >二维码</button>
        </div>
      </div>
    </div>

    <div v-if="showCreateModal" class="modal-overlay" @click.self="showCreateModal = false">
      <div class="modal">
        <div class="modal-header">
          <h3>登记新作品</h3>
          <button class="modal-close" @click="showCreateModal = false">×</button>
        </div>
        <div class="modal-body">
          <div class="form-group">
            <label>作品名称 *</label>
            <input v-model="form.title" type="text" placeholder="如：青花茶盏" />
          </div>
          <div class="form-row">
            <div class="form-group">
              <label>学员姓名 *</label>
              <input v-model="form.student_name" type="text" />
            </div>
            <div class="form-group">
              <label>泥料类型</label>
              <select v-model="form.clay_type">
                <option value="">请选择</option>
                <option v-for="t in clayTypes" :key="t" :value="t">{{ t }}</option>
              </select>
            </div>
          </div>
          <div class="form-group">
            <label>关联预约</label>
            <select v-model="form.booking_id">
              <option :value="null">暂不关联</option>
              <option v-for="b in bookings" :key="b.id" :value="b.id">
                {{ b.title }} ({{ formatDate(b.start_time) }})
              </option>
            </select>
          </div>
          <div class="form-group">
            <label>作品描述</label>
            <textarea v-model="form.description" placeholder="作品尺寸、特点、创作思路等"></textarea>
          </div>
          <div v-if="errorMsg" class="error-box">⚠️ {{ errorMsg }}</div>
        </div>
        <div class="modal-footer">
          <button class="btn btn-secondary" @click="showCreateModal = false" :disabled="saving">取消</button>
          <button class="btn btn-primary" @click="saveArtwork" :disabled="saving">{{ saving ? '保存中...' : '登记' }}</button>
        </div>
      </div>
    </div>

    <div v-if="qrArtwork" class="modal-overlay" @click.self="qrArtwork = null">
      <div class="modal qr-modal">
        <div class="modal-header">
          <h3>作品二维码</h3>
          <button class="modal-close" @click="qrArtwork = null">×</button>
        </div>
        <div class="modal-body qr-body">
          <div class="qr-info">
            <h4>{{ qrArtwork.title }}</h4>
            <p>学员：{{ qrArtwork.student_name }}</p>
            <p class="qr-code-text">编号：{{ qrArtwork.qr_code }}</p>
          </div>
          <img :src="`/api/artworks/${qrArtwork.id}/qrcode`" alt="二维码" class="qr-image" />
          <p class="qr-hint">学员扫码即可查看作品烧制进程</p>
          <button
            class="btn btn-outline"
            @click="goToDetail(qrArtwork)"
          >查看详情 →</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import dayjs from 'dayjs'
import api from '@/api'

const router = useRouter()
const loading = ref(true)
const saving = ref(false)
const artworks = ref([])
const bookings = ref([])
const searchName = ref('')
const stageFilter = ref('')
const showCreateModal = ref(false)
const qrArtwork = ref(null)
const errorMsg = ref('')

const clayTypes = ['高白泥', '紫砂', '瓷泥', '陶泥', '粗陶', '炻器', '其他']
const stageOptions = [
  { key: 'drying', name: '入窑前干燥' },
  { key: 'pre_heating', name: '预热阶段' },
  { key: 'bisque_firing', name: '素烧阶段' },
  { key: 'glazing', name: '施釉阶段' },
  { key: 'glaze_firing', name: '釉烧阶段' },
  { key: 'cooling', name: '出窑冷却' },
  { key: 'completed', name: '烧制完成' }
]

const defaultForm = () => ({
  title: '',
  student_name: '',
  clay_type: '',
  booking_id: null,
  description: ''
})
const form = ref(defaultForm())

const filteredArtworks = computed(() => {
  return artworks.value.filter(a => {
    if (searchName.value && !a.student_name.includes(searchName.value)) return false
    if (stageFilter.value && a.current_stage !== stageFilter.value) return false
    return true
  })
})

function formatDate(iso) {
  return dayjs(iso).format('YYYY-MM-DD HH:mm')
}

function getStageName(key) {
  return stageOptions.find(s => s.key === key)?.name || key
}

function stageBadgeClass(key) {
  if (key === 'completed') return 'badge-success'
  if (key === 'drying') return 'badge-info'
  if (key === 'cooling') return 'badge-warning'
  return 'badge-default'
}

function getStepClass(art, stageKey, idx) {
  const currentIdx = stageOptions.findIndex(s => s.key === art.current_stage)
  if (idx < currentIdx) return 'step-done'
  if (idx === currentIdx) return 'step-current'
  return 'step-pending'
}

function calculateProgress(art) {
  const currentIdx = stageOptions.findIndex(s => s.key === art.current_stage)
  if (currentIdx < 0) return 0
  return Math.round((currentIdx / (stageOptions.length - 1)) * 100)
}

async function fetchArtworks() {
  loading.value = true
  try {
    const res = await api.get('/artworks')
    artworks.value = res.data
  } catch (e) {
    console.error(e)
  } finally {
    loading.value = false
  }
}

async function fetchBookings() {
  try {
    const res = await api.get('/bookings', {
      params: { status: ['pending', 'confirmed', 'in_progress'] },
      paramsSerializer: { indexes: null }
    })
    bookings.value = res.data
  } catch (e) {
    console.error('获取预约列表失败:', e)
  }
}

function openCreate() {
  form.value = defaultForm()
  errorMsg.value = ''
  showCreateModal.value = true
}

async function saveArtwork() {
  errorMsg.value = ''
  if (!form.value.title.trim()) { errorMsg.value = '请填写作品名称'; return }
  if (!form.value.student_name.trim()) { errorMsg.value = '请填写学员姓名'; return }

  saving.value = true
  try {
    await api.post('/artworks', form.value)
    showCreateModal.value = false
    await fetchArtworks()
  } catch (e) {
    errorMsg.value = e.response?.data?.detail || '保存失败'
  } finally {
    saving.value = false
  }
}

function showQR(art) {
  qrArtwork.value = art
}

function openDetail(art) {
  router.push(`/artworks/${art.qr_code}`)
}
function goToDetail(art) {
  qrArtwork.value = null
  router.push(`/artworks/${art.qr_code}`)
}

onMounted(() => {
  fetchArtworks()
  fetchBookings()
})
</script>

<style lang="scss" scoped>
.header-actions { display: flex; gap: $spacing-sm; }

.filter-bar {
  display: flex;
  gap: $spacing-md;
  margin-bottom: $spacing-lg;
  flex-wrap: wrap;
}
.filter-input, .filter-select {
  padding: $spacing-sm $spacing-md;
  border: 1px solid $color-border;
  border-radius: $radius-md;
  background: $color-surface;
  min-width: 200px;
}

.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: $spacing-md;
}

.artwork-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: $spacing-md;
}

.artwork-card {
  cursor: pointer;
  transition: all $transition-normal;
  &:hover {
    transform: translateY(-2px);
    box-shadow: $shadow-md;
  }
}

.artwork-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: $spacing-md;
  gap: $spacing-sm;
}
.artwork-title {
  font-size: $font-size-base;
  font-weight: 600;
}

.artwork-info {
  display: flex;
  flex-direction: column;
  gap: $spacing-xs;
  margin-bottom: $spacing-md;
}
.info-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: $font-size-sm;
}
.label { color: $color-text-muted; }
.value { color: $color-text; font-weight: 500; }
.code {
  font-family: monospace;
  font-size: $font-size-xs;
  color: $color-primary;
  background: $color-surface-alt;
  padding: 2px $spacing-sm;
  border-radius: $radius-sm;
}

.progress-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin: $spacing-md 0 $spacing-xs;
  position: relative;

  &::before {
    content: '';
    position: absolute;
    top: 50%;
    left: 0;
    right: 0;
    height: 2px;
    background: $color-border;
    transform: translateY(-50%);
    z-index: 0;
  }
}
.progress-step {
  position: relative;
  z-index: 1;
}
.step-dot {
  width: 12px;
  height: 12px;
  border-radius: 50%;
  background: $color-surface;
  border: 2px solid $color-border;
}
.progress-step.step-done .step-dot {
  background: $color-success;
  border-color: $color-success;
}
.progress-step.step-current .step-dot {
  background: $color-primary;
  border-color: $color-primary;
  box-shadow: 0 0 0 4px rgba($color-primary, 0.2);
}

.progress-labels {
  display: flex;
  justify-content: space-between;
  font-size: $font-size-xs;
  color: $color-text-muted;
  margin-bottom: $spacing-md;
}

.artwork-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-top: $spacing-md;
  border-top: 1px solid $color-border;
}
.update-time {
  font-size: $font-size-xs;
  color: $color-text-muted;
}

.qr-modal { max-width: 400px; }
.qr-body {
  text-align: center;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: $spacing-md;
}
.qr-info {
  h4 { font-size: $font-size-lg; margin-bottom: $spacing-xs; }
  p { color: $color-text-secondary; font-size: $font-size-sm; }
}
.qr-code-text {
  font-family: monospace;
  color: $color-primary;
  font-weight: 600;
}
.qr-image {
  width: 200px;
  height: 200px;
  padding: $spacing-md;
  background: #fff;
  border-radius: $radius-md;
  box-shadow: $shadow-sm;
}
.qr-hint {
  font-size: $font-size-sm;
  color: $color-text-muted;
}

.error-box {
  background: rgba($color-danger, 0.1);
  color: $color-danger;
  padding: $spacing-sm $spacing-md;
  border-radius: $radius-md;
  font-size: $font-size-sm;
  margin-top: $spacing-md;
}

@media (max-width: 768px) {
  .form-row { grid-template-columns: 1fr; }
  .filter-input, .filter-select { min-width: 100%; flex: 1; }
}
</style>
