 import { defineStore } from 'pinia'
 import { ref, computed } from 'vue'
 import { authAPI, familiesAPI } from '@/api/auth'
 
 export const useAuthStore = defineStore('auth', () => {
   const user = ref(JSON.parse(localStorage.getItem('user_info') || 'null'))
   const token = ref(localStorage.getItem('access_token') || '')
   const currentFamily = ref(JSON.parse(localStorage.getItem('current_family') || 'null'))
   const families = ref([])
 
   const isLoggedIn = computed(() => !!token.value)
   const isAdmin = computed(() => {
     if (!currentFamily.value || !user.value) return false
     return true  // Will check role from API
   })
 
   async function login(credentials) {
     const res = await authAPI.login(credentials)
     token.value = res.access_token
     user.value = res.user
     localStorage.setItem('access_token', res.access_token)
     localStorage.setItem('user_info', JSON.stringify(res.user))
     return res
   }
 
   async function register(data) {
     const res = await authAPI.register(data)
     token.value = res.access_token
     user.value = res.user
     localStorage.setItem('access_token', res.access_token)
     localStorage.setItem('user_info', JSON.stringify(res.user))
     return res
   }
 
   async function loadFamilies() {
     const res = await familiesAPI.list()
     families.value = res
     if (!currentFamily.value && res.length > 0) {
       currentFamily.value = res[0]
       localStorage.setItem('current_family', JSON.stringify(res[0]))
     }
     return res
   }
 
   function setCurrentFamily(family) {
     currentFamily.value = family
     localStorage.setItem('current_family', JSON.stringify(family))
   }
 
   function logout() {
     token.value = ''
     user.value = null
     currentFamily.value = null
     families.value = []
     localStorage.removeItem('access_token')
     localStorage.removeItem('user_info')
     localStorage.removeItem('current_family')
   }
 
   return { user, token, currentFamily, families, isLoggedIn, isAdmin, login, register, loadFamilies, setCurrentFamily, logout }
 })
