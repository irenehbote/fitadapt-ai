import { useState } from 'react'
import { getXp, type ExerciseLite, type ProfilePayload } from '../api'

// Pestaña de gamificacion: calcula XP y muestra el handicap justo en un 1v1.
export function GamificationTab({
  profile, exercises,
}: {
  profile: ProfilePayload
  exercises: ExerciseLite[]
}) {
  const [exerciseId, setExerciseId] = useState('goblet_squat')
  const [intensity, setIntensity] = useState(6)
  const [streak, setStreak] = useState(3)
  const [mine, setMine] = useState<number | null>(null)
  const [rival, setRival] = useState<number | null>(null)
  const [error, setError] = useState<string | null>(null)

  async function calcular() {
    setError(null)
    try {
      const yo = await getXp({ exercise_id: exerciseId, intensity, streak_days: streak, conditions: profile.conditions })
      // El rival hace lo mismo pero sin condiciones de salud.
      const otro = await getXp({ exercise_id: exerciseId, intensity, streak_days: streak, conditions: [] })
      setMine(yo.xp)
      setRival(otro.xp)
    } catch (e) {
      setError((e as Error).message)
    }
  }

  const ganador = mine !== null && rival !== null
    ? (mine > rival ? 'Tu' : mine < rival ? 'Rival' : 'Empate') : null

  return (
    <div>
      <div className="row">
        <label>
          Ejercicio
          <select value={exerciseId} onChange={(e) => setExerciseId(e.target.value)}>
            {exercises.map((ex) => <option key={ex.id} value={ex.id}>{ex.name}</option>)}
          </select>
        </label>
        <label>
          Intensidad (1-10)
          <input type="number" min={1} max={10} value={intensity}
                 onChange={(e) => setIntensity(Number(e.target.value))} />
        </label>
        <label>
          Racha (dias)
          <input type="number" min={0} max={60} value={streak}
                 onChange={(e) => setStreak(Number(e.target.value))} />
        </label>
      </div>
      <button onClick={calcular}>Calcular XP (reto 1v1)</button>
      {error && <p className="error">{error}</p>}

      {mine !== null && rival !== null && (
        <div className="card result">
          <div className="metrics">
            <div className="metric">
              <span className="metric-value">{mine}</span>
              <span className="metric-label">Tu XP (con tus condiciones)</span>
            </div>
            <div className="metric">
              <span className="metric-value">{rival}</span>
              <span className="metric-label">Rival XP (sin condiciones)</span>
            </div>
            <div className="metric">
              <span className="metric-value">{ganador}</span>
              <span className="metric-label">Ganador</span>
            </div>
          </div>
          <p className="muted">
            El mismo esfuerzo otorga mas XP a quien entrena con condiciones que lo
            dificultan: ese es el handicap justo.
          </p>
        </div>
      )}
    </div>
  )
}
