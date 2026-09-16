#!/bin/zsh
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
echo "Instalando ABRXOS X Brand Builder V1..."
/bin/zsh "$ROOT/apps/brand-builder/INSTALAR_ABRXOS_X_BRAND_BUILDER_V1.command"
echo "Instalando ABRXOS Content Builder V1..."
/bin/zsh "$ROOT/apps/content-builder/INSTALAR_ABRXOS_CONTENT_BUILDER_V1.command"
echo "✓ Instaladores finalizados."
