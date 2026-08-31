// Cliente de la API de la Fase 9. Sin auth, CORS abierto.
// El frontend NO tiene lógica de negocio: pide y muestra.

const BASE = import.meta.env.VITE_API_BASE || 'http://127.0.0.1:8000'

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
  for (const [k, v] of Object.entries(params || {})) {
    if (v !== undefined && v !== null && v !== '') p.set(k, v)
  }
  const s = p.toString()
  return s ? `?${s}` : ''
}

export const api = {
  players: (filters) => req(`/players${qs(filters)}`),
  player: (id) => req(`/players/${id}`),
  playerSimilar: (id, filters) => req(`/players/${id}/similar${qs(filters)}`),
  playerRoles: (id) => req(`/players/${id}/roles`),
  playerBestTeams: (id, filters) => req(`/players/${id}/best-teams${qs(filters)}`),
  teams: () => req('/teams'),
  teamStyle: (id) => req(`/teams/${id}/style`),
  roles: () => req('/roles'),
  tacticalFit: (body) =>
    req('/scouting/tactical-fit', {
      method: 'POST',
      headers: { 'content-type': 'application/json' },
      body: JSON.stringify(body),
    }),
}
