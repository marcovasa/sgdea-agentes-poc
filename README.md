# sgdea-agentes-poc

Repo de prueba de Once06 para validar el **pipeline de desarrollo con agentes en la nube** antes de llevarlo a PROGESDOC. Replica a escala el stack real (FastAPI + React en Cloud Run) con un mini-SGDEA de radicación de PQRSDF y **6 incidencias de QA reales sembradas**.

```
Excel QA ──► issues ──► etiqueta agente:* ──► Gemini CLI / Claude Code (Vertex AI, en GitHub Actions)
                                                    │  (solo lectura, sin credenciales de escritura)
                                                    ▼
                                    parche + verificación independiente
                                                    │
                                                    ▼
                         PR ──► CI (ruff, bandit, pytest, eslint, tsc, vitest, build)
                            ──► preview en Cloud Run con URL propia
                            ──► revisión IA (Gemini)
                            ──► aprobación humana ──► merge ──► dev ──► (aprobación) ──► prod
```

Todo corre en el GCP del cliente con Workload Identity Federation: **sin llaves, sin suscripciones aparte, sin el equipo de nadie**.

---

## Montaje (≈ 60–90 min)

### 0. Requisitos

- `gcloud` autenticado con rol Owner (o equivalente) en el proyecto de prueba (p. ej. `sandboxpgd`).
- `gh` autenticado (`gh auth login`) como admin de la cuenta/organización de GitHub.
- Python 3.12+ local (solo para el script del Excel).

### 1. Crear el repo en GitHub y subir el código

```bash
# Reemplaza @OWNER por tu usuario de GitHub en el archivo de responsables
sed -i 's/@OWNER/@TU_USUARIO/g' .github/CODEOWNERS && git commit -am "chore: responsables del repo"

gh repo create TU_ORG/sgdea-agentes-poc --public --source . --push
```

> **Público o privado:** la protección de rama y los revisores obligatorios de `prod` solo funcionan en repos públicos o en planes GitHub Pro/Team. El repo no contiene secretos (es una demo), así que público está bien para la prueba.

### 2. Preparar GCP

```bash
PROJECT_ID=sandboxpgd REGION=us-central1 GITHUB_REPO=TU_ORG/sgdea-agentes-poc \
  bash scripts/setup_gcp.sh
```

Crea APIs, Artifact Registry, tres cuentas de servicio de mínimo privilegio y la federación de identidad **restringida a este repo**. Deja las variables en `.gcp-vars.env`.

### 3. Habilitar Claude en Vertex AI (manual, 2 min)

Consola GCP → **Vertex AI → Model Garden** → buscar *Claude* → abrir el modelo que usarás (p. ej. Claude Sonnet) → **Habilitar** y aceptar términos. Confirma la región (`us-east5` o `global`) y la cuota. Gemini no requiere este paso.

### 4. GitHub App del agente (recomendado, 5 min)

Sin esta App, los PRs que abre el agente **no disparan el CI** (limitación de GitHub con el token por defecto).

1. GitHub → Settings → Developer settings → **GitHub Apps → New GitHub App**.
2. Nombre: `once06-agente-poc`. Homepage: cualquier URL. **Webhook: desactivado.**
3. Permisos de repositorio: **Contents**, **Issues** y **Pull requests** en *Read and write*.
4. Crear → **Generate a private key** (descarga un `.pem`) → anotar el **App ID**.
5. **Install App** → solo en `sgdea-agentes-poc`.
6. Guardar en el repo:

```bash
gh variable set APP_ID --repo TU_ORG/sgdea-agentes-poc --body "123456"
gh secret set APP_PRIVATE_KEY --repo TU_ORG/sgdea-agentes-poc < ruta/al/archivo.pem
```

*Atajo si hay prisa:* un token fine-grained con Contents y Pull requests (RW) sobre el repo, guardado como secreto `AGENT_PAT`. Funciona, pero los PRs quedan a tu nombre.

### 5. Configurar GitHub

```bash
GITHUB_REPO=TU_ORG/sgdea-agentes-poc REVISOR=TU_USUARIO bash scripts/setup_github.sh
```

Aplica variables, etiquetas, environments (`preview`, `dev`, `prod` con revisor) y protege `main`: PR obligatorio, check `ci-ok`, 1 aprobación de responsable, historia lineal, sin force-push.

### 6. Primer despliegue

```bash
gh workflow run Deploy --repo TU_ORG/sgdea-agentes-poc
```

Crea los servicios `sgdea-poc-api-dev` y `sgdea-poc-web-dev` y queda esperando tu aprobación para `prod`. Valida que dev abre y lista los 5 radicados de demo.

### 7. Cargar las incidencias y soltar los agentes

```bash
pip install openpyxl
python scripts/excel_a_issues.py incidencias/incidencias_qa_demo.xlsx --repo TU_ORG/sgdea-agentes-poc --dry-run
python scripts/excel_a_issues.py incidencias/incidencias_qa_demo.xlsx --repo TU_ORG/sgdea-agentes-poc --agente ambos
```

Cada incidencia queda como issue y, con `agente:ambos`, **Gemini y Claude la resuelven en paralelo** y abren un PR cada uno. Para empezar con una sola, omite `--agente` y pon la etiqueta a mano en el issue que quieras.

---

## Uso diario

| Quiero… | Hago… |
| --- | --- |
| Que un agente resuelva un issue | Etiqueta `agente:gemini`, `agente:claude` o `agente:ambos` |
| Relanzar un agente | Quita y vuelve a poner la etiqueta, o *Actions → Agente → Run workflow* |
| Revisar un PR | Mirar CI, abrir el **preview** (comentario del bot), leer la **revisión IA**, aprobar |
| Pasar a producción | Merge a `main` → dev automático → aprobar el job `prod` en Actions |
| Cambiar reglas para los agentes | PR sobre `AGENTS.md` (solo lo aprueba el responsable) |

## Variables del repo

| Variable | Para qué | Por defecto |
| --- | --- | --- |
| `GCP_PROJECT_ID`, `GCP_REGION` | Proyecto y región de Cloud Run | — |
| `GCP_WIF_PROVIDER` | Proveedor de Workload Identity | — |
| `GCP_DEPLOY_SA` / `GCP_AGENT_SA` / `GCP_RUNTIME_SA` | Identidades de despliegue, agentes y runtime | — |
| `AR_REPO`, `SERVICE_PREFIX` | Nombres de registro y servicios | `sgdea-poc` |
| `GOOGLE_CLOUD_LOCATION`, `GEMINI_MODEL` | Región y modelo de Gemini | `global`, default del CLI |
| `CLOUD_ML_REGION`, `CLAUDE_MODEL` | Región y modelo de Claude en Vertex | `us-east5`, `claude-sonnet-5` |
| `APP_ID` + secreto `APP_PRIVATE_KEY` | GitHub App del agente | — |

## Seguridad

- El agente corre en un job con **permisos de solo lectura** y una cuenta de servicio con un único rol (`aiplatform.user`). No puede hacer push, ni abrir PRs, ni desplegar.
- Un job separado, sin IA, aplica el parche, **rechaza cambios en rutas protegidas** (`.github/`, `scripts/`, Dockerfiles, `AGENTS.md`) y abre el PR.
- El texto de los issues se trata como datos (archivo), nunca se interpola en comandos.
- La federación de identidad solo acepta tokens de **este** repositorio. No existen llaves JSON.
- Nada llega a `main` sin CI verde y aprobación humana; nada llega a `prod` sin una segunda aprobación.

## Problemas frecuentes

| Síntoma | Causa probable |
| --- | --- |
| `Permission 'iam.serviceAccounts.getAccessToken' denied` | La condición de WIF no coincide con el nombre exacto del repo (mayúsculas incluidas) |
| Claude: `404` o `model not found` | Modelo no habilitado en Model Garden o región sin cuota; ajusta `CLOUD_ML_REGION` / `CLAUDE_MODEL` |
| El PR del agente no corre CI | Falta la GitHub App (se usó el token por defecto) |
| `--allow-unauthenticated` falla | Política de la organización GCP que restringe acceso público; usar IAP o quitar la bandera |
| Preview no aparece en PRs de forks | Intencional: los forks no reciben credenciales |
