#!/usr/bin/env bash
# Prueba de humo: espera a que una URL responda 200 (máx. ~2 minutos).
# Uso: scripts/esperar_salud.sh <url>
set -euo pipefail
url="$1"
for intento in $(seq 1 24); do
  codigo=$(curl -s -o /dev/null -w '%{http_code}' "$url" || true)
  if [[ "$codigo" == "200" ]]; then
    echo "OK $url (intento $intento)"
    exit 0
  fi
  echo "Esperando $url → $codigo (intento $intento)"
  sleep 5
done
echo "::error::$url no respondió 200"
exit 1
