import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { vi, test, expect, beforeEach } from 'vitest'
import AdminDashboard from '../../src/pages/AdminDashboard'
import { useAuth } from '../../src/context/AuthContext'
import { adminService } from '../../src/services/adminService'

vi.mock('../../src/context/AuthContext', () => ({ useAuth: vi.fn() }))
vi.mock('../../src/context/NotifyContext', () => ({ useNotify: () => notify }))
vi.mock('../../src/services/adminService', () => ({
  adminService: {
    dashboard: vi.fn(),
    users: vi.fn(),
    auditLogs: vi.fn(),
    securityAlerts: vi.fn(),
    updateUser: vi.fn(),
    createUser: vi.fn(),
    resolveAlert: vi.fn(),
  },
}))

const notify = vi.fn()
const dashboard = {
  users: 3, patients: 2, doctors: 1, open_alerts: 1, new_users: 2, pending_users: 1,
}
const users = [{
  id: 1, first_name: 'Ali', last_name: 'Ben', email: 'ali@test.com',
  role: 'patient', date_joined: '2026-01-01T00:00:00Z', is_active: true,
}]

beforeEach(() => {
  vi.clearAllMocks()
  useAuth.mockReturnValue({ isAdmin: true })
  adminService.dashboard.mockResolvedValue(dashboard)
  adminService.users.mockResolvedValue(users)
  adminService.auditLogs.mockResolvedValue([])
  adminService.securityAlerts.mockResolvedValue([{
    id: 7, title: 'Connexion inhabituelle', detail: 'Adresse inconnue', status: 'open',
  }])
})

test('loads metrics, users, and security alerts', async () => {
  render(<AdminDashboard />)
  expect(await screen.findByRole('heading', { name: 'Administration' })).toBeInTheDocument()
  expect(screen.getByText('3')).toBeInTheDocument()
  expect(screen.getByText('Ali Ben')).toBeInTheDocument()
  expect(screen.getByText('Connexion inhabituelle')).toBeInTheDocument()
})

test('creates a user from the modal', async () => {
  adminService.createUser.mockResolvedValue({})
  render(<AdminDashboard />)
  await screen.findByText('Ali Ben')
  await userEvent.click(screen.getByRole('button', { name: /Ajouter un utilisateur/ }))
  await userEvent.type(screen.getByLabelText('Prénom'), 'Sara')
  await userEvent.type(screen.getByLabelText('Nom'), 'Test')
  await userEvent.type(screen.getByLabelText('Email'), 'sara@test.com')
  await userEvent.type(screen.getByLabelText('Mot de passe'), 'Secret123!')
  await userEvent.click(screen.getByRole('button', { name: 'Créer le compte' }))
  await waitFor(() => expect(adminService.createUser).toHaveBeenCalledWith({
    first_name: 'Sara', last_name: 'Test', email: 'sara@test.com', password: 'Secret123!',
  }))
  expect(notify).toHaveBeenCalledWith('Compte créé avec le rôle patient par défaut.')
})

test('resolves an open security alert', async () => {
  adminService.resolveAlert.mockResolvedValue({})
  render(<AdminDashboard />)
  await userEvent.click(await screen.findByRole('button', { name: 'Résoudre' }))
  await waitFor(() => expect(adminService.resolveAlert).toHaveBeenCalledWith(7))
  expect(notify).toHaveBeenCalledWith('Alerte marquée comme résolue.')
})
