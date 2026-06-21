<template>
  <div class="page-container">
    <div class="page-header">
      <div>
        <h1>🔥 烧制曲线配置</h1>
        <p class="subtitle">预设不同泥料的升温、保温、降温曲线参数</p>
      </div>
      <button class="btn btn-primary" @click="openCreate">
        <span>+</span> 新建曲线
      </button>
    </div>

    <div class="filter-bar">
      <label class="filter-label">按泥料筛选：</label>
      <select v-model="clayTypeFilter" class="filter-select">
        <option value="">全部泥料</option>
        <option v-for="t in clayTypes" :key="t" :value="t">{{ t }}</option>
      </select>
    </div>

    <div v-if="loading" class="empty-state">
      <div class="empty-icon">⏳</div>
      <div class="empty-text">加载中...</div>
    </div>
    <div v-else-if="filteredCurves.length === 0" class="empty-state">
      <div class="empty-icon">📋</div>
      <div class="empty-text">暂无烧制曲线，点击右上角"新建曲线"添加</div>
    </div>
    <div v-else class="curve-grid">
      <div v-for="curve in filteredCurves" :key="curve.id" class="curve-card card">
        <div class="curve-header">
          <div>
            <h3 class="curve-name">{{ curve.name }}</h3>
            <div class="curve-meta">
              <span class="tag">{{ curve.clay_type }}</span>
              <span v-if="curve.is_default" class="badge badge-success">默认推荐</span>
              <span v-if="curve.created_by" class="curve-creator">by {{ curve.created_by }}</span>
            </div>
          </div>
          <div class="curve-actions">
            <button class="btn btn-outline btn-sm" @click="editCurve(curve)">编辑</button>
            <button class="btn btn-danger btn-sm" @click="deleteCurve(curve)">删除</button>
          </div>
        </div>

        <div v-if="curve.description" class="curve-desc">{{ curve.description }}</div>

        <div class="curve-chart">
          <svg viewBox="0 0 600 200" class="chart-svg">
            <defs>
              <linearGradient id="tempGrad" x1="0%" y1="100%" x2="0%" y2="0%">
                <stop offset="0%" stop-color="#C4A77D" stop-opacity="0.3"/>
                <stop offset="100%" stop-color="#C77B6A" stop-opacity="0.3"/>
              </linearGradient>
            </defs>
            <path :d="areaPath(curve.stages)" fill="url(#tempGrad)"/>
            <path :d="linePath(curve.stages)" fill="none" stroke="#8B7355" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/>
            <circle
              v-for="(p, idx) in chartPoints(curve.stages)"
              :key="idx"
              :cx="p.x" :cy="p.y" r="5"
              fill="#fff" stroke="#8B7355" stroke-width="2"
            />
          </svg>
          <div class="chart-labels">
            <span v-for="(s, idx) in curve.stages" :key="idx" class="stage-label" :title="s.name">
              {{ s.name }}: {{ s.start_temp }}℃ → {{ s.end_temp }}℃ ({{ s.duration_minutes }}分钟)
            </span>
          </div>
        </div>
      </div>
    </div>

    <div v-if="showModal" class="modal-overlay" @click.self="showModal = false">
      <div class="modal modal-lg">
        <div class="modal-header">
          <h3>{{ editingCurve ? '编辑曲线' : '新建烧制曲线' }}</h3>
          <button class="modal-close" @click="showModal = false">×</button>
        </div>
        <div class="modal-body">
          <div class="form-row">
            <div class="form-group">
              <label>曲线名称 *</label>
              <input v-model="form.name" type="text" placeholder="如：高白泥素烧标准曲线" />
            </div>
            <div class="form-group">
              <label>适用泥料 *</label>
              <select v-model="form.clay_type">
                <option value="">请选择</option>
                <option v-for="t in clayTypes" :key="t" :value="t">{{ t }}</option>
              </select>
            </div>
          </div>
          <div class="form-row">
            <div class="form-group">
              <label>创建人</label>
              <input v-model="form.created_by" type="text" />
            </div>
            <div class="form-group">
              <label style="display:flex;align-items:center;gap:8px;">
                <input type="checkbox" v-model="form.is_default" style="width:auto;" />
                设为该泥料默认推荐曲线
              </label>
            </div>
          </div>
          <div class="form-group">
            <label>曲线说明</label>
            <textarea v-model="form.description" placeholder="曲线特点、适用场景等"></textarea>
          </div>

          <div class="stages-section">
            <div class="stages-header">
              <h4>烧制阶段配置</h4>
              <button class="btn btn-outline btn-sm" @click="addStage">+ 添加阶段</button>
            </div>
            <div v-for="(stage, idx) in form.stages" :key="idx" class="stage-editor">
              <div class="stage-head">
                <span class="stage-num">阶段 {{ idx + 1 }}</span>
                <button class="stage-remove" @click="removeStage(idx)" v-if="form.stages.length > 1">×</button>
              </div>
              <div class="stage-form">
                <div class="form-group">
                  <label>阶段名称</label>
                  <input v-model="stage.name" type="text" placeholder="如：预热阶段" />
                </div>
                <div class="form-group">
                  <label>类型</label>
                  <select v-model="stage.stage_type">
                    <option value="heating">升温</option>
                    <option value="holding">保温</option>
                    <option value="cooling">降温</option>
                  </select>
                </div>
                <div class="form-group">
                  <label>起始温度(℃)</label>
                  <input type="number" v-model.number="stage.start_temp" />
                </div>
                <div class="form-group">
                  <label>结束温度(℃)</label>
                  <input type="number" v-model.number="stage.end_temp" />
                </div>
                <div class="form-group">
                  <label>时长(分钟)</label>
                  <input type="number" v-model.number="stage.duration_minutes" />
                </div>
                <div class="form-group">
                  <label>备注</label>
                  <input v-model="stage.notes" type="text" />
                </div>
              </div>
            </div>
          </div>

          <div v-if="form.stages.length > 0" class="curve-preview">
            <h5>曲线预览</h5>
            <svg viewBox="0 0 600 180" class="chart-svg">
              <path :d="linePath(form.stages)" fill="none" stroke="#8B7355" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
          </div>

          <div v-if="errorMsg" class="error-box">⚠️ {{ errorMsg }}</div>
        </div>
        <div class="modal-footer">
          <button class="btn btn-secondary" @click="showModal = false" :disabled="saving">取消</button>
          <button class="btn btn-primary" @click="saveCurve" :disabled="saving">{{ saving ? '保存中...' : '保存' }}</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import api from '@/api'

const loading = ref(true)
const saving = ref(false)
const curves = ref([])
const clayTypeFilter = ref('')
const showModal = ref(false)
const editingCurve = ref(null)
const errorMsg = ref('')

const clayTypes = ['高白泥', '紫砂', '瓷泥', '陶泥', '粗陶', '炻器', '其他']

const filteredCurves = computed(() => {
  if (!clayTypeFilter.value) return curves.value
  return curves.value.filter(c => c.clay_type === clayTypeFilter.value)
})

const defaultForm = () => ({
  name: '',
  clay_type: '',
  description: '',
  created_by: '',
  is_default: false,
  stages: [
    { name: '预热阶段', stage_type: 'heating', start_temp: 20, end_temp: 300, duration_minutes: 120, notes: '' },
    { name: '氧化阶段', stage_type: 'heating', start_temp: 300, end_temp: 900, duration_minutes: 180, notes: '' },
    { name: '高温烧制', stage_type: 'heating', start_temp: 900, end_temp: 1250, duration_minutes: 240, notes: '' },
    { name: '保温阶段', stage_type: 'holding', start_temp: 1250, end_temp: 1250, duration_minutes: 60, notes: '' },
    { name: '自然冷却', stage_type: 'cooling', start_temp: 1250, end_temp: 200, duration_minutes: 480, notes: '' }
  ]
})

const form = ref(defaultForm())

function chartPoints(stages) {
  if (!stages || stages.length === 0) return []
  const maxTemp = Math.max(...stages.map(s => Math.max(s.end_temp, s.start_temp)), 100)
  const totalTime = stages.reduce((acc, s) => acc + (s.duration_minutes || 0), 1)
  const points = []
  let accTime = 0
  points.push({ x: 0, y: 180 - (stages[0].start_temp / maxTemp) * 160 })
  for (const s of stages) {
    accTime += s.duration_minutes || 0
    const x = (accTime / totalTime) * 580 + 10
    const y = 180 - (s.end_temp / maxTemp) * 160
    points.push({ x, y })
  }
  return points
}

function linePath(stages) {
  const pts = chartPoints(stages)
  if (pts.length === 0) return ''
  return pts.map((p, i) => `${i === 0 ? 'M' : 'L'} ${p.x} ${p.y}`).join(' ')
}

function areaPath(stages) {
  const pts = chartPoints(stages)
  if (pts.length === 0) return ''
  return linePath(stages) + ` L ${pts[pts.length - 1].x} 180 L ${pts[0].x} 180 Z`
}

async function fetchCurves() {
  loading.value = true
  try {
    const res = await api.get('/firing-curves')
    curves.value = res.data
  } catch (e) {
    console.error(e)
  } finally {
    loading.value = false
  }
}

function openCreate() {
  editingCurve.value = null
  form.value = defaultForm()
  errorMsg.value = ''
  showModal.value = true
}

function editCurve(curve) {
  editingCurve.value = curve
  form.value = {
    name: curve.name,
    clay_type: curve.clay_type,
    description: curve.description || '',
    created_by: curve.created_by || '',
    is_default: curve.is_default,
    stages: JSON.parse(JSON.stringify(curve.stages))
  }
  errorMsg.value = ''
  showModal.value = true
}

function addStage() {
  const last = form.value.stages[form.value.stages.length - 1]
  form.value.stages.push({
    name: '新阶段',
    stage_type: 'heating',
    start_temp: last?.end_temp || 0,
    end_temp: last?.end_temp || 0,
    duration_minutes: 60,
    notes: ''
  })
}

function removeStage(idx) {
  form.value.stages.splice(idx, 1)
}

async function saveCurve() {
  errorMsg.value = ''
  if (!form.value.name.trim()) { errorMsg.value = '请填写曲线名称'; return }
  if (!form.value.clay_type) { errorMsg.value = '请选择适用泥料'; return }
  if (!form.value.stages.length) { errorMsg.value = '请至少添加一个阶段'; return }

  saving.value = true
  try {
    if (editingCurve.value) {
      await api.put(`/firing-curves/${editingCurve.value.id}`, form.value)
    } else {
      await api.post('/firing-curves', form.value)
    }
    showModal.value = false
    await fetchCurves()
  } catch (e) {
    errorMsg.value = e.response?.data?.detail || '保存失败'
  } finally {
    saving.value = false
  }
}

async function deleteCurve(curve) {
  if (!confirm(`确定要删除曲线「${curve.name}」吗？`)) return
  try {
    await api.delete(`/firing-curves/${curve.id}`)
    await fetchCurves()
  } catch (e) {
    alert('删除失败')
  }
}

onMounted(fetchCurves)
</script>

<style lang="scss" scoped>
.modal-lg { max-width: 900px; }

.filter-bar {
  display: flex;
  align-items: center;
  gap: $spacing-sm;
  margin-bottom: $spacing-md;
}
.filter-select {
  padding: $spacing-sm $spacing-md;
  border: 1px solid $color-border;
  border-radius: $radius-md;
  background: $color-surface;
}

.curve-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(480px, 1fr));
  gap: $spacing-md;
}

.curve-card {
  padding: $spacing-lg;
}
.curve-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: $spacing-sm;
}
.curve-name {
  font-size: $font-size-lg;
  font-weight: 600;
  color: $color-text;
}
.curve-meta {
  display: flex;
  align-items: center;
  gap: $spacing-sm;
  margin-top: $spacing-xs;
  flex-wrap: wrap;
}
.curve-creator {
  font-size: $font-size-xs;
  color: $color-text-muted;
}
.curve-actions {
  display: flex;
  gap: $spacing-xs;
}
.curve-desc {
  font-size: $font-size-sm;
  color: $color-text-secondary;
  margin-bottom: $spacing-md;
  line-height: 1.5;
}
.curve-chart {
  background: $color-surface-alt;
  border-radius: $radius-md;
  padding: $spacing-md;
}
.chart-svg {
  width: 100%;
  height: 180px;
}
.chart-labels {
  margin-top: $spacing-sm;
  display: flex;
  flex-wrap: wrap;
  gap: $spacing-xs;
  .stage-label {
    font-size: $font-size-xs;
    color: $color-text-muted;
    background: $color-surface;
    padding: 2px $spacing-sm;
    border-radius: $radius-sm;
  }
}

.stages-section {
  background: $color-surface-alt;
  border-radius: $radius-md;
  padding: $spacing-md;
  margin-top: $spacing-md;
}
.stages-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: $spacing-md;
  h4 { font-size: $font-size-base; font-weight: 600; }
}
.stage-editor {
  background: $color-surface;
  border-radius: $radius-md;
  padding: $spacing-md;
  margin-bottom: $spacing-sm;
}
.stage-head {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: $spacing-sm;
}
.stage-num {
  font-weight: 600;
  color: $color-primary;
}
.stage-remove {
  width: 28px;
  height: 28px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: $radius-full;
  color: $color-danger;
  font-size: 18px;
  &:hover { background: rgba($color-danger, 0.1); }
}
.stage-form {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: $spacing-sm;
}
.stage-form .form-group { margin-bottom: 0; }

.curve-preview {
  margin-top: $spacing-md;
  padding: $spacing-md;
  background: $color-surface-alt;
  border-radius: $radius-md;
  h5 { font-size: $font-size-sm; margin-bottom: $spacing-sm; color: $color-text-secondary; }
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
  .curve-grid { grid-template-columns: 1fr; }
  .stage-form { grid-template-columns: 1fr 1fr; }
}
</style>
