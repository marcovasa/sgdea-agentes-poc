#!/usr/bin/env bash
# Prepara el proyecto GCP para el pipeline (idempotente: se puede correr varias veces).
#
# Uso:
#   PROJECT_ID=sandboxpgd REGION=us-central1 GITHUB_REPO=org/sgdea-agentes-poc bash scripts/setup_gcp.sh
#
# Crea:
#   - APIs: Cloud Run, Artifact Registry, IAM Credentials, STS, Vertex AI
#   - Artifact Registry "sgdea-poc"
#   - 3 cuentas de servicio con mínimo privilegio:
#       sgdea-poc-deploy  → despliega en Cloud Run y publica imágenes
#       sgdea-poc-agente  → SOLO invoca modelos en Vertex AI (Gemini y Claude)
#       sgdea-poc-run     → identidad con la que corren los contenedores (sin roles)
#   - Workload Identity Federation: GitHub Actions de ESE repo (y solo ese) obtiene
#     credenciales de corta duración. No se crean llaves JSON.
set -euo pipefail

: "${PROJECT_ID:?Define PROJECT_ID}"
: "${REGION:=us-central1}"
: "${GITHUB_REPO:?Define GITHUB_REPO como owner/repo}"
AR_REPO="${AR_REPO:-sgdea-poc}"
POOL="${POOL:-github-pool}"
PROVIDER="${PROVIDER:-github}"

gcloud config set project "$PROJECT_ID" >/dev/null
NUMERO=$(gcloud projects describe "$PROJECT_ID" --format='value(projectNumber)')

echo "==> Habilitando APIs"
gcloud services enable \
  run.googleapis.com artifactregistry.googleapis.com iam.googleapis.com \
  iamcredentials.googleapis.com sts.googleapis.com aiplatform.googleapis.com \
  cloudresourcemanager.googleapis.com

echo "==> Artifact Registry"
gcloud artifacts repositories describe "$AR_REPO" --location "$REGION" >/dev/null 2>&1 || \
  gcloud artifacts repositories create "$AR_REPO" --repository-format docker --location "$REGION" \
    --description "Imágenes del repo de prueba del pipeline con agentes"

crear_sa() {
  local id="$1" nombre="$2"
  gcloud iam service-accounts describe "${id}@${PROJECT_ID}.iam.gserviceaccount.com" >/dev/null 2>&1 || \
    gcloud iam service-accounts create "$id" --display-name "$nombre"
}

echo "==> Cuentas de servicio"
crear_sa sgdea-poc-deploy "Pipeline: despliegue Cloud Run"
crear_sa sgdea-poc-agente "Pipeline: agentes IA (Vertex AI)"
crear_sa sgdea-poc-run    "Runtime de los servicios Cloud Run"

SA_DEPLOY="sgdea-poc-deploy@${PROJECT_ID}.iam.gserviceaccount.com"
SA_AGENTE="sgdea-poc-agente@${PROJECT_ID}.iam.gserviceaccount.com"
SA_RUN="sgdea-poc-run@${PROJECT_ID}.iam.gserviceaccount.com"

echo "==> Roles (mínimo privilegio)"
gcloud projects add-iam-policy-binding "$PROJECT_ID" --member "serviceAccount:${SA_DEPLOY}" \
  --role roles/run.admin --condition=None >/dev/null
gcloud artifacts repositories add-iam-policy-binding "$AR_REPO" --location "$REGION" \
  --member "serviceAccount:${SA_DEPLOY}" --role roles/artifactregistry.writer >/dev/null
gcloud iam service-accounts add-iam-policy-binding "$SA_RUN" \
  --member "serviceAccount:${SA_DEPLOY}" --role roles/iam.serviceAccountUser >/dev/null
gcloud projects add-iam-policy-binding "$PROJECT_ID" --member "serviceAccount:${SA_AGENTE}" \
  --role roles/aiplatform.user --condition=None >/dev/null

echo "==> Workload Identity Federation (solo el repo ${GITHUB_REPO})"
gcloud iam workload-identity-pools describe "$POOL" --location global >/dev/null 2>&1 || \
  gcloud iam workload-identity-pools create "$POOL" --location global --display-name "GitHub Actions"

gcloud iam workload-identity-pools providers describe "$PROVIDER" --location global \
  --workload-identity-pool "$POOL" >/dev/null 2>&1 || \
  gcloud iam workload-identity-pools providers create-oidc "$PROVIDER" \
    --location global --workload-identity-pool "$POOL" \
    --display-name "GitHub OIDC" \
    --issuer-uri "https://token.actions.githubusercontent.com" \
    --attribute-mapping "google.subject=assertion.sub,attribute.repository=assertion.repository,attribute.repository_owner=assertion.repository_owner,attribute.ref=assertion.ref" \
    --attribute-condition "assertion.repository == '${GITHUB_REPO}'"

PRINCIPAL="principalSet://iam.googleapis.com/projects/${NUMERO}/locations/global/workloadIdentityPools/${POOL}/attribute.repository/${GITHUB_REPO}"
for sa in "$SA_DEPLOY" "$SA_AGENTE"; do
  gcloud iam service-accounts add-iam-policy-binding "$sa" \
    --member "$PRINCIPAL" --role roles/iam.workloadIdentityUser >/dev/null
done

WIF_PROVIDER="projects/${NUMERO}/locations/global/workloadIdentityPools/${POOL}/providers/${PROVIDER}"

cat <<EOF

✅ GCP listo. Variables para GitHub (las aplica scripts/setup_github.sh):

  GCP_PROJECT_ID   = ${PROJECT_ID}
  GCP_REGION       = ${REGION}
  GCP_WIF_PROVIDER = ${WIF_PROVIDER}
  GCP_DEPLOY_SA    = ${SA_DEPLOY}
  GCP_AGENT_SA     = ${SA_AGENTE}
  GCP_RUNTIME_SA   = ${SA_RUN}
  AR_REPO          = ${AR_REPO}

⚠️  Paso manual pendiente: habilitar los modelos de Claude en Vertex AI Model Garden
    (consola → Vertex AI → Model Garden → Claude → Habilitar / aceptar términos) y
    confirmar cuota en la región que usarás (CLOUD_ML_REGION, p. ej. us-east5 o global).
EOF

# Archivo para setup_github.sh
cat > .gcp-vars.env <<EOF
GCP_PROJECT_ID=${PROJECT_ID}
GCP_REGION=${REGION}
GCP_WIF_PROVIDER=${WIF_PROVIDER}
GCP_DEPLOY_SA=${SA_DEPLOY}
GCP_AGENT_SA=${SA_AGENTE}
GCP_RUNTIME_SA=${SA_RUN}
AR_REPO=${AR_REPO}
EOF
echo "Variables guardadas en .gcp-vars.env (no se versiona)."
