<template>
  <div class="modal-overlay" @click.self="$emit('close')">
    <div class="modal">
      <div class="modal-header">
        <h3>{{ isEdit ? '编辑预约' : '新建预约' }}</h3>
        <button class="modal-close" @click="$emit('close')">×</button>
      </div>
      <div class="modal-body">
        <div class="form-group">
          <label>预约标题 *</label>
          <input v-model="form.title" type="text" placeholder="如：高白泥素烧批次" />
        </div>
        <div class="form-group">
          <label>预约窑炉 *</label>
          <select v-model="form.kiln_id">
            <option v-for="k in kilns" :key="k.id" :value="k.id">
              {{ k.name }} ({{ k.capacity || '—' }})
            </option>
          </select>
        </div>
        <div class="form-row">
          <div class="form-group">
            <label>预约人 *</label>
            <input v-model="form.booker_name" type="text" placeholder="姓名" />
          </div>
          <div class="form-group">
            <label>联系方式</label>
            <input v-model="form.booker_contact" type="text" placeholder="手机/微信" />
          </div>
        </div>
        <div class="form-row">
          <div class="form-group">
            <label>入窑时间 *</label>
            <input v-model="form.start_time" type="datetime-local" />
          </div>
          <div class="form-group">
            <label>出窑时间 *</label>
            <input v-model="form.end_time" type="datetime-local" />
          </div>
        </div>
        <div class="form-group">
          <label>烧制曲线</label>
          <select v-model="form.firing_curve_id">
            <option :value="null">不指定</option>
            <option v-for="c in curves" :key="c.id" :value="c.id">
              {{ c.name }} ({{ c.clay_type }}){{ c.is_default ? ' · 默认' : '' }}
            </option>
          </select>
        </div>
        <div class="form-group">
          <label>状态</label>
          <select v-model="form.status">
            <option value="pending">待确认</option>
            <option value="confirmed">已确认</option>
            <option value="in_progress">烧制中</option>
            <option value="completed">已完成</option>
            <option value="cancelled">已取消</option>
          </select>
        </div>
        <div class="form-group">
          <label>备注</label>
          <textarea v-model="form.notes" placeholder="特殊要求、注意事项等"></textarea>
        </div>

        <div v-if="errorMessage" class="error-box">
          ⚠️ {{ errorMessage }}
        </div>
      </div>
      <div class="modal-footer">
        <button v-if="isEdit" class="btn btn-danger" @click="handleDelete" :disabled="submitting">删除</button>
        <div class="spacer"></div>
        <button class="btn btn-secondary" @click="$emit('close')" :disabled="submitting">取消</button>
        <button class="btn btn-primary" @click="handleSave" :disabled="submitting">
          {{ submitting ? '保存中...' : '保存' }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import dayjs from 'dayjs'
import api from '@/api'

const props = defineProps({
  booking: { type: Object, default: null },
  kilns: { type: Array, default: () => [] },
  curves: { type: Array, default: () => [] }
})
const emit = defineEmits(['close', 'saved', 'conflict'])

const submitting = ref(false)
const errorMessage = ref('')

const defaultForm = () => ({
  title: '',
  kiln_id: props.kilns[0]?.id || null,
  booker_name: '',
  booker_contact: '',
  start_time: dayjs().hour(9).minute(0).second(0).format('YYYY-MM-DDTHH:mm'),
  end_time: dayjs().hour(18).minute(0).second(0).format('YYYY-MM-DDTHH:mm'),
  firing_curve_id: null,
  status: 'pending',
  notes: ''
})

const form = ref(defaultForm())
const isEdit = computed(() => !!props.booking?.id)

watch(() => props.booking, (val) => {
  if (val) {
    form.value = {
      title: val.title || '',
      kiln_id: val.kiln_id,
      booker_name: val.booker_name || '',
      booker_contact: val.booker_contact || '',
      start_time: val.start_time ? dayjs(val.start_time).format('YYYY-MM-DDTHH:mm') : '',
      end_time: val.end_time ? dayjs(val.end_time).format('YYYY-MM-DDTHH:mm') : '',
      firing_curve_id: val.firing_curve_id || null,
      status: val.status || 'pending',
      notes: val.notes || ''
    }
  } else {
    form.value = defaultForm()
  }
}, { immediate: true })

function validate() {
  if (!form.value.title.trim()) {
    errorMessage.value = '请填写预约标题'
    return false
  }
  if (!form.value.kiln_id) {
    errorMessage.value = '请选择窑炉'
    return false
  }
  if (!form.value.booker_name.trim()) {
    errorMessage.value = '请填写预约人姓名'
    return false
  }
  if (!form.value.start_time || !form.value.end_time) {
    errorMessage.value = '请填写起止时间'
    return false
  }
  if (dayjs(form.value.start_time).isAfter(form.value.end_time)) {
    errorMessage.value = '结束时间必须晚于开始时间'
    return false
  }
  return true
}

async function handleSave() {
  errorMessage.value = ''
  if (!validate()) return

  submitting.value = true
  try {
    const payload = {
      ...form.value,
      start_time: dayjs(form.value.start_time).toISOString(),
      end_time: dayjs(form.value.end_time).toISOString()
    }

    if (isEdit.value) {
      await api.put(`/bookings/${props.booking.id}`, payload)
    } else {
      await api.post('/bookings', payload)
    }
    emit('saved')
  } catch (e) {
    const msg = e.response?.data?.detail || '保存失败'
    errorMessage.value = msg
    emit('conflict', msg)
  } finally {
    submitting.value = false
  }
}

async function handleDelete() {
  if (!confirm('确定要删除此预约吗？')) return
  submitting.value = true
  try {
    await api.delete(`/bookings/${props.booking.id}`)
    emit('saved')
  } catch (e) {
    errorMessage.value = '删除失败'
  } finally {
    submitting.value = false
  }
}
</script>

<style lang="scss" scoped>
.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: $spacing-md;
}
.spacer { flex: 1; }
.error-box {
  background: rgba($color-danger, 0.1);
  color: $color-danger;
  padding: $spacing-sm $spacing-md;
  border-radius: $radius-md;
  font-size: $font-size-sm;
  margin-top: $spacing-md;
}
@media (max-width: 600px) {
  .form-row {
    grid-template-columns: 1fr;
  }
}
</style>
