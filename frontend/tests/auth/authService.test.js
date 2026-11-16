import { vi, test, expect, beforeEach } from 'vitest'
import { authService } from '../../src/services/authService'
import { request, tokens } from '../../src/services/http'

vi.mock('../../src/services/http', () => ({
  request: vi.fn(),
  tokens: { set: vi.fn(), clear: vi.fn(), get: vi.fn() },
}))

beforeEach(() => vi.clearAllMocks())

test('login posts credentials and stores the access token', async () => {
  request.mockResolvedValue({ access: 'tok123' })
  await authService.login('a@b.com', 'pw')
  expect(request).toHaveBeenCalledWith('/auth/login/', {
    method: 'POST', json: { email: 'a@b.com', password: 'pw' }, auth: false,
  })
  expect(tokens.set).toHaveBeenCalledWith('tok123')
})

test('register posts to /auth/register/', async () => {
  request.mockResolvedValue({})
  await authService.register({ email: 'x@y.com' })
  expect(request).toHaveBeenCalledWith('/auth/register/', {
    method: 'POST', json: { email: 'x@y.com' }, auth: false,
  })
})

test('logout clears the token', () => {
  authService.logout()
  expect(tokens.clear).toHaveBeenCalled()
})
