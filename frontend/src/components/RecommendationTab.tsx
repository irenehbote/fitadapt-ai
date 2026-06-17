import { useState } from 'react'
import { getRecommendation, type ProfilePayload, type Recommendation } from '../api'
import { RecommendationView } from './RecommendationView'

// Pestaña de recomendacion semanal a partir del perfil actual.
export function RecommendationTab({ profile }: { profile: ProfilePayload }) {
  const [rec, setRec] = useState<Recommendation | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  async function generar() {
    setLoading(true)
    setError(null)
    try {
      setRec(await getRecommendation(profile))
    } catch (e) {
      setError((e as Error).message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div>
      <button onClick={generar} disabled={loading}>
        {loading ? 'Generando…' : 'Generar recomendacion'}
      </button>
      {error && <p className="error">{error}</p>}
      {rec && <RecommendationView rec={rec} />}
    </div>
  )
}
