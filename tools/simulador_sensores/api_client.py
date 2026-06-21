import json
import os
import urllib.request
import urllib.error
import urllib.parse
from dataclasses import dataclass

BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8001")
ADMIN_EMAIL = os.getenv("ADMIN_EMAIL", "test@agtechuns.com")
ADMIN_PASS = os.getenv("ADMIN_PASS", "password123")


@dataclass
class APICampo:
    nombre_campo: str
    descripcion_campo: str = ""


@dataclass
class APIParcela:
    nombre_parcela: str
    nombre_campo: str = ""
    nombre_cultivo: str = ""


@dataclass
class APISensor:
    device_id: str
    nombre_campo: str
    nombre_parcela: str
    tipo: str
    activo: bool
    admin_email: str = ""


class APIClient:
    def __init__(self, base_url: str = BACKEND_URL, email: str = ADMIN_EMAIL, password: str = ADMIN_PASS):
        self.base_url = base_url.rstrip("/")
        self.email = email
        self.password = password
        self.token: str | None = None

    def _request(self, method: str, path: str, body: dict | None = None) -> dict | list:
        url = f"{self.base_url}{path}"
        headers = {"Accept": "application/json"}
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        data = None
        if body is not None:
            data = json.dumps(body).encode("utf-8")
            headers["Content-Type"] = "application/json"
        req = urllib.request.Request(url, data=data, headers=headers, method=method)
        try:
            with urllib.request.urlopen(req, timeout=10) as resp:
                raw = resp.read().decode("utf-8")
                if not raw:
                    return {}
                return json.loads(raw)
        except urllib.error.HTTPError as e:
            body_text = e.read().decode("utf-8", errors="replace")
            raise RuntimeError(f"HTTP {e.code} on {method} {path}: {body_text}") from e

    def authenticate(self):
        resp = self._request("POST", "/auth/login", {
            "emailUsuario": self.email,
            "password": self.password,
        })
        if isinstance(resp, dict):
            self.token = resp.get("accessToken") or resp.get("access_token") or ""
        if not self.token:
            raise RuntimeError(f"Authentication failed: no token in response: {resp}")

    def get_campos(self) -> list[APICampo]:
        raw = self._request("GET", "/api/campos")
        items = raw if isinstance(raw, list) else (raw.get("data", []) if isinstance(raw, dict) else [])
        return [APICampo(nombre_campo=c.get("nombreCampo", ""), descripcion_campo=c.get("descripcionCampo", "")) for c in items]

    def get_parcelas(self, nombre_campo: str) -> list[APIParcela]:
        encoded = urllib.parse.quote(nombre_campo, safe="")
        raw = self._request("GET", f"/api/campos/{encoded}/parcelas")
        items = raw if isinstance(raw, list) else (raw.get("data", []) if isinstance(raw, dict) else [])
        return [APIParcela(nombre_parcela=p.get("nombreParcela", ""), nombre_campo=nombre_campo, nombre_cultivo=p.get("nombreCultivo", "")) for p in items]

    def get_sensores(self) -> list[APISensor]:
        raw = self._request("GET", "/api/sensores")
        items = raw if isinstance(raw, list) else (raw.get("data", []) if isinstance(raw, dict) else [])
        return [APISensor(
            device_id=s.get("deviceId", ""),
            nombre_campo=s.get("nombreCampo", ""),
            nombre_parcela=s.get("nombreParcela", ""),
            tipo=s.get("tipo", ""),
            activo=s.get("activo", False),
            admin_email=s.get("adminEmail", ""),
        ) for s in items]

    def create_sensor(self, device_id: str, nombre_campo: str, nombre_parcela: str, tipo: str = "temperatura_humedad", activo: bool = True) -> dict:
        return self._request("POST", "/api/sensores", {
            "deviceId": device_id,
            "nombreCampo": nombre_campo,
            "nombreParcela": nombre_parcela,
            "tipo": tipo,
            "activo": activo,
        })

    def delete_sensor(self, device_id: str):
        encoded = urllib.parse.quote(device_id, safe="")
        try:
            self._request("DELETE", f"/api/sensores/{encoded}")
        except RuntimeError as e:
            if "HTTP 404" in str(e):
                return
            raise
