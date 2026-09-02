import { useEffect, useState } from 'react'
import { NavLink, Navigate, Route, Routes } from 'react-router-dom'
import { api, setSeason } from './api'
import PlayerSearch from './pages/PlayerSearch'
import PlayerProfile from './pages/PlayerProfile'
import TeamProfile from './pages/TeamProfile'
import TacticalFit from './pages/TacticalFit'

function Layout({ children }) {
  const [seasons, setSeasons] = useState([])
  const [season, setSeasonId] = useState(null)

  useEffect(() => {
    api
      .seasons()
      .then((d) => {
        setSeasons(d.items)
        setSeasonId(String(d.default))
        setSeason(d.default)
      })
      .catch(() => {})
  }, [])

  const onChange = (e) => {
    setSeasonId(e.target.value)
    setSeason(e.target.value)
  }

  // agrupadas por competición para el <optgroup> (solo las que existen)
  const groups = []
  for (const s of seasons) {
    let g = groups.find((x) => x.competition === s.competition)
    if (!g) {
      g = { competition: s.competition, tier: s.tier, items: [] }
      groups.push(g)
    }
    g.items.push(s)
  }

  return (
    <div className="app">
      <header className="topbar">
        <span className="wordmark">
          scouting<b>-engine</b>
        </span>
        <nav className="nav">
          <NavLink to="/players" className={({ isActive }) => (isActive ? 'active' : '')}>
            Jugadores
          </NavLink>
          <NavLink to="/teams" className={({ isActive }) => (isActive ? 'active' : '')}>
            Equipos
          </NavLink>
          <NavLink to="/fit" className={({ isActive }) => (isActive ? 'active' : '')}>
            Encaje táctico
          </NavLink>
        </nav>
        {seasons.length > 1 && (
          <label className="season-picker">
            {groups.length > 1 ? 'competición' : 'temporada'}
            <select value={season || ''} onChange={onChange}>
              {groups.map((g) => (
                <optgroup key={g.competition} label={g.competition}>
                  {g.items.map((s) => (
                    <option key={s.id} value={s.id}>
                      {groups.length > 1 ? `${g.competition} · ${s.name}` : s.name}
                    </option>
                  ))}
                </optgroup>
              ))}
            </select>
          </label>
        )}
      </header>
      {/* key: al cambiar de temporada, remonta el contenido -> refetch limpio, sin mezclar */}
      <main className="main" key={season || 'loading'}>
        {season ? children : <div className="state">Cargando temporadas…</div>}
      </main>
    </div>
  )
}

export default function App() {
  return (
    <Layout>
      <Routes>
        <Route path="/" element={<Navigate to="/players" replace />} />
        <Route path="/players" element={<PlayerSearch />} />
        <Route path="/players/:id" element={<PlayerProfile />} />
        <Route path="/teams" element={<TeamProfile />} />
        <Route path="/teams/:id" element={<TeamProfile />} />
        <Route path="/fit" element={<TacticalFit />} />
        <Route path="*" element={<div className="state">Ruta no encontrada.</div>} />
      </Routes>
    </Layout>
  )
}
