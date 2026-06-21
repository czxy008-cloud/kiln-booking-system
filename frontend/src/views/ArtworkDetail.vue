<template>
  <div class="page-container artwork-detail-page">
    <div v-if="loading" class="empty-state">
      <div class="empty-icon">⏳</div>
      <div class="empty-text">加载中...</div>
    </div>
    <div v-else-if="!artwork" class="empty-state">
      <div class="empty-icon">❓</div>
      <div class="empty-text">作品不存在，请检查二维码是否正确</div>
      <router-link to="/artworks" class="btn btn-outline">返回作品列表</router-link>
    </div>
    <div v-else>
      <button class="back-btn" @click="$router.back()">← 返回</button>

      <div class="artwork-header card">
        <div class="artwork-info">
          <h1 class="artwork-title">{{ artwork.title }}</h1>
          <div class="artwork-meta">
            <span class="meta-item">👤 {{ artwork.student_name }}</span>
            <span v-if="artwork.clay_type" class="tag">{{ artwork.clay_type }}</span>
            <span class="badge" :class="stageBadgeClass(artwork.current_stage)">
              {{ currentStageName }}
            </span>
          </div>
          <p v-if="artwork.description" class="artwork-desc">{{ artwork.description }}</p>
          <div class="artwork-code">
            <span class="code-label">作品编号</span>
            <span class="code-value">{{ artwork.qr_code }}</span>
          </div>
        </div>
        <div class="qr-section">
          <img :src="`/api/artworks/${artwork.id}/qrcode`" alt="二维码" class="qr-img" />
          <p class="qr-text">扫码查看进度</p>
        </div>
      </div>

      <div class="timeline-section card">
        <h2 class="section-title">🔥 烧制进度</h2>
        <div class="progress-summary">
          <div class="progress-bar-wrap">
            <div class="progress-fill" :style="{ width: progressPercent + '%' }"></div>
          </div>
          <span class="progress-text">{{ progressPercent }}%</span>
        </div>

        <div class="timeline">
          <div
            v-for="(stage, idx) in artwork.stages"
            :key="stage.id"
            class="timeline-item"
            :class="getStageItemClass(stage)"
          >
            <div class="timeline-dot">
              <span v-if="stage.status === 'completed'">✓</span>
              <span v-else-if="stage.status === 'in_progress'">●</span>
              <span v-else>{{ idx + 1 }}</span>
            </div>
            <div class="timeline-content">
              <div class="timeline-head">
                <h3 class="stage-name">{{ stage.stage_name }}</h3>
                <span class="badge" :class="statusBadgeClass(stage.status)">
                  {{ statusText(stage.status) }}
                </span>
              </div>

              <div class="stage-details">
                <div v-if="stage.temperature" class="detail-item">
                  <span class="detail-label">🌡️ 温度</span>
                  <span class="detail-value">{{ stage.temperature }}℃</span>
                </div>
                <div v-if="stage.operator" class="detail-item">
                  <span class="detail-label">👤 操作人</span>
                  <span class="detail-value">{{ stage.operator }}</span>
                </div>
                <div v-if="stage.started_at" class="detail-item">
                  <span class="detail-label">🕐 开始</span>
                  <span class="detail-value">{{ formatDate(stage.started_at) }}</span>
                </div>
                <div v-if="stage.completed_at" class="detail-item">
                  <span class="detail-label">✅ 完成</span>
                  <span class="detail-value">{{ formatDate(stage.completed_at) }}</span>
                </div>
              </div>

              <div v-if="stage.photo_path" class="stage-photo">
                <img
                  :src="photoUrl(stage.photo_path)"
                  :alt="stage.stage_name"
                  class="photo-img"
                  @click="previewPhoto(stage.photo_path)"
                />
              </div>

              <p v-if="stage.notes" class="stage-notes">📝 {{ stage.notes }}</p>

              <div v-if="isManager && (stage.status === 'in_progress' || stage.status === 'pending')" class="stage-actions">
                <button
                  v-if="stage.status === 'pending'"
                  class="btn btn-primary btn-sm"
                  @click="startStage(stage)"
                >开始此阶段</button>
                <button
                  v-if="stage.status === 'in_progress'"
                  class="btn btn-outline btn-sm"
                  @click="openStageEditor(stage)"
                >更新状态</button>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div v-if="isManager" class="manager-section card">
        <h2 class="section-title">⚙️ 管理员操作</h2>
        <p class="section-desc">更新当前阶段状态、上传照片记录</p>
        <div class="manager-actions">
          <button class="btn btn-outline" @click="goBack">返回列表</button>
        </div>
      </div>
    </div>

    <div v-if="showStageModal" class="modal-overlay" @click.self="showStageModal = false">
      <div class="modal">
        <div class="modal-header">
          <h3>更新阶段：{{ editingStage?.stage_name }}</h3>
          <button class="modal-close" @click="showStageModal = false">×</button>
        </div>
        <div class="modal-body">
          <div class="form-group">
            <label>阶段状态</label>
            <select v-model="stageForm.status">
              <option value="pending">未开始</option>
              <option value="in_progress">进行中</option>
              <option value="completed">已完成</option>
            </select>
          </div>
          <div class="form-row">
            <div class="form-group">
              <label>当前温度(℃)</label>
              <input type="number" v-model.number="stageForm.temperature" />
            </div>
            <div class="form-group">
              <label>操作人</label>
              <input v-model="stageForm.operator" type="text" />
            </div>
          </div>
          <div class="form-group">
            <label>阶段备注</label>
            <textarea v-model="stageForm.notes" placeholder="此阶段的情况说明、问题记录等"></textarea>
          </div>
          <div class="form-group">
            <label>上传照片</label>
            <input
              type="file"
              accept="image/*"
              @change="handlePhotoUpload"
              class="file-input"
            />
            <div v-if="uploadingPhoto" class="upload-status">上传中...</div>
            <div v-if="stageForm.photo_path" class="photo-preview">
              <img :src="photoUrl(stageForm.photo_path)" alt="预览" />
            </div>
          </div>
          <div v-if="errorMsg" class="error-box">⚠️ {{ errorMsg }}</div>
        </div>
        <div class="modal-footer">
          <button class="btn btn-secondary" @click="showStageModal = false" :disabled="saving">取消</button>
          <button class="btn btn-primary" @click="saveStageUpdate" :disabled="saving || uploadingPhoto">
            {{ saving ? '保存中...' : '保存' }}
          </button>
        </div>
      </div>
    </div>

    <div v-if="previewImage" class="modal-overlay preview-modal" @click="previewImage = null">
      <img :src="previewImage" alt="预览" class="preview-img" @click.stop />
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import dayjs from 'dayjs'
import api from '@/api'
import { useAuthStore } from '@/stores/auth'

const route = useRoute()
const authStore = useAuthStore()
const loading = ref(true)
const saving = ref(false)
const uploadingPhoto = ref(false)
const artwork = ref(null)
const isManager = computed(() => authStore.isLoggedIn)
const showStageModal = ref(false)
const editingStage = ref(null)
const previewImage = ref(null)
const errorMsg = ref('')

const stageForm = ref({
  status: 'in_progress',
  temperature: null,
  operator: '',
  notes: '',
  photo_path: ''
})

const stageOptions = [
  { key: 'drying', name: '入窑前干燥' },
  { key: 'pre_heating', name: '预热阶段' },
  { key: 'bisque_firing', name: '素烧阶段' },
  { key: 'glazing', name: '施釉阶段' },
  { key: 'glaze_firing', name: '釉烧阶段' },
  { key: 'cooling', name: '出窑冷却' },
  { key: 'completed', name: '烧制完成' }
]

const currentStageName = computed(() => {
  if (!artwork.value) return ''
  return stageOptions.find(s => s.key === artwork.value.current_stage)?.name || artwork.value.current_stage
})

const progressPercent = computed(() => {
  if (!artwork.value) return 0
  const currentIdx = stageOptions.findIndex(s => s.key === artwork.value.current_stage)
  if (currentIdx < 0) return 0
  return Math.round((currentIdx / (stageOptions.length - 1)) * 100)
})

function formatDate(iso) {
  return iso ? dayjs(iso).format('YYYY-MM-DD HH:mm') : ''
}

function stageBadgeClass(key) {
  if (key === 'completed') return 'badge-success'
  if (key === 'drying') return 'badge-info'
  if (key === 'cooling') return 'badge-warning'
  return 'badge-default'
}

function statusBadgeClass(status) {
  return {
    completed: 'badge-success',
    in_progress: 'badge-warning',
    pending: 'badge-default'
  }[status] || 'badge-default'
}

function statusText(s) {
  return { completed: '已完成', in_progress: '进行中', pending: '未开始' }[s] || s
}

function getStageItemClass(stage) {
  if (stage.status === 'completed') return 'stage-done'
  if (stage.status === 'in_progress') return 'stage-current'
  return 'stage-pending'
}

function photoUrl(path) {
  if (!path) return ''
  if (path.startsWith('http')) return path
  const filename = path.split(/[\\/]/).pop()
  return `/api/uploads/artwork-photo/${filename}`
}

async function fetchArtwork() {
  loading.value = true
  try {
    const qrCode = route.params.qrCode
    const res = await api.get(`/artworks/by-qr/${qrCode}`)
    artwork.value = res.data
  } catch (e) {
    console.error(e)
    artwork.value = null
  } finally {
    loading.value = false
  }
}

async function startStage(stage) {
  try {
    await api.put(`/artworks/${artwork.value.id}/stages/${stage.stage_key}`, {
      status: 'in_progress',
      started_at: new Date().toISOString()
    })
    await fetchArtwork()
  } catch (e) {
    alert('操作失败')
  }
}

function openStageEditor(stage) {
  editingStage.value = stage
  stageForm.value = {
    status: stage.status,
    temperature: stage.temperature || null,
    operator: stage.operator || '',
    notes: stage.notes || '',
    photo_path: stage.photo_path || ''
  }
  errorMsg.value = ''
  showStageModal.value = true
}

async function handlePhotoUpload(e) {
  const file = e.target.files?.[0]
  if (!file) return

  uploadingPhoto.value = true
  try {
    const formData = new FormData()
    formData.append('file', file)
    const res = await api.post('/uploads/artwork-photo', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
    stageForm.value.photo_path = res.data.file_path
  } catch (e) {
    errorMsg.value = '照片上传失败'
  } finally {
    uploadingPhoto.value = false
  }
}

async function saveStageUpdate() {
  errorMsg.value = ''
  saving.value = true
  try {
    const payload = { ...stageForm.value }
    if (payload.status === 'completed' && !editingStage.value.completed_at) {
      payload.completed_at = new Date().toISOString()
    }
    if (payload.status === 'in_progress' && !editingStage.value.started_at) {
      payload.started_at = new Date().toISOString()
    }
    await api.put(
      `/artworks/${artwork.value.id}/stages/${editingStage.value.stage_key}`,
      payload
    )
    showStageModal.value = false
    await fetchArtwork()
  } catch (e) {
    errorMsg.value = e.response?.data?.detail || '保存失败'
  } finally {
    saving.value = false
  }
}

function previewPhoto(path) {
  previewImage.value = photoUrl(path)
}

function goBack() {
  window.location.href = '/artworks'
}

onMounted(fetchArtwork)
</script>

<style lang="scss" scoped>
.artwork-detail-page {
  max-width: 900px;
}

.back-btn {
  color: $color-text-secondary;
  font-size: $font-size-sm;
  margin-bottom: $spacing-md;
  display: inline-flex;
  align-items: center;
  padding: $spacing-sm 0;
  &:hover { color: $color-primary; }
}

.artwork-header {
  display: flex;
  gap: $spacing-xl;
  align-items: flex-start;
  flex-wrap: wrap;

  @media (max-width: 600px) {
    flex-direction: column;
    align-items: center;
    text-align: center;
  }
}

.artwork-info {
  flex: 1;
  min-width: 280px;
}

.artwork-title {
  font-size: $font-size-xxl;
  font-weight: 600;
  margin-bottom: $spacing-sm;
}

.artwork-meta {
  display: flex;
  gap: $spacing-sm;
  align-items: center;
  flex-wrap: wrap;
  margin-bottom: $spacing-md;

  @media (max-width: 600px) {
    justify-content: center;
  }
}

.meta-item {
  color: $color-text-secondary;
  font-size: $font-size-sm;
}

.artwork-desc {
  color: $color-text-secondary;
  line-height: 1.6;
  margin-bottom: $spacing-md;
  padding: $spacing-sm $spacing-md;
  background: $color-surface-alt;
  border-radius: $radius-md;
}

.artwork-code {
  display: inline-flex;
  align-items: center;
  gap: $spacing-sm;
  padding: $spacing-sm $spacing-md;
  background: $color-surface-alt;
  border-radius: $radius-md;
}
.code-label {
  font-size: $font-size-xs;
  color: $color-text-muted;
}
.code-value {
  font-family: monospace;
  font-weight: 600;
  color: $color-primary;
}

.qr-section {
  text-align: center;
}
.qr-img {
  width: 140px;
  height: 140px;
  padding: $spacing-sm;
  background: #fff;
  border-radius: $radius-md;
  box-shadow: $shadow-sm;
}
.qr-text {
  font-size: $font-size-xs;
  color: $color-text-muted;
  margin-top: $spacing-xs;
}

.section-title {
  font-size: $font-size-lg;
  font-weight: 600;
  margin-bottom: $spacing-md;
}
.section-desc {
  color: $color-text-muted;
  font-size: $font-size-sm;
  margin-bottom: $spacing-md;
}

.progress-summary {
  display: flex;
  align-items: center;
  gap: $spacing-md;
  margin-bottom: $spacing-xl;
}
.progress-bar-wrap {
  flex: 1;
  height: 10px;
  background: $color-surface-alt;
  border-radius: $radius-full;
  overflow: hidden;
}
.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, $color-warning, $color-success);
  border-radius: $radius-full;
  transition: width 0.5s ease;
}
.progress-text {
  font-weight: 600;
  color: $color-primary;
  min-width: 50px;
  text-align: right;
}

.timeline {
  position: relative;
  padding-left: 40px;

  &::before {
    content: '';
    position: absolute;
    left: 15px;
    top: 0;
    bottom: 0;
    width: 2px;
    background: $color-border;
  }
}

.timeline-item {
  position: relative;
  padding-bottom: $spacing-xl;

  &:last-child { padding-bottom: 0; }

  &.stage-done .timeline-dot {
    background: $color-success;
    border-color: $color-success;
    color: #fff;
  }
  &.stage-current .timeline-dot {
    background: $color-primary;
    border-color: $color-primary;
    color: #fff;
    box-shadow: 0 0 0 6px rgba($color-primary, 0.15);
  }
  &.stage-pending .timeline-dot {
    background: $color-surface;
    border-color: $color-border;
    color: $color-text-muted;
  }
}

.timeline-dot {
  position: absolute;
  left: -40px;
  top: 0;
  width: 32px;
  height: 32px;
  border-radius: 50%;
  border: 2px solid;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: $font-size-sm;
  font-weight: 600;
  background: $color-surface;
}

.timeline-content {
  background: $color-surface-alt;
  border-radius: $radius-md;
  padding: $spacing-md;
}

.timeline-head {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: $spacing-sm;
  flex-wrap: wrap;
  gap: $spacing-sm;
}
.stage-name {
  font-size: $font-size-base;
  font-weight: 600;
}

.stage-details {
  display: flex;
  flex-wrap: wrap;
  gap: $spacing-md;
  margin-bottom: $spacing-sm;
}
.detail-item {
  font-size: $font-size-sm;
}
.detail-label {
  color: $color-text-muted;
  margin-right: $spacing-xs;
}
.detail-value {
  color: $color-text;
  font-weight: 500;
}

.stage-photo {
  margin: $spacing-sm 0;
}
.photo-img {
  max-width: 240px;
  max-height: 180px;
  border-radius: $radius-md;
  cursor: pointer;
  transition: transform $transition-fast;
  &:hover { transform: scale(1.02); }
}

.stage-notes {
  font-size: $font-size-sm;
  color: $color-text-secondary;
  padding: $spacing-sm;
  background: $color-surface;
  border-radius: $radius-sm;
  margin: $spacing-sm 0;
}

.stage-actions {
  margin-top: $spacing-md;
  display: flex;
  gap: $spacing-sm;
}

.manager-actions {
  display: flex;
  gap: $spacing-sm;
}

.file-input {
  width: 100%;
  padding: $spacing-sm;
  border: 1px dashed $color-border;
  border-radius: $radius-md;
  background: $color-surface;
  cursor: pointer;

  &:hover { border-color: $color-primary; }
}
.upload-status {
  font-size: $font-size-sm;
  color: $color-primary;
  margin-top: $spacing-xs;
}
.photo-preview {
  margin-top: $spacing-sm;
  img {
    max-width: 200px;
    max-height: 150px;
    border-radius: $radius-md;
  }
}

.preview-modal {
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(0,0,0,0.85);
}
.preview-img {
  max-width: 90%;
  max-height: 90vh;
  border-radius: $radius-lg;
  box-shadow: $shadow-lg;
}

.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: $spacing-md;
}

.error-box {
  background: rgba($color-danger, 0.1);
  color: $color-danger;
  padding: $spacing-sm $spacing-md;
  border-radius: $radius-md;
  font-size: $font-size-sm;
  margin-top: $spacing-md;
}

@media (max-width: 600px) {
  .form-row { grid-template-columns: 1fr; }
  .timeline { padding-left: 32px; }
  .timeline-dot { left: -32px; width: 26px; height: 26px; font-size: $font-size-xs; }
}
</style>
