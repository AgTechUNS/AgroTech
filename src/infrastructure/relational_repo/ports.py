from datetime import datetime
from typing import Optional, Protocol

from . import models


class RelationalRepositoryInterface(Protocol):
    # ── Usuarios ──────────────────────────────────────────────
    async def get_usuario_by_email(self, email: str) -> Optional[models.Usuario]:
        ...

    async def create_usuario(
        self, email: str, nombre: str, hash_password: str, telefono: Optional[str] = None
    ) -> models.Usuario:
        ...

    async def list_usuarios(self) -> list[models.Usuario]:
        ...

    # ── Roles ─────────────────────────────────────────────────
    async def create_rol(self, nombre_rol: str, descripcion: Optional[str] = None) -> models.Rol:
        ...

    async def list_roles(self) -> list[models.Rol]:
        ...

    # ── Usuario-Rol-Campo ─────────────────────────────────────
    async def assign_rol_to_usuario(
        self, email_usuario: str, nombre_rol: str, nombre_campo: str
    ) -> models.UsuarioRolCampo:
        ...

    async def list_roles_by_usuario(self, email_usuario: str) -> list[models.UsuarioRolCampo]:
        ...

    # ── Campos ────────────────────────────────────────────────
    async def get_campo_by_nombre(self, nombre: str) -> Optional[models.Campo]:
        ...

    async def create_campo(
        self, nombre: str, coordenadas: str, descripcion: Optional[str] = None
    ) -> models.Campo:
        ...

    async def list_campos(self) -> list[models.Campo]:
        ...

    # ── Parcelas ──────────────────────────────────────────────
    async def get_parcela_by_nombre(self, nombre: str) -> Optional[models.Parcela]:
        ...

    async def create_parcela(
        self, nombre: str, coordenadas: str, nombre_campo: str, descripcion: Optional[str] = None
    ) -> models.Parcela:
        ...

    async def list_parcelas_by_campo(self, nombre_campo: str) -> list[models.Parcela]:
        ...

    # ── Cultivos ──────────────────────────────────────────────
    async def create_cultivo(self, nombre: str, variedad: Optional[str] = None) -> models.Cultivo:
        ...

    async def list_cultivos(self) -> list[models.Cultivo]:
        ...

    async def get_cultivo_by_nombre(self, nombre: str) -> Optional[models.Cultivo]:
        ...

    # ── Registro Cultivo ──────────────────────────────────────
    async def registrar_siembra(
        self, nombre_parcela: str, nombre_cultivo: str, fecha_siembra: datetime
    ) -> models.RegistroCultivo:
        ...

    async def registrar_cosecha(
        self, nombre_parcela: str, nombre_cultivo: str, fecha_siembra: datetime, fecha_cosecha: datetime
    ) -> Optional[models.RegistroCultivo]:
        ...

    async def get_historial_cultivos(self, nombre_parcela: str) -> list[models.RegistroCultivo]:
        ...

    # ── Sensores ──────────────────────────────────────────────
    async def create_sensor(self, nombre_codigo: str, estado: bool = True) -> models.Sensor:
        ...

    async def get_sensor(self, nombre_codigo: str) -> Optional[models.Sensor]:
        ...

    async def list_sensores(self) -> list[models.Sensor]:
        ...

    # ── Sensor-Parcela ────────────────────────────────────────
    async def instalar_sensor_en_parcela(
        self, nombre_codigo_sensor: str, nombre_parcela: str, nombre_campo: str, fecha_instalacion: datetime
    ) -> models.SensorParcela:
        ...

    async def retirar_sensor_de_parcela(
        self, nombre_codigo_sensor: str, nombre_parcela: str, fecha_instalacion: datetime, fecha_retiro: datetime
    ) -> Optional[models.SensorParcela]:
        ...

    async def list_sensores_by_parcela(self, nombre_parcela: str) -> list[models.SensorParcela]:
        ...

    # ── Reglas ────────────────────────────────────────────────
    async def create_regla(
        self, nombre_regla: str, nombre_campo: str, formula: str, umbral: float, descripcion: Optional[str] = None
    ) -> models.Regla:
        ...

    async def list_reglas_by_campo(self, nombre_campo: str) -> list[models.Regla]:
        ...

    async def list_reglas(self) -> list[models.Regla]:
        ...

    # ── Ventana Temporal ──────────────────────────────────────
    async def create_ventana_temporal(
        self, fecha_ini: datetime, fecha_fin: datetime, nombre_parcela: str
    ) -> models.VentanaTemporal:
        ...

    async def list_ventanas_by_parcela(self, nombre_parcela: str) -> list[models.VentanaTemporal]:
        ...

    # ── Imágenes Satelitales ──────────────────────────────────
    async def create_imagen_satelital(
        self, id_imagen: str, fecha_captura: datetime, proveedor: str
    ) -> models.ImagenSatelital:
        ...

    async def list_imagenes(self) -> list[models.ImagenSatelital]:
        ...

    # ── Parcela-Imagen Satelital ──────────────────────────────
    async def asociar_imagen_a_parcela(
        self, id_imagen: str, nombre_parcela: str, ndvi: Optional[float] = None, ndmi: Optional[float] = None
    ) -> models.ParcelaImagenSatelital:
        ...

    async def get_imagenes_by_parcela(
        self, nombre_parcela: str, limit: int = 50
    ) -> list[models.ParcelaImagenSatelital]:
        ...

    # ── Predicciones ──────────────────────────────────────────
    async def create_prediccion(
        self, fecha_emision: datetime, resultado: str, fecha_ini: datetime, fecha_fin: datetime,
        nombre_regla: str, nombre_campo: str
    ) -> models.Prediccion:
        ...

    async def list_predicciones_by_campo(
        self, nombre_campo: str, page: int = 1, limit: int = 20
    ) -> tuple[list[models.Prediccion], int]:
        ...

    # ── Alertas ───────────────────────────────────────────────
    async def create_alerta(
        self, fecha_emision: datetime, mensaje: str, nombre_parcela: str, email_usuario: str | None = None
    ) -> models.Alerta:
        ...

    async def list_alertas_by_usuario(
        self, email_usuario: str, page: int = 1, limit: int = 20
    ) -> tuple[list[models.Alerta], int]:
        ...

    async def list_alertas_by_parcela(
        self, nombre_parcela: str, page: int = 1, limit: int = 20
    ) -> tuple[list[models.Alerta], int]:
        ...

    # ── Ejecución Batch ───────────────────────────────────────
    async def create_ejecucion_batch(self, fecha_ini: datetime, estado: str = "EN_CURSO") -> models.EjecucionBatch:
        ...

    async def finalizar_ejecucion_batch(
        self, fecha_ini: datetime, estado: str, fecha_fin: datetime
    ) -> Optional[models.EjecucionBatch]:
        ...

    async def list_ejecuciones_batch(self) -> list[models.EjecucionBatch]:
        ...
