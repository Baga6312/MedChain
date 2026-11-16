import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { vi, test, expect, beforeEach } from 'vitest'
import RoleDashboard from '../../src/pages/RoleDashboard'
import { useAuth } from '../../src/context/AuthContext'
import { request } from '../../src/services/http'

vi.mock('../../src/context/AuthContext', () => ({ useAuth: vi.fn() }))
vi.mock('../../src/context/NotifyContext', () => ({ useNotify: () => notify }))
vi.mock('../../src/services/http', () => ({ request: vi.fn() }))

const notify = vi.fn()
const patient = { role: 'patient', first_name: 'Ali', email: 'ali@test.com' }
const episode = { id: 4, doctor_name: 'Dr House', status: 'requested', reason: 'Suivi' }

beforeEach(() => {
  vi.clearAllMocks()
  useAuth.mockReturnValue({ user: patient })
  request.mockImplementation((path) => {
    if (path === '/treatment-episodes/') return Promise.resolve([episode])
    if (path === '/doctors/') return Promise.resolve([{ id: 2, name: 'Dr House', specialty: 'Cardiologie' }])
    return Promise.resolve([])
  })
})

test('loads patient treatment request form and episodes', async () => {
  render(<RoleDashboard />)
  expect(await screen.findByRole('heading', { name: 'Bonjour Ali' })).toBeInTheDocument()
  expect(screen.getByText('Demander un traitement')).toBeInTheDocument()
  expect(screen.getByText('Dr House')).toBeInTheDocument()
})

test('submits a treatment request', async () => {
  request.mockImplementation((path, options) => {
    if (path === '/treatment-episodes/') {
      return options ? Promise.resolve({}) : Promise.resolve([episode])
    }
    if (path === '/doctors/') return Promise.resolve([{ id: 2, name: 'Dr House', specialty: 'Cardiologie' }])
    return Promise.resolve([])
  })
  render(<RoleDashboard />)
  await screen.findByText('Dr House')
  await userEvent.selectOptions(screen.getByRole('combobox'), '2')
  await userEvent.type(screen.getByPlaceholderText('Motif'), 'Consultation')
  await userEvent.click(screen.getByRole('button', { name: 'Envoyer la demande' }))
  await waitFor(() => expect(request).toHaveBeenCalledWith('/treatment-episodes/', {
    method: 'POST', json: { doctor: 2, reason: 'Consultation' },
  }))
  expect(notify).toHaveBeenCalledWith('Demande de traitement envoyée.')
})

test('loads timeline details when a patient expands an episode', async () => {
  request.mockImplementation((path) => {
    if (path === '/treatment-episodes/') return Promise.resolve([episode])
    if (path === '/doctors/') return Promise.resolve([])
    if (path.endsWith('/timeline/')) return Promise.resolve({ integrity: { status: 'verified', errors: [] }, phases: [], events: [] })
    if (path.endsWith('/integrity/')) return Promise.resolve({ status: 'verified', errors: [] })
    return Promise.resolve([])
  })
  render(<RoleDashboard />)
  await userEvent.click(await screen.findByRole('button', { name: /Timeline/ }))
  expect(await screen.findByText('Enregistrement vérifié')).toBeInTheDocument()
  expect(request).toHaveBeenCalledWith('/treatment-episodes/4/timeline/')
})
