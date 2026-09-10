export default function Hero({ onReservar }: { onReservar?: () => void }) {
  return (
    <section className="hero section">
      <div className="container">
        <span className="eyebrow">Terapia online y presencial</span>
        <h1>Tu espacio seguro para cuidar tu mente</h1>
        <p className="hero-sub">
          Sesiones de psicología personalizadas en un entorno cálido y confidencial.
          Online o presencial, a tu ritmo.
        </p>
        <div className="hero-acciones">
          <button className="btn" onClick={onReservar}>Reservar sesión</button>
          <a className="btn secondary" href="#como-funciona">Cómo funciona</a>
        </div>
      </div>
    </section>
  )
}
