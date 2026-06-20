"""Pruebas de componente del API Controller.

Ejercitan el controller de forma AISLADA contra los adaptadores mock:
no requieren PostgreSQL, InfluxDB ni el Security Controller real.
Ejecutar desde la raíz del repo:  pytest -v
"""
import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from api import registrar_api

ADMIN = {"Authorization": "Bearer admin"}
AGRONOMO_C1 = {"Authorization": "Bearer agronomo:c1"}


@pytest.fixture
def client():
    app = FastAPI()
    registrar_api(app)
    return TestClient(app)


# --- Seguridad / RBAC ---
def test_sin_token_devuelve_401(client):
    assert client.get("/campos").status_code == 401


def test_admin_ve_todos_los_campos(client):
    r = client.get("/campos", headers=ADMIN)
    assert r.status_code == 200 and len(r.json()) == 2


def test_agronomo_solo_ve_sus_campos(client):       # RBAC a nivel de recurso
    r = client.get("/campos", headers=AGRONOMO_C1)
    assert r.status_code == 200 and [c["id"] for c in r.json()] == ["c1"]


def test_agronomo_no_puede_crear_campo(client):     # RBAC a nivel de operación
    assert client.post("/campos", headers=AGRONOMO_C1,
                       json={"nombre": "Nuevo"}).status_code == 403


# --- CU-03: alta de parcela + validación de polígono (INT-01) ---
def test_poligono_invalido_devuelve_422(client):
    r = client.post("/parcelas", headers=ADMIN,
                    json={"nombre": "x", "campo_id": "c1", "poligono": [[0, 0], [1, 1]]})
    assert r.status_code == 422


def test_parcela_valida_cierra_el_anillo(client):
    r = client.post("/parcelas", headers=ADMIN, json={
        "nombre": "Lote Z", "campo_id": "c1", "cultivo_id": "cu1",
        "poligono": [[-62.2, -38.7], [-62.1, -38.7], [-62.1, -38.6]]})
    assert r.status_code == 201
    poly = r.json()["poligono"]
    assert poly[0] == poly[-1]


def test_agronomo_no_crea_en_campo_ajeno(client):
    r = client.post("/parcelas", headers=AGRONOMO_C1,
                    json={"nombre": "x", "campo_id": "c2",
                          "poligono": [[0, 0], [1, 0], [1, 1]]})
    assert r.status_code == 403


# --- CU-01 / CU-08 / CU-06 ---
def test_estado_de_parcela_cu01(client):
    r = client.get("/parcelas/p1/estado", headers=ADMIN)
    assert r.status_code == 200 and "ultima_lectura" in r.json()


def test_prediccion_cu08(client):
    r = client.get("/predicciones", params={"parcela_id": "p1"}, headers=ADMIN)
    assert r.status_code == 200 and "ndvi" in r.json()


def test_reporte_cu06(client):
    r = client.get("/reportes", params={"campo_id": "c1"}, headers=ADMIN)
    assert r.status_code == 200 and r.json()["campo_id"] == "c1"


# --- Errores y PER-02 ---
def test_parcela_inexistente_404(client):
    assert client.get("/parcelas/NO_EXISTE", headers=ADMIN).status_code == 404


def test_header_de_rendimiento_per02(client):
    r = client.get("/cultivos", headers=ADMIN)
    assert "x-process-time" in {k.lower() for k in r.headers}
