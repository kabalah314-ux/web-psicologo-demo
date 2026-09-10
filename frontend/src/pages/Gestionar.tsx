import { useState, useEffect } from 'react'
import { useParams } from 'react-router-dom'
import { getCita, cancelarCita, getIcs } from '../api'

export default function Gestionar() {
  const { token } = useParams<{ token: string }>()
  const [cita, setCita] = useState<any>(null)
  const [error, setError] = useState('')
  const [cargando, setCargando] = useState(true)
  const [cancelando, setCancelando] = useState(false)

  useEffect(() => {
    if (!token) return
    getCita(token)
      .then(c => setCita(c))
      .catch(e => setError(e.message))
      .finally(() => setCargando(false))
  }, [token])

  const cancelar = async () => {
    if (!token || !confirm('¿Seguro que quieres cancelar la cita?')) return
    setCancelando(true)
    try {
      await cancelarCita(token)
      setCita({ ...cita, estado: 'cancelada' })
    } catch (e: any) {
      setError(e.message)
    }
    setCancelando(false)
  }

  const descargarIcs = () => {
    if (!token) return
    window.open(`/api/publico/citas/${token}/ics`, '_blank')
  }

  if (cargando) return <div className="container section"><p>Cargando...</p></div>
  if (error) return <div className="container section"><p className="error">{error}</p></div>
  if (!cita) return <div className="container section"><p>Cita no encontrada</p></div>

  return (
    <div className="container section">
      <span className="eyebrow">Gestionar cita</span>
      <h2>Detalle de tu cita</h2>
      <div className="card" style={{ marginTop: 30, maxWidth: 600 }}>
        <div className="campo"><strong>Fecha:</strong> {cita.inicio_local}</div>
        <div className="campo"><strong>Modalidad:</strong> {cita.modalidad}</div>
        <div className="campo"><strong>Tipo:</strong> {cita.tipo_sesion}</div>
        <div className="campo"><strong>Estado:</strong> {cita.estado}</div>
        {cita.video_enlace && <div className="campo"><strong>Enlace video:</strong> <a href={cita.video_enlace} target="_blank" rel="noopener noreferrer">{cita.video_enlace}</a></div>}
        {cita.estado === 'activa' && (
          <div style={{ marginTop: 20, display: 'flex', gap: 12 }}>
            {cita.puede_cancelar && (
              <button className="btn secondary" onClick={cancelar} disabled={cancelando}>
                {cancelando ? 'Cancelando...' : 'Cancelar cita'}
              </button>
            )}
            <button className="btn" onClick={descargarIcs}>Descargar .ics</button>
          </div>
        )}
        {cita.estado === 'cancelada' && <p style={{ marginTop: 16, color: 'var(--muted)' }}>Esta cita ha sido cancelada.</p>}
        <p style={{ marginTop: 16, fontSize: '.85rem', color: 'var(--muted)' }}>
          Límite de cancelación: {cita.limite_cancelacion_local}
        </p>
      </div>
    </div>
  )
}
