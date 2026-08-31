// Primitivas de UI (componentes). Los formateadores puros están en format.js.

// Una sola barra horizontal 0-100 — el lenguaje visual de todo el sistema.
// `variant`: strong (percentil de jugador, ya orientado) | neutral (valor de
// equipo, ni bueno ni malo) | weak (eje que trabaja en contra) | signal.
export function Bar({ label, value, max = 100, weight, variant = 'strong', labelWidth }) {
  const pct = Math.max(0, Math.min(100, (value / max) * 100))
  return (
    <div className="bar-row" style={labelWidth ? { '--label-w': labelWidth } : undefined}>
      {label !== undefined && (
        <span className="bl" title={label}>
          {label}
          {weight != null && <span className="w">×{weight}</span>}
        </span>
      )}
      <span className="bar-track">
        <span className={`bar-fill ${variant}`} style={{ width: `${pct}%` }} />
      </span>
      <span className="bv">{Number(value).toFixed(value % 1 === 0 ? 0 : 1)}</span>
    </div>
  )
}

export function Loading({ what = 'datos' }) {
  return <div className="state">Cargando {what}…</div>
}

export function ErrorState({ error }) {
  return <div className="state error">{error?.message || 'Error inesperado'}</div>
}
