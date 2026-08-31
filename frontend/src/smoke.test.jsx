/**
 * Smoke test de las 4 pantallas contra la API REAL (Fase 9).
 * Requiere uvicorn en http://127.0.0.1:8000 (o VITE_API_BASE).
 *
 *   npm test
 *
 * No mockea: renderiza cada página, espera a que resuelva el fetch y
 * comprueba que aparece contenido coherente con lo validado en fases
 * anteriores (Camavinga Ball Winner 90.1 = Fase 5, fit 92.3 = Fase 8,
 * top-5 de similares = Fase 6, estilo de Barça = Fase 8).
 */
import { render, screen, waitFor, within } from '@testing-library/react'
import { MemoryRouter, Route, Routes } from 'react-router-dom'
import { expect, test } from 'vitest'

import PlayerSearch from './pages/PlayerSearch'
import PlayerProfile from './pages/PlayerProfile'
import TeamProfile from './pages/TeamProfile'
import TacticalFit from './pages/TacticalFit'
import { posCode, sideMark, axisName } from './format'

const mount = (path, routes) =>
  render(
    <MemoryRouter initialEntries={[path]}>
      <Routes>{routes}</Routes>
    </MemoryRouter>,
  )

test('helpers', () => {
  expect(posCode('centrocampista')).toBe('MF')
  expect(sideMark('izquierda')).toBe('L')
  expect(sideMark('centro')).toBe('')
  expect(axisName('press_intensity')).toBe('intensidad de presión')
})

test('búsqueda de jugadores: filtra y lista contra la API', async () => {
  mount('/players', <Route path="/players" element={<PlayerSearch />} />)
  await waitFor(() => expect(screen.getByText(/con datos/)).toBeDefined(), { timeout: 5000 })
  // 339 jugadores con >=900 min (= pool de Fase 3)
  await waitFor(() => expect(screen.getByText(/339 con datos/)).toBeDefined())
  expect(screen.getAllByRole('row').length).toBeGreaterThan(10)
})

test('ficha de jugador: role fit con desglose + similares (Camavinga)', async () => {
  mount('/players/396', <Route path="/players/:id" element={<PlayerProfile />} />)
  await waitFor(() => expect(screen.getByRole('heading', { name: 'Eduardo Camavinga' })).toBeDefined(), {
    timeout: 5000,
  })
  // Ball Winner 90.1 (= Fase 5) y su desglose visible ('entradas' aparece
  // en el desglose del rol y en el perfil de percentiles)
  await waitFor(() => expect(screen.getByText('90.1')).toBeDefined())
  await waitFor(() => expect(screen.getAllByText('entradas').length).toBeGreaterThan(0))
  // percentiles agrupados
  await waitFor(() => expect(screen.getByText('Perfil de percentiles')).toBeDefined())
  // similares: top-1 real
  await waitFor(() => expect(screen.getByText('Johnny Cardoso')).toBeDefined(), { timeout: 5000 })
})

test('perfil de equipo: agregado + formaciones + muestra insuficiente (Barça)', async () => {
  mount('/teams/10', <Route path="/teams/:id" element={<TeamProfile />} />)
  await waitFor(() => expect(screen.getByText('agregado')).toBeDefined(), { timeout: 5000 })
  await waitFor(() => expect(screen.getByText('4-2-3-1')).toBeDefined())
  await waitFor(() => expect(screen.getByText('4-3-3')).toBeDefined())
  // 4-1-4-1 (1 partido) va en "muestra insuficiente"
  await waitFor(() => expect(screen.getByText(/muestra insuficiente/)).toBeDefined())
  await waitFor(() => expect(screen.getByText('4-1-4-1')).toBeDefined())
})

test('encaje táctico: ranking coincide con la Fase 8 (Ball Winner en Dep. Alavés)', async () => {
  const user = (await import('@testing-library/user-event')).default.setup()
  mount('/fit', <Route path="/fit" element={<TacticalFit />} />)
  await waitFor(() => expect(screen.getByText('Deportivo Alavés')).toBeDefined(), { timeout: 5000 })

  const selects = screen.getAllByRole('combobox')
  await user.selectOptions(selects[0], '11') // Deportivo Alavés
  await user.selectOptions(selects[1], '1') // Ball Winner
  await user.click(screen.getByRole('button', { name: 'Buscar' }))

  await waitFor(() => expect(screen.getByText(/Ball Winner/)).toBeDefined(), { timeout: 5000 })
  // top-1 = Camavinga con fit 92.3 (idéntico a la validación de Fase 8)
  await waitFor(() => {
    const row = screen.getByText('Eduardo Camavinga').closest('tr')
    expect(within(row).getByText('92.3')).toBeDefined()
  })
})
