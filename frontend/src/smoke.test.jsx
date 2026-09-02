/**
 * Smoke test de las pantallas contra la API REAL (Fase 9 + 11 + 12a).
 * Requiere uvicorn en http://127.0.0.1:8000 (o VITE_API_BASE) con LaLiga
 * 24/25 Y 25/26 cargadas.
 *
 *   npm test
 */
import { render, screen, waitFor, within } from '@testing-library/react'
import { MemoryRouter, Route, Routes } from 'react-router-dom'
import { beforeEach, expect, test } from 'vitest'

import { setSeason } from './api'
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

beforeEach(() => setSeason(null)) // default del backend = 25/26

test('helpers', () => {
  expect(posCode('centrocampista')).toBe('MF')
  expect(sideMark('izquierda')).toBe('L')
  expect(axisName('press_intensity')).toBe('intensidad de presión')
})

test('búsqueda: temporada por defecto (25/26) lista jugadores', async () => {
  mount('/players', <Route path="/players" element={<PlayerSearch />} />)
  await waitFor(() => expect(screen.getByText(/346 con datos/)).toBeDefined(), { timeout: 5000 })
  expect(screen.getAllByRole('row').length).toBeGreaterThan(10)
})

test('ficha 25/26: foto + resumen + roles + similares + mejores equipos (Pedri)', async () => {
  mount('/players/444', <Route path="/players/:id" element={<PlayerProfile />} />)
  await waitFor(() => expect(screen.getByRole('heading', { name: 'Pedri' })).toBeDefined(), {
    timeout: 5000,
  })
  await waitFor(() => expect(document.querySelector('img.player-photo')).toBeTruthy())
  await waitFor(() =>
    expect(
      screen.getByText(/se perfila como Deep-Lying Playmaker \(score 95\.5\)/),
    ).toBeDefined(),
  )
  await waitFor(() => expect(screen.getAllByText('95.5').length).toBeGreaterThan(0))
  await waitFor(() => expect(screen.getByText('Mejores equipos para este perfil')).toBeDefined())
  await waitFor(() => expect(screen.getByText('Arda Güler')).toBeDefined(), { timeout: 5000 })
})

test('equipo 25/26: narrativa + formaciones + muestra insuficiente (Atlético)', async () => {
  mount('/teams/14', <Route path="/teams/:id" element={<TeamProfile />} />)
  await waitFor(() => expect(screen.getByText('agregado')).toBeDefined(), { timeout: 5000 })
  await waitFor(() => expect(screen.getByText(/muestra insuficiente/)).toBeDefined())
})

test('encaje táctico 24/25 preservado: Ball Winner en Dep. Alavés = Camavinga 92.3', async () => {
  setSeason('2024/2025')
  const user = (await import('@testing-library/user-event')).default.setup()
  mount('/fit', <Route path="/fit" element={<TacticalFit />} />)
  await waitFor(() => expect(screen.getByText('Deportivo Alavés')).toBeDefined(), { timeout: 5000 })
  const selects = screen.getAllByRole('combobox')
  await user.selectOptions(selects[0], '11')
  await user.selectOptions(selects[1], '1')
  await user.click(screen.getByRole('button', { name: 'Buscar' }))
  await waitFor(
    () => {
      const row = screen.getByText('Eduardo Camavinga').closest('tr')
      expect(within(row).getByText('92.3')).toBeDefined()
    },
    { timeout: 5000 },
  )
})

test('cambio de temporada: mismo jugador, score distinto (Camavinga BW 90.1 vs 79.0)', async () => {
  setSeason('2024/2025')
  const { unmount } = mount('/players/396', <Route path="/players/:id" element={<PlayerProfile />} />)
  await waitFor(() => expect(screen.getByText(/score 90\.1\)/)).toBeDefined(), { timeout: 5000 })
  unmount()

  setSeason('2025/2026')
  mount('/players/396', <Route path="/players/:id" element={<PlayerProfile />} />)
  await waitFor(() => expect(screen.getByText(/score 79\.0\)/)).toBeDefined(), { timeout: 5000 })
})
