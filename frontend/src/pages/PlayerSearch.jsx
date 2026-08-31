import { useMemo, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { api } from '../api'
import { useApi } from '../hooks'
import { ErrorState } from '../ui'
import { posCode, sideMark } from '../format'

const BUCKETS = ['portero', 'central', 'lateral', 'centrocampista', 'extremo', 'delantero']
const SIDES = ['izquierda', 'derecha', 'centro']
const PAGE = 50

export default function PlayerSearch() {
  const nav = useNavigate()
  const teams = useApi(() => api.teams(), [])
  const [f, setF] = useState({
    bucket: '',
    team_id: '',
    min_minutes: 900,
    age_min: '',
    age_max: '',
    side: '',
  })
  const [offset, setOffset] = useState(0)

  const query = useMemo(
    () => ({ ...f, limit: PAGE, offset }),
    [f, offset],
  )
  const res = useApi(() => api.players(query), [query])

  const set = (k) => (e) => {
    setF((prev) => ({ ...prev, [k]: e.target.value }))
    setOffset(0)
  }
  const clear = () => {
    setF({ bucket: '', team_id: '', min_minutes: 900, age_min: '', age_max: '', side: '' })
    setOffset(0)
  }

  const data = res.data
  const total = data?.total_count ?? 0

  return (
    <div>
      <div className="page-head">
        <h1 className="t-xl">Jugadores</h1>
        {data && <span className="count">{total} con datos</span>}
      </div>

      <div className="filters">
        <div className="field">
          <label>posición</label>
          <select value={f.bucket} onChange={set('bucket')}>
            <option value="">todas</option>
            {BUCKETS.map((b) => (
              <option key={b} value={b}>
                {b}
              </option>
            ))}
          </select>
        </div>
        <div className="field">
          <label>equipo</label>
          <select value={f.team_id} onChange={set('team_id')}>
            <option value="">todos</option>
            {(teams.data?.items || []).map((t) => (
              <option key={t.id} value={t.id}>
                {t.name}
              </option>
            ))}
          </select>
        </div>
        <div className="field">
          <label>lado</label>
          <select value={f.side} onChange={set('side')}>
            <option value="">cualquiera</option>
            {SIDES.map((s) => (
              <option key={s} value={s}>
                {s}
              </option>
            ))}
          </select>
        </div>
        <div className="field">
          <label>minutos mín.</label>
          <input className="num" type="number" min="0" step="90" value={f.min_minutes} onChange={set('min_minutes')} />
        </div>
        <div className="field range">
          <div className="field">
            <label>edad</label>
            <input className="num" type="number" min="14" max="45" placeholder="—" value={f.age_min} onChange={set('age_min')} />
          </div>
          <span className="dash">–</span>
          <div className="field">
            <label>&nbsp;</label>
            <input className="num" type="number" min="14" max="45" placeholder="—" value={f.age_max} onChange={set('age_max')} />
          </div>
        </div>
        <button className="btn ghost" onClick={clear}>
          Limpiar
        </button>
      </div>

      {res.error ? (
        <ErrorState error={res.error} />
      ) : (
        <>
          <div className={`swap ${res.loading ? 'loading' : ''}`}>
            <table className="table">
              <thead>
                <tr>
                  <th>jugador</th>
                  <th>pos</th>
                  <th>lado</th>
                  <th className="r">edad</th>
                  <th>equipo</th>
                  <th className="r">min</th>
                </tr>
              </thead>
              <tbody>
                {(data?.items || []).map((p) => (
                  <tr key={p.id} className="clickable" onClick={() => nav(`/players/${p.id}`)}>
                    <td className="name">{p.name}</td>
                    <td className="mono dim">{posCode(p.bucket)}</td>
                    <td className="mono dim">{sideMark(p.side)}</td>
                    <td className="r num">{p.age ?? '—'}</td>
                    <td className="dim">{p.team_name ?? '—'}</td>
                    <td className="r num">{p.minutes}</td>
                  </tr>
                ))}
                {data && data.items.length === 0 && (
                  <tr>
                    <td colSpan={6} className="dim" style={{ padding: '24px 12px' }}>
                      Ningún jugador cumple estos filtros.
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>

          {total > 0 && (
            <div className="pager">
              <button disabled={offset === 0} onClick={() => setOffset(Math.max(0, offset - PAGE))}>
                anteriores
              </button>
              <span className="num">
                {offset + 1}–{Math.min(offset + PAGE, total)} de {total}
              </span>
              <button disabled={offset + PAGE >= total} onClick={() => setOffset(offset + PAGE)}>
                siguientes
              </button>
            </div>
          )}
        </>
      )}
    </div>
  )
}
