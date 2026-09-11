export default function Faq({ onReservar }: { onReservar?: () => void }) {
  const preguntas = [
    { q: '¿Cómo funciona la terapia online?', a: 'Las sesiones online se realizan por videollamada. Recibirás un enlace por email antes de tu cita. Solo necesitas conexión a internet y un dispositivo con cámara.' },
    { q: '¿Puedo cancelar o reprogramar?', a: 'Sí, puedes cancelar o reprogramar hasta 24 horas antes de tu sesión desde el enlace que recibirás por email.' },
    { q: '¿Qué duración tienen las sesiones?', a: 'Las sesiones estándar tienen una duración de 50 minutos, tiempo suficiente para trabajar de forma efectiva.' },
    { q: '¿La primera sesión es de evaluación?', a: 'Sí, la primera sesión es una entrevista inicial donde conocemos tu situación, establecemos objetivos y decidimos juntos el plan terapéutico.' },
    { q: '¿Cómo pago?', a: 'El pago se realiza por transferencia bancaria antes de la sesión. Recibirás los datos de pago junto con la confirmación de tu reserva.' },
  ]

  return (
    <section id="dudas" className="section">
      <div className="container">
        <span className="eyebrow">Preguntas frecuentes</span>
        <h2>Dudas comunes</h2>
        <div style={{ marginTop: 40, maxWidth: 800 }}>
          {preguntas.map((p, i) => (
            <details key={i} className="faq-item">
              <summary>{p.q}</summary>
              <p>{p.a}</p>
            </details>
          ))}
        </div>
        <div style={{ marginTop: 40, textAlign: 'center' }}>
          <button className="btn" onClick={onReservar}>Reservar mi primera sesión</button>
        </div>
      </div>
    </section>
  )
}
