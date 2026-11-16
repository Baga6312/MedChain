import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { MemoryRouter, Routes, Route } from 'react-router-dom'
import { vi, test, expect, beforeEach } from 'vitest'
import RegisterPage from '../../src/pages/RegisterPage'
import { useAuth } from '../../src/context/AuthContext'

vi.mock('../../src/context/AuthContext', () => ({ useAuth: vi.fn() }))
vi.mock('../../src/context/NotifyContext', () => ({ useNotify: () => notify }))
vi.mock('../../src/components/common/ThemeToggle', () => ({ default: () => null }))
vi.mock('../../src/components/auth/OAuthButtons', () => ({ default: () => null }))

const notify = vi.fn()
const register = vi.fn()

beforeEach(() => {
  vi.clearAllMocks()
  useAuth.mockReturnValue({ register })
})

const setup = () => render(
  <MemoryRouter initialEntries={['/register']}>
    <Routes>
      <Route path="/register" element={<RegisterPage />} />
      <Route path="/login" element={<div>LOGIN PAGE</div>} />
    </Routes>
  </MemoryRouter>
)

async function fill(pw = 'Secret123!', pw2 = 'Secret123!') {
  await userEvent.type(screen.getByLabelText('Prénom'), 'Ali')
  await userEvent.type(screen.getByLabelText('Nom'), 'Ben')
  await userEvent.type(screen.getByLabelText('Email'), 'ali@test.com')
  await userEvent.type(screen.getByLabelText('Adresse'), 'Tunis')
  await userEvent.type(screen.getByLabelText('Mot de passe'), pw)
  await userEvent.type(screen.getByLabelText('Confirmer le mot de passe'), pw2)
}

test('renders all 7 fields and the submit button', () => {
  setup()
  expect(screen.getAllByRole('textbox').length + screen.getAllByLabelText(/mot de passe/i).length).toBe(7)
  expect(screen.getByRole('button', { name: "S'inscrire" })).toBeInTheDocument()
})

test('shows error and does not call register when passwords differ', async () => {
  setup()
  await fill('Secret123!', 'Different!')
  await userEvent.click(screen.getByRole('button', { name: "S'inscrire" }))
  expect(await screen.findByText(/ne correspondent pas/)).toBeInTheDocument()
  expect(register).not.toHaveBeenCalled()
})

test('calls register with form data, notifies and goes to /login', async () => {
  register.mockResolvedValue({})
  setup()
  await fill()
  await userEvent.click(screen.getByRole('button', { name: "S'inscrire" }))
  expect(register).toHaveBeenCalledWith(expect.objectContaining({
    first_name: 'Ali', last_name: 'Ben', email: 'ali@test.com', password: 'Secret123!', password2: 'Secret123!',
  }))
  expect(notify).toHaveBeenCalled()
  expect(await screen.findByText('LOGIN PAGE')).toBeInTheDocument()
})

test('shows the API error when register fails', async () => {
  register.mockRejectedValue(new Error('email: déjà utilisé'))
  setup()
  await fill()
  await userEvent.click(screen.getByRole('button', { name: "S'inscrire" }))
  expect(await screen.findByText(/déjà utilisé/)).toBeInTheDocument()
})

test('phone is optional, the other fields are required', () => {
  setup()
  expect(screen.getByLabelText('Téléphone')).not.toBeRequired()
  expect(screen.getByLabelText('Email')).toBeRequired()
})
