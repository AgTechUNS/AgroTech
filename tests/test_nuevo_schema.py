import asyncio
import os
import sys
from datetime import datetime, timezone
from dotenv import load_dotenv
from sqlalchemy import text

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))

from infrastructure.relational_repo.database import Database
from infrastructure.relational_repo.repository import RelationalRepository


async def main():
    dsn = os.getenv("DATABASE_DSN", "postgresql+asyncpg://postgres:postgres@localhost:5432/agrotech")
    print(f"[INFO] Conectando a: {dsn.split('@')[0].split(':')[0] + ':****@' + dsn.split('@')[1] if '@' in dsn else dsn}")

    db = Database(dsn=dsn, echo=False)
    await db.create_tables()
    repo = RelationalRepository(db.session_factory)

    # ── Cleanup total (orden inverso por FKs) ───────────────────
    async with db.session() as session:
        for t in ["prediccion", "alerta", "parcela_imagen_satelital",
                   "sensor_parcela", "registro_cultivo", "ventana_temporal",
                   "usuario_rol_campo", "regla", "parcela",
                   "imagen_satelital", "sensor", "cultivo", "campo",
                   "rol", "usuario", "ejecucion_batch"]:
            await session.execute(text(f"DELETE FROM {t}"))
    print("[OK] Limpieza")

    # ════════════════════════════════════════════════════════════
    # 1. Entidades independientes
    # ════════════════════════════════════════════════════════════

    # -- Usuario --
    u = await repo.create_usuario(email="test@test.com", nombre="Test User", hash_password="abc123")
    assert u.email_usuario == "test@test.com"
    u2 = await repo.get_usuario_by_email("test@test.com")
    assert u2 is not None and u2.nombre == "Test User"
    usuarios = await repo.list_usuarios()
    assert len(usuarios) == 1
    print("[OK] Usuario: crear, obtener, listar")

    # -- Rol --
    r = await repo.create_rol("ADMIN", "Administrador del sistema")
    assert r.nombre_rol == "ADMIN"
    roles = await repo.list_roles()
    assert len(roles) == 1
    print("[OK] Rol: crear, listar")

    # -- Campo --
    c = await repo.create_campo("Campo Test", '{"type":"Point","coordinates":[-62.5,-38.0]}', "Campo de prueba")
    assert c.nombre_campo == "Campo Test"
    c2 = await repo.get_campo_by_nombre("Campo Test")
    assert c2 is not None
    campos = await repo.list_campos()
    assert len(campos) == 1
    print("[OK] Campo: crear, obtener, listar")

    # -- Cultivo --
    cv = await repo.create_cultivo("Trigo", "variedad INTA")
    assert cv.nombre_cultivo == "Trigo"
    cv2 = await repo.get_cultivo_by_nombre("Trigo")
    assert cv2 is not None and cv2.variedad == "variedad INTA"
    cultivos = await repo.list_cultivos()
    assert len(cultivos) == 1
    print("[OK] Cultivo: crear, obtener, listar")

    # -- Sensor --
    s = await repo.create_sensor("SENSOR-001", estado=True)
    assert s.nombre_codigo_sensor == "SENSOR-001"
    s2 = await repo.get_sensor("SENSOR-001")
    assert s2 is not None and s2.estado is True
    sensores = await repo.list_sensores()
    assert len(sensores) == 1
    print("[OK] Sensor: crear, obtener, listar")

    # -- Imagen Satelital --
    now = datetime.now(timezone.utc)
    img = await repo.create_imagen_satelital("S2-2025-001", now, "Sentinel-2")
    assert img.id_imagen == "S2-2025-001"
    imagenes = await repo.list_imagenes()
    assert len(imagenes) == 1
    print("[OK] ImagenSatelital: crear, listar")

    # ════════════════════════════════════════════════════════════
    # 2. Entidades dependientes
    # ════════════════════════════════════════════════════════════

    # -- Parcela (depende de Campo) --
    p = await repo.create_parcela("Lote A", '{"type":"Polygon","coordinates":[]}', "Campo Test", "Lote de prueba")
    assert p.nombre_parcela == "Lote A"
    p2 = await repo.get_parcela_by_nombre("Lote A")
    assert p2 is not None
    parcelas = await repo.list_parcelas_by_campo("Campo Test")
    assert len(parcelas) == 1
    print("[OK] Parcela: crear, obtener, listar por campo")

    # -- Regla (PK compuesta: nombre_regla + nombre_campo) --
    reg = await repo.create_regla("R1", "Campo Test", "temperatura > {umbral}", 38.0, "Alerta de calor")
    assert reg.nombre_regla == "R1" and reg.nombre_campo == "Campo Test"
    reglas = await repo.list_reglas()
    assert len(reglas) == 1
    reglas_campo = await repo.list_reglas_by_campo("Campo Test")
    assert len(reglas_campo) == 1
    print("[OK] Regla: crear, listar, listar por campo")

    # -- Ventana Temporal (PK compuesta: fecha_ini + fecha_fin) --
    vfuturo = datetime(2026, 7, 1, tzinfo=timezone.utc)
    vt = await repo.create_ventana_temporal(now, vfuturo, "Lote A")
    assert vt.fecha_ini == now
    ventanas = await repo.list_ventanas_by_parcela("Lote A")
    assert len(ventanas) == 1
    print("[OK] VentanaTemporal: crear, listar por parcela")

    # ════════════════════════════════════════════════════════════
    # 3. Asociaciones M:N
    # ════════════════════════════════════════════════════════════

    # -- UsuarioRolCampo --
    urc = await repo.assign_rol_to_usuario("test@test.com", "ADMIN", "Campo Test")
    assert urc.email_usuario == "test@test.com"
    roles_user = await repo.list_roles_by_usuario("test@test.com")
    assert len(roles_user) == 1
    print("[OK] UsuarioRolCampo: asignar, listar por usuario")

    # -- SensorParcela --
    sp = await repo.instalar_sensor_en_parcela("SENSOR-001", "Lote A", "Campo Test", now)
    assert sp.nombre_codigo_sensor == "SENSOR-001"
    sensores_parcela = await repo.list_sensores_by_parcela("Lote A")
    assert len(sensores_parcela) == 1
    # Retirar sensor
    sp_ret = await repo.retirar_sensor_de_parcela("SENSOR-001", "Lote A", now, datetime.now(timezone.utc))
    assert sp_ret is not None and sp_ret.fecha_retiro is not None
    print("[OK] SensorParcela: instalar, listar, retirar")

    # -- ParcelaImagenSatelital --
    pis = await repo.asociar_imagen_a_parcela("S2-2025-001", "Lote A", ndvi=0.75, ndmi=0.45)
    assert pis.indice_ndvi == 0.75
    imagenes_parcela = await repo.get_imagenes_by_parcela("Lote A")
    assert len(imagenes_parcela) == 1
    print("[OK] ParcelaImagenSatelital: asociar, listar por parcela")

    # -- RegistroCultivo (siembra + cosecha) --
    rc = await repo.registrar_siembra("Lote A", "Trigo", now)
    assert rc.nombre_parcela == "Lote A"
    historial = await repo.get_historial_cultivos("Lote A")
    assert len(historial) == 1
    # Cosechar
    rc2 = await repo.registrar_cosecha("Lote A", "Trigo", now, vfuturo)
    assert rc2 is not None and rc2.fecha_cosecha == vfuturo
    print("[OK] RegistroCultivo: siembra, cosecha, historial")

    # ════════════════════════════════════════════════════════════
    # 4. Entidades complejas
    # ════════════════════════════════════════════════════════════

    # -- Prediccion (FK compuesta a Regla + VentanaTemporal) --
    pred = await repo.create_prediccion(now, "Clima estable", now, vfuturo, "R1", "Campo Test")
    assert pred.id is not None
    preds, total = await repo.list_predicciones_by_campo("Campo Test")
    assert total == 1
    assert len(preds) == 1
    print("[OK] Prediccion: crear, listar por campo con paginacion")

    # -- Alerta (FK a Parcela + Usuario) --
    al = await repo.create_alerta(now, "Humedad baja detectada", "Lote A", "test@test.com")
    assert al.id is not None
    alertas_user, total_u = await repo.list_alertas_by_usuario("test@test.com")
    assert total_u == 1
    alertas_parcela, total_p = await repo.list_alertas_by_parcela("Lote A")
    assert total_p == 1
    print("[OK] Alerta: crear, listar por usuario y parcela")

    # -- EjecucionBatch --
    eb = await repo.create_ejecucion_batch(now)
    assert eb.estado == "EN_CURSO"
    eb2 = await repo.finalizar_ejecucion_batch(now, "COMPLETADO", vfuturo)
    assert eb2 is not None and eb2.estado == "COMPLETADO"
    batches = await repo.list_ejecuciones_batch()
    assert len(batches) == 1
    print("[OK] EjecucionBatch: crear, finalizar, listar")

    print("\n==> Todos los tests pasaron <==")
    await db.close()


if __name__ == "__main__":
    asyncio.run(main())
