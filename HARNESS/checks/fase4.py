from checks import *
SRC = "frontend/src"
CRITERIOS = [
    existe(f"{SRC}/api.ts"), existe(f"{SRC}/estilos.css"), existe(f"{SRC}/pages/Home.tsx"), existe(f"{SRC}/pages/Gestionar.tsx"),
    existe(f"{SRC}/pages/Admin.tsx"), existe(f"{SRC}/components/ModalReserva.tsx"), existe(f"{SRC}/components/Chat.tsx"),
    existe(f"{SRC}/components/admin/Login.tsx"), existe(f"{SRC}/components/admin/AgendaSemana.tsx"),
    existe(f"{SRC}/components/admin/Disponibilidad.tsx"), existe(f"{SRC}/components/admin/Bloqueos.tsx"),
    existe(f"{SRC}/components/admin/Ajustes.tsx"),
    contiene(f"{SRC}/api.ts", "/api/publico/huecos"), contiene(f"{SRC}/api.ts", "/api/publico/citas"),
    contiene(f"{SRC}/api.ts", "/api/chat"), contiene(f"{SRC}/api.ts", "/api/admin/login"),
    contiene(f"{SRC}/api.ts", "/api/admin/ia/estado"), contiene(f"{SRC}/api.ts", "VITE_API_URL"),
    contiene(f"{SRC}/components/ModalReserva.tsx", 'name="website"'), contiene(f"{SRC}/components/ModalReserva.tsx", "consentimiento"),
    contiene(f"{SRC}/components/Chat.tsx", "024"), contiene(f"{SRC}/components/Chat.tsx", "112"),
    contiene(f"{SRC}/components/Chat.tsx", "abrir_agenda"), contiene(f"{SRC}/components/Chat.tsx", "contacto_urgente"),
    contiene(f"{SRC}/App.tsx", "/gestionar/:token"), contiene(f"{SRC}/App.tsx", "/admin"),
    no_contiene_en_dir(SRC, "No tramita citas reales"), no_contiene_en_dir(SRC, "Agenda de demostración"),
    no_contiene_en_dir(SRC, "datos ficticios"), no_contiene_en_dir(SRC, "localStorage"),
    comando_ok("npm run build", "frontend"), existe("frontend/dist/index.html"),
]