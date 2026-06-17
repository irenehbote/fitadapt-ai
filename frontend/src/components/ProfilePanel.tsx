import { useEffect, useState } from 'react'
import type { Condition, ProfilePayload } from '../api'
import { ENVIRONMENTS, EQUIPMENT, GOALS, MUSCLES } from '../constants'

function toggle(list: string[], value: string): string[] {
  return list.includes(value) ? list.filter((v) => v !== value) : [...list, value]
}

// Panel "Tu perfil": el usuario define sus datos y notifica el perfil hacia arriba.
export function ProfilePanel({
  conditions,
  onChange,
}: {
  conditions: Condition[]
  onChange: (p: ProfilePayload) => void
}) {
  const [name, setName] = useState('Ana')
  const [age, setAge] = useState(31)
  const [goal, setGoal] = useState<ProfilePayload['goal']>('lose')
  const [selectedConditions, setSelectedConditions] = useState<string[]>(['pcos'])
  const [primaryMuscles, setPrimaryMuscles] = useState<string[]>(['glutes'])
  const [environments, setEnvironments] = useState<string[]>(['home'])
  const [equipment, setEquipment] = useState<string[]>(['dumbbell', 'mat'])

  // Cada vez que cambia algo, recomponemos el perfil y avisamos al padre.
  useEffect(() => {
    onChange({
      name,
      age,
      goal,
      conditions: selectedConditions,
      muscle_focus: { primary: primaryMuscles, secondary: [] },
      environments,
      equipment,
    })
  }, [name, age, goal, selectedConditions, primaryMuscles, environments, equipment, onChange])

  return (
    <div className="card">
      <h2>Tu perfil</h2>
      <div className="row">
        <label>
          Nombre
          <input value={name} onChange={(e) => setName(e.target.value)} />
        </label>
        <label>
          Edad
          <input type="number" min={14} max={100} value={age}
                 onChange={(e) => setAge(Number(e.target.value))} />
        </label>
        <label>
          Objetivo
          <select value={goal} onChange={(e) => setGoal(e.target.value as ProfilePayload['goal'])}>
            {GOALS.map((g) => <option key={g.value} value={g.value}>{g.label}</option>)}
          </select>
        </label>
      </div>

      <Checks legend="Condiciones de salud" options={conditions.map((c) => [c.key, c.name])}
              selected={selectedConditions} onToggle={(v) => setSelectedConditions((s) => toggle(s, v))} />
      <Checks legend="Musculos prioritarios" options={MUSCLES.map((m) => [m, m])}
              selected={primaryMuscles} onToggle={(v) => setPrimaryMuscles((s) => toggle(s, v))} />
      <Checks legend="Entornos" options={ENVIRONMENTS.map((m) => [m, m])}
              selected={environments} onToggle={(v) => setEnvironments((s) => toggle(s, v))} />
      <Checks legend="Equipamiento" options={EQUIPMENT.map((m) => [m, m])}
              selected={equipment} onToggle={(v) => setEquipment((s) => toggle(s, v))} />
    </div>
  )
}

// Grupo de checkboxes reutilizable. options = [valor, etiqueta][].
function Checks({
  legend, options, selected, onToggle,
}: {
  legend: string
  options: [string, string][]
  selected: string[]
  onToggle: (value: string) => void
}) {
  return (
    <fieldset>
      <legend>{legend}</legend>
      <div className="checks">
        {options.map(([value, label]) => (
          <label key={value} className="check">
            <input type="checkbox" checked={selected.includes(value)}
                   onChange={() => onToggle(value)} />
            {label}
          </label>
        ))}
      </div>
    </fieldset>
  )
}
