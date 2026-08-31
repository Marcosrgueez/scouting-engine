// Formateadores puros (sin JSX) — separados de ui.jsx para el fast-refresh.

const POS = {
  portero: 'GK',
  central: 'CB',
  lateral: 'FB',
  centrocampista: 'MF',
  extremo: 'W',
  delantero: 'FW',
}
export const posCode = (bucket) => POS[bucket] || '—'

const SIDE = { izquierda: 'L', derecha: 'R', centro: '', desconocido: '?' }
export const sideMark = (lado) => SIDE[lado] ?? ''

const AXIS = {
  possession: 'posesión',
  pass_accuracy: 'precisión de pase',
  crossing_frequency: 'frecuencia de centros',
  press_intensity: 'intensidad de presión',
  directness: 'directitud',
}
export const axisName = (a) => AXIS[a] || a
