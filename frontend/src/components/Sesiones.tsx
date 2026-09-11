export default function Sesiones() {
  return (
    <section id="sesiones" className="section" style={{ background: 'var(--sage)' }}>
      <div className="container">
        <span className="eyebrow">Tipos de sesión</span>
        <h2>¿Qué necesitas?</h2>
        <div className="grid-3" style={{ marginTop: 40 }}>
          <div className="card">
            <h3>Primera sesión</h3>
            <p>Sesión inicial de 50 minutos para conocernos, explorar tu situación y establecer objetivos terapéuticos.</p>
          </div>
          <div className="card">
            <h3>Seguimiento</h3>
            <p>Sesiones regulares de 50 minutos para trabajar en tu bienestar emocional de forma continua.</p>
          </div>
          <div className="card">
            <h3>Especializada</h3>
            <p>Intervenciones focalizadas en áreas específicas como ansiedad, depresión o gestión del estrés.</p>
          </div>
        </div>
      </div>
    </section>
  )
}
