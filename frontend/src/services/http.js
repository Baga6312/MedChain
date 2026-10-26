const BASE = '/api';

export class ApiError extends Error {
  constructor(status, message) {
    super(message);
    this.status = status;
  }
}

function format(body) {
  if (!body) return 'Erreur inattendue.';
  if (body.detail) return body.detail;
  return Object.entries(body)
    .map(([key, value]) => `${key}: ${[].concat(value).join(' ')}`)
    .join(' · ');
}

export const tokens = {
  get: () => localStorage.getItem('access'),
  set: (access) => localStorage.setItem('access', access),
  clear: () => localStorage.removeItem('access'),
};

export async function request(path, { method = 'GET', json, auth = true } = {}) {
  const init = { method, headers: {} };
  if (json !== undefined) {
    init.headers['Content-Type'] = 'application/json';
    init.body = JSON.stringify(json);
  }

  const token = tokens.get();
  if (auth && token) init.headers.Authorization = `Token ${token}`;

  const response = await fetch(`${BASE}${path}`, init);
  if (response.status === 204) return null;

  let body = null;
  try {
    body = await response.json();
  } catch {
    // The response may intentionally have no JSON body.
  }

  if (response.status === 401 && auth) {
    tokens.clear();
    window.location.assign('/login');
  }
  if (!response.ok) throw new ApiError(response.status, format(body));
  return body;
}
