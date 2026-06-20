"""initial schema

Revision ID: 0001
Revises:
Create Date: 2026-06-18 16:30:00.000000

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "0001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ── Entidades Independientes ──────────────────────────────

    op.create_table(
        "usuario",
        sa.Column("email_usuario", sa.String(255), primary_key=True),
        sa.Column("nombre", sa.String(255), nullable=False),
        sa.Column("telefono", sa.String(50), nullable=True),
        sa.Column("hash_password", sa.String(255), nullable=False),
    )

    op.create_table(
        "campo",
        sa.Column("nombre_campo", sa.String(255), primary_key=True),
        sa.Column("coordenadas_campo", sa.Text, nullable=False),
        sa.Column("descripcion_campo", sa.Text, nullable=True),
    )

    op.create_table(
        "rol",
        sa.Column("nombre_rol", sa.String(100), primary_key=True),
        sa.Column("descripcion", sa.Text, nullable=True),
    )

    op.create_table(
        "cultivo",
        sa.Column("nombre_cultivo", sa.String(255), primary_key=True),
        sa.Column("variedad", sa.String(255), nullable=True),
    )

    op.create_table(
        "sensor",
        sa.Column("nombre_codigo_sensor", sa.String(255), primary_key=True),
        sa.Column("estado", sa.Boolean, default=True, nullable=False),
    )

    op.create_table(
        "imagen_satelital",
        sa.Column("id_imagen", sa.String(255), primary_key=True),
        sa.Column("fecha_captura", sa.DateTime(timezone=True), nullable=False),
        sa.Column("proveedor", sa.String(255), nullable=False),
    )

    op.create_table(
        "ejecucion_batch",
        sa.Column("fecha_ini", sa.DateTime(timezone=True), primary_key=True),
        sa.Column("estado", sa.String(50), nullable=False),
        sa.Column("fecha_fin", sa.DateTime(timezone=True), nullable=True),
    )

    # ── Entidades Dependientes ────────────────────────────────

    op.create_table(
        "parcela",
        sa.Column("nombre_parcela", sa.String(255), primary_key=True),
        sa.Column("coordenadas_parcela", sa.Text, nullable=False),
        sa.Column("descripcion_parcela", sa.Text, nullable=True),
        sa.Column("nombre_campo", sa.String(255), sa.ForeignKey("campo.nombre_campo"), nullable=False),
    )

    op.create_table(
        "regla",
        sa.Column("nombre_regla", sa.String(255), primary_key=True),
        sa.Column("nombre_campo", sa.String(255), primary_key=True),
        sa.Column("formula", sa.Text, nullable=False),
        sa.Column("descripcion_regla", sa.Text, nullable=True),
        sa.Column("umbral", sa.Float, nullable=False),
        sa.ForeignKeyConstraint(["nombre_campo"], ["campo.nombre_campo"]),
    )

    op.create_table(
        "ventana_temporal",
        sa.Column("fecha_ini", sa.DateTime(timezone=True), primary_key=True),
        sa.Column("fecha_fin", sa.DateTime(timezone=True), primary_key=True),
        sa.Column("nombre_parcela", sa.String(255), sa.ForeignKey("parcela.nombre_parcela"), nullable=False),
    )

    op.create_table(
        "alerta",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("fecha_emision", sa.DateTime(timezone=True), nullable=False),
        sa.Column("mensaje", sa.Text, nullable=False),
        sa.Column("nombre_parcela", sa.String(255), sa.ForeignKey("parcela.nombre_parcela"), nullable=False),
        sa.Column("email_usuario", sa.String(255), sa.ForeignKey("usuario.email_usuario"), nullable=False),
    )

    # ── Asociaciones (M:N) ────────────────────────────────────

    op.create_table(
        "usuario_rol_campo",
        sa.Column("email_usuario", sa.String(255), sa.ForeignKey("usuario.email_usuario"), primary_key=True),
        sa.Column("nombre_rol", sa.String(100), sa.ForeignKey("rol.nombre_rol"), primary_key=True),
        sa.Column("nombre_campo", sa.String(255), sa.ForeignKey("campo.nombre_campo"), primary_key=True),
    )

    op.create_table(
        "parcela_imagen_satelital",
        sa.Column("id_imagen", sa.String(255), sa.ForeignKey("imagen_satelital.id_imagen"), primary_key=True),
        sa.Column("nombre_parcela", sa.String(255), sa.ForeignKey("parcela.nombre_parcela"), primary_key=True),
        sa.Column("indice_ndvi", sa.Float, nullable=True),
        sa.Column("indice_ndmi", sa.Float, nullable=True),
    )

    op.create_table(
        "registro_cultivo",
        sa.Column("nombre_parcela", sa.String(255), sa.ForeignKey("parcela.nombre_parcela"), primary_key=True),
        sa.Column("nombre_cultivo", sa.String(255), sa.ForeignKey("cultivo.nombre_cultivo"), primary_key=True),
        sa.Column("fecha_siembra", sa.DateTime(timezone=True), primary_key=True),
        sa.Column("fecha_cosecha", sa.DateTime(timezone=True), nullable=True),
    )

    op.create_table(
        "sensor_parcela",
        sa.Column("nombre_codigo_sensor", sa.String(255), sa.ForeignKey("sensor.nombre_codigo_sensor"), primary_key=True),
        sa.Column("nombre_parcela", sa.String(255), sa.ForeignKey("parcela.nombre_parcela"), primary_key=True),
        sa.Column("nombre_campo", sa.String(255), sa.ForeignKey("campo.nombre_campo"), nullable=False),
        sa.Column("fecha_instalacion", sa.DateTime(timezone=True), primary_key=True),
        sa.Column("fecha_retiro", sa.DateTime(timezone=True), nullable=True),
    )

    op.create_table(
        "prediccion",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("fecha_emision", sa.DateTime(timezone=True), nullable=False),
        sa.Column("resultado", sa.Text, nullable=False),
        sa.Column("fecha_ini", sa.DateTime(timezone=True), nullable=False),
        sa.Column("fecha_fin", sa.DateTime(timezone=True), nullable=False),
        sa.Column("nombre_regla", sa.String(255), nullable=False),
        sa.Column("nombre_campo", sa.String(255), nullable=False),
        sa.ForeignKeyConstraint(
            ["nombre_regla", "nombre_campo"],
            ["regla.nombre_regla", "regla.nombre_campo"],
        ),
        sa.ForeignKeyConstraint(
            ["fecha_ini", "fecha_fin"],
            ["ventana_temporal.fecha_ini", "ventana_temporal.fecha_fin"],
        ),
    )


def downgrade() -> None:
    op.drop_table("prediccion")
    op.drop_table("sensor_parcela")
    op.drop_table("registro_cultivo")
    op.drop_table("parcela_imagen_satelital")
    op.drop_table("usuario_rol_campo")
    op.drop_table("alerta")
    op.drop_table("ventana_temporal")
    op.drop_table("regla")
    op.drop_table("parcela")
    op.drop_table("ejecucion_batch")
    op.drop_table("imagen_satelital")
    op.drop_table("sensor")
    op.drop_table("cultivo")
    op.drop_table("rol")
    op.drop_table("campo")
    op.drop_table("usuario")
