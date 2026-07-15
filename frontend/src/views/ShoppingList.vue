<template>
  <div class="shopping-list-page">
    <div class="page-header">
      <h2>🛒 采购清单</h2>
      <div>
        <el-button @click="showAddDialog = true" :disabled="!authStore.currentFamily">添加商品</el-button>
        <el-button @click="batchAddFromLowStock">一键加入待补货商品</el-button>
        <el-button :disabled="!hasPurchased" @click="handleClearPurchased">清空已购</el-button>
        <el-dropdown style="margin-left:8px;">
          <el-button type="primary">导出 <el-icon><Download /></el-icon></el-button>
          <template #dropdown>
            <el-dropdown-item @click="handleExport('csv')">导出 CSV</el-dropdown-item>
            <el-dropdown-item @click="handleExport('xlsx')">导出 Excel</el-dropdown-item>
            <el-dropdown-item @click="handleExport('pdf')">导出 PDF</el-dropdown-item>
          </template>
        </el-dropdown>
      </div>
    </div>
    <el-card style="margin-bottom:16px;">
      <el-radio-group v-model="filterStatus" @change="loadItems" size="small">
        <el-radio-button label="">全部</el-radio-button>
        <el-radio-button label="pending">待采购</el-radio-button>
        <el-radio-button label="purchased">已购</el-radio-button>
      </el-radio-group>
    </el-card>
    <el-card>
      <el-table :data="items" v-loading="loading" empty-text="采购清单是空的">
        <el-table-column label="商品" min-width="150"><template #default="{row}">{{ row.product_name || row.product_id }}</template></el-table-column>
        <el-table-column prop="category_name" label="分类" width="100" />
        <el-table-column prop="quantity" label="数量" width="80" />
        <el-table-column label="优选渠道" width="120"><template #default="{row}">{{ row.plan_channel_name || '-' }}</template></el-table-column>
        <el-table-column label="价格" width="100"><template #default="{row}">{{ row.plan_price ? '¥'+row.plan_price : (row.estimated_price ? '¥'+row.estimated_price : '-') }}</template></el-table-column>
        <el-table-column label="状态" width="100"><template #default="{row}"><el-tag :type="row.status === 'purchased' ? 'success' : row.status === 'cancelled' ? 'info' : 'warning'">{{ {pending:'待采购',purchased:'已购',cancelled:'已取消'}[row.status] }}</el-tag></template></el-table-column>
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{row}">
            <el-button v-if="row.status==='pending'" size="small" type="success" @click="markPurchased(row)">购买</el-button>
            <el-button v-if="row.status==='pending'" size="small" @click="editItem(row)">编辑</el-button>
            <el-button size="small" type="danger" @click="handleDelete(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
    <el-dialog v-model="showAddDialog" title="添加商品到清单" width="500px">
      <el-form :model="addForm" ref="addFormRef" label-width="80px">
        <el-form-item label="商品" prop="product_id" :rules="[{required:true,message:'请选择商品'}]">
          <el-select v-model="addForm.product_id" filterable remote :remote-method="searchProducts" :loading="searching" style="width:100%" placeholder="搜索商品">
            <el-option v-for="p in searchResults" :key="p.id" :label="(p.brand?p.brand+' ':'')+p.name" :value="p.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="数量"><el-input-number v-model="addForm.quantity" :min="0.01" /></el-form-item>
        <el-form-item label="备注"><el-input v-model="addForm.notes" /></el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showAddDialog = false">取消</el-button>
        <el-button type="primary" @click="handleAdd" :loading="adding">添加</el-button>
      </template>
    </el-dialog>
  </div>
</template>
<script setup>
import { ref, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { useAuthStore } from '@/stores/auth'
import { shoppingAPI, productsAPI } from '@/api/auth'
const authStore = useAuthStore()
const loading = ref(false), searching = ref(false), adding = ref(false)
const items = ref([]), filterStatus = ref('')
const showAddDialog = ref(false)
const addForm = ref({ product_id: '', quantity: 1, notes: '' })
const searchResults = ref([])
const hasPurchased = computed(() => items.value.some(i => i.status === 'purchased'))
async function loadItems() {
  if (!authStore.currentFamily) return
  loading.value = true
  try {
    const params = filterStatus.value ? { status: filterStatus.value, page_size: 200 } : { page_size: 200 }
    const res = await shoppingAPI.list(authStore.currentFamily.id, params)
    items.value = res.items || []
  } catch(e) { console.error(e) }
  finally { loading.value = false }
}
async function searchProducts(q) {
  if (!q) return
  searching.value = true
  try {
    const res = await productsAPI.list(authStore.currentFamily.id, { keyword: q, page_size: 20 })
    searchResults.value = res.items || []
  } catch(e) {}
  finally { searching.value = false }
}
async function handleAdd() {
  adding.value = true
  try {
    await shoppingAPI.add(authStore.currentFamily.id, addForm.value)
    ElMessage.success('已添加')
    showAddDialog.value = false
    addForm.value = { product_id: '', quantity: 1, notes: '' }
    await loadItems()
  } catch(e) {}
  finally { adding.value = false }
}
async function markPurchased(row) {
  try {
    await shoppingAPI.markPurchased(row.id, null)
    ElMessage.success('已标记为已购买')
    await loadItems()
  } catch(e) {}
}
async function editItem(row) {}
async function handleDelete(row) {
  await ElMessageBox.confirm('确定从清单移除？','确认')
  try { await shoppingAPI.delete(row.id); ElMessage.success('已移除'); await loadItems() }
  catch(e) {}
}
async function handleClearPurchased() {
  await ElMessageBox.confirm('确定清空所有已购项目？','确认')
  try { await shoppingAPI.clearPurchased(authStore.currentFamily.id); ElMessage.success('已清空'); await loadItems() }
  catch(e) {}
}
async function batchAddFromLowStock() {
  try {
    const lowStock = await productsAPI.getLowStock(authStore.currentFamily.id)
    if (!lowStock.length) { ElMessage.info('没有待补货商品'); return }
    const batchData = { items: lowStock.map(p => ({ product_id: p.id, quantity: 1 })) }
    await shoppingAPI.batchAdd(authStore.currentFamily.id, batchData)
    ElMessage.success(`已添加 ${lowStock.length} 个商品到清单`)
    await loadItems()
  } catch(e) {}
}
function handleExport(fmt) {
  window.open(`/api/v1/export/shopping-list/${authStore.currentFamily.id}?fmt=${fmt}&status=${filterStatus.value}`, '_blank')
}
onMounted(loadItems)
</script>
<style scoped>
.page-header { display:flex; justify-content:space-between; align-items:center; margin-bottom:16px; }
.page-header h2 { margin:0; }
</style>
