export default function ComoFunciona() {
  return (
    <section id="como-funciona" className="section">
      <div className="container">
        <span className="eyebrow">Cómo funciona</span>
        <h2>Un proceso sencillo</h2>
        <div className="grid-3" style={{ marginTop: 40 }}>
          <div className="card">
            <h3>1. Elige tu sesión</h3>
            <p>Selecciona el tipo de sesión que necesitas: primera visita, seguimiento o especializada.</p>
          </div>
          <div className="card">
            <h3>2. Reserva un hueco</h3>
            <p>Consulta la disponibilidad y elige el día y hora que mejor se adapte a ti.</p>
          </div>
          <div className="card">
            <h3>3. Acude a tu cita</h3>
            <p>Recibe un enlace de videoconferencia o acude al despacho. Es tan sencillo como eso.</p>
          </div>
        </div>
      </div>
    </section>
  )
}
