import logging
from datetime import datetime
from typing import Optional

from sqlalchemy import and_, func, select
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
        self, email: str, nombre: str, hash_password: str, telefono: Optional[str] = None
    ) -> models.Usuario:
        usuario = models.Usuario(email_usuario=email, nombre=nombre, hash_password=hash_password, telefono=telefono)
        async with self._session_factory() as session:
            session.add(usuario)
            await self._commit(session, usuario)
            logger.info("Usuario creado: %s", email)
            return usuario

    async def list_usuarios(self) -> list[models.Usuario]:
        async with self._session_factory() as session:
            result = await session.execute(select(models.Usuario).order_by(models.Usuario.nombre))
            return list(result.scalars().all())

    # ── Roles ─────────────────────────────────────────────────

    async def create_rol(self, nombre_rol: str, descripcion: Optional[str] = None) -> models.Rol:
        rol = models.Rol(nombre_rol=nombre_rol, descripcion=descripcion)
        async with self._session_factory() as session:
            session.add(rol)
            await self._commit(session, rol)
            logger.info("Rol creado: %s", nombre_rol)
            return rol

    async def list_roles(self) -> list[models.Rol]:
        async with self._session_factory() as session:
            result = await session.execute(select(models.Rol).order_by(models.Rol.nombre_rol))
            return list(result.scalars().all())

    # ── Usuario-Rol-Campo ─────────────────────────────────────

    async def assign_rol_to_usuario(self, email_usuario: str, nombre_rol: str, nombre_campo: str) -> models.UsuarioRolCampo:
        urc = models.UsuarioRolCampo(email_usuario=email_usuario, nombre_rol=nombre_rol, nombre_campo=nombre_campo)
        async with self._session_factory() as session:
            session.add(urc)
            await self._commit(session, urc)
            logger.info("Rol %s asignado a %s en campo %s", nombre_rol, email_usuario, nombre_campo)
            return urc

    async def list_roles_by_usuario(self, email_usuario: str) -> list[models.UsuarioRolCampo]:
        async with self._session_factory() as session:
            result = await session.execute(
                select(models.UsuarioRolCampo).where(models.UsuarioRolCampo.email_usuario == email_usuario)
            )
            return list(result.scalars().all())

    # ── Campos ────────────────────────────────────────────────

    async def get_campo_by_nombre(self, nombre: str) -> Optional[models.Campo]:
        async with self._session_factory() as session:
            result = await session.execute(select(models.Campo).where(models.Campo.nombre_campo == nombre))
            return result.scalar_one_or_none()

    async def create_campo(self, nombre: str, coordenadas: str, descripcion: Optional[str] = None) -> models.Campo:
        campo = models.Campo(nombre_campo=nombre, coordenadas_campo=coordenadas, descripcion_campo=descripcion)
        async with self._session_factory() as session:
            session.add(campo)
            await self._commit(session, campo)
            logger.info("Campo creado: %s", nombre)
            return campo

    async def list_campos(self) -> list[models.Campo]:
        async with self._session_factory() as session:
            result = await session.execute(select(models.Campo).order_by(models.Campo.nombre_campo))
            return list(result.scalars().all())

    # ── Parcelas ──────────────────────────────────────────────

    async def get_parcela_by_nombre(self, nombre: str) -> Optional[models.Parcela]:
        async with self._session_factory() as session:
            result = await session.execute(select(models.Parcela).where(models.Parcela.nombre_parcela == nombre))
            return result.scalar_one_or_none()

    async def create_parcela(self, nombre: str, coordenadas: str, nombre_campo: str, descripcion: Optional[str] = None) -> models.Parcela:
        parcela = models.Parcela(nombre_parcela=nombre, coordenadas_parcela=coordenadas, nombre_campo=nombre_campo, descripcion_parcela=descripcion)
        async with self._session_factory() as session:
            session.add(parcela)
            await self._commit(session, parcela)
            logger.info("Parcela creada: %s en campo %s", nombre, nombre_campo)
            return parcela

    async def list_parcelas_by_campo(self, nombre_campo: str) -> list[models.Parcela]:
        async with self._session_factory() as session:
            result = await session.execute(
                select(models.Parcela).where(models.Parcela.nombre_campo == nombre_campo).order_by(models.Parcela.nombre_parcela)
            )
            return list(result.scalars().all())

    # ── Cultivos ──────────────────────────────────────────────

    async def create_cultivo(self, nombre: str, variedad: Optional[str] = None) -> models.Cultivo:
        cultivo = models.Cultivo(nombre_cultivo=nombre, variedad=variedad)
        async with self._session_factory() as session:
            session.add(cultivo)
            await self._commit(session, cultivo)
            logger.info("Cultivo creado: %s", nombre)
            return cultivo

    async def list_cultivos(self) -> list[models.Cultivo]:
        async with self._session_factory() as session:
            result = await session.execute(select(models.Cultivo).order_by(models.Cultivo.nombre_cultivo))
            return list(result.scalars().all())

    async def get_cultivo_by_nombre(self, nombre: str) -> Optional[models.Cultivo]:
        async with self._session_factory() as session:
            result = await session.execute(select(models.Cultivo).where(models.Cultivo.nombre_cultivo == nombre))
            return result.scalar_one_or_none()

    # ── Registro Cultivo ──────────────────────────────────────

    async def registrar_siembra(self, nombre_parcela: str, nombre_cultivo: str, fecha_siembra: datetime) -> models.RegistroCultivo:
        rc = models.RegistroCultivo(nombre_parcela=nombre_parcela, nombre_cultivo=nombre_cultivo, fecha_siembra=fecha_siembra)
        async with self._session_factory() as session:
            session.add(rc)
            await self._commit(session, rc)
            logger.info("Siembra registrada: %s en %s", nombre_cultivo, nombre_parcela)
            return rc

    async def registrar_cosecha(self, nombre_parcela: str, nombre_cultivo: str, fecha_siembra: datetime, fecha_cosecha: datetime) -> Optional[models.RegistroCultivo]:
        async with self._session_factory() as session:
            result = await session.execute(
                select(models.RegistroCultivo).where(
                    and_(
                        models.RegistroCultivo.nombre_parcela == nombre_parcela,
                        models.RegistroCultivo.nombre_cultivo == nombre_cultivo,
                        models.RegistroCultivo.fecha_siembra == fecha_siembra,
                    )
                )
            )
            rc = result.scalar_one_or_none()
            if rc is None:
                return None
            rc.fecha_cosecha = fecha_cosecha
            await self._commit(session, rc)
            logger.info("Cosecha registrada: %s en %s", nombre_cultivo, nombre_parcela)
            return rc

    async def get_historial_cultivos(self, nombre_parcela: str) -> list[models.RegistroCultivo]:
        async with self._session_factory() as session:
            result = await session.execute(
                select(models.RegistroCultivo)
                .where(models.RegistroCultivo.nombre_parcela == nombre_parcela)
                .order_by(models.RegistroCultivo.fecha_siembra.desc())
            )
            return list(result.scalars().all())

    # ── Sensores ──────────────────────────────────────────────

    async def create_sensor(self, nombre_codigo: str, estado: bool = True) -> models.Sensor:
        sensor = models.Sensor(nombre_codigo_sensor=nombre_codigo, estado=estado)
        async with self._session_factory() as session:
            session.add(sensor)
            await self._commit(session, sensor)
            logger.info("Sensor creado: %s (activo=%s)", nombre_codigo, estado)
            return sensor

    async def get_sensor(self, nombre_codigo: str) -> Optional[models.Sensor]:
        async with self._session_factory() as session:
            result = await session.execute(select(models.Sensor).where(models.Sensor.nombre_codigo_sensor == nombre_codigo))
            return result.scalar_one_or_none()

    async def list_sensores(self) -> list[models.Sensor]:
        async with self._session_factory() as session:
            result = await session.execute(select(models.Sensor).order_by(models.Sensor.nombre_codigo_sensor))
            return list(result.scalars().all())

    # ── Sensor-Parcela ────────────────────────────────────────

    async def instalar_sensor_en_parcela(self, nombre_codigo_sensor: str, nombre_parcela: str, nombre_campo: str, fecha_instalacion: datetime) -> models.SensorParcela:
        sp = models.SensorParcela(nombre_codigo_sensor=nombre_codigo_sensor, nombre_parcela=nombre_parcela, nombre_campo=nombre_campo, fecha_instalacion=fecha_instalacion)
        async with self._session_factory() as session:
            session.add(sp)
            await self._commit(session, sp)
            logger.info("Sensor %s instalado en parcela %s", nombre_codigo_sensor, nombre_parcela)
            return sp

    async def retirar_sensor_de_parcela(self, nombre_codigo_sensor: str, nombre_parcela: str, fecha_instalacion: datetime, fecha_retiro: datetime) -> Optional[models.SensorParcela]:
        async with self._session_factory() as session:
            result = await session.execute(
                select(models.SensorParcela).where(
                    and_(
                        models.SensorParcela.nombre_codigo_sensor == nombre_codigo_sensor,
                        models.SensorParcela.nombre_parcela == nombre_parcela,
                        models.SensorParcela.fecha_instalacion == fecha_instalacion,
                    )
                )
            )
            sp = result.scalar_one_or_none()
            if sp is None:
                return None
            sp.fecha_retiro = fecha_retiro
            await self._commit(session, sp)
            logger.info("Sensor %s retirado de parcela %s", nombre_codigo_sensor, nombre_parcela)
            return sp

    async def list_sensores_by_parcela(self, nombre_parcela: str) -> list[models.SensorParcela]:
        async with self._session_factory() as session:
            result = await session.execute(
                select(models.SensorParcela)
                .where(models.SensorParcela.nombre_parcela == nombre_parcela)
                .order_by(models.SensorParcela.fecha_instalacion.desc())
            )
            return list(result.scalars().all())

    # ── Reglas ────────────────────────────────────────────────

    async def create_regla(self, nombre_regla: str, nombre_campo: str, formula: str, umbral: float, descripcion: Optional[str] = None) -> models.Regla:
        regla = models.Regla(nombre_regla=nombre_regla, nombre_campo=nombre_campo, formula=formula, umbral=umbral, descripcion_regla=descripcion)
        async with self._session_factory() as session:
            session.add(regla)
            await self._commit(session, regla)
            logger.info("Regla creada: %s en campo %s", nombre_regla, nombre_campo)
            return regla

    async def list_reglas_by_campo(self, nombre_campo: str) -> list[models.Regla]:
        async with self._session_factory() as session:
            result = await session.execute(
                select(models.Regla).where(models.Regla.nombre_campo == nombre_campo).order_by(models.Regla.nombre_regla)
            )
            return list(result.scalars().all())

    async def list_reglas(self) -> list[models.Regla]:
        async with self._session_factory() as session:
            result = await session.execute(select(models.Regla).order_by(models.Regla.nombre_regla))
            return list(result.scalars().all())

    async def get_regla_by_nombre_and_campo(self, nombre_regla: str, nombre_campo: str) -> Optional[models.Regla]:
        async with self._session_factory() as session:
            result = await session.execute(
                select(models.Regla).where(
                    and_(
                        models.Regla.nombre_regla == nombre_regla,
                        models.Regla.nombre_campo == nombre_campo,
                    )
                )
            )
            return result.scalar_one_or_none()

    async def update_regla(
        self, nombre_regla: str, nombre_campo: str, *,
        formula: str | None = None, umbral: float | None = None,
        descripcion: str | None = None,
    ) -> Optional[models.Regla]:
        async with self._session_factory() as session:
            result = await session.execute(
                select(models.Regla).where(
                    and_(
                        models.Regla.nombre_regla == nombre_regla,
                        models.Regla.nombre_campo == nombre_campo,
                    )
                )
            )
            regla = result.scalar_one_or_none()
            if regla is None:
                logger.warning("Regla no encontrada: %s / %s", nombre_regla, nombre_campo)
                return None
            if formula is not None:
                regla.formula = formula
            if umbral is not None:
                regla.umbral = umbral
            if descripcion is not None:
                regla.descripcion_regla = descripcion
            await self._commit(session, regla)
            logger.info("Regla actualizada: %s en campo %s", nombre_regla, nombre_campo)
            return regla

    async def delete_regla(self, nombre_regla: str, nombre_campo: str) -> bool:
        async with self._session_factory() as session:
            result = await session.execute(
                select(models.Regla).where(
                    and_(
                        models.Regla.nombre_regla == nombre_regla,
                        models.Regla.nombre_campo == nombre_campo,
                    )
                )
            )
            regla = result.scalar_one_or_none()
            if regla is None:
                return False
            await session.delete(regla)
            await session.commit()
            logger.info("Regla eliminada: %s en campo %s", nombre_regla, nombre_campo)
            return True

    # ── Ventana Temporal ──────────────────────────────────────

    async def create_ventana_temporal(self, fecha_ini: datetime, fecha_fin: datetime, nombre_parcela: str) -> models.VentanaTemporal:
        vt = models.VentanaTemporal(fecha_ini=fecha_ini, fecha_fin=fecha_fin, nombre_parcela=nombre_parcela)
        async with self._session_factory() as session:
            session.add(vt)
            await self._commit(session, vt)
            logger.info("Ventana temporal creada para parcela %s", nombre_parcela)
            return vt

    async def list_ventanas_by_parcela(self, nombre_parcela: str) -> list[models.VentanaTemporal]:
        async with self._session_factory() as session:
            result = await session.execute(
                select(models.VentanaTemporal)
                .where(models.VentanaTemporal.nombre_parcela == nombre_parcela)
                .order_by(models.VentanaTemporal.fecha_ini.desc())
            )
            return list(result.scalars().all())

    # ── Imágenes Satelitales ──────────────────────────────────

    async def create_imagen_satelital(self, id_imagen: str, fecha_captura: datetime, proveedor: str) -> models.ImagenSatelital:
        img = models.ImagenSatelital(id_imagen=id_imagen, fecha_captura=fecha_captura, proveedor=proveedor)
        async with self._session_factory() as session:
            session.add(img)
            await self._commit(session, img)
            logger.info("Imagen satelital creada: %s", id_imagen)
            return img

    async def list_imagenes(self) -> list[models.ImagenSatelital]:
        async with self._session_factory() as session:
            result = await session.execute(select(models.ImagenSatelital).order_by(models.ImagenSatelital.fecha_captura.desc()))
            return list(result.scalars().all())

    # ── Parcela-Imagen Satelital ──────────────────────────────

    async def asociar_imagen_a_parcela(self, id_imagen: str, nombre_parcela: str, ndvi: Optional[float] = None, ndmi: Optional[float] = None) -> models.ParcelaImagenSatelital:
        pis = models.ParcelaImagenSatelital(id_imagen=id_imagen, nombre_parcela=nombre_parcela, indice_ndvi=ndvi, indice_ndmi=ndmi)
        async with self._session_factory() as session:
            session.add(pis)
            await self._commit(session, pis)
            logger.info("Imagen %s asociada a parcela %s", id_imagen, nombre_parcela)
            return pis

    async def get_imagenes_by_parcela(self, nombre_parcela: str, limit: int = 50) -> list[models.ParcelaImagenSatelital]:
        async with self._session_factory() as session:
            result = await session.execute(
                select(models.ParcelaImagenSatelital)
                .where(models.ParcelaImagenSatelital.nombre_parcela == nombre_parcela)
                .order_by(models.ParcelaImagenSatelital.id_imagen.desc())
                .limit(limit)
            )
            return list(result.scalars().all())

    # ── Predicciones ──────────────────────────────────────────

    async def create_prediccion(self, fecha_emision: datetime, resultado: str, fecha_ini: datetime, fecha_fin: datetime, nombre_campo: str, nombre_regla: str | None = None) -> models.Prediccion:
        p = models.Prediccion(fecha_emision=fecha_emision, resultado=resultado, fecha_ini=fecha_ini, fecha_fin=fecha_fin, nombre_regla=nombre_regla, nombre_campo=nombre_campo)
        async with self._session_factory() as session:
            session.add(p)
            await self._commit(session, p)
            logger.info("Prediccion creada para campo %s", nombre_campo)
            return p

    async def list_predicciones_by_campo(self, nombre_campo: str, page: int = 1, limit: int = 20) -> tuple[list[models.Prediccion], int]:
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

    # ── Alertas ───────────────────────────────────────────────

    async def create_alerta(self, fecha_emision: datetime, mensaje: str, nombre_parcela: str, email_usuario: str | None = None) -> models.Alerta:
        alerta = models.Alerta(fecha_emision=fecha_emision, mensaje=mensaje, nombre_parcela=nombre_parcela, email_usuario=email_usuario)
        async with self._session_factory() as session:
            session.add(alerta)
            await self._commit(session, alerta)
            logger.info("Alerta creada para parcela %s", nombre_parcela)
            return alerta

    async def list_alertas_by_usuario(self, email_usuario: str, page: int = 1, limit: int = 20) -> tuple[list[models.Alerta], int]:
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

    async def list_alertas_by_parcela(self, nombre_parcela: str, page: int = 1, limit: int = 20) -> tuple[list[models.Alerta], int]:
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

    # ── Ejecución Batch ───────────────────────────────────────

    async def create_ejecucion_batch(self, fecha_ini: datetime, estado: str = "EN_CURSO") -> models.EjecucionBatch:
        eb = models.EjecucionBatch(fecha_ini=fecha_ini, estado=estado)
        async with self._session_factory() as session:
            session.add(eb)
            await self._commit(session, eb)
            logger.info("Ejecucion batch iniciada: %s", fecha_ini.isoformat())
            return eb

    async def finalizar_ejecucion_batch(self, fecha_ini: datetime, estado: str, fecha_fin: datetime) -> Optional[models.EjecucionBatch]:
        async with self._session_factory() as session:
            eb = await session.get(models.EjecucionBatch, fecha_ini)
            if eb is None:
                return None
            eb.estado = estado
            eb.fecha_fin = fecha_fin
            await self._commit(session, eb)
            logger.info("Ejecucion batch finalizada: %s -> %s", fecha_ini.isoformat(), estado)
            return eb

    async def list_ejecuciones_batch(self) -> list[models.EjecucionBatch]:
        async with self._session_factory() as session:
            result = await session.execute(select(models.EjecucionBatch).order_by(models.EjecucionBatch.fecha_ini.desc()))
            return list(result.scalars().all())
