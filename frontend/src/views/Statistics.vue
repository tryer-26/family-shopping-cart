<template>
  <div class="statistics-page">
    <div class="page-header"><h2>📊 数据报表</h2></div>
    <el-row :gutter="16" style="margin-bottom:16px;">
      <el-col :span="6"><el-card shadow="hover"><div class="stat-card"><div class="stat-value" style="color:#409eff;">{{ monthlyData.total_spending || 0 }}</div><div class="stat-label">{{ currentYear }}年{{ currentMonth }}月总支出</div></div></el-card></el-col>
      <el-col :span="6"><el-card shadow="hover"><div class="stat-card"><div class="stat-value" style="color:#67c23a;">{{ monthlyData.total_items || 0 }}</div><div class="stat-label">{{ currentYear }}年{{ currentMonth }}月采购项</div></div></el-card></el-col>
    </el-row>
    <el-row :gutter="16">
      <el-col :span="12"><el-card><template #header><span>分类支出占比</span></template><div ref="categoryChartRef" style="height:300px;"></div><div v-if="!hasCategoryData" style="text-align:center;color:#909399;padding:80px 0;">暂无数据</div></el-card></el-col>
      <el-col :span="12"><el-card><template #header><span>月度支出趋势</span></template><div ref="trendChartRef" style="height:300px;"></div><div v-if="yearlyData.length === 0" style="text-align:center;color:#909399;padding:80px 0;">暂无数据</div></el-card></el-col>
    </el-row>
  </div>
</template>
<script setup>
import { ref, computed, onMounted, nextTick, watch } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { statisticsAPI } from '@/api/auth'
const authStore = useAuthStore()
const currentYear = ref(2026), currentMonth = ref(new Date().getMonth() + 1)
const monthlyData = ref({})
const yearlyData = ref([])
const categoryChartRef = ref(null), trendChartRef = ref(null)
const hasCategoryData = computed(() => (monthlyData.value.category_breakdown || []).length > 0)
async function loadData() {
  if (!authStore.currentFamily) return
  const fid = authStore.currentFamily.id
  try {
    monthlyData.value = await statisticsAPI.monthly(fid, currentYear.value, currentMonth.value)
    yearlyData.value = await statisticsAPI.yearly(fid, currentYear.value)
    await nextTick()
    renderCharts()
  } catch(e) { console.error(e) }
}
function renderCharts() {
  try {
    import('echarts').then(({ default: echarts }) => {
      if (categoryChartRef.value && hasCategoryData.value) {
        const catChart = echarts.init(categoryChartRef.value)
        catChart.setOption({
          tooltip: { trigger: 'item', formatter: '{b}: ¥{c} ({d}%)' },
          series: [{
            type: 'pie', radius: ['40%', '70%'],
            data: monthlyData.value.category_breakdown.map(c => ({ name: c.name, value: c.total })),
            label: { show: true, formatter: '{b}\n¥{c}' },
          }],
        })
      }
      if (trendChartRef.value && yearlyData.value.length > 0) {
        const trendChart = echarts.init(trendChartRef.value)
        trendChart.setOption({
          xAxis: { type: 'category', data: ['1月','2月','3月','4月','5月','6月','7月','8月','9月','10月','11月','12月'] },
          yAxis: { type: 'value' },
          series: [{ type: 'bar', data: yearlyData.value.map(m => m.total_spending), itemStyle: { color: '#409eff' } }],
          tooltip: { trigger: 'axis' },
        })
      }
    })
  } catch(e) {}
}
watch(() => authStore.currentFamily, loadData)
onMounted(loadData)
</script>
<style scoped>
.page-header { margin-bottom:16px; }
.page-header h2 { margin:0; }
.stat-card { text-align:center; padding:8px 0; }
.stat-value { font-size:28px; font-weight:bold; }
.stat-label { font-size:13px; color:#909399; margin-top:4px; }
</style>
