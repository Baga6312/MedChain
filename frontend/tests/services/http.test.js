import { vi, test, expect, beforeEach } from 'vitest'
import { request, tokens, ApiError } from '../../src/services/http'

const mockFetch = (status, body) => {
  global.fetch = vi.fn().mockResolvedValue({
    status, ok: status >= 200 && status < 300, json: async () => body,
  })
}

beforeEach(() => {
  localStorage.clear()
  vi.restoreAllMocks()
  Object.defineProperty(window, 'location', { value: { assign: vi.fn() }, writable: true })
})

test('tokens set / get / clear', () => {
  tokens.set('abc')
  expect(tokens.get()).toBe('abc')
  tokens.clear()
  expect(tokens.get()).toBeNull()
})

test('sends the Token header when logged in', async () => {
  tokens.set('abc')
  mockFetch(200, { ok: true })
  await request('/auth/me/')
  expect(fetch.mock.calls[0][0]).toBe('/api/auth/me/')
  expect(fetch.mock.calls[0][1].headers.Authorization).toBe('Token abc')
})

test('sends JSON body with POST', async () => {
  mockFetch(200, {})
  await request('/x/', { method: 'POST', json: { a: 1 }, auth: false })
  expect(fetch.mock.calls[0][1].body).toBe('{"a":1}')
})

test('returns null on 204', async () => {
  mockFetch(204, null)
  expect(await request('/x/')).toBeNull()
})

test('throws ApiError with the detail message', async () => {
  mockFetch(400, { detail: 'Mauvais identifiants' })
  await expect(request('/x/')).rejects.toMatchObject({ status: 400, message: 'Mauvais identifiants' })
})

test('formats field errors', async () => {
  mockFetch(400, { email: ['invalide'] })
  await expect(request('/x/')).rejects.toThrow('email: invalide')
})

test('401 clears the token and redirects to /login', async () => {
  tokens.set('abc')
  mockFetch(401, { detail: 'no' })
  await expect(request('/x/')).rejects.toBeInstanceOf(ApiError)
  expect(tokens.get()).toBeNull()
  expect(window.location.assign).toHaveBeenCalledWith('/login')
})
