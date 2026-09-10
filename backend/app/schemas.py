from datetime import datetime
from typing import Literal
from pydantic import BaseModel, EmailStr, Field, field_validator

class CitaEntrada(BaseModel):
    inicio: datetime
    modalidad: Literal["online", "presencial"]
    tipo_sesion: str
    nombre: str = Field(min_length=2, max_length=80)
    email: EmailStr
    telefono: str = ""
    consentimiento: Literal[True]
    website: str = ""

    @field_validator("telefono")
    @classmethod
    def validar_telefono(cls, v):
        if v == "":
            return v
        import re
        if not re.match(r"^[+0-9 ]{6,20}$", v):
            raise ValueError("Teléfono no válido")
        return v

class ReagendarEntrada(BaseModel):
    nuevo_inicio: datetime

class ContactoUrgente(BaseModel):
    nombre: str
    telefono: str
