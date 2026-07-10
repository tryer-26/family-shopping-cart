<template>
  <div class="products-page">
    <div class="page-header">
      <h2>📦 商品库</h2>
      <el-button type="primary" @click="showDialog = true" :disabled="!authStore.currentFamily">新增商品</el-button>
    </div>
    <el-card style="margin-bottom:16px;">
      <el-form :inline="true" :model="filters" size="small">
        <el-form-item label="分类"><el-select v-model="filters.category_id" placeholder="全部分类" clearable style="width:150px"><el-option v-for="c in categories" :key="c.id" :label="(c.emoji||'')+' '+c.name" :value="c.id" /></el-select></el-form-item>
        <el-form-item label="搜索"><el-input v-model="filters.keyword" placeholder="名称/品牌" clearable style="width:200px" @keyup.enter="loadProducts" /></el-form-item>
        <el-form-item><el-button type="primary" @click="loadProducts">查询</el-button><el-button @click="resetFilters">重置</el-button></el-form-item>
      </el-form>
    </el-card>
    <el-card>
      <el-table :data="products" v-loading="loading" empty-text="暂无商品">
        <el-table-column prop="name" label="名称" min-width="140" />
        <el-table-column prop="brand" label="品牌" width="100" />
        <el-table-column prop="specification" label="规格" width="100" />
        <el-table-column prop="current_stock" label="库存" width="70" />
        <el-table-column prop="monthly_consumption" label="月均消耗" width="100" />
        <el-table-column label="评分" width="80"><template #default="{row}"><el-rate :model-value="row.rating" disabled size="small" /></template></el-table-column>
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{row}">
            <el-button size="small" @click="editProduct(row)">编辑</el-button>
            <el-button size="small" @click="addToCart(row)">加入清单</el-button>
            <el-button size="small" type="danger" @click="handleDelete(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
      <el-pagination v-if="total > pageSize" v-model:current-page="page" :page-size="pageSize" :total="total" layout="prev,pager,next" @current-change="loadProducts" style="margin-top:16px;justify-content:center;" />
    </el-card>
    <el-dialog v-model="showDialog" :title="editingId ? '编辑商品' : '新增商品'" width="600px">
      <el-form :model="form" ref="formRef" label-width="100px" :rules="rules">
        <el-form-item label="分类" prop="category_id"><el-select v-model="form.category_id" style="width:100%"><el-option v-for="c in categories" :key="c.id" :label="(c.emoji||'')+' '+c.name" :value="c.id" /></el-select></el-form-item>
        <el-row :gutter="12">
          <el-col :span="12"><el-form-item label="名称" prop="name"><el-input v-model="form.name" /></el-form-item></el-col>
          <el-col :span="12"><el-form-item label="品牌"><el-input v-model="form.brand" /></el-form-item></el-col>
        </el-row>
        <el-row :gutter="12">
          <el-col :span="8"><el-form-item label="规格"><el-input v-model="form.specification" /></el-form-item></el-col>
          <el-col :span="8"><el-form-item label="单位"><el-input v-model="form.unit" /></el-form-item></el-col>
          <el-col :span="8"><el-form-item label="存放位置"><el-input v-model="form.storage_location" /></el-form-item></el-col>
        </el-row>
        <el-row :gutter="12">
          <el-col :span="12"><el-form-item label="当前库存"><el-input-number v-model="form.current_stock" :min="0" style="width:100%" /></el-form-item></el-col>
          <el-col :span="12"><el-form-item label="月均消耗"><el-input-number v-model="form.monthly_consumption" :min="0" style="width:100%" /></el-form-item></el-col>
        </el-row>
        <el-form-item label="备注"><el-input v-model="form.notes" type="textarea" :rows="2" /></el-form-item>
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
import { productsAPI, categoriesAPI, shoppingAPI } from '@/api/auth'
const authStore = useAuthStore()
const loading = ref(false), saving = ref(false), showDialog = ref(false), editingId = ref('')
const products = ref([]), categories = ref([]), total = ref(0), page = ref(1), pageSize = ref(20)
const formRef = ref(null)
const filters = reactive({ category_id: '', keyword: '' })
const form = reactive({ category_id: '', name: '', brand: '', specification: '', unit: '个', current_stock: 0, monthly_consumption: 0, storage_location: '', notes: '' })
const rules = { category_id: [{ required: true, message: '请选择分类', trigger: 'change' }], name: [{ required: true, message: '请输入名称', trigger: 'blur' }] }
async function loadCategories() {
  if (!authStore.currentFamily) return
  try { categories.value = await categoriesAPI.getTree(authStore.currentFamily.id) }
  catch(e) {}
}
async function loadProducts() {
  if (!authStore.currentFamily) return
  loading.value = true
  try {
    const res = await productsAPI.list(authStore.currentFamily.id, { ...filters, page: page.value, page_size: pageSize.value })
    products.value = res.items || []
    total.value = res.total || 0
  } catch(e) { console.error(e) }
  finally { loading.value = false }
}
function resetFilters() { filters.category_id = ''; filters.keyword = ''; page.value = 1; loadProducts() }
function editProduct(row) {
  editingId.value = row.id
  Object.assign(form, { category_id: row.category_id, name: row.name, brand: row.brand || '', specification: row.specification || '', unit: row.unit, current_stock: row.current_stock, monthly_consumption: row.monthly_consumption, storage_location: row.storage_location || '', notes: row.notes || '' })
  showDialog.value = true
}
async function handleSave() {
  const valid = await formRef.value.validate().catch(() => false)
  if (!valid) return
  saving.value = true
  try {
    if (editingId.value) {
      await productsAPI.update(editingId.value, form)
      ElMessage.success('已更新')
    } else {
      await productsAPI.create(authStore.currentFamily.id, form)
      ElMessage.success('已创建')
    }
    showDialog.value = false; editingId.value = ''
    await loadProducts()
  } catch(e) {}
  finally { saving.value = false }
}
async function addToCart(row) {
  try {
    await shoppingAPI.add(authStore.currentFamily.id, { product_id: row.id, quantity: 1 })
    ElMessage.success('已加入采购清单')
  } catch(e) {}
}
async function handleDelete(row) {
  await ElMessageBox.confirm(`确定删除「${row.name}」？`, '确认')
  try { await productsAPI.delete(row.id); ElMessage.success('已删除'); await loadProducts() }
  catch(e) {}
}
onMounted(() => { loadCategories(); loadProducts() })
</script>
<style scoped>
.page-header { display:flex; justify-content:space-between; align-items:center; margin-bottom:16px; }
.page-header h2 { margin:0; }
</style>
