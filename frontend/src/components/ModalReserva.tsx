import { useState, useEffect } from 'react'
import { getHuecos, reservarCita, getConfig } from '../api'
import type { Hueco, Config } from '../tipos'

interface Props {
  open: boolean
  onClose: () => void
  onReservada: (token: string) => void
}

function formatearHueco(isoLocal: string) {
  try {
    const [fecha, hora] = isoLocal.split('T')
    const [y, m, d] = fecha.split('-')
    const fechaObj = new Date(Number(y), Number(m) - 1, Number(d))
    const dias = ['Dom', 'Lun', 'Mar', 'Mié', 'Jue', 'Vie', 'Sáb']
    const meses = ['ene', 'feb', 'mar', 'abr', 'may', 'jun', 'jul', 'ago', 'sep', 'oct', 'nov', 'dic']
    return `${dias[fechaObj.getDay()]} ${Number(d)} ${meses[fechaObj.getMonth()]} · ${hora}`
  } catch {
    return isoLocal
  }
}

export default function ModalReserva({ open, onClose, onReservada }: Props) {
  const [paso, setPaso] = useState<'form' | 'huecos' | 'ok' | 'error'>('form')
  const [config, setConfig] = useState<Config | null>(null)
  const [modalidad, setModalidad] = useState('online')
  const [tipoSesion, setTipoSesion] = useState('')
  const [nombre, setNombre] = useState('')
  const [email, setEmail] = useState('')
  const [telefono, setTelefono] = useState('')
  const [consentimiento, setConsentimiento] = useState(false)
  const [website, setWebsite] = useState('')
  const [huecos, setHuecos] = useState<Hueco[]>([])
  const [seleccionado, setSeleccionado] = useState<Hueco | null>(null)
  const [cargando, setCargando] = useState(false)
  const [error, setError] = useState('')

  useEffect(() => {
    if (open) {
      getConfig().then(c => {
        setConfig(c)
        if (c.tipos_sesion.length > 0) setTipoSesion(c.tipos_sesion[0].id)
      }).catch(() => {})
    }
  }, [open])

  const buscarHuecos = async () => {
    setCargando(true)
    setError('')
    try {
      const hoy = new Date()
      const desde = hoy.toISOString().split('T')[0]
      const res = await getHuecos(modalidad, desde, 14)
      setHuecos(res.huecos)
      setPaso('huecos')
    } catch {
      setError('No se pudieron cargar los huecos')
    }
    setCargando(false)
  }

  const reservar = async () => {
    if (!seleccionado || !consentimiento) return
    setCargando(true)
    setError('')
    try {
      const res = await reservarCita({
        inicio: seleccionado.inicio,
        modalidad,
        tipo_sesion: tipoSesion,
        nombre,
        email,
        telefono,
        consentimiento: true,
        website,
      })
      onReservada(res.token)
      setPaso('ok')
    } catch (e: any) {
      setError(e.message || 'Error al reservar')
    }
    setCargando(false)
  }

  if (!open) return null

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content" onClick={e => e.stopPropagation()}>
        <button className="modal-close" onClick={onClose}>×</button>

        {paso === 'form' && (
          <>
            <h2>Reservar sesión</h2>
            <div className="field">
              <label>Modalidad</label>
              <select value={modalidad} onChange={e => setModalidad(e.target.value)}>
                <option value="online">Online</option>
                <option value="presencial">Presencial</option>
              </select>
            </div>
            <div className="field">
              <label>Tipo de sesión</label>
              <select value={tipoSesion} onChange={e => setTipoSesion(e.target.value)}>
                {config?.tipos_sesion.map(t => (
                  <option key={t.id} value={t.id}>{t.nombre} — {t.precio_texto}</option>
                ))}
              </select>
            </div>
            <div className="field">
              <label>Nombre</label>
              <input value={nombre} onChange={e => setNombre(e.target.value)} />
            </div>
            <div className="field">
              <label>Email</label>
              <input type="email" value={email} onChange={e => setEmail(e.target.value)} />
            </div>
            <div className="field">
              <label>Teléfono (opcional)</label>
              <input value={telefono} onChange={e => setTelefono(e.target.value)} />
            </div>
            <input type="text" name="website" value={website} onChange={e => setWebsite(e.target.value)} style={{ display: 'none' }} tabIndex={-1} autoComplete="off" />
            <div className="field">
              <label className="checkbox-label">
                <input type="checkbox" checked={consentimiento} onChange={e => setConsentimiento(e.target.checked)} />
                He leído y acepto la política de privacidad y tratamiento de datos
              </label>
            </div>
            {error && <p className="error">{error}</p>}
            <button className="btn" onClick={buscarHuecos} disabled={!nombre || !email || !consentimiento || cargando}>
              {cargando ? 'Buscando...' : 'Buscar huecos disponibles'}
            </button>
          </>
        )}

        {paso === 'huecos' && (
          <>
            <h2>Elige un hueco</h2>
            {huecos.length === 0 ? (
              <p>No hay huecos disponibles en los próximos días.</p>
            ) : (
              <div className="huecos-lista">
                {huecos.slice(0, 20).map((h, i) => (
                  <button
                    key={i}
                    className={`hueco-btn ${seleccionado === h ? 'seleccionado' : ''}`}
                    onClick={() => setSeleccionado(h)}
                  >
                    {formatearHueco(h.inicio_local)}
                  </button>
                ))}
              </div>
            )}
            {error && <p className="error">{error}</p>}
            <div className="modal-acciones">
              <button className="btn secondary" onClick={() => setPaso('form')}>Volver</button>
              <button className="btn" onClick={reservar} disabled={!seleccionado || cargando}>
                {cargando ? 'Reservando...' : 'Confirmar reserva'}
              </button>
            </div>
          </>
        )}

        {paso === 'ok' && (
          <div className="modal-ok">
            <h2>¡Reserva confirmada!</h2>
            <p>Recibirás un email con los detalles y un enlace para gestionar tu cita.</p>
            <button className="btn" onClick={onClose}>Cerrar</button>
          </div>
        )}
      </div>
    </div>
  )
}
