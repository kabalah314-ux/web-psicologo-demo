import { useState, useEffect } from 'react'
import { adminAjustes, adminPutAjustes } from '../../api'

export default function Disponibilidad({ token }: { token: string }) {
  const [disponibilidad, setDisponibilidad] = useState<any[]>([])
  const [cargando, setCargando] = useState(true)
  const [guardando, setGuardando] = useState(false)

  useEffect(() => {
    adminAjustes(token)
      .then(res => {
        const disp = res.disponibilidad || []
        setDisponibilidad(disp.length > 0 ? disp : [
          { dia_semana: 0, inicio: '09:00', fin: '14:00', modalidades: ['online', 'presencial'] },
          { dia_semana: 0, inicio: '16:00', fin: '20:00', modalidades: ['online', 'presencial'] },
          { dia_semana: 1, inicio: '09:00', fin: '14:00', modalidades: ['online', 'presencial'] },
          { dia_semana: 1, inicio: '16:00', fin: '20:00', modalidades: ['online', 'presencial'] },
          { dia_semana: 2, inicio: '09:00', fin: '14:00', modalidades: ['online', 'presencial'] },
          { dia_semana: 2, inicio: '16:00', fin: '20:00', modalidades: ['online', 'presencial'] },
          { dia_semana: 3, inicio: '09:00', fin: '14:00', modalidades: ['online', 'presencial'] },
          { dia_semana: 3, inicio: '16:00', fin: '20:00', modalidades: ['online', 'presencial'] },
          { dia_semana: 4, inicio: '09:00', fin: '14:00', modalidades: ['online', 'presencial'] },
          { dia_semana: 4, inicio: '16:00', fin: '20:00', modalidades: ['online', 'presencial'] },
        ])
      })
      .catch(() => {})
      .finally(() => setCargando(false))
  }, [token])

  const guardar = async () => {
    setGuardando(true)
    try {
      await adminPutAjustes(token, { disponibilidad })
    } catch {}
    setGuardando(false)
  }

  const dias = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo']

  if (cargando) return <p>Cargando disponibilidad...</p>

  return (
    <div>
      <span className="eyebrow">Disponibilidad semanal</span>
      <h2>Horarios</h2>
      <div style={{ marginTop: 20 }}>
        {dias.map((dia, i) => {
          const bloques = disponibilidad.filter(d => d.dia_semana === i)
          return (
            <div key={i} className="card" style={{ marginBottom: 12 }}>
              <strong>{dia}</strong>
              {bloques.length === 0 ? (
                <p> No disponible</p>
              ) : (
                bloques.map((b, j) => (
                  <div key={j} style={{ marginTop: 8 }}>
                    <input
                      type="time"
                      value={b.inicio}
                      onChange={e => {
                        const nueva = [...disponibilidad]
                        const idx = disponibilidad.indexOf(b)
                        nueva[idx] = { ...nueva[idx], inicio: e.target.value }
                        setDisponibilidad(nueva)
                      }}
                      style={{ width: 120, display: 'inline-block' }}
                    />
                    {' — '}
                    <input
                      type="time"
                      value={b.fin}
                      onChange={e => {
                        const nueva = [...disponibilidad]
                        const idx = disponibilidad.indexOf(b)
                        nueva[idx] = { ...nueva[idx], fin: e.target.value }
                        setDisponibilidad(nueva)
                      }}
                      style={{ width: 120, display: 'inline-block' }}
                    />
                  </div>
                ))
              )}
            </div>
          )
        })}
      </div>
      <button className="btn" onClick={guardar} disabled={guardando} style={{ marginTop: 20 }}>
        {guardando ? 'Guardando...' : 'Guardar disponibilidad'}
      </button>
    </div>
  )
}
