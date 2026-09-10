import { useState, useEffect } from 'react'
import { adminAjustes, adminPutAjustes, adminIaEstado, adminTelegramTest } from '../../api'

export default function Ajustes({ token }: { token: string }) {
  const [ajustes, setAjustes] = useState<any>(null)
  const [cargando, setCargando] = useState(true)
  const [guardando, setGuardando] = useState(false)
  const [iaEstado, setIaEstado] = useState<any>(null)
  const [testResult, setTestResult] = useState<string | null>(null)

  useEffect(() => {
    Promise.all([adminAjustes(token), adminIaEstado(token)])
      .then(([a, ia]) => { setAjustes(a); setIaEstado(ia) })
      .catch(() => {})
      .finally(() => setCargando(false))
  }, [token])

  const guardar = async () => {
    setGuardando(true)
    try {
      await adminPutAjustes(token, ajustes)
    } catch {}
    setGuardando(false)
  }

  const testTelegram = async () => {
    const res = await adminTelegramTest(token)
    setTestResult(res.ok ? 'Mensaje enviado correctamente' : 'Error al enviar')
    setTimeout(() => setTestResult(null), 3000)
  }

  if (cargando) return <p>Cargando ajustes...</p>
  if (!ajustes) return <p>Error cargando ajustes</p>

  return (
    <div>
      <span className="eyebrow">Configuración</span>
      <h2>Ajustes</h2>

      <div className="card" style={{ marginTop: 20, marginBottom: 20 }}>
        <h3>General</h3>
        <div className="two-cols" style={{ marginTop: 16 }}>
          <div className="field">
            <label>Nombre profesional</label>
            <input value={ajustes.nombre_profesional || ''} onChange={e => setAjustes({ ...ajustes, nombre_profesional: e.target.value })} />
          </div>
          <div className="field">
            <label>Zona horaria</label>
            <input value={ajustes.zona_horaria || ''} onChange={e => setAjustes({ ...ajustes, zona_horaria: e.target.value })} />
          </div>
        </div>
        <div className="two-cols">
          <div className="field">
            <label>Plazo cancelación (horas)</label>
            <input type="number" value={ajustes.plazo_cancelacion_horas || 24} onChange={e => setAjustes({ ...ajustes, plazo_cancelacion_horas: parseInt(e.target.value) })} />
          </div>
          <div className="field">
            <label>Dirección presencial</label>
            <input value={ajustes.direccion_presencial || ''} onChange={e => setAjustes({ ...ajustes, direccion_presencial: e.target.value })} />
          </div>
        </div>
      </div>

      <div className="card" style={{ marginBottom: 20 }}>
        <h3>Inteligencia Artificial</h3>
        <p style={{ marginTop: 8 }}>
          Estado: {iaEstado?.openrouter_configurado ? '✅ Configurado' : '⚠️ Sin configurar'} —
          Free tier: {iaEstado?.is_free_tier ? 'Sí' : 'No'}
        </p>
      </div>

      <div className="card" style={{ marginBottom: 20 }}>
        <h3>Notificaciones Telegram</h3>
        <button className="btn secondary compact" onClick={testTelegram}>Enviar test</button>
        {testResult && <span style={{ marginLeft: 12 }}>{testResult}</span>}
      </div>

      <button className="btn" onClick={guardar} disabled={guardando} style={{ marginTop: 10 }}>
        {guardando ? 'Guardando...' : 'Guardar ajustes'}
      </button>
    </div>
  )
}
