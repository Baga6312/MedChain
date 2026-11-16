import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { MemoryRouter, Outlet, Route, Routes } from 'react-router-dom'
import { vi, test, expect, beforeEach } from 'vitest'
import AppShell from '../../src/components/layout/AppShell'
import { useAuth } from '../../src/context/AuthContext'

vi.mock('../../src/context/AuthContext', () => ({ useAuth: vi.fn() }))
vi.mock('../../src/components/common/ThemeToggle', () => ({ default: () => <button>Theme</button> }))
vi.mock('../../src/components/layout/Sidebar', () => ({ default: () => <aside>Sidebar</aside> }))

beforeEach(() => vi.clearAllMocks())

test('renders shell chrome, user role, and nested route', async () => {
  useAuth.mockReturnValue({ user: { first_name: 'Ali', email: 'ali@test.com', role: 'doctor' } })
  render(
    <MemoryRouter initialEntries={['/dashboard']}>
      <Routes><Route element={<AppShell />}><Route path="/dashboard" element={<div>Dashboard content</div>} /></Route></Routes>
    </MemoryRouter>,
  )
  expect(screen.getByText('Sidebar')).toBeInTheDocument()
  expect(screen.getByText('Dashboard content')).toBeInTheDocument()
  expect(screen.getByText('Ali')).toBeInTheDocument()
  expect(screen.getByText('Praticien vérifié')).toBeInTheDocument()
})

test('navigates to settings from the account button', async () => {
  useAuth.mockReturnValue({ user: { email: 'patient@test.com', role: 'patient' } })
  render(
    <MemoryRouter initialEntries={['/dashboard']}>
      <Routes>
        <Route element={<AppShell />}><Route path="/dashboard" element={<div>Dashboard</div>} /><Route path="/settings" element={<div>Settings</div>} /></Route>
      </Routes>
    </MemoryRouter>,
  )
  await userEvent.click(screen.getByRole('button', { name: 'Ouvrir les paramètres du compte' }))
  expect(await screen.findByText('Settings')).toBeInTheDocument()
})
