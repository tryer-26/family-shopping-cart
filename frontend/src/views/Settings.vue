<template>
  <div class="settings-page">
    <div class="page-header"><h2>⚙️ 系统设置</h2></div>
    <el-row :gutter="16">
      <el-col :span="12">
        <el-card style="margin-bottom:16px;">
          <template #header><span>系统配置</span></template>
          <el-descriptions :column="1" border>
            <el-descriptions-item label="系统名称">{{ sysConfig.app_name }}</el-descriptions-item>
            <el-descriptions-item label="版本">{{ sysConfig.app_version }}</el-descriptions-item>
            <el-descriptions-item label="Meilisearch">{{ sysConfig.meilisearch_available ? '✅ 已配置' : '❌ 未配置' }}</el-descriptions-item>
            <el-descriptions-item label="OSS">{{ sysConfig.oss_configured ? '✅ 已配置' : '❌ 未配置（将使用Mock）' }}</el-descriptions-item>
            <el-descriptions-item label="OCR">{{ sysConfig.ocr_configured ? '✅ 已配置' : '❌ 未配置（将使用Mock）' }}</el-descriptions-item>
            <el-descriptions-item label="定时抓取时间">{{ sysConfig.price_scrape_hours || '未配置' }}</el-descriptions-item>
          </el-descriptions>
        </el-card>
      </el-col>
      <el-col :span="12">
        <el-card style="margin-bottom:16px;">
          <template #header><span>家庭设置</span></template>
          <el-form :model="settingsForm" label-width="120px" v-if="authStore.currentFamily">
            <el-form-item v-for="s in settings" :key="s.setting_key" :label="settingLabels[s.setting_key] || s.setting_key">
              <el-input v-model="settingsForm[s.setting_key]" />
            </el-form-item>
            <el-form-item v-if="settings.length === 0">
              <span style="color:#909399;">暂未配置家庭设置项</span>
            </el-form-item>
          </el-form>
          <div v-else style="text-align:center;color:#909399;padding:20px;">请先选择家庭</div>
        </el-card>
        <el-card>
          <template #header><span>数据管理</span></template>
          <div style="display:flex;gap:12px;">
            <el-button type="primary" @click="handleExportBackup">导出数据备份</el-button>
            <el-button @click="handleImportBackup">导入数据备份</el-button>
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>
<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { useAuthStore } from '@/stores/auth'
import { systemAPI, exportAPI } from '@/api/auth'
const authStore = useAuthStore()
const sysConfig = ref({})
const settings = ref([])
const settingsForm = reactive({})
const settingLabels = {
  default_family_id: '默认家庭',
  price_alert_threshold: '价格提醒阈值',
  low_stock_threshold_days: '低库存预警天数',
}
onMounted(async () => {
  try { sysConfig.value = await systemAPI.getConfig() } catch(e) {}
  if (authStore.currentFamily) {
    try {
      settings.value = await systemAPI.getSettings(authStore.currentFamily.id)
      settings.value.forEach(s => { settingsForm[s.setting_key] = s.setting_value })
    } catch(e) {}
  }
})
async function handleExportBackup() {
  if (!authStore.currentFamily) return
  try {
    const blob = await exportAPI.backup(authStore.currentFamily.id)
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url; a.download = `hpms_backup_${authStore.currentFamily.id}.json`; a.click()
    URL.revokeObjectURL(url)
    ElMessage.success('备份已下载')
  } catch(e) { ElMessage.error('导出失败') }
}
async function handleImportBackup() {
  ElMessage.info('请在服务器端恢复数据')
}
</script>
<style scoped>
.page-header { margin-bottom:16px; }
.page-header h2 { margin:0; }
</style>
