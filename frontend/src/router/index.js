import { createRouter, createWebHashHistory } from 'vue-router'

const routes = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/Login.vue'),
    meta: { requiresAuth: false },
  },
  {
    path: '/register',
    name: 'Register',
    component: () => import('@/views/Register.vue'),
    meta: { requiresAuth: false },
  },
  {
    path: '/',
    component: () => import('@/components/Layout.vue'),
    meta: { requiresAuth: true },
    redirect: '/dashboard',
    children: [
      { path: 'dashboard', name: 'Dashboard', component: () => import('@/views/Dashboard.vue'), meta: { title: '仪表盘', icon: 'Odometer' } },
      { path: 'categories', name: 'Categories', component: () => import('@/views/Categories.vue'), meta: { title: '分类管理', icon: 'Grid' } },
      { path: 'products', name: 'Products', component: () => import('@/views/Products.vue'), meta: { title: '商品库', icon: 'Goods' } },
      { path: 'shopping-list', name: 'ShoppingList', component: () => import('@/views/ShoppingList.vue'), meta: { title: '采购清单', icon: 'ShoppingCart' } },
      { path: 'prices', name: 'Prices', component: () => import('@/views/Prices.vue'), meta: { title: '价格看板', icon: 'Coin' } },
      { path: 'coupons', name: 'Coupons', component: () => import('@/views/Coupons.vue'), meta: { title: '优惠券', icon: 'Ticket' } },
      { path: 'ocr-search', name: 'OCRSearch', component: () => import('@/views/OCRSearch.vue'), meta: { title: '识图搜品', icon: 'Camera' } },
      { path: 'families', name: 'Families', component: () => import('@/views/Families.vue'), meta: { title: '家庭管理', icon: 'UserFilled' } },
      { path: 'statistics', name: 'Statistics', component: () => import('@/views/Statistics.vue'), meta: { title: '数据报表', icon: 'DataAnalysis' } },
      { path: 'settings', name: 'Settings', component: () => import('@/views/Settings.vue'), meta: { title: '系统设置', icon: 'Setting' } },
    ],
  },
]

const router = createRouter({
  history: createWebHashHistory(),
  routes,
})

// Navigation guard
router.beforeEach((to, from, next) => {
  const token = localStorage.getItem('access_token')
  if (to.meta.requiresAuth && !token) {
    next('/login')
  } else if (!to.meta.requiresAuth && token && to.path === '/login') {
    next('/dashboard')
  } else {
    next()
  }
})

export default router
