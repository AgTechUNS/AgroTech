# AgTechUNS — Auth Service

## Instalación

```bash
# 1. Clonar el repositorio
git clone <url-del-repo>
cd AgroTech

# 2. Crear y activar el entorno virtual
python -m venv venv

# Windows
venv\Scripts\activate

# Linux / macOS
source venv/bin/activate

# 3. Instalar dependencias
pip install -r requirements.txt

# 4. Configurar variables de entorno
cp .env.example .env
# Editá .env con tus valores
```

## Configuración

Copiá `.env.example` a `.env` y completá los valores. Las variables mínimas para desarrollo son `SECRET_KEY` y `DATABASE_URL`.

Para producción, la `SECRET_KEY` se obtiene desde HashiCorp Vault — no debe estar en `.env`.

## Ejecución

```bash
uvicorn main:app --reload --port 8000
```

La documentación interactiva queda disponible en `http://localhost:8000/docs`.

---

## Usuario de prueba

Creado automáticamente al iniciar la aplicación (`startup` en `main.py`).

| Campo          | Valor                    |
| -------------- | ------------------------ |
| Email          | `agronomo@agtech.com`    |
| Contraseña     | `password123`            |
| Rol            | `agronomo`               |
| Campo asignado | UUID generado en startup |

### Ejemplo de login

```bash
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"emailUsuario": "agronomo@agtech.com", "password": "password123"}'
```

### Ejemplo de refresh

```bash
curl -X POST http://localhost:8000/auth/refresh \
  -H "Content-Type: application/json" \
  -d '{"refreshToken": "<refresh_token_del_login>"}'
```
