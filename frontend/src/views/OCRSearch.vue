<template>
  <div class="ocr-page">
    <div class="page-header"><h2>📷 识图搜品</h2></div>
    <el-row :gutter="16">
      <el-col :span="10">
        <el-card>
          <template #header><span>上传商品图片</span></template>
          <el-upload drag :auto-upload="false" :on-change="handleFileChange" accept="image/*" :show-file-list="false">
            <el-icon style="font-size:48px;color:#c0c4cc;"><Plus /></el-icon>
            <div style="margin-top:8px;color:#909399;">点击或拖拽图片到此区域</div>
            <div style="font-size:12px;color:#c0c4cc;margin-top:4px;">支持 JPG/PNG，最大 10MB</div>
          </el-upload>
          <div v-if="previewUrl" style="margin-top:16px;">
            <el-image :src="previewUrl" style="width:100%;max-height:300px;object-fit:contain;" />
            <el-button type="primary" style="width:100%;margin-top:12px;" @click="recognize" :loading="processing">识别商品</el-button>
          </div>
        </el-card>
      </el-col>
      <el-col :span="14">
        <el-card v-if="result">
          <template #header><span>识别结果</span></template>
          <el-descriptions :column="1" border>
            <el-descriptions-item label="品牌">{{ result.brand || '未识别' }}</el-descriptions-item>
            <el-descriptions-item label="名称">{{ result.name || '未识别' }}</el-descriptions-item>
            <el-descriptions-item label="规格">{{ result.specification || '未识别' }}</el-descriptions-item>
            <el-descriptions-item label="匹配商品">
              <span v-if="result.matched_product_name">{{ result.matched_product_name }} <el-tag>{{ result.matched_product_brand || '' }}</el-tag></span>
              <span v-else style="color:#909399;">未匹配</span>
            </el-descriptions-item>
          </el-descriptions>
          <div style="margin-top:16px;display:flex;gap:8px;">
            <el-button type="primary" @click="addToShoppingList">加入采购清单</el-button>
            <el-button @click="result=null;previewUrl=''">重新识别</el-button>
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>
<script setup>
import { ref } from 'vue'
import { ElMessage } from 'element-plus'
import { useAuthStore } from '@/stores/auth'
import { ocrAPI, shoppingAPI } from '@/api/auth'
const authStore = useAuthStore()
const previewUrl = ref('')
const selectedFile = ref(null)
const processing = ref(false)
const result = ref(null)
function handleFileChange(uploadFile) {
  selectedFile.value = uploadFile.raw
  previewUrl.value = URL.createObjectURL(uploadFile.raw)
  result.value = null
}
async function recognize() {
  if (!selectedFile.value || !authStore.currentFamily) return
  processing.value = true
  try {
    result.value = await ocrAPI.recognize(authStore.currentFamily.id, selectedFile.value)
    ElMessage.success('识别完成')
  } catch(e) { ElMessage.error('识别失败') }
  finally { processing.value = false }
}
async function addToShoppingList() {
  if (!result.value.matched_product_id) { ElMessage.warning('未匹配到商品，无法加入清单'); return }
  try {
    await shoppingAPI.add(authStore.currentFamily.id, { product_id: result.value.matched_product_id, quantity: 1 })
    ElMessage.success('已加入采购清单')
  } catch(e) {}
}
</script>
<style scoped>
.page-header { margin-bottom:16px; }
.page-header h2 { margin:0; }
</style>
