export default function Profesional() {
  return (
    <section id="sobre-mi" className="section" style={{ background: 'var(--sage)' }}>
      <div className="container two-cols" style={{ alignItems: 'center' }}>
        <div>
          <span className="eyebrow">Sobre mí</span>
          <h2>Tu psicóloga de confianza</h2>
          <p style={{ marginTop: 20 }}>
            Soy psicóloga colegiada con más de 10 años de experiencia. Mi enfoque integra la terapia cognitivo-conductual
            con técnicas de terapia de tercera generación para ofrecerte un tratamiento adaptado a tus necesidades.
          </p>
          <p style={{ marginTop: 16 }}>
            Creo firmemente en la importancia de crear un espacio seguro y sin juicios donde puedas explorar tus
            emociones y desarrollar herramientas para tu bienestar.
          </p>
        </div>
        <div className="profesional-foto">
          <div className="profile-placeholder">
            <span className="monogram">ψ</span>
            <p>Espacio seguro y profesional</p>
          </div>
        </div>
      </div>
    </section>
  )
}
