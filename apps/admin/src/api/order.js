import request from './request'

export function getOrderList(params = {}) {
  return request.get('/borrows', { params })
}

export function getOrderDetail(orderId) {
  return request.get(`/borrows/${orderId}`)
}

export function getCurrentOrder() {
  return request.get('/borrows/current')
}

export function getTimeStats(params = {}) {
  return request.get('/admin/statistics/orders', { params })
}

export function getDeviceStats(params = {}) {
  return request.get('/admin/statistics/devices', { params })
}

export function exportStatistics(params = {}) {
  return request.get('/admin/statistics/export', { params, responseType: 'blob' })
}
