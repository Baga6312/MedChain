import { render, screen } from '@testing-library/react'
import { MemoryRouter, Routes, Route } from 'react-router-dom'
import { vi, test, expect, beforeEach } from 'vitest'
import OAuthCallbackPage from '../../src/pages/OAuthCallbackPage'
import { useAuth } from '../../src/context/AuthContext'

vi.mock('../../src/context/AuthContext', () => ({ useAuth: vi.fn() }))

beforeEach(() => {
  vi.clearAllMocks()
  window.history.replaceState({}, '', '/oauth/callback')
})

const setup = (hash) => {
  window.location.hash = hash
  const acceptToken = vi.fn()
  useAuth.mockReturnValue({ acceptToken })
  render(
    <MemoryRouter initialEntries={['/oauth/callback']}>
      <Routes>
        <Route path="/oauth/callback" element={<OAuthCallbackPage />} />
        <Route path="/dashboard" element={<div>Dashboard</div>} />
        <Route path="/login" element={<div>Login</div>} />
      </Routes>
    </MemoryRouter>,
  )
  return acceptToken
}

test('accepts the access token and redirects to dashboard', async () => {
  const acceptToken = setup('#access=token-123')
  expect(acceptToken).toHaveBeenCalledWith('token-123')
})

test('redirects to login when the callback has no token', async () => {
  setup('')
  expect(await screen.findByText('Login')).toBeInTheDocument()
})
