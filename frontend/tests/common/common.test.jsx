import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { vi, test, expect, beforeEach } from 'vitest'
import LoadingState from '../../src/components/common/LoadingState'
import ThemeToggle from '../../src/components/common/ThemeToggle'
import Toast from '../../src/components/common/Toast'
import { useTheme } from '../../src/context/ThemeContext'

vi.mock('../../src/context/ThemeContext', () => ({ useTheme: vi.fn() }))

beforeEach(() => vi.clearAllMocks())

test('renders the default and custom loading labels', () => {
  const { rerender } = render(<LoadingState />)
  expect(screen.getByRole('status')).toHaveTextContent('Chargement…')
  rerender(<LoadingState label="Chargement des dossiers" />)
  expect(screen.getByRole('status')).toHaveTextContent('Chargement des dossiers')
})

test('toggles theme with the correct accessible label', async () => {
  const toggleTheme = vi.fn()
  useTheme.mockReturnValue({ theme: 'light', toggleTheme })
  render(<ThemeToggle />)
  const button = screen.getByRole('button', { name: 'Activer le mode sombre' })
  await userEvent.click(button)
  expect(toggleTheme).toHaveBeenCalledOnce()
})

test('renders success, danger, and empty toast states', () => {
  const { rerender } = render(<Toast toast={null} />)
  expect(screen.queryByText(/Profil/)).not.toBeInTheDocument()
  rerender(<Toast toast={{ tone: 'success', message: 'Enregistré' }} />)
  expect(screen.getByText('Enregistré')).toBeInTheDocument()
  expect(screen.getByText('Enregistré').parentElement).toHaveClass('success')
  rerender(<Toast toast={{ tone: 'danger', message: 'Échec' }} />)
  expect(screen.getByText('Échec').parentElement).toHaveClass('danger')
})
