import { useState } from 'react'
import { loginAdmin } from '../../api'

export default function Login({ onLogin }: { onLogin: (token: string) => void }) {
  const [usuario, setUsuario] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [cargando, setCargando] = useState(false)

  const submit = async (e: React.FormEvent) => {
    e.preventDefault()
    setCargando(true)
    setError('')
    try {
      const res = await loginAdmin(usuario, password)
      onLogin(res.token)
    } catch (e: any) {
      setError(e.message || 'Credenciales inválidas')
    }
    setCargando(false)
  }

  return (
    <div className="admin-login section" style={{ minHeight: '80vh', display: 'grid', placeItems: 'center' }}>
      <div className="card" style={{ width: '100%', maxWidth: 420, padding: 36 }}>
        <span className="eyebrow">Área privada</span>
        <h2>Acceso profesional</h2>
        <form onSubmit={submit} style={{ marginTop: 24 }}>
          <div className="field">
            <label>Usuario</label>
            <input value={usuario} onChange={e => setUsuario(e.target.value)} autoFocus />
          </div>
          <div className="field">
            <label>Contraseña</label>
            <input type="password" value={password} onChange={e => setPassword(e.target.value)} />
          </div>
          {error && <p className="error">{error}</p>}
          <button className="btn" type="submit" disabled={cargando} style={{ width: '100%', marginTop: 8 }}>
            {cargando ? 'Entrando...' : 'Entrar al panel'}
          </button>
        </form>
        <div style={{ marginTop: 20, textAlign: 'center' }}>
          <a href="/" style={{ fontSize: '0.84rem', color: 'var(--muted)' }}>← Volver al sitio web</a>
        </div>
      </div>
    </div>
  )
}
