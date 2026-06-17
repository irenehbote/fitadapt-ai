import { useEffect, useState } from 'react'
import {
  deleteProfile, getProfileRecommendation, listProfiles, saveProfile,
  type ProfilePayload, type ProfileSummary, type Recommendation,
} from '../api'
import { RecommendationView } from './RecommendationView'

// Pestaña de persistencia: guarda el perfil actual y gestiona los guardados.
export function SavedProfilesTab({ profile }: { profile: ProfilePayload }) {
  const [profiles, setProfiles] = useState<ProfileSummary[]>([])
  const [rec, setRec] = useState<Recommendation | null>(null)
  const [msg, setMsg] = useState<string | null>(null)
  const [error, setError] = useState<string | null>(null)

  async function refrescar() {
    try {
      setProfiles(await listProfiles())
    } catch (e) {
      setError((e as Error).message)
    }
  }

  useEffect(() => { void refrescar() }, [])

  async function guardar() {
    setError(null); setMsg(null)
    try {
      const { id } = await saveProfile(profile)
      setMsg(`Perfil "${profile.name}" guardado con id ${id}.`)
      await refrescar()
    } catch (e) {
      setError((e as Error).message)
    }
  }

  async function verRecomendacion(id: number) {
    setError(null)
    try {
      setRec(await getProfileRecommendation(id))
    } catch (e) {
      setError((e as Error).message)
    }
  }

  async function borrar(id: number) {
    setError(null)
    try {
      await deleteProfile(id)
      setRec(null)
      await refrescar()
    } catch (e) {
      setError((e as Error).message)
    }
  }

  return (
    <div>
      <button onClick={guardar}>Guardar el perfil actual</button>
      {msg && <p className="ok-msg">{msg}</p>}
      {error && <p className="error">{error}</p>}

      <div className="card">
        <h3>Perfiles guardados</h3>
        {profiles.length === 0 && <p className="muted">Aun no hay perfiles guardados.</p>}
        <ul className="saved-list">
          {profiles.map((p) => (
            <li key={p.id}>
              <span>#{p.id} · {p.name} · {p.goal}</span>
              <span className="actions">
                <button className="small" onClick={() => verRecomendacion(p.id)}>Ver plan</button>
                <button className="small danger" onClick={() => borrar(p.id)}>Borrar</button>
              </span>
            </li>
          ))}
        </ul>
      </div>

      {rec && <RecommendationView rec={rec} />}
    </div>
  )
}
