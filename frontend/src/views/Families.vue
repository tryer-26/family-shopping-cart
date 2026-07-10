<template>
  <div class="families-page">
    <div class="page-header"><h2>👨‍👩‍👧‍👦 家庭管理</h2><el-button type="primary" @click="showCreateDialog=true">创建家庭</el-button></div>
    <el-row :gutter="16">
      <el-col v-for="family in authStore.families" :key="family.id" :span="8">
        <el-card :class="{ 'active-card': currentFamily?.id === family.id }" shadow="hover" style="margin-bottom:16px;cursor:pointer;" @click="switchFamily(family)">
          <div style="display:flex;align-items:center;justify-content:space-between;">
            <div>
              <span style="font-size:24px;">{{ family.emoji || '🏠' }}</span>
              <span style="font-size:16px;font-weight:bold;margin-left:8px;">{{ family.name }}</span>
            </div>
            <el-tag v-if="currentFamily?.id === family.id" type="primary" size="small">当前</el-tag>
          </div>
          <p style="color:#909399;font-size:13px;margin-top:8px;">{{ family.description || '暂无描述' }}</p>
        </el-card>
      </el-col>
    </el-row>
    <div v-if="authStore.families.length === 0" style="text-align:center;padding:60px 0;color:#909399;">
      <p style="font-size:16px;margin-bottom:16px;">还没有加入任何家庭</p>
      <el-button type="primary" @click="showCreateDialog=true">创建第一个家庭</el-button>
    </div>
    <el-card v-if="currentFamily" style="margin-top:16px;">
      <template #header><span>{{ currentFamily.emoji || '' }} {{ currentFamily.name }} - 成员管理</span></template>
      <el-table :data="members" v-loading="loadingMembers">
        <el-table-column label="头像" width="60"><template #default="{row}"><el-avatar :size="32" :src="row.avatar">{{ row.username?.[0] }}</el-avatar></template></el-table-column>
        <el-table-column prop="username" label="用户名" min-width="120" />
        <el-table-column prop="email" label="邮箱" min-width="160" />
        <el-table-column label="角色" width="100"><template #default="{row}"><el-tag :type="row.role==='admin'?'primary':'success'">{{ row.role==='admin'?'管理员':'成员' }}</el-tag></template></el-table-column>
        <el-table-column label="操作" width="150">
          <template #default="{row}">
            <el-button v-if="row.role==='member' && isCurrentFamilyAdmin" size="small" @click="setAdmin(row)">设为管理员</el-button>
            <el-button v-if="row.user_id !== authStore.user?.id && isCurrentFamilyAdmin" size="small" type="danger" @click="removeMember(row)">移除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
    <el-dialog v-model="showCreateDialog" title="创建家庭" width="400px">
      <el-form :model="createForm" ref="createFormRef" label-width="80px" :rules="createRules">
        <el-form-item label="名称" prop="name"><el-input v-model="createForm.name" /></el-form-item>
        <el-form-item label="描述"><el-input v-model="createForm.description" type="textarea" :rows="2" /></el-form-item>
        <el-form-item label="图标"><el-input v-model="createForm.emoji" maxlength="10" placeholder="🏠" /></el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showCreateDialog=false">取消</el-button>
        <el-button type="primary" @click="handleCreate" :loading="creating">创建</el-button>
      </template>
    </el-dialog>
  </div>
</template>
<script setup>
import { ref, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { useAuthStore } from '@/stores/auth'
import { familiesAPI } from '@/api/auth'
const authStore = useAuthStore()
const currentFamily = computed(() => authStore.currentFamily)
const loadingMembers = ref(false), creating = ref(false), showCreateDialog = ref(false)
const members = ref([])
const createForm = ref({ name:'', description:'', emoji:'' })
const createRules = { name:[{required:true,message:'请输入名称'}] }
const isCurrentFamilyAdmin = computed(() => true) // Will check from API
onMounted(() => { if (authStore.isLoggedIn) authStore.loadFamilies(); loadMembers() })
async function loadMembers() {
  if (!currentFamily.value) return
  loadingMembers.value = true
  try { members.value = await familiesAPI.getMembers(currentFamily.value.id) }
  catch(e) {}
  finally { loadingMembers.value = false }
}
function switchFamily(family) {
  authStore.setCurrentFamily(family)
  loadMembers()
}
async function handleCreate() {
  creating.value = true
  try {
    await familiesAPI.create(createForm.value)
    ElMessage.success('家庭已创建')
    showCreateDialog.value = false
    createForm.value = { name:'', description:'', emoji:'' }
    await authStore.loadFamilies()
  } catch(e) {}
  finally { creating.value = false }
}
async function setAdmin(row) {
  try {
    await familiesAPI.updateMemberRole(currentFamily.value.id, row.user_id, { role: 'admin' })
    ElMessage.success('已设为管理员')
    await loadMembers()
  } catch(e) {}
}
async function removeMember(row) {
  await ElMessageBox.confirm(`确定移除 ${row.username}？`,'确认')
  try { await familiesAPI.removeMember(currentFamily.value.id, row.user_id); ElMessage.success('已移除'); await loadMembers() }
  catch(e) {}
}
</script>
<style scoped>
.page-header { display:flex; justify-content:space-between; align-items:center; margin-bottom:16px; }
.page-header h2 { margin:0; }
.active-card { border-color: #409eff; }
</style>
