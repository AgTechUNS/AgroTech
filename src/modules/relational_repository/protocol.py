from typing import Protocol

from modules.relational_repository.dtos import ParcelaCreateDTO, UsuarioDTO


class RelationalRepositoryProtocol(Protocol):
    async def obtener_usuario_por_email(self, email: str) -> UsuarioDTO | None:
        ...

    async def crear_parcela(self, datos: ParcelaCreateDTO) -> None:
        ...
