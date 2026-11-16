import { render, screen } from '@testing-library/react'
import { MemoryRouter, Routes, Route } from 'react-router-dom'
import { vi, test, expect } from 'vitest'
import ResourcePage from '../../src/pages/ResourcePage'

vi.mock('../../src/components/crud/crudPage', () => ({
  default: ({ resource }) => <div>CRUD {resource}</div>,
}))
vi.mock('../../src/context/NotifyContext', () => ({ useNotify: () => vi.fn() }))

const setup = (path) => render(
  <MemoryRouter initialEntries={[path]}>
    <Routes><Route path="/:resource" element={<ResourcePage />} /></Routes>
  </MemoryRouter>
)

test('renders the CRUD page for a known resource', () => {
  setup('/doctors')
  expect(screen.getByText('CRUD doctors')).toBeInTheDocument()
})

test('redirects unknown resources to /patients', () => {
  setup('/unknown')
  expect(screen.getByText('CRUD patients')).toBeInTheDocument()
})