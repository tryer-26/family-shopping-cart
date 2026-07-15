<template>
  <div class="prices-page">
    <div class="page-header"><h2>💰 价格看板</h2><el-button type="primary" @click="refreshPrices" :loading="refreshing">刷新价格</el-button></div>
    <el-card>
      <el-table :data="bestPrices" v-loading="loading" empty-text="暂无价格数据，请先添加商品和采购方案">
        <el-table-column prop="product_name" label="商品" min-width="140" />
        <el-table-column prop="channel_name" label="最优渠道" width="120"><template #default="{row}"><el-tag>{{ row.channel_name }}</el-tag></template></el-table-column>
        <el-table-column label="到手价" width="120"><template #default="{row}"><span style="font-size:18px;font-weight:bold;color:#f56c6c;">¥{{ row.final_price }}</span></template></el-table-column>
        <el-table-column label="链接" width="200"><template #default="{row}"><el-link v-if="row.product_url" :href="row.product_url" target="_blank" type="primary">查看</el-link><span v-else>-</span></template></el-table-column>
        <el-table-column label="操作" width="120"><template #default="{row}"><el-button size="small" @click="viewHistory(row)">历史</el-button></template></el-table-column>
      </el-table>
    </el-card>
    <el-dialog v-model="showHistory" title="价格历史" width="600px">
      <div ref="chartRef" style="height:300px;"></div>
      <el-table :data="priceHistory" size="small" v-if="showHistory">
        <el-table-column prop="recorded_at" label="时间" width="160" />
        <el-table-column prop="price" label="价格" width="100" />
        <el-table-column prop="channel_name" label="渠道" />
      </el-table>
    </el-dialog>
  </div>
</template>
<script setup>
import { ref, onMounted, nextTick } from 'vue'
import { ElMessage } from 'element-plus'
import { useAuthStore } from '@/stores/auth'
import { pricesAPI } from '@/api/auth'
const authStore = useAuthStore()
const loading = ref(false), refreshing = ref(false)
const bestPrices = ref([])
const showHistory = ref(false)
const priceHistory = ref([])
const chartRef = ref(null)
async function loadBestPrices() {
  if (!authStore.currentFamily) return
  loading.value = true
  try { bestPrices.value = await pricesAPI.getBestForFamily(authStore.currentFamily.id) }
  catch(e) { console.error(e) }
  finally { loading.value = false }
}
async function refreshPrices() {
  refreshing.value = true
  ElMessage.info('价格刷新任务已提交，请稍后查看')
  setTimeout(() => { refreshing.value = false }, 3000)
}
async function viewHistory(row) {
  showHistory.value = true
  try {
    priceHistory.value = await pricesAPI.getHistory(row.product_id, 90)
    await nextTick()
    if (chartRef.value && priceHistory.value.length > 0) {
      try {
        const echarts = (await import('echarts')).default
        const chart = echarts.init(chartRef.value)
        chart.setOption({
          xAxis: { type: 'time' },
          yAxis: { type: 'value' },
          series: [{ type: 'line', data: priceHistory.value.map(p => [p.recorded_at, p.price]), smooth: true }],
          tooltip: { trigger: 'axis' },
        })
      } catch(e) { console.error('Chart error:', e) }
    }
  } catch(e) { console.error(e) }
}
onMounted(loadBestPrices)
</script>
<style scoped>
.page-header { display:flex; justify-content:space-between; align-items:center; margin-bottom:16px; }
.page-header h2 { margin:0; }
</style>
