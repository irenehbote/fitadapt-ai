import { useState } from 'react'
import { getProgress, type ProfilePayload, type ProgressResult } from '../api'

// Pestaña de informe de progreso entre dos medidas. Usa la 1a condicion del perfil.
export function ProgressTab({ profile }: { profile: ProfilePayload }) {
  const [w0, setW0] = useState(80)
  const [waist0, setWaist0] = useState(90)
  const [w1, setW1] = useState(76)
  const [waist1, setWaist1] = useState(85)
  const [days, setDays] = useState(84)
  const [res, setRes] = useState<ProgressResult | null>(null)
  const [error, setError] = useState<string | null>(null)

  async function calcular() {
    setError(null)
    try {
      setRes(await getProgress({
        before: { label: 'inicio', weight_kg: w0, waist_cm: waist0 },
        after: { label: 'ahora', weight_kg: w1, waist_cm: waist1 },
        days_between: days,
        condition: profile.conditions[0],
      }))
    } catch (e) {
      setError((e as Error).message)
    }
  }

  return (
    <div>
      <div className="row">
        <label>Peso inicial (kg)
          <input type="number" value={w0} onChange={(e) => setW0(Number(e.target.value))} /></label>
        <label>Cintura inicial (cm)
          <input type="number" value={waist0} onChange={(e) => setWaist0(Number(e.target.value))} /></label>
      </div>
      <div className="row">
        <label>Peso actual (kg)
          <input type="number" value={w1} onChange={(e) => setW1(Number(e.target.value))} /></label>
        <label>Cintura actual (cm)
          <input type="number" value={waist1} onChange={(e) => setWaist1(Number(e.target.value))} /></label>
        <label>Dias entre medidas
          <input type="number" min={1} value={days} onChange={(e) => setDays(Number(e.target.value))} /></label>
      </div>
      <button onClick={calcular}>Generar informe</button>
      {error && <p className="error">{error}</p>}

      {res && (
        <div className="card result">
          <div className="metrics">
            <div className="metric">
              <span className="metric-value">{res.weight_change_pct}%</span>
              <span className="metric-label">Cambio de peso</span>
            </div>
            <div className="metric">
              <span className="metric-value">{res.waist_change_cm} cm</span>
              <span className="metric-label">Cambio de cintura</span>
            </div>
            <div className="metric">
              <span className="metric-value">{res.progress_score}</span>
              <span className="metric-label">Puntuacion (0-100)</span>
            </div>
            <div className="metric">
              <span className="metric-value">{res.plausible ? 'Si' : '!'}</span>
              <span className="metric-label">Plausible</span>
            </div>
          </div>
          <ul className="notes">{res.commentary.map((n, i) => <li key={i}>{n}</li>)}</ul>
        </div>
      )}
    </div>
  )
}
