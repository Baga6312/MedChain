import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { MemoryRouter, Routes, Route } from 'react-router-dom'
import { vi, test, expect, beforeEach } from 'vitest'
import Sidebar from '../../src/components/layout/Sidebar'
import { useAuth } from '../../src/context/AuthContext'

vi.mock('../../src/context/AuthContext', () => ({ useAuth: vi.fn() }))

beforeEach(() => vi.clearAllMocks())

const setup = (auth, path = '/dashboard') => {
  useAuth.mockReturnValue(auth)
  return render(
    <MemoryRouter initialEntries={[path]}>
      <Routes><Route path="*" element={<><Sidebar /><div>Current page</div></>} /></Routes>
    </MemoryRouter>,
  )
}

test('shows patient navigation and hides administration', () => {
  setup({ isAdmin: false, user: { role: 'patient' }, logout: vi.fn() })
  expect(screen.getByRole('button', { name: /Mon espace/ })).toBeInTheDocument()
  expect(screen.getByRole('button', { name: /Médecins/ })).toBeInTheDocument()
  expect(screen.queryByRole('button', { name: /Administration/ })).not.toBeInTheDocument()
  expect(screen.queryByRole('button', { name: /Dossiers médicaux/ })).toBeInTheDocument()
})

test('shows admin navigation and logs out', async () => {
  const logout = vi.fn()
  setup({ isAdmin: true, user: { role: 'admin' }, logout })
  expect(screen.getByRole('button', { name: /Administration/ })).toBeInTheDocument()
  expect(screen.queryByRole('button', { name: /Mon espace/ })).not.toBeInTheDocument()
  await userEvent.click(screen.getByRole('button', { name: 'Déconnexion' }))
  expect(logout).toHaveBeenCalledOnce()
})
