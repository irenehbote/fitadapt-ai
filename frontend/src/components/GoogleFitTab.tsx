import { useState } from 'react'
import { getGoogleFit, type GoogleFitResult } from '../api'

// Pestaña que simula como los datos de Google Fit ajustan el plan del dia.
export function GoogleFitTab() {
  const [steps, setSteps] = useState(12000)
  const [sleep, setSleep] = useState(5)
  const [hrTrend, setHrTrend] = useState('increasing')
  const [res, setRes] = useState<GoogleFitResult | null>(null)
  const [error, setError] = useState<string | null>(null)

  async function calcular() {
    setError(null)
    try {
      setRes(await getGoogleFit({
        steps_today: steps, sleep_hours_last_night: sleep, resting_hr_trend: hrTrend,
      }))
    } catch (e) {
      setError((e as Error).message)
    }
  }

  return (
    <div>
      <p className="muted">
        Datos importados (la conexion OAuth real con Google Fit no esta integrada;
        aqui los introduces a mano para ver su efecto).
      </p>
      <div className="row">
        <label>Pasos hoy
          <input type="number" min={0} value={steps} onChange={(e) => setSteps(Number(e.target.value))} /></label>
        <label>Horas dormidas
          <input type="number" min={0} max={12} value={sleep} onChange={(e) => setSleep(Number(e.target.value))} /></label>
        <label>FC en reposo
          <select value={hrTrend} onChange={(e) => setHrTrend(e.target.value)}>
            <option value="stable">estable</option>
            <option value="increasing">subiendo</option>
            <option value="decreasing">bajando</option>
          </select>
        </label>
      </div>
      <button onClick={calcular}>Ver ajustes</button>
      {error && <p className="error">{error}</p>}

      {res && (
        <div className="card result">
          <div className="metrics">
            <div className="metric">
              <span className="metric-value">{res.intensity_cap}/10</span>
              <span className="metric-label">Intensidad maxima</span>
            </div>
            <div className="metric">
              <span className="metric-value">{res.reduce_cardio ? 'Si' : 'No'}</span>
              <span className="metric-label">Reducir cardio</span>
            </div>
            <div className="metric">
              <span className="metric-value">{res.suggest_deload ? 'Si' : 'No'}</span>
              <span className="metric-label">Sugerir descarga</span>
            </div>
          </div>
          <ul className="notes">{res.notes.map((n, i) => <li key={i}>{n}</li>)}</ul>
        </div>
      )}
    </div>
  )
}
