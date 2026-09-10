import { useParams } from 'react-router-dom'

export default function Gestionar() {
  const { token } = useParams()
  return <div className="container"><h1>Gestionar cita</h1><p>Token: {token}</p></div>
}
