import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { MemoryRouter } from 'react-router-dom'
import { vi, test, expect, beforeEach } from 'vitest'
import LoginPage from '../src/pages/LoginPage'
import { useAuth } from '../src/context/AuthContext'

vi.mock('../src/context/AuthContext', () => ({ useAuth: vi.fn() }))
vi.mock('../src/components/common/ThemeToggle', () => ({ default: () => null }))
vi.mock('../src/components/auth/OAuthButtons', () => ({ default: () => null }))

const login = vi.fn()
const refreshUser = vi.fn()

beforeEach(() => {
  vi.clearAllMocks()
  useAuth.mockReturnValue({ isAuthed: false, user: null, login, refreshUser })
})

const setup = () => render(<MemoryRouter><LoginPage /></MemoryRouter>)

test('renders email, password and submit button', () => {
  setup()
  expect(screen.getByLabelText('Email')).toBeInTheDocument()
  expect(screen.getByLabelText('Mot de passe')).toBeInTheDocument()
  expect(screen.getByRole('button', { name: 'Se connecter' })).toBeInTheDocument()
})

test('submits credentials to login()', async () => {
  login.mockResolvedValue()
  refreshUser.mockResolvedValue({ role: 'patient' })
  setup()
  await userEvent.type(screen.getByLabelText('Email'), 'a@b.com')
  await userEvent.type(screen.getByLabelText('Mot de passe'), 'secret123')
  await userEvent.click(screen.getByRole('button', { name: 'Se connecter' }))
  expect(login).toHaveBeenCalledWith('a@b.com', 'secret123')
})

test('shows error when login fails', async () => {
  login.mockRejectedValue(new Error('Identifiants invalides'))
  setup()
  await userEvent.type(screen.getByLabelText('Email'), 'a@b.com')
  await userEvent.type(screen.getByLabelText('Mot de passe'), 'wrong')
  await userEvent.click(screen.getByRole('button', { name: 'Se connecter' }))
  expect(await screen.findByText(/Identifiants invalides/)).toBeInTheDocument()
})