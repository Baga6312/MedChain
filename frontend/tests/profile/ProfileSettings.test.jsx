import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { vi, test, expect, beforeEach } from 'vitest'
import ProfileSettings from '../../src/components/profile/ProfileSettings'
import { useAuth } from '../../src/context/AuthContext'
import { request } from '../../src/services/http'

vi.mock('../../src/context/AuthContext', () => ({ useAuth: vi.fn() }))
vi.mock('../../src/context/NotifyContext', () => ({ useNotify: () => notify }))
vi.mock('../../src/services/http', () => ({ request: vi.fn() }))

const notify = vi.fn()
const user = { first_name: 'Ali', last_name: 'Ben', email: 'ali@test.com', phone: '', address: '', role: 'patient' }

beforeEach(() => {
  vi.clearAllMocks()
  useAuth.mockReturnValue({ user, refreshUser: vi.fn().mockResolvedValue(user) })
  request.mockResolvedValue({})
})

test('renders the profile identity and fields', () => {
  render(<ProfileSettings />)
  expect(screen.getByRole('heading', { name: 'Ali' })).toBeInTheDocument()
  expect(screen.getByLabelText('Email')).toHaveValue('ali@test.com')
  expect(screen.getByLabelText('Email')).toBeDisabled()
})

test('submits profile changes and refreshes the user', async () => {
  const refreshUser = vi.fn().mockResolvedValue(user)
  useAuth.mockReturnValue({ user, refreshUser })
  render(<ProfileSettings />)
  await userEvent.clear(screen.getByLabelText('Téléphone'))
  await userEvent.type(screen.getByLabelText('Téléphone'), '555')
  await userEvent.click(screen.getByRole('button', { name: 'Enregistrer les changements' }))
  await waitFor(() => expect(request).toHaveBeenCalledWith('/auth/profile/', expect.objectContaining({ method: 'PATCH', formData: expect.any(FormData) })))
  expect(refreshUser).toHaveBeenCalled()
  expect(notify).toHaveBeenCalledWith('Profil mis à jour.')
})

test('shows API errors when saving fails', async () => {
  request.mockRejectedValue(new Error('Profil invalide'))
  render(<ProfileSettings />)
  await userEvent.click(screen.getByRole('button', { name: 'Enregistrer les changements' }))
  expect(await screen.findByText('Profil invalide')).toBeInTheDocument()
})
