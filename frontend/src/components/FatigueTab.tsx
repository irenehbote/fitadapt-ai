import { useState } from 'react'
import { getFatigue, type FatigueResult } from '../api'

// Pestaña de fatiga por turnos de trabajo y descanso.
export function FatigueTab() {
  const [days, setDays] = useState(4)
  const [nights, setNights] = useState(3)
  const [sleep, setSleep] = useState(5)
  const [stress, setStress] = useState(6)
  const [res, setRes] = useState<FatigueResult | null>(null)
  const [error, setError] = useState<string | null>(null)

  async function calcular() {
    setError(null)
    try {
      setRes(await getFatigue({
        consecutive_work_days: days, night_shifts_this_week: nights,
        hours_slept_last_night: sleep, stress_level: stress,
      }))
    } catch (e) {
      setError((e as Error).message)
    }
  }

  return (
    <div>
      <div className="row">
        <label>Dias seguidos trabajados
          <input type="number" min={0} max={14} value={days} onChange={(e) => setDays(Number(e.target.value))} /></label>
        <label>Turnos de noche (semana)
          <input type="number" min={0} max={7} value={nights} onChange={(e) => setNights(Number(e.target.value))} /></label>
        <label>Horas dormidas
          <input type="number" min={0} max={12} value={sleep} onChange={(e) => setSleep(Number(e.target.value))} /></label>
        <label>Estres (1-10)
          <input type="number" min={1} max={10} value={stress} onChange={(e) => setStress(Number(e.target.value))} /></label>
      </div>
      <button onClick={calcular}>Calcular fatiga</button>
      {error && <p className="error">{error}</p>}

      {res && (
        <div className="card result">
          <div className="metrics">
            <div className="metric">
              <span className="metric-value">{res.score}</span>
              <span className="metric-label">Fatiga (0-100)</span>
            </div>
            <div className="metric">
              <span className="metric-value">{res.intensity_cap}/10</span>
              <span className="metric-label">Intensidad maxima hoy</span>
            </div>
            <div className="metric">
              <span className="metric-value">{res.high_fatigue ? 'Si' : 'No'}</span>
              <span className="metric-label">Fatiga alta</span>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
