<template>
  <div class="coupons-page">
    <div class="page-header"><h2>🎫 优惠券管理</h2><el-button type="primary" @click="showDialog=true" :disabled="!authStore.currentFamily">新增优惠券</el-button></div>
    <el-row :gutter="16" style="margin-bottom:16px;">
      <el-col :span="8"><el-card shadow="hover"><div class="mini-stat"><div class="mini-val">{{ stats.total || 0 }}</div><div class="mini-label">总优惠券</div></div></el-card></el-col>
      <el-col :span="8"><el-card shadow="hover"><div class="mini-stat"><div class="mini-val" style="color:#67c23a;">{{ stats.available || 0 }}</div><div class="mini-label">可用</div></div></el-card></el-col>
      <el-col :span="8"><el-card shadow="hover"><div class="mini-stat"><div class="mini-val" style="color:#e6a23c;">{{ expiring.length }}</div><div class="mini-label">即将过期</div></div></el-card></el-col>
    </el-row>
    <el-card>
      <el-table :data="coupons" v-loading="loading" empty-text="暂无优惠券">
        <el-table-column prop="name" label="名称" min-width="140" />
        <el-table-column label="类型" width="80"><template #default="{row}"><el-tag>{{ row.type }}</el-tag></template></el-table-column>
        <el-table-column label="面额" width="100"><template #default="{row}"><span style="font-weight:bold;color:#f56c6c;">¥{{ row.face_value }}</span></template></el-table-column>
        <el-table-column label="门槛" width="100"><template #default="{row}">满¥{{ row.min_order_amount }}</template></el-table-column>
        <el-table-column label="有效期" width="200"><template #default="{row}">{{ dayjs(row.valid_from).format('MM-DD') }} ~ {{ dayjs(row.valid_until).format('MM-DD') }}</template></el-table-column>
        <el-table-column label="状态" width="80"><template #default="{row}"><el-tag :type="row.is_used?'info':'success'">{{ row.is_used?'已用':'可用' }}</el-tag></template></el-table-column>
        <el-table-column label="操作" width="150" fixed="right">
          <template #default="{row}">
            <el-button v-if="!row.is_used" size="small" @click="markUsed(row)">已使用</el-button>
            <el-button size="small" type="danger" @click="handleDelete(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
    <el-dialog v-model="showDialog" title="新增优惠券" width="500px">
      <el-form :model="form" ref="formRef" label-width="100px" :rules="rules">
        <el-form-item label="名称" prop="name"><el-input v-model="form.name" /></el-form-item>
        <el-form-item label="类型" prop="type"><el-select v-model="form.type" style="width:100%"><el-option label="满减" value="满减" /><el-option label="折扣" value="折扣" /><el-option label="直降" value="直降" /></el-select></el-form-item>
        <el-row :gutter="12">
          <el-col :span="12"><el-form-item label="面额" prop="face_value"><el-input-number v-model="form.face_value" :min="0" style="width:100%" /></el-form-item></el-col>
          <el-col :span="12"><el-form-item label="门槛"><el-input-number v-model="form.min_order_amount" :min="0" style="width:100%" /></el-form-item></el-col>
        </el-row>
        <el-row :gutter="12">
          <el-col :span="12"><el-form-item label="开始日期" prop="valid_from"><el-date-picker v-model="form.valid_from" type="datetime" style="width:100%" /></el-form-item></el-col>
          <el-col :span="12"><el-form-item label="结束日期" prop="valid_until"><el-date-picker v-model="form.valid_until" type="datetime" style="width:100%" /></el-form-item></el-col>
        </el-row>
        <el-form-item label="适用渠道"><el-input v-model="form.applicable_channel" placeholder="如京东/淘宝/不限" /></el-form-item>
        <el-form-item label="备注"><el-input v-model="form.notes" type="textarea" /></el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showDialog=false">取消</el-button>
        <el-button type="primary" @click="handleSave" :loading="saving">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>
<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import dayjs from 'dayjs'
import { useAuthStore } from '@/stores/auth'
import { couponsAPI } from '@/api/auth'
const authStore = useAuthStore()
const loading = ref(false), saving = ref(false), showDialog = ref(false)
const coupons = ref([]), expiring = ref([])
const stats = ref({ total:0, available:0 })
const formRef = ref(null)
const form = reactive({ name:'', type:'满减', face_value:0, min_order_amount:0, valid_from:null, valid_until:null, applicable_channel:'', notes:'' })
const rules = { name:[{required:true,message:'请输入名称'}], type:[{required:true,message:'请选择类型'}], face_value:[{required:true,message:'请输入面额'}], valid_from:[{required:true,message:'请选择开始日期'}], valid_until:[{required:true,message:'请选择结束日期'}] }
async function loadCoupons() {
  if (!authStore.currentFamily) return
  loading.value = true
  try {
    const fid = authStore.currentFamily.id
    const res = await couponsAPI.list(fid, { page_size: 200 })
    coupons.value = res.items || []
    stats.value = { total: coupons.value.length, available: coupons.value.filter(c => !c.is_used).length }
    expiring.value = await couponsAPI.getExpiring(fid)
  } catch(e) { console.error(e) }
  finally { loading.value = false }
}
async function handleSave() {
  const valid = await formRef.value.validate().catch(() => false)
  if (!valid) return
  saving.value = true
  try {
    await couponsAPI.create(authStore.currentFamily.id, {
      ...form,
      valid_from: dayjs(form.valid_from).format('YYYY-MM-DDTHH:mm:ss'),
      valid_until: dayjs(form.valid_until).format('YYYY-MM-DDTHH:mm:ss'),
    })
    ElMessage.success('已创建')
    showDialog.value = false
    await loadCoupons()
  } catch(e) {}
  finally { saving.value = false }
}
async function markUsed(row) {
  try { await couponsAPI.markUsed(row.id); ElMessage.success('已标记'); await loadCoupons() }
  catch(e) {}
}
async function handleDelete(row) {
  await ElMessageBox.confirm('确定删除？','确认')
  try { await couponsAPI.delete(row.id); ElMessage.success('已删除'); await loadCoupons() }
  catch(e) {}
}
onMounted(loadCoupons)
</script>
<style scoped>
.page-header { display:flex; justify-content:space-between; align-items:center; margin-bottom:16px; }
.page-header h2 { margin:0; }
.mini-stat { text-align:center; padding:8px 0; }
.mini-val { font-size:32px; font-weight:bold; }
.mini-label { font-size:13px; color:#909399; margin-top:4px; }
</style>
