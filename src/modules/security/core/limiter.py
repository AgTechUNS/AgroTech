"""
limiter.py — Instancia compartida de slowapi para rate limiting.

Debe ser el mismo objeto registrado en app.state.limiter (main.py)
y usado en los routers. Crear múltiples instancias desconecta
los decoradores @limiter.limit() del middleware.

Uso en main.py:
    from modules.security.core.limiter import limiter
    app.state.limiter = limiter

Uso en routers:
    from modules.security.core.limiter import limiter
    @limiter.limit("5/minute")
"""

from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
