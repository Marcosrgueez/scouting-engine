// Cliente de la API. Sin auth, CORS abierto.
// Fase 12a: temporada global. setSeason() la fija; se añade ?season= a todo.

const BASE = import.meta.env.VITE_API_BASE || 'http://127.0.0.1:8000'

let _season = null // nombre de temporada, ej '2025/2026'; null = default del backend
export function setSeason(name) {
  _season = name || null
}
export function getSeason() {
  return _season
}

async function req(path, opts) {
  let res
  try {
    res = await fetch(BASE + path, opts)
  } catch {
    throw new Error(`No se puede contactar la API en ${BASE}. ¿Está corriendo uvicorn?`)
  }
  const body = await res.json().catch(() => null)
  if (!res.ok) {
    const detail = body && body.detail
    const msg = Array.isArray(detail)
      ? detail.map((d) => `${d.loc?.join('.')}: ${d.msg}`).join('; ')
      : detail || `HTTP ${res.status}`
    const err = new Error(msg)
    err.status = res.status
    throw err
  }
  return body
}

const qs = (params) => {
  const p = new URLSearchParams()
  const merged = { ...(params || {}) }
  if (_season && merged.season === undefined) merged.season = _season
  for (const [k, v] of Object.entries(merged)) {
    if (v !== undefined && v !== null && v !== '') p.set(k, v)
  }
  const s = p.toString()
  return s ? `?${s}` : ''
}

export const api = {
  seasons: () => req('/seasons'),
  players: (filters) => req(`/players${qs(filters)}`),
  player: (id) => req(`/players/${id}${qs()}`),
  playerSimilar: (id, filters) => req(`/players/${id}/similar${qs(filters)}`),
  playerRoles: (id) => req(`/players/${id}/roles${qs()}`),
  playerBestTeams: (id, filters) => req(`/players/${id}/best-teams${qs(filters)}`),
  teams: () => req(`/teams${qs()}`),
  teamStyle: (id) => req(`/teams/${id}/style${qs()}`),
  roles: () => req('/roles'),
  tacticalFit: (body) =>
    req(`/scouting/tactical-fit${qs()}`, {
      method: 'POST',
      headers: { 'content-type': 'application/json' },
      body: JSON.stringify(body),
    }),
}
