import { useEffect } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import { api } from '../api'
import { useApi } from '../hooks'
import { Bar, ErrorState, Loading } from '../ui'
import { axisName } from '../format'

// orden fijo de ejes para que todos los perfiles se lean igual
const AXIS_ORDER = ['possession', 'pass_accuracy', 'directness', 'crossing_frequency', 'press_intensity']
const sortAxes = (axes) =>
  [...axes].sort((a, b) => AXIS_ORDER.indexOf(a.style_axis) - AXIS_ORDER.indexOf(b.style_axis))

function StyleBars({ axes }) {
  return sortAxes(axes).map((a) => (
    <Bar key={a.style_axis} label={axisName(a.style_axis)} value={a.percentile} variant="neutral" labelWidth="170px" />
  ))
}

export default function TeamProfile() {
  const { id } = useParams()
  const nav = useNavigate()
  const teams = useApi(() => api.teams(), [])
  const style = useApi(() => api.teamStyle(id), [id], { skip: !id })

  // si no hay :id pero ya tenemos equipos, entra en el primero
  useEffect(() => {
    if (!id && teams.data?.items?.length) {
      nav(`/teams/${teams.data.items[0].id}`, { replace: true })
    }
  }, [id, teams.data, nav])

  const d = style.data

  return (
    <div>
      <div className="page-head">
        <h1 className="t-xl">Estilo de equipo</h1>
        {d && <span className="count">{d.by_formation.length + 1} perfiles — LaLiga 2024/25</span>}
      </div>

      <div className="filters">
        <div className="field">
          <label>equipo</label>
          <select value={id || ''} onChange={(e) => nav(`/teams/${e.target.value}`)}>
            {(teams.data?.items || []).map((t) => (
              <option key={t.id} value={t.id}>
                {t.name}
              </option>
            ))}
          </select>
        </div>
      </div>

      {style.loading && <Loading what="el estilo" />}
      {style.error && <ErrorState error={style.error} />}

      {d && (
        <div style={{ marginTop: 18, maxWidth: 640 }}>
          <div className="formation-group" style={{ borderTop: 0 }}>
            <div className="fg-head">
              <span className="fg-name">agregado</span>
              <span className="fg-n">{d.aggregate.n_matches} partidos, todas las formaciones</span>
            </div>
            <StyleBars axes={d.aggregate.axes} />
          </div>

          <h2 className="t-l section-title" style={{ marginTop: 30, marginBottom: 4 }}>
            Por formación
          </h2>
          {d.by_formation.map((fp) => (
            <div className="formation-group" key={fp.formation}>
              <div className="fg-head">
                <span className="fg-name">{fp.formation}</span>
                <span className="fg-n">{fp.n_matches} partidos</span>
              </div>
              <StyleBars axes={fp.axes} />
            </div>
          ))}

          {d.formations_below_threshold.length > 0 && (
            <div className="insufficient">
              <h4>muestra insuficiente (&lt; {d.min_matches} partidos — sin perfil de estilo)</h4>
              {d.formations_below_threshold.map((f) => (
                <div className="row" key={f.formation || 'null'}>
                  <span className="fn">{f.formation || '—'}</span>
                  <span>
                    {f.n_matches} {f.n_matches === 1 ? 'partido' : 'partidos'}
                  </span>
                </div>
              ))}
            </div>
          )}

          <p className="t-meta" style={{ marginTop: 22 }}>
            Percentil entre los 20 equipos de LaLiga. Un valor alto no es "mejor": es lo que
            hace ese equipo (posesión alta, presión baja…).
          </p>
        </div>
      )}
    </div>
  )
}
