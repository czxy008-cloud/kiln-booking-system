<template>
  <div class="page-container">
    <div class="page-header">
      <div>
        <h1>🏭 窑炉管理</h1>
        <p class="subtitle">管理工作室所有窑炉设备信息</p>
      </div>
      <button class="btn btn-primary" @click="openCreate">
        <span>+</span> 新增窑炉
      </button>
    </div>

    <div v-if="loading" class="empty-state">
      <div class="empty-icon">⏳</div>
      <div class="empty-text">加载中...</div>
    </div>
    <div v-else-if="kilns.length === 0" class="empty-state">
      <div class="empty-icon">🏚️</div>
      <div class="empty-text">暂无窑炉设备，点击右上角添加</div>
    </div>
    <div v-else class="kiln-grid">
      <div v-for="k in kilns" :key="k.id" class="kiln-card card">
        <div class="kiln-status" :class="k.status"></div>
        <h3 class="kiln-name">{{ k.name }}</h3>
        <div class="kiln-info">
          <div class="info-item">
            <span class="info-label">容量</span>
            <span class="info-value">{{ k.capacity || '—' }}</span>
          </div>
          <div class="info-item">
            <span class="info-label">最高温度</span>
            <span class="info-value">{{ k.max_temperature ? k.max_temperature + '℃' : '—' }}</span>
          </div>
          <div class="info-item">
            <span class="info-label">状态</span>
            <span class="badge" :class="'badge-' + statusClass(k.status)">
              {{ statusText(k.status) }}
            </span>
          </div>
        </div>
        <p v-if="k.description" class="kiln-desc">{{ k.description }}</p>
        <div class="kiln-footer">
          <span class="update-time">更新于 {{ formatDate(k.updated_at) }}</span>
          <div class="kiln-actions">
            <button class="btn btn-outline btn-sm" @click="editKiln(k)">编辑</button>
            <button class="btn btn-danger btn-sm" @click="deleteKiln(k)">删除</button>
          </div>
        </div>
      </div>
    </div>

    <div v-if="showModal" class="modal-overlay" @click.self="showModal = false">
      <div class="modal">
        <div class="modal-header">
          <h3>{{ editingKiln ? '编辑窑炉' : '新增窑炉' }}</h3>
          <button class="modal-close" @click="showModal = false">×</button>
        </div>
        <div class="modal-body">
          <div class="form-group">
            <label>窑炉名称 *</label>
            <input v-model="form.name" type="text" placeholder="如：1号电窑" />
          </div>
          <div class="form-row">
            <div class="form-group">
              <label>容量</label>
              <input v-model="form.capacity" type="text" placeholder="如：0.5立方米" />
            </div>
            <div class="form-group">
              <label>最高温度(℃)</label>
              <input type="number" v-model.number="form.max_temperature" placeholder="如：1300" />
            </div>
          </div>
          <div class="form-group">
            <label>状态</label>
            <select v-model="form.status">
              <option value="active">运行中</option>
              <option value="inactive">停用</option>
              <option value="maintenance">维护中</option>
            </select>
          </div>
          <div class="form-group">
            <label>备注说明</label>
            <textarea v-model="form.description" placeholder="窑炉特点、使用注意事项等"></textarea>
          </div>
          <div v-if="errorMsg" class="error-box">⚠️ {{ errorMsg }}</div>
        </div>
        <div class="modal-footer">
          <button class="btn btn-secondary" @click="showModal = false" :disabled="saving">取消</button>
          <button class="btn btn-primary" @click="saveKiln" :disabled="saving">{{ saving ? '保存中...' : '保存' }}</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import dayjs from 'dayjs'
import api from '@/api'

const loading = ref(true)
const saving = ref(false)
const kilns = ref([])
const showModal = ref(false)
const editingKiln = ref(null)
const errorMsg = ref('')

const defaultForm = () => ({
  name: '',
  capacity: '',
  max_temperature: 1300,
  status: 'active',
  description: ''
})
const form = ref(defaultForm())

function formatDate(iso) {
  return dayjs(iso).format('YYYY-MM-DD HH:mm')
}
function statusText(s) {
  return { active: '运行中', inactive: '停用', maintenance: '维护中' }[s] || s
}
function statusClass(s) {
  return { active: 'success', inactive: 'default', maintenance: 'warning' }[s] || 'default'
}

async function fetchKilns() {
  loading.value = true
  try {
    const res = await api.get('/kilns')
    kilns.value = res.data
  } catch (e) {
    console.error(e)
  } finally {
    loading.value = false
  }
}

function openCreate() {
  editingKiln.value = null
  form.value = defaultForm()
  errorMsg.value = ''
  showModal.value = true
}

function editKiln(k) {
  editingKiln.value = k
  form.value = {
    name: k.name,
    capacity: k.capacity || '',
    max_temperature: k.max_temperature || null,
    status: k.status,
    description: k.description || ''
  }
  errorMsg.value = ''
  showModal.value = true
}

async function saveKiln() {
  errorMsg.value = ''
  if (!form.value.name.trim()) { errorMsg.value = '请填写窑炉名称'; return }
  saving.value = true
  try {
    if (editingKiln.value) {
      await api.put(`/kilns/${editingKiln.value.id}`, form.value)
    } else {
      await api.post('/kilns', form.value)
    }
    showModal.value = false
    await fetchKilns()
  } catch (e) {
    errorMsg.value = e.response?.data?.detail || '保存失败'
  } finally {
    saving.value = false
  }
}

async function deleteKiln(k) {
  if (!confirm(`确定要删除窑炉「${k.name}」吗？相关预约记录也会被删除。`)) return
  try {
    await api.delete(`/kilns/${k.id}`)
    await fetchKilns()
  } catch (e) {
    alert('删除失败')
  }
}

onMounted(fetchKilns)
</script>

<style lang="scss" scoped>
.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: $spacing-md;
}

.kiln-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: $spacing-md;
}

.kiln-card {
  position: relative;
  padding: $spacing-lg;
  padding-top: $spacing-lg + 8px;
  overflow: hidden;
}

.kiln-status {
  position: absolute;
  top: 0; left: 0; right: 0;
  height: 4px;
  &.active { background: $color-success; }
  &.inactive { background: $color-text-muted; }
  &.maintenance { background: $color-warning; }
}

.kiln-name {
  font-size: $font-size-lg;
  font-weight: 600;
  margin-bottom: $spacing-md;
}

.kiln-info {
  display: flex;
  flex-direction: column;
  gap: $spacing-xs;
  margin-bottom: $spacing-md;
}
.info-item {
  display: flex;
  justify-content: space-between;
  font-size: $font-size-sm;
}
.info-label {
  color: $color-text-muted;
}
.info-value {
  color: $color-text;
  font-weight: 500;
}

.kiln-desc {
  font-size: $font-size-sm;
  color: $color-text-secondary;
  line-height: 1.5;
  margin-bottom: $spacing-md;
  padding: $spacing-sm;
  background: $color-surface-alt;
  border-radius: $radius-sm;
}

.kiln-footer {
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
.kiln-actions {
  display: flex;
  gap: $spacing-xs;
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
}
</style>
