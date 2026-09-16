from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
HTML=ROOT/'ABRXOS_X_BRAND_BUILDER_V1.html'

def test_brand_html_has_required_workspaces():
    text=HTML.read_text(encoding='utf-8')
    for token in [
        'ABRXOS X','Brand Builder','nav-overview','nav-raw','nav-method','nav-adapter','nav-references','nav-qa',
        'method-summary','method-tools','rawContext','adapter-json','exportPackage','referenceFiles',
        'Cinematic Edit','Dynamic Edit','Clean Edit','Ver las 25 tools','importAdapterFile','Importar Brand Adapter'
    ]:
        assert token in text, token
    assert 'localStorage' in text
    assert '/api/export' in text
    assert '/api/brand/save' in text
