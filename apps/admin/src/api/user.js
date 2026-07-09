import request from './request'

export function getUserProfile() {
  return request.get('/users/me')
}

export function updateUserProfile(data) {
  return request.patch('/users/me', data)
}

export function topUpDeposit(amount) {
  return request.post('/users/me/deposit/topup', { amount })
}

export function getDepositLedger(params = {}) {
  return request.get('/users/me/deposit/ledger', { params })
}

export function getAdminDepositLedger(params = {}) {
  return request.get('/admin/deposits/ledger', { params })
}

export function adjustUserDeposit(userId, amount, remark) {
  return request.post(`/admin/users/${userId}/deposit/adjust`, { amount, remark })
}

export function getUserList(params = {}) {
  return request.get('/admin/users', { params })
}

export function freezeUser(userId, action) {
  return request.post(`/admin/users/${userId}/freeze`, { action })
}

export function resetUserSms(userId) {
  return request.post(`/admin/users/${userId}/reset-sms`)
}

export function exportUsers() {
  return request.get('/admin/users/export', { responseType: 'blob' })
}