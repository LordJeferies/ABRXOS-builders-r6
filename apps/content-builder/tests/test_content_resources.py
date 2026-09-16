from pathlib import Path
import json
ROOT=Path(__file__).resolve().parents[1]
RES=ROOT/'resources'/'canon_r6'

def test_r6_resource_snapshot_complete():
    assert (RES/'ONE_FILE_CONTEXT_R6.txt').exists()
    prompts=list((RES/'prompts').glob('PROMPT_*.txt'))
    assert len(prompts)>=14
    for typ in ['INTRO','VERTICAL','HORIZONTAL','FULL_EPISODE','CAROUSEL','QUOTE','THREAD','NOTE','PDF','SCRIPT']:
        d=RES/'fichas'/typ
        assert d.exists(), typ
        assert any(d.glob('FICHA_*_R6.json')), typ
    assert (RES/'fichas'/'ABRXOS_TODAS_LAS_FICHAS_R6.json').exists()
    for name in ['XR_FAMILIES_R6.json','MOTION_LIBRARY_R6.json','CINE_LIBRARY_R6.json','SFX_LIBRARY_R6.json','MUSIC_LIBRARY_R6.json','CAPTIONS_R6.json','EDIT_PROFILES_R6.json']:
        p=RES/'libraries'/name
        assert p.exists(), name
        json.loads(p.read_text(encoding='utf-8'))
