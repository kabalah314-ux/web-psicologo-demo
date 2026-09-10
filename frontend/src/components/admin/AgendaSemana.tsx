import { useState, useEffect } from 'react'
import { adminCitas, adminPatchCita } from '../../api'

export default function AgendaSemana({ token }: { token: string }) {
  const [citas, setCitas] = useState<any[]>([])
  const [cargando, setCargando] = useState(true)

  useEffect(() => {
    adminCitas(token)
      .then(res => setCitas(res.citas || []))
      .catch(() => {})
      .finally(() => setCargando(false))
  }, [token])

  const cambiarEstado = async (id: string, estado: string) => {
    try {
      await adminPatchCita(token, id, { estado })
      setCitas(citas.map(c => c._id === id ? { ...c, estado } : c))
    } catch {}
  }

  if (cargando) return <p>Cargando agenda...</p>

  return (
    <div>
      <span className="eyebrow">Agenda semanal</span>
      <h2>Citas</h2>
      {citas.length === 0 ? (
        <p style={{ marginTop: 20 }}>No hay citas registradas.</p>
      ) : (
        <div style={{ marginTop: 20 }}>
          {citas.map(c => (
            <div key={c._id} className="card" style={{ marginBottom: 12 }}>
              <div className="two-cols">
                <div>
                  <strong>{c.nombre}</strong>
                  <p>{c.email}</p>
                  <p>{new Date(c.inicio).toLocaleString('es-ES')} — {c.tipo_sesion} ({c.modalidad})</p>
                </div>
                <div style={{ textAlign: 'right' }}>
                  <span className={`badge badge-${c.estado}`}>{c.estado}</span>
                  {c.estado === 'activa' && (
                    <button className="btn secondary compact" style={{ marginLeft: 8 }} onClick={() => cambiarEstado(c._id, 'cancelada')}>
                      Cancelar
                    </button>
                  )}
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
