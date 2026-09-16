#!/bin/zsh
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
/bin/zsh "$ROOT/apps/content-builder/INSTALAR_ABRXOS_CONTENT_BUILDER_V1.command"
