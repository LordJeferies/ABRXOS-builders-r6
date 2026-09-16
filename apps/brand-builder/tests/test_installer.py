from pathlib import Path
import json
ROOT=Path(__file__).resolve().parents[1]

def test_installer_release_files_present_and_safe():
    inst=ROOT/'INSTALAR_ABRXOS_X_BRAND_BUILDER_V1.command'
    assert inst.exists()
    text=inst.read_text(encoding='utf-8')
    assert 'command -v python3' in text
    assert 'osacompile' in text
    assert '~/Applications/ABRXOS' in text or 'HOME/Applications/ABRXOS' in text or '$HOME/Applications/ABRXOS' in text
    assert 'rm -rf /' not in text
    assert (ROOT/'COMANDOS_TERMINAL.txt').exists()
    assert (ROOT/'README.md').exists()
    v=json.loads((ROOT/'VERSION.json').read_text(encoding='utf-8'))
    assert v['version']=='1.0.0'
