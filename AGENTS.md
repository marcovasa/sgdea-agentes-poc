# AGENTS.md — Reglas del proyecto para agentes de código

Este archivo es el contexto único que leen **todos** los agentes (Gemini CLI, Claude Code, Antigravity, Jules) y las personas. `GEMINI.md` y `CLAUDE.md` solo apuntan aquí. Si una regla cambia, se cambia aquí, por PR.

## Qué es este proyecto

Mini-SGDEA: módulo de **radicación de PQRSDF** (peticiones, quejas, reclamos, sugerencias, denuncias, consultas y solicitudes de información) según la Ley 1755 de 2015. Es el repo de prueba del pipeline de desarrollo con agentes de Once06; replica a escala el stack de PROGESDOC.

## Stack

- **Backend** (`backend/`): Python 3.12, FastAPI, SQLAlchemy 2.0, Pydantic v2. Tests con pytest. Lint con ruff, seguridad con bandit.
- **Frontend** (`frontend/`): React 19 + TypeScript + Vite. Tests con Vitest + Testing Library. Lint con ESLint.
- **Infra**: Cloud Run (un servicio para API y otro para web), Artifact Registry, GitHub Actions con Workload Identity Federation. Sin llaves en el repo.

## Mapa del código

| Ruta | Qué hay |
| --- | --- |
| `backend/app/models.py` | Modelos SQLAlchemy y enums (`TipoPQRSDF`, `EstadoRadicado`) |
| `backend/app/schemas.py` | Contratos de entrada/salida (Pydantic) |
| `backend/app/services/radicacion.py` | Reglas de negocio: número de radicado, búsqueda, creación |
| `backend/app/services/plazos.py` | Cálculo de fecha de vencimiento por tipo |
| `backend/app/routers/radicados.py` | Endpoints `/api/radicados` |
| `frontend/src/App.tsx` | Pantalla de radicación y listado |
| `frontend/src/api.ts` | Cliente HTTP del front |

## Comandos (córrelos antes de terminar)

```bash
# Backend
cd backend && pip install -r requirements-dev.txt
ruff check . && ruff format --check .
bandit -q -c pyproject.toml -r app
pytest

# Frontend
cd frontend && npm ci
npm run lint && npm run typecheck && npm test && npm run build
```

## Reglas de trabajo (obligatorias)

1. **Alcance**: resuelve solo lo que pide el issue. No refactorices, no renombres, no "mejores" código que no está en el alcance.
2. **Tests primero**: todo arreglo de bug lleva un test que falla sin el arreglo y pasa con él. Toda funcionalidad nueva lleva tests de los criterios de aceptación.
3. **No rompas lo que funciona**: los tests existentes deben seguir pasando. Si un test existente contradice el issue, explícalo en el resumen; no lo borres.
4. **Rutas prohibidas**: no modifiques `.github/`, `scripts/`, `Dockerfile`, `nginx.conf`, `AGENTS.md`, `GEMINI.md`, `CLAUDE.md` ni `.gitignore`. El pipeline rechaza el PR si las tocas.
5. **Dependencias**: no agregues librerías nuevas salvo que el issue lo pida explícitamente.
6. **Contratos**: si cambias un campo de la API, actualiza `schemas.py` y `frontend/src/types.ts` en el mismo cambio.
7. **Idioma**: nombres de dominio, mensajes al usuario y comentarios en español. Mensajes de error de la API en español.
8. **Datos sensibles**: nunca escribas credenciales, tokens ni datos personales reales en código o tests. Usa datos ficticios.
9. **Resumen final**: al terminar, escribe en `.agent/resumen.md` qué cambiaste, por qué, qué tests agregaste y cualquier duda o supuesto. Ese texto va al cuerpo del PR.

## Dominio — reglas de negocio vigentes

- Número de radicado: `AAAA-<prefijo>-<consecutivo>`; prefijo por tipo: P, Q, R, S, D, C, I. Consecutivo anual por tipo.
- Plazos de respuesta (Ley 1755/2015): petición, queja, reclamo, sugerencia y denuncia 15 días; consulta 30 días; información/documentos 10 días.
- Estados: `RADICADO` → `EN_TRAMITE` → `RESPONDIDO`.

## Criterios de revisión de PR

Un PR se aprueba si: cumple los criterios de aceptación del issue, trae tests, el CI está verde, el preview funciona, y el diff es mínimo y legible.
