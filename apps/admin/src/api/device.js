import request from './request'

export function getDeviceList(params = {}) {
  return request.get('/devices', { params })
}

export function getDeviceByCode(deviceCode) {
  return request.get(`/devices/${deviceCode}`)
}

export function createDevice(data) {
  return request.post('/devices', data)
}

export function updateDevice(deviceCode, data) {
  return request.put(`/devices/${deviceCode}`, data)
}

export function deleteDevice(deviceCode) {
  return request.delete(`/devices/${deviceCode}`)
}
