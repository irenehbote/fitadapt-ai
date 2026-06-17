// Cliente de la API de FitAdapt AI.
// En desarrollo, Vite redirige /api al backend (ver vite.config.ts).

export interface Condition { key: string; name: string }
export interface ExerciseLite { id: string; name: string; environments: string[] }

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

export interface HormonalResult {
  phase: string
  intensity_factor: number
  notes: string[]
}

export interface FatigueResult {
  score: number
  high_fatigue: boolean
  intensity_cap: number
}

export interface GoogleFitResult {
  intensity_cap: number
  reduce_cardio: boolean
  suggest_deload: boolean
  notes: string[]
}

export interface XpResult { exercise: string; xp: number }

export interface ProgressResult {
  days_between: number
  weight_change_pct: number
  waist_change_cm: number
  body_fat_change: number | null
  progress_score: number
  weekly_weight_change_kg: number
  plausible: boolean
  commentary: string[]
}

export interface ProfileSummary { id: number; name: string; goal: string }

export interface BodyFatResult {
  body_fat_pct: number
  method: string
  category: string
  confidence_note: string
  circumferences?: Record<string, number>
}

// En desarrollo: '/api' (proxy de Vite). En produccion se puede fijar
// VITE_API_BASE al backend desplegado (Render). Por defecto, '/api'.
const BASE = import.meta.env.VITE_API_BASE ?? '/api'

async function getJson<T>(path: string): Promise<T> {
  const res = await fetch(`${BASE}${path}`)
  const data = await res.json()
  if (!res.ok) throw new Error(data.error ?? `Error ${res.status}`)
  return data as T
}

async function send<T>(path: string, method: string, body?: unknown): Promise<T> {
  const res = await fetch(`${BASE}${path}`, {
    method,
    headers: body ? { 'Content-Type': 'application/json' } : undefined,
    body: body ? JSON.stringify(body) : undefined,
  })
  const data = await res.json()
  if (!res.ok) throw new Error(data.error ?? `Error ${res.status}`)
  return data as T
}

// --- Catalogo / recomendacion ---
export const getConditions = () => getJson<{ conditions: Condition[] }>('/conditions').then((d) => d.conditions)
export const getExercises = () => getJson<{ exercises: ExerciseLite[] }>('/exercises').then((d) => d.exercises)
export const getRecommendation = (p: ProfilePayload) => send<Recommendation>('/recommendations', 'POST', p)

// --- Modulos sin estado ---
export const getHormonal = (conditions: string[], cycle_day: number, cycle_length = 28) =>
  send<HormonalResult>('/hormonal', 'POST', { conditions, cycle_day, cycle_length })

export const getFatigue = (b: {
  consecutive_work_days: number; night_shifts_this_week: number
  hours_slept_last_night: number; stress_level: number
}) => send<FatigueResult>('/fatigue', 'POST', b)

export const getGoogleFit = (b: {
  steps_today?: number; sleep_hours_last_night?: number; resting_hr_trend?: string
}) => send<GoogleFitResult>('/google-fit', 'POST', b)

export const getXp = (b: {
  exercise_id: string; intensity: number; streak_days: number; conditions: string[]
}) => send<XpResult>('/xp', 'POST', b)

export const getProgress = (b: {
  before: { label: string; weight_kg: number; waist_cm: number; body_fat_pct?: number }
  after: { label: string; weight_kg: number; waist_cm: number; body_fat_pct?: number }
  days_between: number; condition?: string
}) => send<ProgressResult>('/progress', 'POST', b)

// --- Composicion corporal ---
export const getBodyFat = (b: {
  sex: string; height_cm: number
  neck_cm?: number; waist_cm?: number; hip_cm?: number
  weight_kg?: number; age?: number
}) => send<BodyFatResult>('/body-fat', 'POST', b)

export const getBodyFatPhoto = (b: {
  front_image_b64: string; side_image_b64: string; height_cm: number; sex: string
}) => send<BodyFatResult>('/body-fat/photo', 'POST', b)

// --- Persistencia de perfiles ---
export const saveProfile = (p: ProfilePayload) => send<{ id: number }>('/profiles', 'POST', p)
export const listProfiles = () => getJson<{ profiles: ProfileSummary[] }>('/profiles').then((d) => d.profiles)
export const deleteProfile = (id: number) => send<{ deleted: boolean }>(`/profiles/${id}`, 'DELETE')
export const getProfileRecommendation = (id: number) => getJson<Recommendation>(`/profiles/${id}/recommendation`)
