import { useState } from 'react'
import { Link, useNavigate, useParams } from 'react-router-dom'
import { api } from '../api'
import { useApi } from '../hooks'
import { Bar, ErrorState, Loading } from '../ui'
import { axisName, sideMark } from '../format'

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
            <Bar key={b.stat_type_code} label={b.stat_type_label} value={b.percentile} weight={b.weight} variant="strong" />
          ))}
        </div>
      )}
    </div>
  )
}

function BestTeamRow({ r, rank }) {
  const [open, setOpen] = useState(false)
  return (
    <>
      <tr className="clickable" onClick={() => setOpen(!open)}>
        <td className="r num dim">{rank}</td>
        <td className="name">{r.team_name}</td>
        <td className="r num dim">{r.role_score.toFixed(0)}</td>
        <td className="r num dim">{r.style_component.toFixed(0)}</td>
        <td className="r num" style={{ color: 'var(--signal)', fontWeight: 500 }}>
          {r.score.toFixed(1)}
        </td>
        <td className="mono dim r" style={{ fontSize: 11 }}>{open ? '−' : '+'}</td>
      </tr>
      {open && (
        <tr className="fit-expand">
          <td colSpan={6}>
            <div className="inner expand-enter">
              <p className="t-meta" style={{ marginBottom: 8 }}>{r.team_narrative}</p>
              {r.breakdown.map((b) => (
                <div className="axis-line" key={b.style_axis}>
                  <span className="an">
                    {axisName(b.style_axis)}
                    {b.direction === 'negative' && <span className="against"> (en contra)</span>}
                  </span>
                  <Bar value={b.effective_percentile} variant={b.direction === 'negative' ? 'weak' : 'strong'} labelWidth="0px" />
                  <span className="num" style={{ textAlign: 'right', fontSize: 11, color: 'var(--text-dim)' }}>
                    p{b.team_percentile.toFixed(0)} → {b.effective_percentile.toFixed(0)}
                  </span>
                </div>
              ))}
            </div>
          </td>
        </tr>
      )}
    </>
  )
}

export default function PlayerProfile() {
  const { id } = useParams()
  const nav = useNavigate()
  const p = useApi(() => api.player(id), [id])
  const roles = useApi(() => api.playerRoles(id), [id])
  const [simFilter, setSimFilter] = useState({ side: '', age_max: '' })
  const sim = useApi(() => api.playerSimilar(id, simFilter), [id, simFilter.side, simFilter.age_max])
  const [roleId, setRoleId] = useState('')
  const best = useApi(() => api.playerBestTeams(id, roleId ? { role_id: roleId } : {}), [id, roleId])

  if (p.loading) return <Loading what="el jugador" />
  if (p.error) return <ErrorState error={p.error} />
  const d = p.data

  const groups = {}
  for (const pc of d.percentiles) (groups[pc.category] ||= []).push(pc)
  for (const k in groups) groups[k].sort((a, b) => b.percentile - a.percentile)
  const cats = CAT_ORDER.filter((c) => groups[c])

  return (
    <div>
      <Link to="/players" className="backlink">
        ‹ volver a la búsqueda
      </Link>

      <div className="player-hero">
        {d.photo_url && <img className="player-photo" src={d.photo_url} alt="" />}
        <div>
          <h1 className="t-xl">{d.name}</h1>
          <div className="profile-meta">
            <span>{d.position_label || d.bucket || '—'}</span>
            <span>{d.team_name || 'sin equipo'}</span>
            <span>edad <span className="num">{d.age ?? '—'}</span></span>
            <span><span className="num">{d.minutes}</span> min</span>
            {d.height_cm && <span><span className="num">{d.height_cm}</span> cm</span>}
          </div>
        </div>
      </div>

      <p className={`player-summary ${d.summary.has_role ? '' : 'muted'}`}>{d.summary.text}</p>

      <div className="two-col">
        <div className="col">
          <h2 className="t-l section-title">Encaje por rol</h2>
          {roles.loading && <Loading what="los roles" />}
          {roles.error && <ErrorState error={roles.error} />}
          {roles.data && roles.data.items.length === 0 && <p className="empty-note">{roles.data.note}</p>}
          {roles.data?.items.map((it, i) => (
            <RoleFit key={it.role_id} item={it} defaultOpen={i === 0} />
          ))}
        </div>

        <div className="rule" />

        <div className="col">
          <h2 className="t-l section-title">Perfil de percentiles</h2>
          {d.percentiles.length === 0 ? (
            <p className="empty-note">Sin percentiles: no llega al umbral de {d.min_minutes_threshold} minutos.</p>
          ) : (
            <div className="swap">
              {cats.map((c) => (
                <div className="cat-group" key={c}>
                  <h4>{CAT[c] || c}</h4>
                  {groups[c].map((pc) => (
                    <Bar key={pc.stat_type_code} label={pc.stat_type_label} value={pc.percentile} variant="strong" labelWidth="160px" />
                  ))}
                </div>
              ))}
            </div>
          )}
        </div>
      </div>

      {/* MEJORES EQUIPOS (tactical fit invertido) */}
      <div className="block" style={{ marginTop: 34 }}>
        <h2 className="t-l section-title">Mejores equipos para este perfil</h2>
        {best.error && <ErrorState error={best.error} />}
        {best.data && best.data.count === 0 && <p className="empty-note">{best.data.note}</p>}
        {best.data && best.data.count > 0 && (
          <>
            <div className="filters" style={{ marginBottom: 12 }}>
              <div className="field">
                <label>rol</label>
                <select value={roleId} onChange={(e) => setRoleId(e.target.value)}>
                  {best.data.available_roles.map((rr) => (
                    <option key={rr.role_id} value={rr.role_id}>
                      {rr.role_label} ({rr.score.toFixed(0)})
                    </option>
                  ))}
                </select>
              </div>
              <div className="field">
                <label>&nbsp;</label>
                <span className="t-meta">
                  role score fijo <span className="num">{best.data.role_score?.toFixed(1)}</span>; lo ordena el estilo del equipo
                </span>
              </div>
            </div>
            <div className={`swap ${best.loading ? 'loading' : ''}`}>
              <table className="table">
                <thead>
                  <tr>
                    <th className="r">#</th>
                    <th>equipo</th>
                    <th className="r">role</th>
                    <th className="r">style</th>
                    <th className="r">fit</th>
                    <th className="r" aria-label="expandir"></th>
                  </tr>
                </thead>
                <tbody>
                  {best.data.ranking.map((r, i) => (
                    <BestTeamRow key={r.team_id} r={r} rank={i + 1} />
                  ))}
                </tbody>
              </table>
            </div>
          </>
        )}
      </div>

      {/* SIMILARES */}
      <div className="block" style={{ marginTop: 34 }}>
        <h2 className="t-l section-title">Jugadores similares</h2>
        <div className="filters" style={{ marginBottom: 12 }}>
          <div className="field">
            <label>lado</label>
            <select value={simFilter.side} onChange={(e) => setSimFilter((s) => ({ ...s, side: e.target.value }))}>
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
                    <tr key={s.similar_player_id} className="clickable" onClick={() => nav(`/players/${s.similar_player_id}`)}>
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
            <p className="t-meta" style={{ marginTop: 8 }}>{sim.data.note}</p>
          </>
        )}
      </div>
    </div>
  )
}
