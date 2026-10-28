import { request } from './http';

export const adminService = {
  dashboard: () => request('/admin/dashboard/'),
  users: (query = '') => request(`/admin/users/${query ? `?q=${encodeURIComponent(query)}` : ''}`),
  createUser: (data) => request('/admin/users/', { method: 'POST', json: data }),
  updateUser: (data) => request('/admin/users/', { method: 'PATCH', json: data }),
  forceLogout: (id) => request(`/admin/users/${id}/force-logout/`, { method: 'POST', json: {} }),
  auditLogs: () => request('/admin/audit-logs/'),
  securityAlerts: () => request('/admin/security-alerts/'),
  resolveAlert: (id) => request('/admin/security-alerts/', {
    method: 'PATCH',
    json: { alert_id: id },
  }),
};
