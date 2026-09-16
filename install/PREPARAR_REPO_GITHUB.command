#!/bin/zsh
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$SCRIPT_DIR"
echo "ABRXOS · preparar repo GitHub"
echo "Ruta: $SCRIPT_DIR"
if [[ ! -d .git ]]; then
  git init
fi
git status --short
echo
echo "No se hizo push automático."
echo "Siguiente paso recomendado:"
echo '  git add .'
echo '  git commit -m "Initial ABRXOS Builders V1 + Canon R6"'
echo '  gh repo create ABRXOS-builders-r6 --private --source=. --remote=origin --push'
