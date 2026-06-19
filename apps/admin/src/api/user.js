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

export function adjustUserDeposit(userId, amount, remark) {
  return request.post(`/admin/users/${userId}/deposit/adjust`, { amount, remark })
}
