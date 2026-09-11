import { useState } from 'react'
import Hero from '../components/Hero'
import ComoFunciona from '../components/ComoFunciona'
import Sesiones from '../components/Sesiones'
import Areas from '../components/Areas'
import Profesional from '../components/Profesional'
import Faq from '../components/Faq'
import Chat from '../components/Chat'
import ModalReserva from '../components/ModalReserva'

export default function Home() {
  const [chatAbierto, setChatAbierto] = useState(false)
  const [modalAbierto, setModalAbierto] = useState(false)
  const [tokenReserva, setTokenReserva] = useState<string | null>(null)

  return (
    <>
      <header className="site-header">
        <nav className="container nav" aria-label="Navegación principal">
          <a className="brand" href="/" aria-label="Tu Espacio, inicio">
            <span className="brand-mark" aria-hidden="true">ψ</span>
            <span><strong>tu espacio</strong><small>Psicología</small></span>
          </a>
          <div className="nav-links">
            <a href="#como-funciona">Cómo funciona</a>
            <a href="#sesiones">Sesiones</a>
            <a href="#areas">Especialidades</a>
            <a href="#sobre-mi">Sobre mí</a>
            <a href="#dudas">Dudas</a>
            <button className="btn compact" onClick={() => setModalAbierto(true)}>
              Reservar cita ↗
            </button>
          </div>
        </nav>
      </header>

      <main>
        <Hero onReservar={() => setModalAbierto(true)} />
        <ComoFunciona />
        <Sesiones />
        <Areas />
        <Profesional />
        <Faq onReservar={() => setModalAbierto(true)} />
      </main>

      <footer className="site-footer">
        <div className="container footer-row">
          <div>
            <p style={{ fontWeight: 600, color: 'var(--ink)' }}>Tu Espacio · Psicología y Bienestar Emocional</p>
            <p style={{ fontSize: '0.84rem' }}>Acompañamiento psicológico profesional, personalizado y confidencial.</p>
          </div>
          <div className="footer-links">
            <a href="#sobre-mi">Colegiada y Sanitaria</a>
            <a href="/admin">Acceso administración</a>
          </div>
        </div>
      </footer>

      <button
        className="chat-fab"
        onClick={() => setChatAbierto(!chatAbierto)}
        aria-label={chatAbierto ? 'Cerrar chat' : 'Abrir chat'}
      >
        {chatAbierto ? '×' : '💬'}
      </button>

      {chatAbierto && (
        <div className="chat-panel">
          <Chat onAbrirAgenda={() => { setChatAbierto(false); setModalAbierto(true) }} />
        </div>
      )}

      <ModalReserva
        open={modalAbierto}
        onClose={() => { setModalAbierto(false); setTokenReserva(null) }}
        onReservada={(token) => setTokenReserva(token)}
      />

      {tokenReserva && (
        <div className="token-info container" style={{ marginTop: 20, textAlign: 'center' }}>
          <p>Tu enlace de gestión: <a href={`/gestionar/${tokenReserva}`}>gestionar/{tokenReserva.slice(0, 8)}...</a></p>
        </div>
      )}
    </>
  )
}
