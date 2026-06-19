import request from './request'

export function login(phone, smsCode) {
  return request.post('/auth/login', {
    phone,
    sms_code: smsCode
  })
}

export function sendSmsCode(phone) {
  return request.post('/auth/sms-code', { phone })
}

export function refreshToken() {
  const refreshToken = localStorage.getItem('refresh_token')
  return request.post('/auth/refresh', { refresh_token: refreshToken })
}

export function getUserProfile() {
  return request.get('/users/me')
}
