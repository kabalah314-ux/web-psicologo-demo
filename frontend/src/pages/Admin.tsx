import { useState } from 'react'
import Login from '../components/admin/Login'
import AgendaSemana from '../components/admin/AgendaSemana'
import Disponibilidad from '../components/admin/Disponibilidad'
import Bloqueos from '../components/admin/Bloqueos'
import Ajustes from '../components/admin/Ajustes'

type Tab = 'agenda' | 'disponibilidad' | 'bloqueos' | 'ajustes'

export default function Admin() {
  const [token, setToken] = useState<string | null>(null)
  const [tab, setTab] = useState<Tab>('agenda')

  if (!token) return <Login onLogin={setToken} />

  const tabs: { id: Tab; label: string }[] = [
    { id: 'agenda', label: 'Agenda' },
    { id: 'disponibilidad', label: 'Disponibilidad' },
    { id: 'bloqueos', label: 'Bloqueos' },
    { id: 'ajustes', label: 'Ajustes' },
  ]

  return (
    <div className="admin-layout">
      <nav className="admin-nav">
        <div className="container">
          <strong>Tu Espacio — Admin</strong>
          <div className="admin-tabs">
            {tabs.map(t => (
              <button key={t.id} className={`tab-btn ${tab === t.id ? 'active' : ''}`} onClick={() => setTab(t.id)}>
                {t.label}
              </button>
            ))}
          </div>
          <button className="btn secondary compact" onClick={() => setToken(null)}>Salir</button>
        </div>
      </nav>
      <main className="admin-main container">
        {tab === 'agenda' && <AgendaSemana token={token} />}
        {tab === 'disponibilidad' && <Disponibilidad token={token} />}
        {tab === 'bloqueos' && <Bloqueos token={token} />}
        {tab === 'ajustes' && <Ajustes token={token} />}
      </main>
    </div>
  )
}
