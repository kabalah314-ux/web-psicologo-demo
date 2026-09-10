const API = import.meta.env.VITE_API_URL || 'http://localhost:8000'

async function request(path: string, options: RequestInit = {}) {
  const res = await fetch(`${API}${path}`, {
    headers: { 'Content-Type': 'application/json', ...options.headers },
    ...options,
  })
  if (!res.ok) {
    const body = await res.json().catch(() => ({ detail: res.statusText }))
    throw new Error(body.detail || res.statusText)
  }
  return res.json()
}

export async function getConfig() {
  return request('/api/publico/config')
}

export async function getHuecos(modalidad: string, desde: string, dias = 14) {
  return request(`/api/publico/huecos?modalidad=${modalidad}&desde=${desde}&dias=${dias}`)
}

export async function reservarCita(datos: any) {
  return request('/api/publico/citas', { method: 'POST', body: JSON.stringify(datos) })
}

export async function getCita(token: string) {
  return request(`/api/publico/citas/${token}`)
}

export async function cancelarCita(token: string) {
  return request(`/api/publico/citas/${token}/cancelar`, { method: 'POST' })
}

export async function reagendarCita(token: string, nuevo_inicio: string) {
  return request(`/api/publico/citas/${token}/reagendar`, {
    method: 'POST',
    body: JSON.stringify({ nuevo_inicio })
  })
}

export async function getIcs(token: string) {
  const res = await fetch(`${API}/api/publico/citas/${token}/ics`)
  if (!res.ok) throw new Error('Error descargando .ics')
  return res.blob()
}

export async function contactoUrgente(nombre: string, telefono: string) {
  return request('/api/publico/contacto-urgente', {
    method: 'POST',
    body: JSON.stringify({ nombre, telefono })
  })
}

export async function enviarChat(mensajes: { rol: string; contenido: string }[]) {
  return request('/api/chat', { method: 'POST', body: JSON.stringify({ mensajes }) })
}

export async function loginAdmin(usuario: string, password: string) {
  return request('/api/admin/login', { method: 'POST', body: JSON.stringify({ usuario, password }) })
}

export async function adminCitas(token: string, desde?: string, hasta?: string) {
  const params = new URLSearchParams()
  if (desde) params.set('desde', desde)
  if (hasta) params.set('hasta', hasta)
  const res = await fetch(`${API}/api/admin/citas?${params}`, {
    headers: { Authorization: `Bearer ${token}` }
  })
  if (!res.ok) throw new Error('No autorizado')
  return res.json()
}

export async function adminPatchCita(token: string, citaId: string, data: any) {
  const res = await fetch(`${API}/api/admin/citas/${citaId}`, {
    method: 'PATCH',
    headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${token}` },
    body: JSON.stringify(data)
  })
  if (!res.ok) throw new Error('Error')
  return res.json()
}

export async function adminAjustes(token: string) {
  const res = await fetch(`${API}/api/admin/ajustes`, {
    headers: { Authorization: `Bearer ${token}` }
  })
  return res.json()
}

export async function adminPutAjustes(token: string, datos: any) {
  const res = await fetch(`${API}/api/admin/ajustes`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${token}` },
    body: JSON.stringify(datos)
  })
  if (!res.ok) throw new Error('Error guardando ajustes')
  return res.json()
}

export async function adminIaEstado(token: string) {
  const res = await fetch(`${API}/api/admin/ia/estado`, {
    headers: { Authorization: `Bearer ${token}` }
  })
  return res.json()
}

export async function adminTelegramTest(token: string) {
  const res = await fetch(`${API}/api/admin/telegram/test`, {
    method: 'POST',
    headers: { Authorization: `Bearer ${token}` }
  })
  return res.json()
}
