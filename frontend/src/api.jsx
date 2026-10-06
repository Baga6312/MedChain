const BASE = '/api';

export class ApiError extends Error {
  constructor(status, message) {
    super(message);
    this.status = status;
  }
}

// DRF returns {detail: "..."} or {field: ["msg"]}
function format(body) {
  if (!body) return 'Erreur inattendue.';
  if (body.detail) return body.detail;
  return Object.entries(body)
    .map(([k, v]) => `${k}: ${[].concat(v).join(' ')}`)
    .join(' · ');
}

// GET/DELETE send no body and no query string; POST/PUT send JSON only (backend rejects anything else).
async function request(path, { method = 'GET', json } = {}) {
  const init = { method };
  if (json !== undefined) {
    init.headers = { 'Content-Type': 'application/json' };
    init.body = JSON.stringify(json);
  }
  const res = await fetch(`${BASE}${path}`, init);
  if (res.status === 204) return null;
  let body = null;
  try {
    body = await res.json();
  } catch {
    /* empty body */
  }
  if (!res.ok) throw new ApiError(res.status, format(body));
  return body;
}

export const api = {
  list: (resource) =>
    request(`/${resource}/`).then((d) => (Array.isArray(d) ? d : d.results ?? [])),
  create: (resource, data) => request(`/${resource}/`, { method: 'POST', json: data }),
  // PUT requires "id" in the body
  update: (resource, id, data) =>
    request(`/${resource}/${id}/`, { method: 'PUT', json: { ...data, id } }),
  remove: (resource, id) => request(`/${resource}/${id}/`, { method: 'DELETE' }),
};