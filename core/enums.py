"""
enums.py — Enumeraciones compartidas del sistema AgTechUNS.

Viven en core/ para evitar dependencias circulares:
  - auth/models.py    importa RoleEnum para la columna SQLAlchemy
  - security/roles.py importa RoleEnum para la lógica RBAC

Regla: ningún módulo define sus propios enums de negocio —
todos los importan desde acá.
"""

import enum


class RoleEnum(str, enum.Enum):
    """
    Roles del sistema definidos en el modelo de datos AgTechUNS.

    Hereda de str para que SQLAlchemy, Pydantic y python-jose
    puedan serializarlo directamente como string sin conversión extra.

    Valores:
      ADMINISTRADOR : acceso total al sistema.
      AGRONOMO      : acceso limitado a sus campos asignados.
    """

    ADMINISTRADOR = "administrador"
    AGRONOMO      = "agronomo"