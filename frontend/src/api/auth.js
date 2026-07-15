import request from './request'

export const authAPI = {
  login(data) { return request.post('/auth/login', data) },
  register(data) { return request.post('/auth/register', data) },
  refreshToken(refresh_token) { return request.post('/auth/refresh', { refresh_token }) },
  getProfile() { return request.get('/auth/me') },
  updateProfile(data) { return request.put('/auth/me', data) },
  changePassword(data) { return request.put('/auth/password', data) },
}

export const familiesAPI = {
  list() { return request.get('/families') },
  get(id) { return request.get(`/families/${id}`) },
  create(data) { return request.post('/families', data) },
  update(id, data) { return request.put(`/families/${id}`, data) },
  delete(id) { return request.delete(`/families/${id}`) },
  getMembers(id) { return request.get(`/families/${id}/members`) },
  addMember(id, data) { return request.post(`/families/${id}/members`, data) },
  removeMember(familyId, userId) { return request.delete(`/families/${familyId}/members/${userId}`) },
  updateMemberRole(familyId, userId, data) { return request.put(`/families/${familyId}/members/${userId}/role`, data) },
}

export const categoriesAPI = {
  getTree(familyId) { return request.get(`/categories/family/${familyId}`) },
  create(familyId, data) { return request.post(`/categories/family/${familyId}`, data) },
  update(id, data) { return request.put(`/categories/${id}`, data) },
  delete(id) { return request.delete(`/categories/${id}`) },
  initDefaults(familyId) { return request.post(`/categories/family/${familyId}/init-defaults`) },
}

export const productsAPI = {
  list(familyId, params) { return request.get(`/products/family/${familyId}`, { params }) },
  get(id) { return request.get(`/products/${id}`) },
  create(familyId, data) { return request.post(`/products/family/${familyId}`, data) },
  update(id, data) { return request.put(`/products/${id}`, data) },
  delete(id) { return request.delete(`/products/${id}`) },
  getLowStock(familyId, thresholdDays = 3) { return request.get(`/products/low-stock/family/${familyId}`, { params: { threshold_days: thresholdDays } }) },
  createPlan(productId, data) { return request.post(`/products/${productId}/plans`, data) },
  updatePlan(planId, data) { return request.put(`/products/plans/${planId}`, data) },
  deletePlan(planId) { return request.delete(`/products/plans/${planId}`) },
  setPrimaryPlan(productId, planId) { return request.put(`/products/${productId}/plans/${planId}/set-primary`) },
}

export const pricesAPI = {
  createChannel(planId, data) { return request.post(`/prices/channels/plan/${planId}`, data) },
  listChannels(planId) { return request.get(`/prices/channels/plan/${planId}`) },
  updateChannel(id, data) { return request.put(`/prices/channels/${id}`, data) },
  deleteChannel(id) { return request.delete(`/prices/channels/${id}`) },
  getHistory(productId, days = 90) { return request.get(`/prices/history/${productId}`, { params: { days } }) },
  getBest(productId) { return request.get(`/prices/best/${productId}`) },
  getBestForFamily(familyId) { return request.get(`/prices/best-for-family/${familyId}`) },
  triggerScrape(productId, url) { return request.post(`/prices/scrape/${productId}`, null, { params: { url } }) },
}

export const couponsAPI = {
  list(familyId, params) { return request.get(`/coupons/family/${familyId}`, { params }) },
  create(familyId, data) { return request.post(`/coupons/family/${familyId}`, data) },
  update(id, data) { return request.put(`/coupons/${id}`, data) },
  delete(id) { return request.delete(`/coupons/${id}`) },
  getExpiring(familyId, days = 7) { return request.get(`/coupons/family/${familyId}/expiring`, { params: { within_days: days } }) },
  markUsed(id) { return request.post(`/coupons/${id}/use`) },
}

export const shoppingAPI = {
  list(familyId, params) { return request.get(`/shopping-list/family/${familyId}`, { params }) },
  add(familyId, data) { return request.post(`/shopping-list/family/${familyId}`, data) },
  batchAdd(familyId, data) { return request.post(`/shopping-list/family/${familyId}/batch`, data) },
  update(id, data) { return request.put(`/shopping-list/${id}`, data) },
  delete(id) { return request.delete(`/shopping-list/${id}`) },
  markPurchased(id, price) { return request.post(`/shopping-list/${id}/purchase`, null, { params: { actual_price: price } }) },
  clearPurchased(familyId) { return request.delete(`/shopping-list/family/${familyId}/clear-purchased`) },
  getStats(familyId) { return request.get(`/shopping-list/family/${familyId}/stats`) },
}

export const searchAPI = {
  search(q, familyId, limit = 20) { return request.get('/search/products', { params: { q, family_id: familyId, limit } }) },
  searchLocal(q, familyId) { return request.get('/search/products/local', { params: { q, family_id: familyId } }) },
}

export const ocrAPI = {
  recognize(familyId, file, asyncMode = false) {
    const formData = new FormData()
    formData.append('file', file)
    formData.append('async_mode', asyncMode)
    return request.post(`/ocr/recognize/${familyId}`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })
  },
  getHistory(familyId, limit = 20) { return request.get(`/ocr/history/${familyId}`, { params: { limit } }) },
  matchProduct(logId, productId) { return request.post(`/ocr/match-product/${logId}/${productId}`) },
}

export const statisticsAPI = {
  dashboard(familyId) { return request.get(`/statistics/dashboard/${familyId}`) },
  monthly(familyId, year, month) { return request.get(`/statistics/monthly/${familyId}`, { params: { year, month } }) },
  yearly(familyId, year) { return request.get(`/statistics/yearly/${familyId}`, { params: { year } }) },
}

export const exportAPI = {
  shoppingList(familyId, fmt, status) { return request.get(`/export/shopping-list/${familyId}`, { params: { fmt, status }, responseType: 'blob' }) },
  backup(familyId) { return request.get(`/export/backup/${familyId}`, { responseType: 'blob' }) },
}

export const systemAPI = {
  getConfig() { return request.get('/system/config') },
  getSettings(familyId) { return request.get(`/system/settings/${familyId}`) },
  updateSetting(familyId, key, data) { return request.put(`/system/settings/${familyId}/${key}`, data) },
  deleteSetting(familyId, key) { return request.delete(`/system/settings/${familyId}/${key}`) },
}
