<template>
  <div class="dashboard">
    <h2 style="margin-bottom: 20px;">📊 仪表盘</h2>
    <div v-if="!authStore.currentFamily" style="text-align:center;padding:60px 0;color:#909399;">
      <p style="font-size:18px;margin-bottom:16px;">请先创建或加入一个家庭</p>
      <el-button type="primary" @click="$router.push('/families')">前往家庭管理</el-button>
    </div>
    <template v-else>
      <el-row :gutter="16" style="margin-bottom:16px;">
        <el-col :span="6"><el-card shadow="hover"><div class="stat-card"><div class="stat-icon" style="background:#e6f7ff;"><el-icon style="font-size:28px;color:#1890ff;"><Goods /></el-icon></div><div class="stat-info"><div class="stat-value">{{ stats.total_products || 0 }}</div><div class="stat-label">商品总数</div></div></div></el-card></el-col>
        <el-col :span="6"><el-card shadow="hover"><div class="stat-card"><div class="stat-icon" style="background:#f6ffed;"><el-icon style="font-size:28px;color:#52c41a;"><Warning /></el-icon></div><div class="stat-info"><div class="stat-value" style="color:#f56c6c;">{{ stats.low_stock_count || 0 }}</div><div class="stat-label">待补货</div></div></div></el-card></el-col>
        <el-col :span="6"><el-card shadow="hover"><div class="stat-card"><div class="stat-icon" style="background:#fff7e6;"><el-icon style="font-size:28px;color:#fa8c16;"><ShoppingCart /></el-icon></div><div class="stat-info"><div class="stat-value">{{ stats.pending_count || 0 }}</div><div class="stat-label">待采购</div></div></div></el-card></el-col>
        <el-col :span="6"><el-card shadow="hover"><div class="stat-card"><div class="stat-icon" style="background:#f0f5ff;"><el-icon style="font-size:28px;color:#2f54eb;"><Coin /></el-icon></div><div class="stat-info"><div class="stat-value">{{ expiringCoupons.length }}</div><div class="stat-label">即将过期优惠券</div></div></div></el-card></el-col>
      </el-row>
      <el-row :gutter="16">
        <el-col :span="12"><el-card><template #header><span>🔔 待补货商品</span></template><el-table :data="lowStock" style="width:100%" v-loading="loading"><el-table-column prop="name" label="商品" min-width="120" /><el-table-column prop="current_stock" label="库存" width="80" /><el-table-column prop="monthly_consumption" label="月均消耗" width="100" /><el-table-column label="操作" width="100"><template #default="{row}"><el-button size="small" type="primary" link @click="addToCart(row)">加入清单</el-button></template></el-table-column></el-table><div v-if="!lowStock.length && !loading" style="text-align:center;padding:20px;color:#909399;">暂无待补货商品</div></el-card></el-col>
        <el-col :span="12"><el-card><template #header><span>📢 即将过期优惠券</span></template><el-table :data="expiringCoupons" style="width:100%" v-loading="loading"><el-table-column prop="name" label="名称" min-width="120" /><el-table-column prop="face_value" label="面额" width="80" /><el-table-column prop="days_until_expiry" label="剩余天数" width="80"><template #default="{row}"><el-tag :type="row.days_until_expiry <= 3 ? 'danger' : 'warning'">{{ row.days_until_expiry }}天</el-tag></template></el-table-column></el-table><div v-if="!expiringCoupons.length && !loading" style="text-align:center;padding:20px;color:#909399;">暂无即将过期优惠券</div></el-card></el-col>
      </el-row>
    </template>
  </div>
</template>
<script setup>
import { ref, onMounted, computed } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { useShoppingStore } from '@/stores/shopping'
import { statisticsAPI, productsAPI, couponsAPI, shoppingAPI } from '@/api/auth'
const authStore = useAuthStore()
const shoppingStore = useShoppingStore()
const loading = ref(false)
const stats = ref({})
const lowStock = ref([])
const expiringCoupons = ref([])
async function loadData() {
  if (!authStore.currentFamily) return
  loading.value = true
  try {
    const familyId = authStore.currentFamily.id
    stats.value = await statisticsAPI.dashboard(familyId)
    lowStock.value = await productsAPI.getLowStock(familyId)
    try { expiringCoupons.value = await couponsAPI.getExpiring(familyId) } catch(e) {}
    shoppingStore.setLowStockCount(stats.value.low_stock_count || 0)
    shoppingStore.loadStats(familyId)
  } catch(e) { console.error(e) }
  finally { loading.value = false }
}
async function addToCart(product) {
  try {
    await shoppingAPI.add(authStore.currentFamily.id, { product_id: product.id, quantity: 1 })
    ElMessage.success('已加入采购清单')
  } catch(e) {}
}
onMounted(loadData)
</script>
<style scoped>
.stat-card { display:flex; align-items:center; gap:16px; }
.stat-icon { width:56px; height:56px; border-radius:12px; display:flex; align-items:center; justify-content:center; }
.stat-value { font-size:28px; font-weight:bold; color:#303133; }
.stat-label { font-size:13px; color:#909399; margin-top:4px; }
</style>
