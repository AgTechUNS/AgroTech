import logging

from sqlalchemy import select

from infrastructure.relational_repo.database import Database
from infrastructure.relational_repo.models import ParcelaModel, UsuarioModel
from modules.relational_repository.dtos import ParcelaCreateDTO, UsuarioDTO

logger = logging.getLogger(__name__)


class SQLAlchemyRelationalRepository:
    def __init__(self, database: Database):
        self._db = database

    async def obtener_usuario_por_email(self, email: str) -> UsuarioDTO | None:
        async with self._db.session() as session:
            result = await session.execute(
                select(UsuarioModel).where(UsuarioModel.email == email)
            )
            row = result.scalar_one_or_none()
            if row is None:
                return None
            return UsuarioDTO(email=row.email, rol=row.rol)

    async def crear_parcela(self, datos: ParcelaCreateDTO) -> None:
        async with self._db.session() as session:
            parcela = ParcelaModel(
                nombre=datos.nombreParcela,
                campo_nombre=datos.nombreCampo,
                coordenadas=datos.coordenadasParcela,
                descripcion=datos.descripcionParcela,
                cultivo_nombre=datos.nombreCultivo,
            )
            session.add(parcela)
