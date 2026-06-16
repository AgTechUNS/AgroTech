import uuid

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from sqlalchemy import select

from auth.dependencies import _engine, _SessionLocal
from auth.models import Base, Usuario, UsuarioRolCampo
from auth.router import limiter, router as auth_router
from core.config import get_settings
from core.enums import RoleEnum
from core.exceptions import register_exception_handlers
from core.hashing import hash_password

settings = get_settings()

app = FastAPI(
    title="AgTechUNS — Auth Service",
    description=(
        "Servicio de autenticación y seguridad de AgTechUNS. "
        "Gestiona identidad (Sign In, Reset Password) "
        "e infraestructura de protección (JWT, RBAC)."
    ),
    version="1.0.0",
    docs_url="/docs" if settings.ENVIRONMENT == "development" else None,
    redoc_url="/redoc" if settings.ENVIRONMENT == "development" else None,
)

# ── CORS primero — debe envolver todo lo demás ─
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # solo la SPA en dev
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Rate limiting ──────────────────────────────
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(SlowAPIMiddleware)

# ── Exception handlers globales ────────────────
register_exception_handlers(app)

# ── Routers ────────────────────────────────────
app.include_router(auth_router)


@app.on_event("startup")
async def create_tables():
    async with _engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with _SessionLocal() as db:
        result = await db.execute(
            select(Usuario).where(Usuario.email_usuario == "agronomo@agtech.com")
        )
        if result.scalar_one_or_none() is None:
            usuario = Usuario(
                email_usuario="agronomo@agtech.com",
                nombre="Juan Agrónomo",
                telefono="1234567890",
                hash_password=hash_password("password123"),
            )
            campo_id = uuid.uuid4()
            rol = UsuarioRolCampo(
                email_usuario="agronomo@agtech.com",
                rol=RoleEnum.AGRONOMO,
                campo_id=campo_id,
            )
            db.add(usuario)
            db.add(rol)
            await db.commit()