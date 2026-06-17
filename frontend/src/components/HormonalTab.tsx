import { useState } from 'react'
import { getHormonal, type HormonalResult, type ProfilePayload } from '../api'

// Pestaña de adaptacion hormonal: usa las condiciones del perfil + el dia del ciclo.
export function HormonalTab({ profile }: { profile: ProfilePayload }) {
  const [cycleDay, setCycleDay] = useState(22)
  const [cycleLength, setCycleLength] = useState(28)
  const [res, setRes] = useState<HormonalResult | null>(null)
  const [error, setError] = useState<string | null>(null)

  async function calcular() {
    setError(null)
    try {
      setRes(await getHormonal(profile.conditions, cycleDay, cycleLength))
    } catch (e) {
      setError((e as Error).message)
    }
  }

  return (
    <div>
      <div className="row">
        <label>
          Dia del ciclo
          <input type="number" min={1} max={cycleLength} value={cycleDay}
                 onChange={(e) => setCycleDay(Number(e.target.value))} />
        </label>
        <label>
          Duracion del ciclo
          <input type="number" min={20} max={40} value={cycleLength}
                 onChange={(e) => setCycleLength(Number(e.target.value))} />
        </label>
      </div>
      <button onClick={calcular}>Calcular adaptacion</button>
      {error && <p className="error">{error}</p>}

      {res && (
        <div className="card result">
          <div className="metrics">
            <div className="metric">
              <span className="metric-value">{res.phase}</span>
              <span className="metric-label">Fase del ciclo</span>
            </div>
            <div className="metric">
              <span className="metric-value">{Math.round(res.intensity_factor * 100)}%</span>
              <span className="metric-label">Intensidad sugerida</span>
            </div>
          </div>
          <ul className="notes">{res.notes.map((n, i) => <li key={i}>{n}</li>)}</ul>
        </div>
      )}
    </div>
  )
}
