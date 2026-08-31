/* Hooks genéricos de fetch: el llamador controla el array de deps, así que
   la regla exhaustive-deps no aplica a este fichero. */
/* eslint-disable react-hooks/exhaustive-deps */
import { useCallback, useEffect, useRef, useState } from 'react'

// Fetch simple con estados de carga/error. No usamos React Query: son 4
// pantallas de lectura + 1 POST, no hay caché ni refetch que justifiquen
// la dependencia. (Con más pantallas y datos compartidos, sí.)
export function useApi(fetcher, deps, { skip = false } = {}) {
  const [state, setState] = useState({ data: null, loading: !skip, error: null })
  const seq = useRef(0)

  useEffect(() => {
    if (skip) {
      setState({ data: null, loading: false, error: null })
      return
    }
    const id = ++seq.current
    setState((s) => ({ ...s, loading: true, error: null }))
    fetcher()
      .then((data) => {
        if (id === seq.current) setState({ data, loading: false, error: null })
      })
      .catch((error) => {
        if (id === seq.current) setState({ data: null, loading: false, error })
      })
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, deps)

  return state
}

// Acción manual (para el POST de tactical-fit): se dispara con run().
export function useAction(fn) {
  const [state, setState] = useState({ data: null, loading: false, error: null })
  const run = useCallback(
    async (...args) => {
      setState({ data: null, loading: true, error: null })
      try {
        const data = await fn(...args)
        setState({ data, loading: false, error: null })
        return data
      } catch (error) {
        setState({ data: null, loading: false, error })
      }
    },
    [fn],
  )
  return { ...state, run }
}
