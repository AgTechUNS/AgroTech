"""
hashing.py — Hashing y verificación de contraseñas con bcrypt.

Responsabilidades:
  - hash_password()    : genera el hash bcrypt a almacenar en la columna
                         hash_password de la tabla USUARIO (PostgreSQL).
  - verify_password()  : compara texto plano contra hash en cada login.
                         Invocado por auth/service.py → verify_credentials().

Consideraciones de seguridad:
  - bcrypt incorpora salt automático en cada llamada a hash() — no es
    necesario gestionar el salt manualmente.
  - El costo (rounds) determina el tiempo de cómputo. A mayor costo,
    más lento para el atacante en fuerza bruta, pero también más lento
    para el usuario legítimo. 12 es el estándar recomendado en 2024.
  - verify() es resistente a timing attacks por diseño de passlib.
"""

import logging

from passlib.context import CryptContext

logger = logging.getLogger(__name__)

# Rounds = 12: balance entre seguridad y latencia (~250ms en hardware moderno).
# Incrementar a 13-14 en producción si el hardware lo permite sin degradar UX.
_pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
    bcrypt__rounds=12,
)


def hash_password(plain_password: str) -> str:
    """
    Genera el hash bcrypt de una contraseña en texto plano.

    El resultado se almacena en la columna hash_password de la tabla
    USUARIO. Cada llamada produce un hash distinto aunque la contraseña
    sea la misma (salt aleatorio incluido automáticamente).

    Parámetros
    ----------
    plain_password : contraseña en texto plano ingresada por el usuario.

    Retorna
    -------
    Hash bcrypt listo para persistir en PostgreSQL.

    Ejemplo
    -------
    >>> hashed = hash_password("mi_clave_segura")
    >>> hashed.startswith("$2b$")
    True
    """
    if not plain_password:
        raise ValueError("La contraseña no puede estar vacía.")

    return _pwd_context.hash(plain_password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verifica si una contraseña en texto plano coincide con su hash bcrypt.

    Invocada en cada intento de login por auth/service.py.
    Usa comparación en tiempo constante para evitar timing attacks.

    Parámetros
    ----------
    plain_password   : contraseña ingresada por el usuario en el login.
    hashed_password  : hash almacenado en la columna hash_password del USUARIO.

    Retorna
    -------
    True si coinciden, False en caso contrario.

    Nota de seguridad
    -----------------
    Esta función NUNCA debe lanzar excepción por credenciales inválidas —
    solo retorna False. La excepción (InvalidCredentialsException) es
    responsabilidad de auth/service.py, para no exponer en qué paso
    falló la autenticación.
    """
    if not plain_password or not hashed_password:
        return False

    try:
        return _pwd_context.verify(plain_password, hashed_password)
    except Exception:
        # Hash malformado u otro error interno — tratamos como fallo silencioso.
        # Logueamos para monitoreo pero no propagamos detalles al caller.
        logger.warning("verify_password: error al verificar hash — posible hash malformado.")
        return False


def needs_rehash(hashed_password: str) -> bool:
    """
    Determina si un hash existente debe ser regenerado.

    passlib detecta automáticamente si el hash fue generado con un costo
    inferior al configurado actualmente (bcrypt__rounds). Útil para
    migración progresiva: al hacer login exitoso, si needs_rehash() es True,
    regenerar y persistir el nuevo hash sin interrumpir al usuario.

    Parámetros
    ----------
    hashed_password : hash almacenado en la base de datos.

    Retorna
    -------
    True si el hash debe actualizarse, False si está al día.

    Uso en auth/service.py
    ----------------------
    if verify_password(plain, stored_hash) and needs_rehash(stored_hash):
        user.hash_password = hash_password(plain)
        await db.commit()
    """
    return _pwd_context.needs_update(hashed_password)
