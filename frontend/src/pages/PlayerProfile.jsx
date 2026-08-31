import { useState } from 'react'
import { Link, useNavigate, useParams } from 'react-router-dom'
import { api } from '../api'
import { useApi } from '../hooks'
import { Bar, ErrorState, Loading } from '../ui'
import { sideMark } from '../format'

const CAT = {
  participacion: 'participación',
  pase: 'pase',
  creacion: 'creación',
  finalizacion: 'finalización',
  duelo: 'duelo',
  regate: 'regate',
  defensa: 'defensa',
  disciplina: 'disciplina',
  posesion: 'posesión',
  porteria: 'portería',
}
const CAT_ORDER = ['pase', 'creacion', 'finalizacion', 'regate', 'duelo', 'defensa', 'posesion', 'disciplina', 'porteria', 'participacion']

function RoleFit({ item, defaultOpen }) {
  const [open, setOpen] = useState(defaultOpen)
  return (
    <div className={`role ${open ? 'open' : ''}`}>
      <button className="role-head" onClick={() => setOpen(!open)} aria-expanded={open}>
        <span className="rname">{item.role_label}</span>
        <span className="rscore">{item.score.toFixed(1)}</span>
        <span className="chev">▶</span>
      </button>
      {open && (
        <div className="role-body expand-enter">
          <div className="meta">
            media ponderada de {item.metrics_used} percentiles (peso total {item.total_weight})
            {item.total_weight < 13 && ' — faltaba alguna métrica'}
          </div>
          {item.breakdown.map((b) => (
            <Bar
              key={b.stat_type_code}
              label={b.stat_type_label}
              value={b.percentile}
              weight={b.weight}
              variant="strong"
            />
          ))}
        </div>
      )}
    </div>
  )
}

export default function PlayerProfile() {
  const { id } = useParams()
  const nav = useNavigate()
  const p = useApi(() => api.player(id), [id])
  const roles = useApi(() => api.playerRoles(id), [id])
  const [simFilter, setSimFilter] = useState({ side: '', age_max: '' })
  const sim = useApi(
    () => api.playerSimilar(id, simFilter),
    [id, simFilter.side, simFilter.age_max],
  )

  if (p.loading) return <Loading what="el jugador" />
  if (p.error) return <ErrorState error={p.error} />
  const d = p.data

  // percentiles agrupados por categoría, cada grupo ordenado por percentil desc
  const groups = {}
  for (const pc of d.percentiles) (groups[pc.category] ||= []).push(pc)
  for (const k in groups) groups[k].sort((a, b) => b.percentile - a.percentile)
  const cats = CAT_ORDER.filter((c) => groups[c])

  return (
    <div>
      <Link to="/players" className="backlink">
        ‹ volver a la búsqueda
      </Link>

      <div className="profile-head">
        <h1 className="t-xl">{d.name}</h1>
      </div>
      <div className="profile-meta">
        <span>{d.position_label || d.bucket || '—'}</span>
        <span>{d.team_name || 'sin equipo'}</span>
        <span>
          edad <span className="num">{d.age ?? '—'}</span>
        </span>
        <span>
          <span className="num">{d.minutes}</span> min
        </span>
        {d.height_cm && (
          <span>
            <span className="num">{d.height_cm}</span> cm
          </span>
        )}
      </div>

      <div className="two-col">
        {/* IZQUIERDA — encaje por rol, interactivo. El desglose es el centro del proyecto. */}
        <div className="col">
          <h2 className="t-l section-title">Encaje por rol</h2>
          {roles.loading && <Loading what="los roles" />}
          {roles.error && <ErrorState error={roles.error} />}
          {roles.data && roles.data.items.length === 0 && (
            <p className="empty-note">{roles.data.note}</p>
          )}
          {roles.data?.items.map((it, i) => (
            <RoleFit key={it.role_id} item={it} defaultOpen={i === 0} />
          ))}
        </div>

        <div className="rule" />

        {/* DERECHA — perfil de percentiles, lectura densa y estática. */}
        <div className="col">
          <h2 className="t-l section-title">Perfil de percentiles</h2>
          {d.percentiles.length === 0 ? (
            <p className="empty-note">
              Sin percentiles: no llega al umbral de {d.min_minutes_threshold} minutos.
            </p>
          ) : (
            <div className="swap">
              {cats.map((c) => (
                <div className="cat-group" key={c}>
                  <h4>{CAT[c] || c}</h4>
                  {groups[c].map((pc) => (
                    <Bar
                      key={pc.stat_type_code}
                      label={pc.stat_type_label}
                      value={pc.percentile}
                      variant="strong"
                      labelWidth="160px"
                    />
                  ))}
                </div>
              ))}
            </div>
          )}
        </div>
      </div>

      {/* SIMILARES */}
      <div className="block" style={{ marginTop: 34 }}>
        <h2 className="t-l section-title">Jugadores similares</h2>
        <div className="filters" style={{ marginBottom: 12 }}>
          <div className="field">
            <label>lado</label>
            <select
              value={simFilter.side}
              onChange={(e) => setSimFilter((s) => ({ ...s, side: e.target.value }))}
            >
              <option value="">cualquiera</option>
              <option value="izquierda">izquierda</option>
              <option value="derecha">derecha</option>
              <option value="centro">centro</option>
            </select>
          </div>
          <div className="field">
            <label>edad máx.</label>
            <input
              className="num"
              type="number"
              min="14"
              max="45"
              placeholder="—"
              value={simFilter.age_max}
              onChange={(e) => setSimFilter((s) => ({ ...s, age_max: e.target.value }))}
            />
          </div>
        </div>

        {sim.error && <ErrorState error={sim.error} />}
        {sim.data && sim.data.items.length === 0 && <p className="empty-note">{sim.data.note}</p>}
        {sim.data && sim.data.items.length > 0 && (
          <>
            <div className={`swap ${sim.loading ? 'loading' : ''}`}>
              <table className="table">
                <thead>
                  <tr>
                    <th className="r">#</th>
                    <th>jugador</th>
                    <th>lado</th>
                    <th className="r">edad</th>
                    <th>equipo</th>
                    <th className="r">similitud</th>
                  </tr>
                </thead>
                <tbody>
                  {sim.data.items.map((s) => (
                    <tr
                      key={s.similar_player_id}
                      className="clickable"
                      onClick={() => nav(`/players/${s.similar_player_id}`)}
                    >
                      <td className="r num dim">{s.rank}</td>
                      <td className="name">{s.name}</td>
                      <td className="mono dim">{sideMark(s.side)}</td>
                      <td className="r num">{s.age ?? '—'}</td>
                      <td className="dim">{s.team_name || '—'}</td>
                      <td className="r num">{s.similarity_score.toFixed(3)}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
            <p className="t-meta" style={{ marginTop: 8 }}>
              {sim.data.note}
            </p>
          </>
        )}
      </div>
    </div>
  )
}
