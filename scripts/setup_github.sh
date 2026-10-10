#!/usr/bin/env bash
# Configura el repo de GitHub: variables, etiquetas, environments y protección de main.
#
# Uso (después de setup_gcp.sh, con gh autenticado como admin del repo):
#   GITHUB_REPO=org/sgdea-agentes-poc REVISOR=tu-usuario bash scripts/setup_github.sh
set -euo pipefail

: "${GITHUB_REPO:?Define GITHUB_REPO como owner/repo}"
: "${REVISOR:?Define REVISOR (usuario de GitHub que aprueba PRs y despliegues a prod)}"
ARCHIVO_VARS="${ARCHIVO_VARS:-.gcp-vars.env}"

echo "==> Variables del repositorio"
if [[ -f "$ARCHIVO_VARS" ]]; then
  while IFS='=' read -r nombre valor; do
    [[ -z "$nombre" || "$nombre" == \#* ]] && continue
    gh variable set "$nombre" --repo "$GITHUB_REPO" --body "$valor"
  done < "$ARCHIVO_VARS"
else
  echo "⚠️  No existe $ARCHIVO_VARS; corre primero scripts/setup_gcp.sh"
fi
gh variable set SERVICE_PREFIX       --repo "$GITHUB_REPO" --body "${SERVICE_PREFIX:-sgdea-poc}"
gh variable set GOOGLE_CLOUD_LOCATION --repo "$GITHUB_REPO" --body "${GOOGLE_CLOUD_LOCATION:-global}"
gh variable set CLOUD_ML_REGION      --repo "$GITHUB_REPO" --body "${CLOUD_ML_REGION:-us-east5}"
gh variable set CLAUDE_MODEL         --repo "$GITHUB_REPO" --body "${CLAUDE_MODEL:-claude-sonnet-5}"
[[ -n "${GEMINI_MODEL:-}" ]] && gh variable set GEMINI_MODEL --repo "$GITHUB_REPO" --body "$GEMINI_MODEL"

echo "==> Etiquetas"
crear_etiqueta() { gh label create "$1" --repo "$GITHUB_REPO" --color "$2" --description "$3" --force >/dev/null; }
crear_etiqueta incidencia    d73a4a "Error reportado por QA o cliente"
crear_etiqueta agente:gemini 1a73e8 "Asignar a Gemini CLI (Vertex AI)"
crear_etiqueta agente:claude d97757 "Asignar a Claude Code (Vertex AI)"
crear_etiqueta agente:ambos  5319e7 "Ambos motores en paralelo (comparación)"
crear_etiqueta agente        5319e7 "PR generado por un agente"
crear_etiqueta motor:gemini  1a73e8 "PR del motor Gemini"
crear_etiqueta motor:claude  d97757 "PR del motor Claude"

echo "==> Environments"
REVISOR_ID=$(gh api "users/${REVISOR}" --jq .id)
gh api -X PUT "repos/${GITHUB_REPO}/environments/preview" >/dev/null
gh api -X PUT "repos/${GITHUB_REPO}/environments/dev" >/dev/null
gh api -X PUT "repos/${GITHUB_REPO}/environments/prod" --input - >/dev/null <<EOF || \
  echo "⚠️  No se pudo poner revisor obligatorio en prod (requiere repo público o plan Team/Enterprise)."
{ "reviewers": [ { "type": "User", "id": ${REVISOR_ID} } ], "deployment_branch_policy": null }
EOF

echo "==> Protección de la rama main"
gh api -X PUT "repos/${GITHUB_REPO}/branches/main/protection" --input - >/dev/null <<'EOF' || \
  echo "⚠️  No se pudo proteger main (en repos privados requiere GitHub Pro/Team)."
{
  "required_status_checks": { "strict": true, "contexts": ["ci-ok"] },
  "enforce_admins": false,
  "required_pull_request_reviews": {
    "required_approving_review_count": 1,
    "dismiss_stale_reviews": true,
    "require_code_owner_reviews": true
  },
  "restrictions": null,
  "required_linear_history": true,
  "allow_force_pushes": false,
  "allow_deletions": false,
  "required_conversation_resolution": true
}
EOF

echo "==> Merge solo por squash y borrado automático de ramas"
gh api -X PATCH "repos/${GITHUB_REPO}" \
  -F allow_squash_merge=true -F allow_merge_commit=false -F allow_rebase_merge=false \
  -F delete_branch_on_merge=true >/dev/null

cat <<EOF

✅ GitHub listo.
Pendiente (recomendado): crear la GitHub App "agente" y guardar APP_ID (variable) y
APP_PRIVATE_KEY (secreto). Sin ella, los PRs que abre el agente NO disparan el CI.
Ver README → "GitHub App del agente".
EOF
