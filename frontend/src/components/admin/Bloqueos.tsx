import { useState, useEffect } from 'react'

export default function Bloqueos({ token }: { token: string }) {
  const [bloqueos, setBloqueos] = useState<any[]>([])
  const [cargando, setCargando] = useState(true)
  const [inicio, setInicio] = useState('')
  const [fin, setFin] = useState('')
  const [motivo, setMotivo] = useState('')
  const [creando, setCreando] = useState(false)

  const cargar = () => {
    fetch('/api/admin/bloqueos', { headers: { Authorization: `Bearer ${token}` } })
      .then(r => r.json())
      .then(res => setBloqueos(res.bloqueos || []))
      .catch(() => {})
      .finally(() => setCargando(false))
  }

  useEffect(() => { cargar() }, [])

  const crear = async () => {
    if (!inicio || !fin) return
    setCreando(true)
    try {
      await fetch('/api/admin/bloqueos', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${token}` },
        body: JSON.stringify({ inicio: new Date(inicio).toISOString(), fin: new Date(fin).toISOString(), motivo })
      })
      setInicio('')
      setFin('')
      setMotivo('')
      cargar()
    } catch {}
    setCreando(false)
  }

  const eliminar = async (id: string) => {
    if (!confirm('¿Eliminar este bloqueo?')) return
    try {
      await fetch(`/api/admin/bloqueos/${id}`, {
        method: 'DELETE',
        headers: { Authorization: `Bearer ${token}` }
      })
      cargar()
    } catch {}
  }

  if (cargando) return <p>Cargando bloqueos...</p>

  return (
    <div>
      <span className="eyebrow">Bloqueos de agenda</span>
      <h2>Bloqueos</h2>
      <div className="card" style={{ marginTop: 20, marginBottom: 20 }}>
        <div className="two-cols">
          <div className="field">
            <label>Inicio</label>
            <input type="datetime-local" value={inicio} onChange={e => setInicio(e.target.value)} />
          </div>
          <div className="field">
            <label>Fin</label>
            <input type="datetime-local" value={fin} onChange={e => setFin(e.target.value)} />
          </div>
        </div>
        <div className="field">
          <label>Motivo (opcional)</label>
          <input value={motivo} onChange={e => setMotivo(e.target.value)} />
        </div>
        <button className="btn compact" onClick={crear} disabled={creando || !inicio || !fin}>
          {creando ? 'Creando...' : 'Crear bloqueo'}
        </button>
      </div>

      {bloqueos.length === 0 ? (
        <p>No hay bloqueos registrados.</p>
      ) : (
        bloqueos.map(b => (
          <div key={b._id} className="card" style={{ marginBottom: 12 }}>
            <div className="two-cols">
              <div>
                <p><strong>{new Date(b.inicio).toLocaleString('es-ES')} — {new Date(b.fin).toLocaleString('es-ES')}</strong></p>
                {b.motivo && <p>{b.motivo}</p>}
              </div>
              <div style={{ textAlign: 'right' }}>
                <button className="btn secondary compact" onClick={() => eliminar(b._id)}>Eliminar</button>
              </div>
            </div>
          </div>
        ))
      )}
    </div>
  )
}
