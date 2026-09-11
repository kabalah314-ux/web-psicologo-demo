export default function Hero({ onReservar }: { onReservar?: () => void }) {
  return (
    <section className="hero">
      <div className="container">
        <div className="hero-grid">
          <div>
            <span className="eyebrow">Un espacio para parar, sentir y comprender</span>
            <h1>No tienes que poder con todo a solas.</h1>
            <p className="hero-sub">
              A veces, el primer paso es encontrar un lugar donde poder ser tú.
              Un espacio de escucha profesional para comprender lo que te pasa y explorar nuevas maneras de cuidarte.
            </p>
            <div className="hero-acciones">
              <button className="btn" onClick={onReservar}>
                Reservar sesión <span aria-hidden="true">↗</span>
              </button>
              <a className="btn secondary" href="#como-funciona">Cómo funciona</a>
            </div>
            <div className="hero-tags">
              <span className="pill">◌ Online y presencial</span>
              <span className="pill">◈ Colegiada y sanitaria</span>
              <span className="pill">◇ Sin permanencia</span>
            </div>
          </div>

          <div className="hero-art">
            <div className="art-shell">
              <svg viewBox="0 0 200 240" fill="none" xmlns="http://www.w3.org/2000/svg">
                <circle cx="100" cy="85" r="45" fill="#244b42" fillOpacity="0.12" />
                <path d="M45 220 C45 155 155 155 155 220 Z" fill="#244b42" fillOpacity="0.16" />
                <circle cx="100" cy="75" r="30" fill="#244b42" fillOpacity="0.75" />
                <path d="M60 220 C60 170 140 170 140 220 Z" fill="#244b42" fillOpacity="0.85" />
                <circle cx="130" cy="45" r="16" fill="#f0d9ca" />
              </svg>
            </div>
            <div className="floating-card">
              <strong>Un paso a la vez</strong>
              <span>Primera sesión informativa y sin compromiso</span>
            </div>
          </div>
        </div>

        <div className="trust-strip">
          <div><b>01</b> <span>100% Confidencial y seguro</span></div>
          <div><b>02</b> <span>Sesiones online y presencial</span></div>
          <div><b>03</b> <span>A tu ritmo, tú decides</span></div>
        </div>
      </div>
    </section>
  )
}

