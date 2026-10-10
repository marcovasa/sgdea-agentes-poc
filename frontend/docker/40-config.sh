#!/bin/sh
# Escribe la configuración de runtime del front a partir de variables de entorno de Cloud Run.
set -eu
cat > /usr/share/nginx/html/config.js <<EOF
window.__CONFIG__ = { API_URL: '${API_URL:-}' }
EOF
echo "config.js generado (API_URL=${API_URL:-<vacío>})"
