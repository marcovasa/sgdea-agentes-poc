#!/usr/bin/env bash
# Despliega una imagen en Cloud Run y escribe la URL resultante en stdout.
#
# Uso:
#   scripts/cloudrun_desplegar.sh <servicio> <imagen> <env-vars> [tag]
#
# Sin tag: revisión normal con 100% del tráfico (dev / prod).
# Con tag: revisión SIN tráfico con URL propia https://<tag>---<servicio>... (preview de PR).
#
# Requiere: GCP_REGION, GCP_RUNTIME_SA (cuenta de servicio con la que corre el contenedor).
set -euo pipefail

servicio="$1"
imagen="$2"
env_vars="$3"
tag="${4:-}"

: "${GCP_REGION:?Falta GCP_REGION}"
: "${GCP_RUNTIME_SA:?Falta GCP_RUNTIME_SA}"

comunes=(
  --region "$GCP_REGION"
  --image "$imagen"
  --service-account "$GCP_RUNTIME_SA"
  --set-env-vars "$env_vars"
  --allow-unauthenticated
  --port 8080
  --cpu 1
  --memory 512Mi
  --min-instances 0
  --max-instances 3
  --quiet
)

existe=true
gcloud run services describe "$servicio" --region "$GCP_REGION" --format='value(name)' >/dev/null 2>&1 || existe=false

if [[ -n "$tag" && "$existe" == true ]]; then
  # Preview: la revisión no recibe tráfico; solo responde por su URL con tag.
  gcloud run deploy "$servicio" "${comunes[@]}" --no-traffic --tag "$tag" >&2
else
  # Primer despliegue del servicio (o despliegue normal): recibe el 100% del tráfico.
  gcloud run deploy "$servicio" "${comunes[@]}" ${tag:+--tag "$tag"} >&2
  if [[ -z "$tag" ]]; then
    gcloud run services update-traffic "$servicio" --region "$GCP_REGION" --to-latest --quiet >&2
  fi
fi

url_base=$(gcloud run services describe "$servicio" --region "$GCP_REGION" --format='value(status.url)')
if [[ -n "$tag" ]]; then
  echo "https://${tag}---${url_base#https://}"
else
  echo "$url_base"
fi
