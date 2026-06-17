import type { Recommendation } from '../api'

// Muestra el resultado de la recomendacion de forma legible.
export function RecommendationView({ rec }: { rec: Recommendation }) {
  const topVolumen = Object.entries(rec.volume_allocation)
    .sort((a, b) => b[1] - a[1])
    .slice(0, 4)

  return (
    <div className="card result">
      <h2>Tu plan adaptado</h2>

      <div className="metrics">
        <Metric label="Cardio / semana" value={rec.cardio_sessions_per_week.join('-')} />
        <Metric label="Fuerza / semana" value={rec.strength_sessions_per_week.join('-')} />
        <Metric label="HIIT / semana (max)" value={String(rec.weekly_hiit_limit)} />
        <Metric label="Intensidad max hoy" value={`${rec.max_intensity_today}/10`} />
      </div>

      <h3>Musculos con mas volumen</h3>
      <ul className="chips">
        {topVolumen.map(([m, v]) => (
          <li key={m} className="chip">{m}: {v} series</li>
        ))}
      </ul>

      <h3>Ejercicios seguros ({rec.safe_exercise_count})</h3>
      <ul className="chips">
        {rec.safe_exercises.map((e) => (
          <li key={e} className="chip subtle">{e}</li>
        ))}
      </ul>

      {rec.notes.length > 0 && (
        <>
          <h3>Notas de adaptacion</h3>
          <ul className="notes">
            {rec.notes.map((n, i) => <li key={i}>{n}</li>)}
          </ul>
        </>
      )}
    </div>
  )
}

function Metric({ label, value }: { label: string; value: string }) {
  return (
    <div className="metric">
      <span className="metric-value">{value}</span>
      <span className="metric-label">{label}</span>
    </div>
  )
}
