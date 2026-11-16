import { vi, test, expect, beforeEach } from 'vitest'
import { api } from '../../src/services/resourceService'
import { request } from '../../src/services/http'

vi.mock('../../src/services/http', () => ({ request: vi.fn() }))

beforeEach(() => vi.clearAllMocks())

test('list returns a plain array as is', async () => {
  request.mockResolvedValue([{ id: 1 }])
  expect(await api.list('patients')).toEqual([{ id: 1 }])
  expect(request).toHaveBeenCalledWith('/patients/')
})

test('list unwraps paginated results', async () => {
  request.mockResolvedValue({ results: [{ id: 2 }] })
  expect(await api.list('doctors')).toEqual([{ id: 2 }])
})

test('list falls back to an empty array', async () => {
  request.mockResolvedValue({})
  expect(await api.list('doctors')).toEqual([])
})

test('create sends POST', async () => {
  await api.create('patients', { name: 'A' })
  expect(request).toHaveBeenCalledWith('/patients/', { method: 'POST', json: { name: 'A' } })
})

test('update sends PUT with the id merged in', async () => {
  await api.update('patients', 3, { name: 'B' })
  expect(request).toHaveBeenCalledWith('/patients/3/', { method: 'PUT', json: { name: 'B', id: 3 } })
})

test('remove sends DELETE', async () => {
  await api.remove('patients', 3)
  expect(request).toHaveBeenCalledWith('/patients/3/', { method: 'DELETE' })
})