import { request, tokens } from './http';

export const authService = {
  async login(email, password) {
    const d = await request('/auth/login/', { method: 'POST', json: { email, password }, auth: false });
    tokens.set(d.access);
  },
  register: (data) => request('/auth/register/', { method: 'POST', json: data, auth: false }),
  oauthStart: (provider) => window.location.assign(`/api/auth/${provider}/login/`),
  logout: () => tokens.clear(),
};