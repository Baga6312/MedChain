export const tokens = {
  get: () => localStorage.getItem('access'),
  set: (a) => localStorage.setItem('access', a),
  clear: () => localStorage.removeItem('access'),
};

export async function request(path, { method = 'GET', json, auth = true } = {}) {
  const init = { method, headers: {} };
  if (json !== undefined) {
    init.headers['Content-Type'] = 'application/json';
    init.body = JSON.stringify(json);
  }
  const t = tokens.get();
  if (auth && t) init.headers.Authorization = `Bearer ${t}`;

  const res = await fetch(`${BASE}${path}`, init);
  if (res.status === 204) return null;
  let body = null;
  try {
    body = await res.json();
  } catch {
    /* empty body */
  }
  if (res.status === 401 && auth) {
    tokens.clear();
    window.location.assign('/login');
  }
  if (!res.ok) throw new ApiError(res.status, format(body));
  return body;
}