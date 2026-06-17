import { useEffect, useState } from 'react'
import {
  getConditions,
  getRecommendation,
  type Condition,
  type ProfilePayload,
  type Recommendation,
} from './api'
import { ENVIRONMENTS, EQUIPMENT, GOALS, MUSCLES } from './constants'
import { RecommendationView } from './components/RecommendationView'

// Alterna un valor dentro de una lista (para los checkboxes multiseleccion).
function toggle(list: string[], value: string): string[] {
  return list.includes(value) ? list.filter((v) => v !== value) : [...list, value]
}

export function App() {
  const [conditions, setConditions] = useState<Condition[]>([])
  const [loadError, setLoadError] = useState<string | null>(null)

  const [name, setName] = useState('Ana')
  const [age, setAge] = useState(31)
  const [goal, setGoal] = useState<ProfilePayload['goal']>('lose')
  const [selectedConditions, setSelectedConditions] = useState<string[]>(['pcos'])
  const [primaryMuscles, setPrimaryMuscles] = useState<string[]>(['glutes'])
  const [environments, setEnvironments] = useState<string[]>(['home'])
  const [equipment, setEquipment] = useState<string[]>(['dumbbell', 'mat'])

  const [rec, setRec] = useState<Recommendation | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  // Al cargar, pedimos las condiciones disponibles a la API.
  useEffect(() => {
    getConditions()
      .then(setConditions)
      .catch((e: Error) => setLoadError(e.message))
  }, [])

  async function onSubmit(e: React.FormEvent) {
    e.preventDefault()
    setLoading(true)
    setError(null)
    try {
      const payload: ProfilePayload = {
        name,
        age,
        goal,
        conditions: selectedConditions,
        muscle_focus: { primary: primaryMuscles, secondary: [] },
        environments,
        equipment,
      }
      setRec(await getRecommendation(payload))
    } catch (err) {
      setError((err as Error).message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="app">
      <header>
        <h1>FitAdapt AI 🏋️‍♀️</h1>
        <p>Recomendacion de ejercicio adaptada a tu salud, objetivo y entorno.</p>
      </header>

      {loadError && (
        <p className="error">
          No se pudo conectar con la API ({loadError}). Asegurate de tenerla en
          marcha: <code>python -m backend.api.app</code>
        </p>
      )}

      <form className="card" onSubmit={onSubmit}>
        <div className="row">
          <label>
            Nombre
            <input value={name} onChange={(e) => setName(e.target.value)} />
          </label>
          <label>
            Edad
            <input
              type="number" min={14} max={100} value={age}
              onChange={(e) => setAge(Number(e.target.value))}
            />
          </label>
          <label>
            Objetivo
            <select value={goal} onChange={(e) => setGoal(e.target.value as ProfilePayload['goal'])}>
              {GOALS.map((g) => <option key={g.value} value={g.value}>{g.label}</option>)}
            </select>
          </label>
        </div>

        <fieldset>
          <legend>Condiciones de salud</legend>
          <div className="checks">
            {conditions.map((c) => (
              <label key={c.key} className="check">
                <input
                  type="checkbox"
                  checked={selectedConditions.includes(c.key)}
                  onChange={() => setSelectedConditions((s) => toggle(s, c.key))}
                />
                {c.name}
              </label>
            ))}
          </div>
        </fieldset>

        <fieldset>
          <legend>Musculos prioritarios</legend>
          <div className="checks">
            {MUSCLES.map((m) => (
              <label key={m} className="check">
                <input
                  type="checkbox"
                  checked={primaryMuscles.includes(m)}
                  onChange={() => setPrimaryMuscles((s) => toggle(s, m))}
                />
                {m}
              </label>
            ))}
          </div>
        </fieldset>

        <fieldset>
          <legend>Entornos disponibles</legend>
          <div className="checks">
            {ENVIRONMENTS.map((env) => (
              <label key={env} className="check">
                <input
                  type="checkbox"
                  checked={environments.includes(env)}
                  onChange={() => setEnvironments((s) => toggle(s, env))}
                />
                {env}
              </label>
            ))}
          </div>
        </fieldset>

        <fieldset>
          <legend>Equipamiento</legend>
          <div className="checks">
            {EQUIPMENT.map((eq) => (
              <label key={eq} className="check">
                <input
                  type="checkbox"
                  checked={equipment.includes(eq)}
                  onChange={() => setEquipment((s) => toggle(s, eq))}
                />
                {eq}
              </label>
            ))}
          </div>
        </fieldset>

        <button type="submit" disabled={loading}>
          {loading ? 'Generando…' : 'Generar recomendacion'}
        </button>
        {error && <p className="error">{error}</p>}
      </form>

      {rec && <RecommendationView rec={rec} />}
    </div>
  )
}
