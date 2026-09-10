import { useState, useRef, useEffect } from 'react'
import { enviarChat, getHuecos, contactoUrgente } from '../api'

interface Mensaje { rol: 'usuario' | 'asistente'; contenido: string }

export default function Chat({ onAbrirAgenda }: { onAbrirAgenda?: () => void }) {
  const [mensajes, setMensajes] = useState<Mensaje[]>([
    { rol: 'asistente', contenido: 'Hola, soy el asistente de Tu Espacio. ¿En qué puedo ayudarte?' }
  ])
  const [input, setInput] = useState('')
  const [cargando, setCargando] = useState(false)
  const [mostrarContacto, setMostrarContacto] = useState(false)
  const [nombreUrgente, setNombreUrgente] = useState('')
  const [telUrgente, setTelUrgente] = useState('')
  const fin = useRef<HTMLDivElement>(null)

  useEffect(() => { fin.current?.scrollIntoView({ behavior: 'smooth' }) }, [mensajes])

  const enviar = async () => {
    if (!input.trim() || cargando) return
    const userMsg: Mensaje = { rol: 'usuario', contenido: input.trim() }
    const nuevos = [...mensajes, userMsg]
    setMensajes(nuevos)
    setInput('')
    setCargando(true)
    try {
      const apiMsgs = nuevos.map(m => ({ rol: m.rol, contenido: m.contenido }))
      const res = await enviarChat(apiMsgs)
      setMensajes([...nuevos, { rol: 'asistente', contenido: res.respuesta }])
    } catch {
      setMensajes([...nuevos, { rol: 'asistente', contenido: 'Lo siento, ha habido un error. Inténtalo de nuevo.' }])
    }
    setCargando(false)
  }

  const manejarAccion = (texto: string) => {
    const lower = texto.toLowerCase()
    if (lower.includes('abrir_agenda') || lower.includes('reservar') || lower.includes('cita')) {
      onAbrirAgenda?.()
    }
    if (lower.includes('contacto_urgente') || lower.includes('urgente')) {
      setMostrarContacto(true)
    }
  }

  const enviarContactoUrgente = async () => {
    if (!nombreUrgente || !telUrgente) return
    try {
      await contactoUrgente(nombreUrgente, telUrgente)
      setMensajes([...mensajes, { rol: 'asistente', contenido: 'Mensaje enviado. Si es una emergencia, llama al 024 o al 112.' }])
      setMostrarContacto(false)
    } catch {
      setMensajes([...mensajes, { rol: 'asistente', contenido: 'Error al enviar. Si es urgente, llama al 024 (Línea de la Vida) o al 112.' }])
    }
  }

  return (
    <div className="chat-container">
      <div className="chat-mensajes">
        {mensajes.map((m, i) => (
          <div key={i} className={`chat-msg ${m.rol}`}>
            {m.contenido}
          </div>
        ))}
        {cargando && <div className="chat-msg asistente typing">Escribiendo...</div>}
        <div ref={fin} />
      </div>

      <div className="chat-input">
        <input
          value={input}
          onChange={e => setInput(e.target.value)}
          onKeyDown={e => e.key === 'Enter' && enviar()}
          placeholder="Escribe tu mensaje..."
          disabled={cargando}
        />
        <button className="btn compact" onClick={enviar} disabled={cargando}>Enviar</button>
      </div>

      <div className="chat-acciones-rapidas">
        <button className="btn secondary compact" onClick={() => { setInput('Quiero reservar una cita'); }}>Reservar cita</button>
        <button className="btn secondary compact" onClick={() => setMostrarContacto(true)}>Contacto urgente</button>
      </div>

      {mostrarContacto && (
        <div className="chat-contacto-urgente">
          <p><strong>Contacto de urgencia</strong></p>
          <p>Si estás en crisis, llama ahora:</p>
          <p className="numeros-urgencia"><a href="tel:024">024</a> · <a href="tel:112">112</a></p>
          <div className="field">
            <label>Nombre</label>
            <input value={nombreUrgente} onChange={e => setNombreUrgente(e.target.value)} />
          </div>
          <div className="field">
            <label>Teléfono</label>
            <input value={telUrgente} onChange={e => setTelUrgente(e.target.value)} />
          </div>
          <button className="btn compact" onClick={enviarContactoUrgente}>Enviar aviso</button>
          <button className="btn secondary compact" onClick={() => setMostrarContacto(false)}>Cancelar</button>
        </div>
      )}
    </div>
  )
}
