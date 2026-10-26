import { request } from './http';

export const api = {
  list: (resource) =>
    request(`/${resource}/`).then((d) => (Array.isArray(d) ? d : d.results ?? [])),
  create: (resource, data) => request(`/${resource}/`, { method: 'POST', json: data }),
  update: (resource, id, data) =>
    request(`/${resource}/${id}/`, { method: 'PUT', json: { ...data, id } }),
  remove: (resource, id) => request(`/${resource}/${id}/`, { method: 'DELETE' }),
};