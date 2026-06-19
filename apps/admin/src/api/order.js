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
