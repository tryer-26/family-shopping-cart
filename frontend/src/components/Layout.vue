<template>
  <el-container class="layout-container">
    <el-aside :width="isCollapse ? '64px' : '220px'" class="layout-aside">
      <div class="logo-area">
        <span v-if="!isCollapse" class="logo-text">🛒 HPMS</span>
        <span v-else class="logo-text-mini">🛒</span>
      </div>
      <el-menu
        :default-active="route.path"
        :collapse="isCollapse"
        :router="true"
        background-color="#1d1e1f"
        text-color="#bfcbd9"
        active-text-color="#409eff"
      >
        <el-menu-item index="/dashboard">
          <el-icon><Odometer /></el-icon>
          <span>仪表盘</span>
        </el-menu-item>
        <el-menu-item index="/categories">
          <el-icon><Grid /></el-icon>
          <span>分类管理</span>
        </el-menu-item>
        <el-menu-item index="/products">
          <el-icon><Goods /></el-icon>
          <span>商品库</span>
        </el-menu-item>
        <el-menu-item index="/shopping-list">
          <el-icon><ShoppingCart /></el-icon>
          <span>采购清单</span>
        </el-menu-item>
        <el-menu-item index="/prices">
          <el-icon><Coin /></el-icon>
          <span>价格看板</span>
        </el-menu-item>
        <el-menu-item index="/coupons">
          <el-icon><Ticket /></el-icon>
          <span>优惠券</span>
        </el-menu-item>
        <el-menu-item index="/ocr-search">
          <el-icon><Camera /></el-icon>
          <span>识图搜品</span>
        </el-menu-item>
        <el-menu-item index="/families">
          <el-icon><UserFilled /></el-icon>
          <span>家庭管理</span>
        </el-menu-item>
        <el-menu-item index="/statistics">
          <el-icon><DataAnalysis /></el-icon>
          <span>数据报表</span>
        </el-menu-item>
        <el-menu-item index="/settings">
          <el-icon><Setting /></el-icon>
          <span>系统设置</span>
        </el-menu-item>
      </el-menu>
    </el-aside>
    <el-container>
      <el-header class="layout-header">
        <div class="header-left">
          <el-button @click="isCollapse = !isCollapse" text>
            <el-icon><Fold v-if="!isCollapse" /><Expand v-else /></el-icon>
          </el-button>
          <el-select
            v-if="authStore.families.length > 0"
            v-model="selectedFamilyId"
            @change="switchFamily"
            size="small"
            style="width: 180px; margin-left: 12px;"
          >
            <el-option
              v-for="f in authStore.families"
              :key="f.id"
              :label="(f.emoji || '🏠') + ' ' + f.name"
              :value="f.id"
            />
          </el-select>
        </div>
        <div class="header-right">
          <el-badge :value="shoppingStore.pendingCount" :hidden="!shoppingStore.pendingCount" style="margin-right: 16px;">
            <el-button @click="$router.push('/shopping-list')" text size="small">
              <el-icon><ShoppingCart /></el-icon> 待采购
            </el-button>
          </el-badge>
          <el-dropdown @command="handleCommand">
            <span class="user-info">
              <el-avatar :size="32" :src="authStore.user?.avatar">{{ authStore.user?.username?.[0] }}</el-avatar>
              <span style="margin-left: 8px;">{{ authStore.user?.username }}</span>
            </span>
            <template #dropdown>
              <el-dropdown-item command="profile">个人信息</el-dropdown-item>
              <el-dropdown-item command="logout" divided>退出登录</el-dropdown-item>
            </template>
          </el-dropdown>
        </div>
      </el-header>
      <el-main class="layout-main">
        <router-view />
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useShoppingStore } from '@/stores/shopping'

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()
const shoppingStore = useShoppingStore()

const isCollapse = ref(false)
const selectedFamilyId = ref(authStore.currentFamily?.id || '')

onMounted(async () => {
  if (authStore.isLoggedIn) {
    try {
      await authStore.loadFamilies()
      if (!selectedFamilyId.value && authStore.families.length > 0) {
        selectedFamilyId.value = authStore.families[0].id
        authStore.setCurrentFamily(authStore.families[0])
      }
      if (selectedFamilyId.value) {
        await shoppingStore.loadStats(selectedFamilyId.value)
      }
    } catch (e) {
      console.error('Failed to load initial data:', e)
    }
  }
})

function switchFamily(familyId) {
  const family = authStore.families.find(f => f.id === familyId)
  if (family) {
    authStore.setCurrentFamily(family)
    shoppingStore.loadStats(familyId)
  }
}

function handleCommand(command) {
  if (command === 'logout') {
    authStore.logout()
    router.push('/login')
  } else if (command === 'profile') {
    // Navigate to profile page or show dialog
  }
}
</script>

<style scoped>
.layout-container {
  height: 100vh;
}
.layout-aside {
  background-color: #1d1e1f;
  overflow-y: auto;
  transition: width 0.3s;
}
.logo-area {
  height: 60px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
  font-size: 20px;
  font-weight: bold;
  border-bottom: 1px solid #2d2d2d;
}
.logo-text-mini {
  font-size: 24px;
}
.layout-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  background: #fff;
  border-bottom: 1px solid #e4e7ed;
  padding: 0 16px;
  height: 60px;
}
.header-left, .header-right {
  display: flex;
  align-items: center;
}
.user-info {
  display: flex;
  align-items: center;
  cursor: pointer;
}
.layout-main {
  background-color: #f5f7fa;
  padding: 20px;
  overflow-y: auto;
}
</style>
