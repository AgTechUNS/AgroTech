import json
import os
import sys
import pathlib
import urllib.request
import urllib.error
import urllib.parse

TOOLS_DIR = pathlib.Path(__file__).parent.resolve()
SPA_DATA_DIR = TOOLS_DIR.parents[0] / ".data"
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8001")
ADMIN_EMAIL = os.getenv("ADMIN_EMAIL", "test@agtechuns.com")
ADMIN_PASS = os.getenv("ADMIN_PASS", "password123")

CAMPOS_FILE = SPA_DATA_DIR / "campos.json"
PARCELAS_FILE = SPA_DATA_DIR / "parcelas.json"

def fetch_json(url: str, token: str | None = None):
    headers = {"Accept": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req, timeout=10) as resp:
        return json.loads(resp.read().decode("utf-8"))

def post_json(url: str, data: dict):
    body = json.dumps(data).encode("utf-8")
    req = urllib.request.Request(url, data=body, headers={
        "Content-Type": "application/json",
        "Accept": "application/json",
    })
    with urllib.request.urlopen(req, timeout=10) as resp:
        return json.loads(resp.read().decode("utf-8"))

def login() -> str:
    try:
        resp = post_json(f"{BACKEND_URL}/auth/login", {
            "emailUsuario": ADMIN_EMAIL,
            "password": ADMIN_PASS,
        })
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8")
        print(f"ERROR: Login failed (HTTP {e.code}): {body}")
        sys.exit(1)
    except urllib.error.URLError as e:
        print(f"ERROR: Could not reach backend at {BACKEND_URL}: {e.reason}")
        sys.exit(1)
    token = resp.get("accessToken") or resp.get("access_token") or resp.get("token") or ""
    if not token:
        print(f"ERROR: No token in login response: {resp}")
        sys.exit(1)
    return token

def sync():
    SPA_DATA_DIR.mkdir(parents=True, exist_ok=True)

    print(f"Logging in as {ADMIN_EMAIL}...")
    token = login()
    print("OK: Authenticated")

    # Fetch campos
    try:
        campos_raw = fetch_json(f"{BACKEND_URL}/api/campos", token)
    except urllib.error.HTTPError as e:
        print(f"ERROR: Backend returned {e.code} for /api/campos")
        sys.exit(1)

    if isinstance(campos_raw, dict) and "data" in campos_raw:
        campos = campos_raw["data"]
    elif isinstance(campos_raw, list):
        campos = campos_raw
    else:
        campos = []

    with open(CAMPOS_FILE, "w") as f:
        json.dump(campos, f, indent=2)
    print(f"OK: {len(campos)} campos exported to {CAMPOS_FILE}")

    all_parcelas = []
    for c in campos:
        nombre = c.get("nombreCampo", "")
        if not nombre:
            continue
        try:
            parcelas_raw = fetch_json(
                f"{BACKEND_URL}/api/campos/{urllib.parse.quote(nombre, safe='')}/parcelas", token
            )
        except urllib.error.HTTPError as e:
            if e.code == 404:
                continue
            print(f"  WARN: could not fetch parcelas for '{nombre}': HTTP {e.code}")
            continue
        except urllib.error.URLError:
            continue

        if isinstance(parcelas_raw, dict) and "data" in parcelas_raw:
            parcelas = parcelas_raw["data"]
        elif isinstance(parcelas_raw, list):
            parcelas = parcelas_raw
        else:
            parcelas = []

        for p in parcelas:
            p["nombreCampo"] = nombre
        all_parcelas.extend(parcelas)
        print(f"  {nombre}: {len(parcelas)} parcelas")

    with open(PARCELAS_FILE, "w") as f:
        json.dump(all_parcelas, f, indent=2)
    print(f"OK: {len(all_parcelas)} parcelas exported to {PARCELAS_FILE}")

if __name__ == "__main__":
    sync()
