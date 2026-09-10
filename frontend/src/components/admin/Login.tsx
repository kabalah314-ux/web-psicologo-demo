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
    <div className="admin-login section">
      <div className="container" style={{ maxWidth: 400 }}>
        <h2>Acceso administración</h2>
        <form onSubmit={submit} style={{ marginTop: 30 }}>
          <div className="field">
            <label>Usuario</label>
            <input value={usuario} onChange={e => setUsuario(e.target.value)} />
          </div>
          <div className="field">
            <label>Contraseña</label>
            <input type="password" value={password} onChange={e => setPassword(e.target.value)} />
          </div>
          {error && <p className="error">{error}</p>}
          <button className="btn" type="submit" disabled={cargando}>
            {cargando ? 'Entrando...' : 'Entrar'}
          </button>
        </form>
      </div>
    </div>
  )
}
