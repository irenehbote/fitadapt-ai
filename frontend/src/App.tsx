import { useEffect, useState } from 'react'
import {
  getConditions, getExercises,
  type Condition, type ExerciseLite, type ProfilePayload,
} from './api'
import { ProfilePanel } from './components/ProfilePanel'
import { RecommendationTab } from './components/RecommendationTab'
import { SavedProfilesTab } from './components/SavedProfilesTab'
import { HormonalTab } from './components/HormonalTab'
import { GamificationTab } from './components/GamificationTab'
import { FatigueTab } from './components/FatigueTab'
import { GoogleFitTab } from './components/GoogleFitTab'
import { ProgressTab } from './components/ProgressTab'

const TABS = [
  { id: 'reco', label: 'Recomendacion' },
  { id: 'hormonal', label: 'Hormonal' },
  { id: 'gamification', label: 'Gamificacion' },
  { id: 'progress', label: 'Progreso' },
  { id: 'fatigue', label: 'Fatiga / turnos' },
  { id: 'googlefit', label: 'Google Fit' },
  { id: 'saved', label: 'Perfiles guardados' },
] as const

type TabId = (typeof TABS)[number]['id']

export function App() {
  const [conditions, setConditions] = useState<Condition[]>([])
  const [exercises, setExercises] = useState<ExerciseLite[]>([])
  const [profile, setProfile] = useState<ProfilePayload | null>(null)
  const [tab, setTab] = useState<TabId>('reco')
  const [loadError, setLoadError] = useState<string | null>(null)

  useEffect(() => {
    getConditions().then(setConditions).catch((e: Error) => setLoadError(e.message))
    getExercises().then(setExercises).catch((e: Error) => setLoadError(e.message))
  }, [])

  return (
    <div className="app">
      <header>
        <h1>FitAdapt AI 🏋️‍♀️</h1>
        <p>Ejercicio adaptado a tu salud, objetivo, ciclo, turnos y entorno.</p>
      </header>

      {loadError && (
        <p className="error">
          No se pudo conectar con la API ({loadError}). Arranca el backend:{' '}
          <code>python -m backend.api.app</code>
        </p>
      )}

      <ProfilePanel conditions={conditions} onChange={setProfile} />

      <nav className="tabs">
        {TABS.map((t) => (
          <button key={t.id} className={tab === t.id ? 'tab active' : 'tab'}
                  onClick={() => setTab(t.id)}>
            {t.label}
          </button>
        ))}
      </nav>

      <section>
        {!profile && <p className="muted">Define tu perfil arriba para empezar.</p>}
        {profile && tab === 'reco' && <RecommendationTab profile={profile} />}
        {profile && tab === 'hormonal' && <HormonalTab profile={profile} />}
        {profile && tab === 'gamification' && <GamificationTab profile={profile} exercises={exercises} />}
        {profile && tab === 'progress' && <ProgressTab profile={profile} />}
        {tab === 'fatigue' && <FatigueTab />}
        {tab === 'googlefit' && <GoogleFitTab />}
        {profile && tab === 'saved' && <SavedProfilesTab profile={profile} />}
      </section>
    </div>
  )
}
