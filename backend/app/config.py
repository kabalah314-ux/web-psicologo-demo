from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    MONGO_URI: str = ""
    MONGO_DB: str = "tuespacio"
    FRONTEND_URL: str = "http://localhost:5173"
    CORS_ORIGINS: str = "http://localhost:5173"
    API_URL_PROD: str = ""
    ADMIN_USUARIO: str = "admin"
    ADMIN_PASSWORD: str = "cambiame-ya"
    JWT_SECRET: str = "cambiame-32-caracteres-aleatorios"
    CRON_SECRET: str = "cambiame-32-caracteres-aleatorios"
    TELEGRAM_BOT_TOKEN: str = ""
    TELEGRAM_CHAT_ID: str = ""
    RESEND_API_KEY: str = ""
    EMAIL_FROM: str = "Tu Espacio <onboarding@resend.dev>"
    OPENROUTER_API_KEY: str = ""
    OPENROUTER_MODELOS: str = ""
    MODO_TEST: str = "false"

    @property
    def modo_test(self) -> bool:
        return self.MODO_TEST.lower() == "true"

    @property
    def cors_origins_list(self) -> list[str]:
        return [o.strip() for o in self.CORS_ORIGINS.split(",") if o.strip()]

settings = Settings()
