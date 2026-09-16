#!/bin/zsh
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
echo "== Python compile =="
python3 -m py_compile apps/brand-builder/app.py apps/brand-builder/brand_engine.py apps/content-builder/app.py apps/content-builder/content_engine.py tools/VALIDAR_R6.py
echo "== Brand tests =="
python3 -m pytest -q apps/brand-builder/tests
echo "== Content tests =="
python3 -m pytest -q apps/content-builder/tests
echo "== JSON parse =="
python3 - <<'PY'
import json, pathlib
root=pathlib.Path('canon/r6/json')
count=0
for p in root.rglob('*.json'):
    json.loads(p.read_text(encoding='utf-8')); count+=1
print('JSON PASS:',count)
PY
echo "ALL PASS"
