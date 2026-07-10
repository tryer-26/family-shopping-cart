 import { defineStore } from 'pinia'
 import { ref } from 'vue'
 import { shoppingAPI } from '@/api/auth'
 
 export const useShoppingStore = defineStore('shopping', () => {
   const pendingCount = ref(0)
   const lowStockCount = ref(0)
   const currentItems = ref([])
 
   async function loadStats(familyId) {
     try {
       const res = await shoppingAPI.getStats(familyId)
       pendingCount.value = res.pending_count || 0
     } catch (e) {
       console.error('Failed to load shopping stats:', e)
     }
   }
 
   function setLowStockCount(count) {
     lowStockCount.value = count
   }
 
   return { pendingCount, lowStockCount, currentItems, loadStats, setLowStockCount }
 })
