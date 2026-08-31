import { useState } from 'react'
import { api } from '../api'
import { useAction, useApi } from '../hooks'
import { Bar, ErrorState } from '../ui'
import { axisName } from '../format'

function Row({ r, rank }) {
  const [open, setOpen] = useState(false)
  return (
    <>
      <tr className="clickable" onClick={() => setOpen(!open)}>
        <td className="r num dim">{rank}</td>
        <td className="name">{r.player_name}</td>
        <td className="r num dim">{r.role_score.toFixed(0)}</td>
        <td className="r num dim">{r.style_component.toFixed(0)}</td>
        <td className="r num" style={{ color: 'var(--signal)', fontWeight: 500 }}>
          {r.score.toFixed(1)}
        </td>
        <td className="mono dim r" style={{ fontSize: 11 }}>
          {open ? '−' : '+'}
        </td>
      </tr>
      {open && (
        <tr className="fit-expand">
          <td colSpan={6}>
            <div className="inner expand-enter">
              <div className="t-meta" style={{ marginBottom: 6 }}>
                fit = 0.7 × role ({r.role_score}) + 0.3 × style ({r.style_component})
              </div>
              {r.breakdown.map((b) => (
                <div className="axis-line" key={b.style_axis}>
                  <span className="an">
                    {axisName(b.style_axis)}
                    {b.direction === 'negative' && <span className="against"> (en contra)</span>}
                  </span>
                  <Bar
                    value={b.effective_percentile}
                    variant={b.direction === 'negative' ? 'weak' : 'strong'}
                    labelWidth="0px"
                  />
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

export default function TacticalFit() {
  const teams = useApi(() => api.teams(), [])
  const roles = useApi(() => api.roles(), [])
  const [teamId, setTeamId] = useState('')
  const [roleId, setRoleId] = useState('')
  const [formation, setFormation] = useState('')

  // formaciones disponibles del equipo elegido, para el desplegable
  const style = useApi(() => api.teamStyle(teamId), [teamId], { skip: !teamId })
  const formations = style.data?.by_formation?.map((f) => f.formation) || []

  const fit = useAction(api.tacticalFit)

  const run = () => {
    if (!teamId || !roleId) return
    fit.run({
      team_id: Number(teamId),
      role_id: Number(roleId),
      formation: formation || undefined,
    })
  }

  const d = fit.data

  return (
    <div>
      <div className="page-head">
        <h1 className="t-xl">Encaje táctico</h1>
      </div>

      <div className="filters">
        <div className="field">
          <label>equipo</label>
          <select
            value={teamId}
            onChange={(e) => {
              setTeamId(e.target.value)
              setFormation('')
            }}
          >
            <option value="">elegir…</option>
            {(teams.data?.items || []).map((t) => (
              <option key={t.id} value={t.id}>
                {t.name}
              </option>
            ))}
          </select>
        </div>
        <div className="field">
          <label>rol</label>
          <select value={roleId} onChange={(e) => setRoleId(e.target.value)}>
            <option value="">elegir…</option>
            {(roles.data?.items || []).map((r) => (
              <option key={r.id} value={r.id}>
                {r.label}
              </option>
            ))}
          </select>
        </div>
        <div className="field">
          <label>formación</label>
          <select value={formation} onChange={(e) => setFormation(e.target.value)} disabled={!teamId}>
            <option value="">agregado del equipo</option>
            {formations.map((f) => (
              <option key={f} value={f}>
                {f}
              </option>
            ))}
          </select>
        </div>
        <button className="btn" onClick={run} disabled={!teamId || !roleId || fit.loading}>
          {fit.loading ? 'Calculando…' : 'Buscar'}
        </button>
      </div>

      {fit.error && <ErrorState error={fit.error} />}

      {d && (
        <div style={{ marginTop: 18 }}>
          <div className="fit-summary">
            <div className="fit-title">
              <span className="mono">{d.role_label}</span> en{' '}
              <span className="mono">{d.team_name}</span>
              {d.formation ? (
                <>
                  {' '}con <span className="mono">{d.formation}</span>
                </>
              ) : (
                ' (estilo agregado)'
              )}
            </div>
            <div className="fit-facts">
              <span>
                <span className="num">{d.count}</span> jugadores
              </span>
              <span>
                <span className="num">{d.n_matches}</span> partidos de muestra
              </span>
              <span>
                pesos <span className="num">{Math.round(d.w_role * 100)}</span> role /{' '}
                <span className="num">{Math.round(d.w_style * 100)}</span> style
              </span>
            </div>
          </div>

          <table className="table">
            <thead>
              <tr>
                <th className="r">#</th>
                <th>jugador</th>
                <th className="r">role</th>
                <th className="r">style</th>
                <th className="r">fit</th>
                <th className="r" aria-label="expandir"></th>
              </tr>
            </thead>
            <tbody>
              {d.ranking.map((r, i) => (
                <Row key={r.player_id} r={r} rank={i + 1} />
              ))}
            </tbody>
          </table>
          <p className="t-meta" style={{ marginTop: 10 }}>
            Clic en una fila para ver por qué. El estilo del equipo es el mismo para todos; lo
            que cambia el orden es el role score de cada jugador.
          </p>
        </div>
      )}

      {!d && !fit.error && !fit.loading && (
        <p className="empty-note" style={{ marginTop: 16 }}>
          Elige equipo y rol. La formación es opcional: si la dejas en "agregado", se usa el
          estilo medio del equipo en toda la temporada. Una formación sin muestra suficiente
          (&lt; 5 partidos) no aparece en el desplegable.
        </p>
      )}
    </div>
  )
}
