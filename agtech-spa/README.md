# AgTechUNS SPA

Frontend de la Plataforma de Monitoreo Agrícola Inteligente. Construido con **Next.js 14** (App Router), **React 18** y **TypeScript**.

## Inicio Rápido

```bash
npm install
npm run dev
```

Abrir [http://localhost:3000](http://localhost:3000).

## Login

| Campo     | Valor                |
|-----------|----------------------|
| Email     | `test@agtechuns.com` |
| Password  | `12345678`           |

Mock auth habilitado via `NEXT_PUBLIC_MOCK_AUTH=true` en `.env.local`.

## Módulos Implementados

| Módulo    | Rutas                                     | Descripción                                    |
|-----------|-------------------------------------------|------------------------------------------------|
| Campos    | `/campos`, `/campos/crear`, `/campos/[nombreCampo]` | CRUD con dibujo de polígonos en mapa Leaflet |
| Cultivos  | `/cultivos`, `/cultivos/crear`            | Catálogo de cultivos                           |
| Parcelas  | `/campos/[nombreCampo]/parcelas/crear`    | Asociadas a un campo con selección de cultivo |
| Reglas    | `/reglas`, `/reglas/crear`                | Reglas con métrica/operador/valor              |
| Dashboard | `/`                                       | Home con resumen (TODO)                        |

## Arquitectura

```
Página → lib/services/ (fetch) → /api/* (Next.js API Route) → lib/data/store.ts → .data/*.json
```

Las API Routes actúan como **BFF**. Cuando el Relational Repository esté disponible, swichearán a `BACKEND_URL`.

## Persistencia

Los datos se almacenan en archivos JSON bajo `.data/` (gitignored). Se siembran con datos de ejemplo al primer acceso.

## Tecnologías

- **Next.js 14** — App Router, API Routes, SSR
- **React 18** — Server/Client Components
- **Leaflet + react-leaflet** — Mapas (OpenStreetMap, sin API key)
- **leaflet-draw** — Dibujo de polígonos
- **react-hook-form + zod** — Formularios y validación
- **recharts** — Gráficos (dashboard futuro)

## Variables de Entorno

| Variable | Descripción |
|----------|-------------|
| `NEXT_PUBLIC_MOCK_AUTH` | `true` para mock de login |
| `BACKEND_URL` | URL del backend (vacío = usa JSON store) |
