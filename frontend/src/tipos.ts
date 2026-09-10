export interface Hueco {
  inicio: string
  inicio_local: string
  fin: string
}

export interface Cita {
  id: string
  token: string
  nombre: string
  email: string
  telefono: string
  inicio: string
  fin: string
  modalidad: string
  tipo_sesion: string
  estado: string
}

export interface Config {
  nombre_profesional: string
  tipos_sesion: { id: string; nombre: string; duracion_min: number; precio_texto: string }[]
  modalidades: string[]
  plazo_cancelacion_horas: number
  direccion_presencial: string
  textos: { politica_cancelacion: string }
  zona_horaria: string
}
