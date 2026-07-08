import request from './request'

export function getFaultList(params) {
  return request.get('/admin/faults', { params })
}

export function processFault(id, data) {
  return request.put(`/admin/faults/${id}`, data)
}