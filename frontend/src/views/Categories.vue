<template>
  <div class="categories-page">
    <div class="page-header">
      <h2>📂 分类管理</h2>
      <div>
        <el-button type="primary" @click="initDefaults" :disabled="!authStore.currentFamily">初始化默认分类</el-button>
        <el-button type="primary" @click="showDialog = true" :disabled="!authStore.currentFamily">新增分类</el-button>
      </div>
    </div>
    <el-card>
      <el-table :data="categoryTree" row-key="id" default-expand-all :tree-props="{children:'children'}" v-loading="loading" empty-text="暂无分类，请先初始化或添加">
        <el-table-column prop="emoji" label="" width="50"><template #default="{row}">{{ row.emoji || '📦' }}</template></el-table-column>
        <el-table-column prop="name" label="分类名称" min-width="150" />
        <el-table-column prop="sort_order" label="排序" width="80" />
        <el-table-column prop="is_active" label="状态" width="80"><template #default="{row}"><el-tag :type="row.is_active ? 'success' : 'info'">{{ row.is_active ? '启用' : '禁用' }}</el-tag></template></el-table-column>
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{row}">
            <el-button size="small" @click="editCategory(row)">编辑</el-button>
            <el-button size="small" type="danger" @click="handleDelete(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
    <el-dialog v-model="showDialog" :title="editingId ? '编辑分类' : '新增分类'" width="400px">
      <el-form :model="form" :rules="rules" ref="formRef" label-width="80px">
        <el-form-item label="名称" prop="name"><el-input v-model="form.name" /></el-form-item>
        <el-form-item label="emoji"><el-input v-model="form.emoji" placeholder="如 🧹" maxlength="10" /></el-form-item>
        <el-form-item label="排序"><el-input-number v-model="form.sort_order" :min="0" /></el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showDialog = false">取消</el-button>
        <el-button type="primary" @click="handleSave" :loading="saving">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>
<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { useAuthStore } from '@/stores/auth'
import { categoriesAPI } from '@/api/auth'
const authStore = useAuthStore()
const loading = ref(false)
const saving = ref(false)
const showDialog = ref(false)
const editingId = ref('')
const categoryTree = ref([])
const formRef = ref(null)
const form = reactive({ name: '', emoji: '', sort_order: 0, parent_id: null })
const rules = { name: [{ required: true, message: '请输入分类名称', trigger: 'blur' }] }
async function loadTree() {
  if (!authStore.currentFamily) return
  loading.value = true
  try { categoryTree.value = await categoriesAPI.getTree(authStore.currentFamily.id) }
  catch(e) { console.error(e) }
  finally { loading.value = false }
}
async function initDefaults() {
  await ElMessageBox.confirm('将创建6个默认分类（洗护清洁、食品零食等），确定继续？', '提示')
  saving.value = true
  try {
    await categoriesAPI.initDefaults(authStore.currentFamily.id)
    ElMessage.success('默认分类创建成功')
    await loadTree()
  } catch(e) {}
  finally { saving.value = false }
}
function editCategory(row) {
  editingId.value = row.id
  form.name = row.name
  form.emoji = row.emoji || ''
  form.sort_order = row.sort_order
  form.parent_id = row.parent_id
  showDialog.value = true
}
async function handleSave() {
  const valid = await formRef.value.validate().catch(() => false)
  if (!valid) return
  saving.value = true
  try {
    const data = { name: form.name, emoji: form.emoji, sort_order: form.sort_order }
    if (editingId.value) {
      await categoriesAPI.update(editingId.value, data)
      ElMessage.success('分类已更新')
    } else {
      await categoriesAPI.create(authStore.currentFamily.id, data)
      ElMessage.success('分类已创建')
    }
    showDialog.value = false
    resetForm()
    await loadTree()
  } catch(e) {}
  finally { saving.value = false }
}
async function handleDelete(row) {
  await ElMessageBox.confirm(`确定删除分类「${row.name}」？`, '确认')
  try {
    await categoriesAPI.delete(row.id)
    ElMessage.success('已删除')
    await loadTree()
  } catch(e) {}
}
function resetForm() {
  editingId.value = ''
  form.name = ''
  form.emoji = ''
  form.sort_order = 0
  form.parent_id = null
}
onMounted(loadTree)
</script>
<style scoped>
.page-header { display:flex; justify-content:space-between; align-items:center; margin-bottom:16px; }
.page-header h2 { margin:0; }
</style>
