// Cliente de la API de FitAdapt AI.
// En desarrollo, Vite redirige /api al backend (ver vite.config.ts).

export interface Condition {
  key: string
  name: string
}

export interface ProfilePayload {
  name: string
  age: number
  goal: 'lose' | 'maintain' | 'gain'
  conditions: string[]
  muscle_focus: { primary: string[]; secondary: string[] }
  environments: string[]
  equipment: string[]
}

export interface Recommendation {
  cardio_sessions_per_week: number[]
  strength_sessions_per_week: number[]
  weekly_hiit_limit: number
  max_intensity_today: number
  safe_exercise_count: number
  safe_exercises: string[]
  volume_allocation: Record<string, number>
  notes: string[]
}

const BASE = '/api'

export async function getConditions(): Promise<Condition[]> {
  const res = await fetch(`${BASE}/conditions`)
  if (!res.ok) throw new Error('No se pudieron cargar las condiciones')
  const data = await res.json()
  return data.conditions as Condition[]
}

export async function getRecommendation(payload: ProfilePayload): Promise<Recommendation> {
  const res = await fetch(`${BASE}/recommendations`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  })
  const data = await res.json()
  if (!res.ok) throw new Error(data.error ?? 'Error al generar la recomendacion')
  return data as Recommendation
}
