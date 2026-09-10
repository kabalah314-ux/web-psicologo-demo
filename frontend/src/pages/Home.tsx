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
      <Hero onReservar={() => setModalAbierto(true)} />
      <ComoFunciona />
      <Sesiones />
      <Areas />
      <Profesional />
      <Faq onReservar={() => setModalAbierto(true)} />

      <button className="chat-fab" onClick={() => setChatAbierto(!chatAbierto)}>
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
        <div className="token-info container">
          <p>Tu enlace de gestión: <a href={`/gestionar/${tokenReserva}`}>gestionar/{tokenReserva.slice(0, 8)}...</a></p>
        </div>
      )}
    </>
  )
}
