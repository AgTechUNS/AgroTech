from pydantic import BaseModel, EmailStr


class ParcelaCreateDTO(BaseModel):
    nombreParcela: str
    nombreCampo: str
    coordenadasParcela: str
    descripcionParcela: str | None = None
    nombreCultivo: str | None = None


class UsuarioDTO(BaseModel):
    email: EmailStr
    rol: str
