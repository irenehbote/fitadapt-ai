import { useState } from 'react'
import { getBodyFat, getBodyFatPhoto, type BodyFatResult } from '../api'

// Lee un fichero y devuelve su contenido en base64 (sin el prefijo data:).
function fileToBase64(file: File): Promise<string> {
  return new Promise((resolve, reject) => {
    const reader = new FileReader()
    reader.onerror = () => reject(new Error('No se pudo leer el archivo'))
    reader.onload = () => {
      const result = String(reader.result)
      resolve(result.includes(',') ? result.split(',')[1] : result)
    }
    reader.readAsDataURL(file)
  })
}

function ResultCard({ r }: { r: BodyFatResult }) {
  return (
    <div className="card result">
      <div className="metrics">
        <div className="metric">
          <span className="metric-value">{r.body_fat_pct}%</span>
          <span className="metric-label">Grasa estimada</span>
        </div>
        <div className="metric">
          <span className="metric-value">{r.category}</span>
          <span className="metric-label">Categoria</span>
        </div>
        <div className="metric">
          <span className="metric-value">{r.method}</span>
          <span className="metric-label">Metodo</span>
        </div>
      </div>
      {r.circumferences && (
        <ul className="chips">
          {Object.entries(r.circumferences).map(([k, v]) => (
            <li key={k} className="chip">{k}: {v} cm</li>
          ))}
        </ul>
      )}
      <p className="muted">{r.confidence_note}</p>
    </div>
  )
}

// Pestaña de composicion corporal: medidas manuales (Navy) o estimacion por foto.
export function CompositionTab() {
  const [sex, setSex] = useState('female')
  const [height, setHeight] = useState(165)

  // Medidas manuales
  const [neck, setNeck] = useState(34)
  const [waist, setWaist] = useState(75)
  const [hip, setHip] = useState(95)
  const [manual, setManual] = useState<BodyFatResult | null>(null)

  // Fotos
  const [front, setFront] = useState<File | null>(null)
  const [side, setSide] = useState<File | null>(null)
  const [photo, setPhoto] = useState<BodyFatResult | null>(null)
  const [loadingPhoto, setLoadingPhoto] = useState(false)

  const [error, setError] = useState<string | null>(null)

  async function calcularManual() {
    setError(null)
    try {
      setManual(await getBodyFat({
        sex, height_cm: height, neck_cm: neck, waist_cm: waist,
        hip_cm: sex === 'female' ? hip : undefined,
      }))
    } catch (e) {
      setError((e as Error).message)
    }
  }

  async function calcularFoto() {
    setError(null)
    if (!front || !side) {
      setError('Sube una foto frontal y una lateral.')
      return
    }
    setLoadingPhoto(true)
    try {
      const [f, s] = await Promise.all([fileToBase64(front), fileToBase64(side)])
      setPhoto(await getBodyFatPhoto({
        front_image_b64: f, side_image_b64: s, height_cm: height, sex,
      }))
    } catch (e) {
      setError((e as Error).message)
    } finally {
      setLoadingPhoto(false)
    }
  }

  return (
    <div>
      <div className="row">
        <label>Sexo
          <select value={sex} onChange={(e) => setSex(e.target.value)}>
            <option value="female">mujer</option>
            <option value="male">hombre</option>
          </select>
        </label>
        <label>Altura (cm)
          <input type="number" min={120} max={220} value={height}
                 onChange={(e) => setHeight(Number(e.target.value))} /></label>
      </div>

      <div className="card">
        <h3>Por medidas (formula Navy)</h3>
        <div className="row">
          <label>Cuello (cm)
            <input type="number" value={neck} onChange={(e) => setNeck(Number(e.target.value))} /></label>
          <label>Cintura (cm)
            <input type="number" value={waist} onChange={(e) => setWaist(Number(e.target.value))} /></label>
          {sex === 'female' && (
            <label>Cadera (cm)
              <input type="number" value={hip} onChange={(e) => setHip(Number(e.target.value))} /></label>
          )}
        </div>
        <button onClick={calcularManual}>Estimar por medidas</button>
        {manual && <ResultCard r={manual} />}
      </div>

      <div className="card">
        <h3>Por foto <span className="badge">experimental</span></h3>
        <p className="muted">
          Sube una foto <b>frontal</b> y una <b>lateral</b> de cuerpo entero. Es una
          estimacion orientativa (~±5-8%) y requiere el modelo de vision en el backend.
        </p>
        <div className="row">
          <label>Foto frontal
            <input type="file" accept="image/*"
                   onChange={(e) => setFront(e.target.files?.[0] ?? null)} /></label>
          <label>Foto lateral
            <input type="file" accept="image/*"
                   onChange={(e) => setSide(e.target.files?.[0] ?? null)} /></label>
        </div>
        <button onClick={calcularFoto} disabled={loadingPhoto}>
          {loadingPhoto ? 'Analizando…' : 'Estimar por foto'}
        </button>
        {photo && <ResultCard r={photo} />}
      </div>

      {error && <p className="error">{error}</p>}
    </div>
  )
}
