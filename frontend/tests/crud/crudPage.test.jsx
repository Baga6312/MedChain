import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { vi, test, expect, beforeEach } from 'vitest'
import CrudPage from '../../src/components/crud/crudPage'
import { api } from '../../src/services/resourceService'

vi.mock('../../src/services/resourceService', () => ({
  api: { list: vi.fn(), create: vi.fn(), update: vi.fn(), remove: vi.fn() },
}))

const notify = vi.fn()
const patient = { id: 1, name: 'Ali', birth_date: '2000-01-01', phone: '123' }
const setup = (resource = 'patients') => render(<CrudPage resource={resource} notify={notify} />)

beforeEach(() => {
  vi.clearAllMocks()
  api.list.mockResolvedValue([patient])
})

test('lists rows and shows the count', async () => {
  setup()
  expect(await screen.findByText('Ali')).toBeInTheDocument()
  expect(screen.getByRole('heading', { name: 'Patients' })).toBeInTheDocument()
  expect(screen.getByText('1 enregistrement(s)')).toBeInTheDocument()
})

test('shows empty message when there is no data', async () => {
  api.list.mockResolvedValue([])
  setup()
  expect(await screen.findByText('Aucun enregistrement.')).toBeInTheDocument()
})

test('shows the error when loading fails', async () => {
  api.list.mockRejectedValue(new Error('Serveur indisponible'))
  setup()
  expect(await screen.findByText(/Serveur indisponible/)).toBeInTheDocument()
})

test('creates a record (nullable date is sent as null)', async () => {
  api.create.mockResolvedValue({})
  setup()
  await screen.findByText('Ali')
  await userEvent.click(screen.getByRole('button', { name: /Ajouter/ }))
  expect(screen.getByText('Nouveau patient')).toBeInTheDocument()
  await userEvent.type(screen.getByLabelText('Nom'), 'Sara')
  await userEvent.type(screen.getByLabelText('Téléphone'), '555')
  await userEvent.click(screen.getByRole('button', { name: 'Enregistrer' }))
  expect(api.create).toHaveBeenCalledWith('patients', { name: 'Sara', birth_date: null, phone: '555' })
  expect(notify).toHaveBeenCalledWith('Créé.')
  await waitFor(() => expect(api.list).toHaveBeenCalledTimes(2))
})

test('edits a record with prefilled values', async () => {
  api.update.mockResolvedValue({})
  setup()
  await userEvent.click(await screen.findByRole('button', { name: 'Modifier' }))
  expect(screen.getByText('Modifier patient #1')).toBeInTheDocument()
  expect(screen.getByLabelText('Nom')).toHaveValue('Ali')
  await userEvent.clear(screen.getByLabelText('Nom'))
  await userEvent.type(screen.getByLabelText('Nom'), 'Omar')
  await userEvent.click(screen.getByRole('button', { name: 'Enregistrer' }))
  expect(api.update).toHaveBeenCalledWith('patients', 1, { name: 'Omar', birth_date: '2000-01-01', phone: '123' })
  expect(notify).toHaveBeenCalledWith('Modifié.')
})

test('cancel closes the form without saving', async () => {
  setup()
  await userEvent.click(await screen.findByRole('button', { name: /Ajouter/ }))
  await userEvent.click(screen.getByRole('button', { name: 'Annuler' }))
  expect(screen.queryByText('Nouveau patient')).not.toBeInTheDocument()
  expect(api.create).not.toHaveBeenCalled()
})

test('deletes after confirmation', async () => {
  vi.spyOn(window, 'confirm').mockReturnValue(true)
  api.remove.mockResolvedValue(null)
  setup()
  await userEvent.click(await screen.findByRole('button', { name: 'Supprimer' }))
  expect(api.remove).toHaveBeenCalledWith('patients', 1)
  expect(notify).toHaveBeenCalledWith('Supprimé.')
})

test('does not delete when confirmation is refused', async () => {
  vi.spyOn(window, 'confirm').mockReturnValue(false)
  setup()
  await userEvent.click(await screen.findByRole('button', { name: 'Supprimer' }))
  expect(api.remove).not.toHaveBeenCalled()
})

test('notifies with "danger" when delete fails', async () => {
  vi.spyOn(window, 'confirm').mockReturnValue(true)
  api.remove.mockRejectedValue(new Error('Interdit'))
  setup()
  await userEvent.click(await screen.findByRole('button', { name: 'Supprimer' }))
  await waitFor(() => expect(notify).toHaveBeenCalledWith('Interdit', 'danger'))
})

test('foreign keys are displayed by name (appointments)', async () => {
  api.list.mockImplementation(async (r) => ({
    appointments: [{ id: 5, patient: 1, doctor: 2, date: '2026-11-20T10:00:00Z', notes: '', status: 'ok' }],
    patients: [{ id: 1, name: 'Ali' }],
    doctors: [{ id: 2, name: 'Dr House' }],
  }[r]))
  setup('appointments')
  expect(await screen.findByText('Ali')).toBeInTheDocument()
  expect(screen.getByText('Dr House')).toBeInTheDocument()
})