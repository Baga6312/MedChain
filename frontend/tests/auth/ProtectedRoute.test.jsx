import { render, screen } from '@testing-library/react'
import { MemoryRouter, Routes, Route } from 'react-router-dom'
import { vi, test, expect } from 'vitest'
import ProtectedRoute from '../../src/components/auth/ProtectedRoute'
import { useAuth } from '../../src/context/AuthContext'

vi.mock('../../src/context/AuthContext', () => ({ useAuth: vi.fn() }))

const setup = () => render(
  <MemoryRouter initialEntries={['/secret']}>
    <Routes>
      <Route path="/login" element={<div>LOGIN PAGE</div>} />
      <Route element={<ProtectedRoute />}>
        <Route path="/secret" element={<div>SECRET</div>} />
      </Route>
    </Routes>
  </MemoryRouter>
)

test('redirects to /login when logged out', () => {
  useAuth.mockReturnValue({ isAuthed: false, authReady: true })
  setup()
  expect(screen.getByText('LOGIN PAGE')).toBeInTheDocument()
})

test('shows loading while profile loads', () => {
  useAuth.mockReturnValue({ isAuthed: true, authReady: false })
  setup()
  expect(screen.getByText(/Chargement du profil/)).toBeInTheDocument()
})

test('shows protected page when logged in', () => {
  useAuth.mockReturnValue({ isAuthed: true, authReady: true })
  setup()
  expect(screen.getByText('SECRET')).toBeInTheDocument()
})
