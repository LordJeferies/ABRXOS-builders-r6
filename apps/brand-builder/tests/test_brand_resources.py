import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
RES=ROOT/'resources'

def test_brand_resources_complete():
    assert (RES/'brand_adapter_template.json').exists()
    assert (RES/'branding_method_registry.json').exists()
    reg=json.loads((RES/'branding_method_registry.json').read_text(encoding='utf-8'))
    assert len(reg['drivers'])==5
    assert sum(len(d['tools']) for d in reg['drivers'])==25
    assert all(d.get('summaryFields') for d in reg['drivers'])
    adapter=json.loads((RES/'brand_adapter_template.json').read_text(encoding='utf-8'))
    assert adapter['schemaVersion']=='abrxos.brand-adapter.r6'
    assert 'captions' in adapter and 'cine' in adapter and 'xr' in adapter
