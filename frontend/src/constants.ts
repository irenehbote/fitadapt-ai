// Opciones fijas que ofrece el formulario.

export const ENVIRONMENTS = ['gym', 'home', 'outdoor'] as const

export const EQUIPMENT = [
  'dumbbell', 'barbell', 'squat_rack', 'bench', 'cable', 'pull_up_bar',
  'resistance_band', 'box', 'bike', 'rower', 'mat',
] as const

export const MUSCLES = [
  'quadriceps', 'glutes', 'hamstrings', 'chest', 'back',
  'shoulders', 'arms', 'core', 'calves',
] as const

export const GOALS: { value: 'lose' | 'maintain' | 'gain'; label: string }[] = [
  { value: 'lose', label: 'Perder peso' },
  { value: 'maintain', label: 'Mantener' },
  { value: 'gain', label: 'Ganar musculo' },
]
