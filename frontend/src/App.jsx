import { NavLink, Navigate, Route, Routes } from 'react-router-dom'
import PlayerSearch from './pages/PlayerSearch'
import PlayerProfile from './pages/PlayerProfile'
import TeamProfile from './pages/TeamProfile'
import TacticalFit from './pages/TacticalFit'

function Layout({ children }) {
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
      </header>
      <main className="main">{children}</main>
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
