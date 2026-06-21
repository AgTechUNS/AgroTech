import json
import logging
import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from . import models

logger = logging.getLogger(__name__)


class RelationalRepository:
    def __init__(self, session_factory: async_sessionmaker[AsyncSession]) -> None:
        self._session_factory = session_factory

    async def _commit(self, session: AsyncSession, obj) -> None:
        try:
            await session.commit()
            await session.refresh(obj)
        except Exception:
            await session.rollback()
            raise

    # ── Usuarios ──────────────────────────────────────────────

    async def get_usuario_by_email(self, email: str) -> Optional[models.Usuario]:
        async with self._session_factory() as session:
            result = await session.execute(
                select(models.Usuario).where(models.Usuario.email_usuario == email)
            )
            return result.scalar_one_or_none()

    async def create_usuario(
        self, email: str, nombre: str, hash_password: str, rol: str,
        admin_email: Optional[str] = None, telefono: Optional[str] = None,
    ) -> models.Usuario:
        usuario = models.Usuario(
            email_usuario=email, nombre=nombre, hash_password=hash_password,
            rol=rol, admin_email=admin_email, telefono=telefono,
        )
        async with self._session_factory() as session:
            session.add(usuario)
            await self._commit(session, usuario)
            logger.info("Usuario creado: %s", email)
            return usuario

    async def list_usuarios(self, admin_email: Optional[str] = None) -> list[models.Usuario]:
        async with self._session_factory() as session:
            q = select(models.Usuario)
            if admin_email:
                q = q.where(
                    (models.Usuario.email_usuario == admin_email) |
                    (models.Usuario.admin_email == admin_email)
                )
            result = await session.execute(q.order_by(models.Usuario.nombre))
            return list(result.scalars().all())

    async def update_usuario(self, email: str, **kwargs) -> Optional[models.Usuario]:
        async with self._session_factory() as session:
            result = await session.execute(
                select(models.Usuario).where(models.Usuario.email_usuario == email)
            )
            usuario = result.scalar_one_or_none()
            if usuario is None:
                return None
            for k, v in kwargs.items():
                if hasattr(usuario, k):
                    setattr(usuario, k, v)
            await self._commit(session, usuario)
            logger.info("Usuario actualizado: %s", email)
            return usuario

    async def delete_usuario(self, email: str) -> bool:
        async with self._session_factory() as session:
            result = await session.execute(
                select(models.Usuario).where(models.Usuario.email_usuario == email)
            )
            usuario = result.scalar_one_or_none()
            if usuario is None:
                return False
            await session.delete(usuario)
            await session.commit()
            return True

    # ── Campos ────────────────────────────────────────────────

    async def get_campo_by_nombre(self, nombre: str) -> Optional[models.Campo]:
        async with self._session_factory() as session:
            result = await session.execute(
                select(models.Campo).where(models.Campo.nombre_campo == nombre)
            )
            return result.scalar_one_or_none()

    async def create_campo(
        self, nombre: str, coordenadas: str, admin_email: str,
        descripcion: Optional[str] = None,
    ) -> models.Campo:
        campo = models.Campo(
            nombre_campo=nombre, coordenadas_campo=coordenadas,
            admin_email=admin_email, descripcion_campo=descripcion,
        )
        async with self._session_factory() as session:
            session.add(campo)
            await self._commit(session, campo)
            logger.info("Campo creado: %s", nombre)
            return campo

    async def list_campos(self, admin_email: Optional[str] = None) -> list[models.Campo]:
        async with self._session_factory() as session:
            q = select(models.Campo)
            if admin_email:
                q = q.where(models.Campo.admin_email == admin_email)
            result = await session.execute(q.order_by(models.Campo.nombre_campo))
            return list(result.scalars().all())

    async def update_campo(self, nombre: str, **kwargs) -> Optional[models.Campo]:
        async with self._session_factory() as session:
            result = await session.execute(
                select(models.Campo).where(models.Campo.nombre_campo == nombre)
            )
            campo = result.scalar_one_or_none()
            if campo is None:
                return None
            for k, v in kwargs.items():
                if hasattr(campo, k):
                    setattr(campo, k, v)
            await self._commit(session, campo)
            logger.info("Campo actualizado: %s", nombre)
            return campo

    async def delete_campo(self, nombre: str) -> bool:
        async with self._session_factory() as session:
            result = await session.execute(
                select(models.Campo).where(models.Campo.nombre_campo == nombre)
            )
            campo = result.scalar_one_or_none()
            if campo is None:
                return False
            await session.delete(campo)
            await session.commit()
            return True

    # ── Parcelas ──────────────────────────────────────────────

    async def get_parcela_by_nombre(self, nombre: str, nombre_campo: str) -> Optional[models.Parcela]:
        async with self._session_factory() as session:
            result = await session.execute(
                select(models.Parcela).where(
                    models.Parcela.nombre_parcela == nombre,
                    models.Parcela.nombre_campo == nombre_campo,
                )
            )
            return result.scalar_one_or_none()

    async def create_parcela(
        self, nombre: str, coordenadas: str, nombre_campo: str, admin_email: str,
        descripcion: Optional[str] = None,
        nombre_cultivo: Optional[str] = None, variedad: Optional[str] = None,
    ) -> models.Parcela:
        parcela = models.Parcela(
            nombre_parcela=nombre, coordenadas_parcela=coordenadas,
            nombre_campo=nombre_campo, admin_email=admin_email,
            descripcion_parcela=descripcion,
            nombre_cultivo=nombre_cultivo, variedad=variedad,
        )
        async with self._session_factory() as session:
            session.add(parcela)
            await self._commit(session, parcela)
            logger.info("Parcela creada: %s en campo %s", nombre, nombre_campo)
            return parcela

    async def list_parcelas_by_campo(self, nombre_campo: str) -> list[models.Parcela]:
        async with self._session_factory() as session:
            result = await session.execute(
                select(models.Parcela)
                .where(models.Parcela.nombre_campo == nombre_campo)
                .order_by(models.Parcela.nombre_parcela)
            )
            return list(result.scalars().all())

    async def update_parcela(self, nombre: str, nombre_campo: str, **kwargs) -> Optional[models.Parcela]:
        async with self._session_factory() as session:
            result = await session.execute(
                select(models.Parcela).where(
                    models.Parcela.nombre_parcela == nombre,
                    models.Parcela.nombre_campo == nombre_campo,
                )
            )
            parcela = result.scalar_one_or_none()
            if parcela is None:
                return None
            for k, v in kwargs.items():
                if hasattr(parcela, k):
                    setattr(parcela, k, v)
            await self._commit(session, parcela)
            return parcela

    async def delete_parcela(self, nombre: str, nombre_campo: str) -> bool:
        async with self._session_factory() as session:
            result = await session.execute(
                select(models.Parcela).where(
                    models.Parcela.nombre_parcela == nombre,
                    models.Parcela.nombre_campo == nombre_campo,
                )
            )
            parcela = result.scalar_one_or_none()
            if parcela is None:
                return False
            await session.delete(parcela)
            await session.commit()
            return True

    # ── Cultivos ──────────────────────────────────────────────

    async def create_cultivo(self, nombre: str, variedad: str, admin_email: str) -> models.Cultivo:
        cultivo = models.Cultivo(nombre_cultivo=nombre, variedad=variedad, admin_email=admin_email)
        async with self._session_factory() as session:
            session.add(cultivo)
            await self._commit(session, cultivo)
            logger.info("Cultivo creado: %s / %s", nombre, variedad)
            return cultivo

    async def list_cultivos(self, admin_email: Optional[str] = None) -> list[models.Cultivo]:
        async with self._session_factory() as session:
            q = select(models.Cultivo)
            if admin_email:
                q = q.where(models.Cultivo.admin_email == admin_email)
            result = await session.execute(q.order_by(models.Cultivo.nombre_cultivo))
            return list(result.scalars().all())

    async def get_cultivo_by_nombre(self, nombre: str, variedad: str) -> Optional[models.Cultivo]:
        async with self._session_factory() as session:
            result = await session.execute(
                select(models.Cultivo).where(
                    models.Cultivo.nombre_cultivo == nombre,
                    models.Cultivo.variedad == variedad,
                )
            )
            return result.scalar_one_or_none()

    async def delete_cultivo(self, nombre: str, variedad: str) -> bool:
        async with self._session_factory() as session:
            result = await session.execute(
                select(models.Cultivo).where(
                    models.Cultivo.nombre_cultivo == nombre,
                    models.Cultivo.variedad == variedad,
                )
            )
            cultivo = result.scalar_one_or_none()
            if cultivo is None:
                return False
            await session.delete(cultivo)
            await session.commit()
            return True

    # ── Reglas ────────────────────────────────────────────────

    async def create_regla(
        self, nombre: str, metrica: str, operador: str, valor: float, admin_email: str,
        descripcion: Optional[str] = None, campos_asignados: Optional[list[str]] = None,
    ) -> models.Regla:
        regla = models.Regla(
            id=uuid.uuid4(),
            nombre=nombre, descripcion=descripcion,
            metrica=metrica, operador=operador, valor=valor,
            admin_email=admin_email,
            campos_asignados=json.dumps(campos_asignados or []),
        )
        async with self._session_factory() as session:
            session.add(regla)
            await self._commit(session, regla)
            logger.info("Regla creada: %s", nombre)
            return regla

    async def get_regla_by_id(self, regla_id: uuid.UUID) -> Optional[models.Regla]:
        async with self._session_factory() as session:
            return await session.get(models.Regla, regla_id)

    async def list_reglas(self, admin_email: Optional[str] = None) -> list[models.Regla]:
        async with self._session_factory() as session:
            q = select(models.Regla)
            if admin_email:
                q = q.where(models.Regla.admin_email == admin_email)
            result = await session.execute(q.order_by(models.Regla.nombre))
            return list(result.scalars().all())

    async def list_reglas_by_campo(self, nombre_campo: str) -> list[models.Regla]:
        """Retorna reglas cuyo campos_asignados contenga nombre_campo."""
        todas = await self.list_reglas()
        return [r for r in todas if nombre_campo in json.loads(r.campos_asignados)]

    async def update_regla(self, regla_id: uuid.UUID, **kwargs) -> Optional[models.Regla]:
        async with self._session_factory() as session:
            regla = await session.get(models.Regla, regla_id)
            if regla is None:
                return None
            if "campos_asignados" in kwargs and isinstance(kwargs["campos_asignados"], list):
                kwargs["campos_asignados"] = json.dumps(kwargs["campos_asignados"])
            for k, v in kwargs.items():
                if hasattr(regla, k):
                    setattr(regla, k, v)
            await self._commit(session, regla)
            logger.info("Regla actualizada: %s", regla_id)
            return regla

    async def delete_regla(self, regla_id: uuid.UUID) -> bool:
        async with self._session_factory() as session:
            regla = await session.get(models.Regla, regla_id)
            if regla is None:
                return False
            await session.delete(regla)
            await session.commit()
            return True

    # Backward-compat: analytics engine busca por nombre + campo
    async def get_regla_by_nombre_and_campo(self, nombre_regla: str, nombre_campo: str) -> Optional[models.Regla]:
        todas = await self.list_reglas()
        for r in todas:
            if r.nombre == nombre_regla and nombre_campo in json.loads(r.campos_asignados):
                return r
        return None

    # ── Sensores ──────────────────────────────────────────────

    async def create_sensor(
        self, device_id: str, nombre_campo: str, nombre_parcela: str,
        tipo: str, admin_email: str, activo: bool = True,
    ) -> models.Sensor:
        sensor = models.Sensor(
            device_id=device_id, nombre_campo=nombre_campo,
            nombre_parcela=nombre_parcela, tipo=tipo,
            activo=activo, admin_email=admin_email,
        )
        async with self._session_factory() as session:
            session.add(sensor)
            await self._commit(session, sensor)
            logger.info("Sensor creado: %s", device_id)
            return sensor

    async def get_sensor(self, device_id: str) -> Optional[models.Sensor]:
        async with self._session_factory() as session:
            return await session.get(models.Sensor, device_id)

    async def list_sensores(self, admin_email: Optional[str] = None) -> list[models.Sensor]:
        async with self._session_factory() as session:
            q = select(models.Sensor)
            if admin_email:
                q = q.where(models.Sensor.admin_email == admin_email)
            result = await session.execute(q.order_by(models.Sensor.device_id))
            return list(result.scalars().all())

    async def update_sensor(self, device_id: str, **kwargs) -> Optional[models.Sensor]:
        async with self._session_factory() as session:
            sensor = await session.get(models.Sensor, device_id)
            if sensor is None:
                return None
            for k, v in kwargs.items():
                if hasattr(sensor, k):
                    setattr(sensor, k, v)
            await self._commit(session, sensor)
            return sensor

    async def delete_sensor(self, device_id: str) -> bool:
        async with self._session_factory() as session:
            sensor = await session.get(models.Sensor, device_id)
            if sensor is None:
                return False
            await session.delete(sensor)
            await session.commit()
            return True

    # ── Alertas ───────────────────────────────────────────────

    async def create_alerta(
        self, fecha_emision: datetime, mensaje: str,
        nombre_parcela: str, email_usuario: Optional[str] = None,
    ) -> models.Alerta:
        alerta = models.Alerta(
            fecha_emision=fecha_emision, mensaje=mensaje,
            nombre_parcela=nombre_parcela, email_usuario=email_usuario,
        )
        async with self._session_factory() as session:
            session.add(alerta)
            await self._commit(session, alerta)
            logger.info("Alerta creada para parcela %s", nombre_parcela)
            return alerta

    async def list_alertas_by_usuario(
        self, email_usuario: str, page: int = 1, limit: int = 20
    ) -> tuple[list[models.Alerta], int]:
        async with self._session_factory() as session:
            count_result = await session.execute(
                select(func.count(models.Alerta.id)).where(models.Alerta.email_usuario == email_usuario)
            )
            total = count_result.scalar() or 0
            result = await session.execute(
                select(models.Alerta)
                .where(models.Alerta.email_usuario == email_usuario)
                .order_by(models.Alerta.fecha_emision.desc())
                .offset((page - 1) * limit)
                .limit(limit)
            )
            return list(result.scalars().all()), total

    async def list_alertas_by_parcela(
        self, nombre_parcela: str, page: int = 1, limit: int = 20
    ) -> tuple[list[models.Alerta], int]:
        async with self._session_factory() as session:
            count_result = await session.execute(
                select(func.count(models.Alerta.id)).where(models.Alerta.nombre_parcela == nombre_parcela)
            )
            total = count_result.scalar() or 0
            result = await session.execute(
                select(models.Alerta)
                .where(models.Alerta.nombre_parcela == nombre_parcela)
                .order_by(models.Alerta.fecha_emision.desc())
                .offset((page - 1) * limit)
                .limit(limit)
            )
            return list(result.scalars().all()), total

    # ── Predicciones ──────────────────────────────────────────

    async def create_prediccion(
        self, fecha_emision: datetime, resultado: str,
        fecha_ini: datetime, fecha_fin: datetime,
        nombre_campo: str, nombre_regla: Optional[str] = None,
    ) -> models.Prediccion:
        p = models.Prediccion(
            fecha_emision=fecha_emision, resultado=resultado,
            fecha_ini=fecha_ini, fecha_fin=fecha_fin,
            nombre_regla=nombre_regla, nombre_campo=nombre_campo,
        )
        async with self._session_factory() as session:
            session.add(p)
            await self._commit(session, p)
            logger.info("Prediccion creada para campo %s", nombre_campo)
            return p

    async def list_predicciones_by_campo(
        self, nombre_campo: str, page: int = 1, limit: int = 20
    ) -> tuple[list[models.Prediccion], int]:
        async with self._session_factory() as session:
            count_result = await session.execute(
                select(func.count(models.Prediccion.id)).where(models.Prediccion.nombre_campo == nombre_campo)
            )
            total = count_result.scalar() or 0
            result = await session.execute(
                select(models.Prediccion)
                .where(models.Prediccion.nombre_campo == nombre_campo)
                .order_by(models.Prediccion.fecha_emision.desc())
                .offset((page - 1) * limit)
                .limit(limit)
            )
            return list(result.scalars().all()), total

    # ── Imágenes Satelitales ──────────────────────────────────

    async def create_imagen_satelital(
        self, id_imagen: str, fecha_captura: datetime, proveedor: str
    ) -> models.ImagenSatelital:
        img = models.ImagenSatelital(id_imagen=id_imagen, fecha_captura=fecha_captura, proveedor=proveedor)
        async with self._session_factory() as session:
            session.add(img)
            await self._commit(session, img)
            return img

    async def list_imagenes(self) -> list[models.ImagenSatelital]:
        async with self._session_factory() as session:
            result = await session.execute(
                select(models.ImagenSatelital).order_by(models.ImagenSatelital.fecha_captura.desc())
            )
            return list(result.scalars().all())

    async def asociar_imagen_a_parcela(
        self, id_imagen: str, nombre_parcela: str,
        nombre_campo: str = "",
        ndvi: Optional[float] = None, ndmi: Optional[float] = None,
    ) -> models.ParcelaImagenSatelital:
        pis = models.ParcelaImagenSatelital(
            id_imagen=id_imagen, nombre_parcela=nombre_parcela,
            nombre_campo=nombre_campo,
            indice_ndvi=ndvi, indice_ndmi=ndmi,
        )
        async with self._session_factory() as session:
            session.add(pis)
            await self._commit(session, pis)
            return pis

    async def get_imagenes_by_parcela(
        self, nombre_parcela: str, nombre_campo: str = "", limit: int = 50
    ) -> list[models.ParcelaImagenSatelital]:
        async with self._session_factory() as session:
            q = select(models.ParcelaImagenSatelital).where(
                models.ParcelaImagenSatelital.nombre_parcela == nombre_parcela
            )
            if nombre_campo:
                q = q.where(models.ParcelaImagenSatelital.nombre_campo == nombre_campo)
            result = await session.execute(
                q.order_by(models.ParcelaImagenSatelital.id_imagen.desc())
                .limit(limit)
            )
            return list(result.scalars().all())

    # ── Ejecución Batch ───────────────────────────────────────

    async def create_ejecucion_batch(self, fecha_ini: datetime, estado: str = "EN_CURSO") -> models.EjecucionBatch:
        eb = models.EjecucionBatch(fecha_ini=fecha_ini, estado=estado)
        async with self._session_factory() as session:
            session.add(eb)
            await self._commit(session, eb)
            return eb

    async def finalizar_ejecucion_batch(
        self, fecha_ini: datetime, estado: str, fecha_fin: datetime
    ) -> Optional[models.EjecucionBatch]:
        async with self._session_factory() as session:
            eb = await session.get(models.EjecucionBatch, fecha_ini)
            if eb is None:
                return None
            eb.estado = estado
            eb.fecha_fin = fecha_fin
            await self._commit(session, eb)
            return eb

    async def list_ejecuciones_batch(self) -> list[models.EjecucionBatch]:
        async with self._session_factory() as session:
            result = await session.execute(
                select(models.EjecucionBatch).order_by(models.EjecucionBatch.fecha_ini.desc())
            )
            return list(result.scalars().all())
