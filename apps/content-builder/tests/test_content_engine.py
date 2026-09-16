import json, tempfile, zipfile, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from content_engine import safe_slug, deep_merge, ContentStore, select_case, resolve_prompt_template, build_content_ai_package


def test_select_case_routes_major_scenarios():
    assert select_case({'workflowMode':'fixed_plan','stage':'ALFA','timingQuality':'exact','contentType':'intro','editProfile':'XR_FULL'})=='01'
    assert select_case({'workflowMode':'fixed_plan','stage':'ALFA','timingQuality':'no_timing','contentType':'intro','editProfile':'XR_FULL'})=='13'
    assert select_case({'workflowMode':'transcript_only','stage':'ALFA','contentType':'intro','editProfile':'XR_FULL'})=='02'
    assert select_case({'workflowMode':'transcript_only','stage':'ALFA','contentType':'vertical','editProfile':'XR_FULL'})=='03'
    assert select_case({'workflowMode':'transcript_only','stage':'ALFA','contentType':'horizontal','editProfile':'XR_FULL'})=='04'
    assert select_case({'workflowMode':'transcript_only','stage':'ALFA','contentType':'carousel','editProfile':'XR_FULL'})=='05'
    assert select_case({'workflowMode':'transcript_only','stage':'BETA','contentType':'vertical','editProfile':'XR_FULL'})=='06'
    assert select_case({'workflowMode':'beta_to_alpha','stage':'ALFA','contentType':'vertical','editProfile':'XR_FULL'})=='07'
    assert select_case({'workflowMode':'update_alpha','stage':'ALFA','contentType':'vertical','editProfile':'XR_FULL'})=='08'
    assert select_case({'workflowMode':'transcript_only','stage':'ALFA','contentType':'vertical','editProfile':'MOTION_SFX'})=='09'
    assert select_case({'workflowMode':'transcript_only','stage':'ALFA','contentType':'vertical','editProfile':'SFX_ONLY'})=='10'
    assert select_case({'workflowMode':'full_episode','stage':'ALFA','contentType':'full_episode','editProfile':'XR_FULL'})=='11'
    assert select_case({'workflowMode':'multi_source','stage':'ALFA','contentType':'vertical','editProfile':'XR_FULL'})=='12'
    assert select_case({'workflowMode':'all_project','stage':'BETA','contentType':'all','editProfile':'XR_FULL'})=='14'


def test_resolve_template_prefers_cinematic_for_xr_full_alpha_video():
    p,t=resolve_prompt_template({'workflowMode':'transcript_only','stage':'ALFA','contentType':'vertical','editProfile':'XR_FULL'})
    assert 'PROMPT_03_' in p.name
    assert t.name=='FICHA_VERTICAL_ALFA_CINEMATIC_R6.json'
    p2,t2=resolve_prompt_template({'workflowMode':'transcript_only','stage':'BETA','contentType':'vertical','editProfile':'XR_FULL'})
    assert 'PROMPT_06_' in p2.name
    assert t2.name=='FICHA_VERTICAL_BETA_R6.json'
    p3,t3=resolve_prompt_template({'workflowMode':'transcript_only','stage':'ALFA','contentType':'quote','editProfile':'XR_FULL'})
    assert p3.name=='PROMPT_STATIC_ALFA_R6.txt'
    assert t3.name=='FICHA_QUOTE_ALFA_R6.json'


def test_store_roundtrip_unknown_fields():
    with tempfile.TemporaryDirectory() as td:
        store=ContentStore(Path(td))
        saved=store.save_draft({'requestId':'REQ1','projectId':'JOC56','unknown':{'x':1}})
        got=store.load_draft(saved['slug'])
        assert got['unknown']['x']==1


def test_content_package_contains_expected_contract():
    with tempfile.TemporaryDirectory() as td:
        td=Path(td); res=td/'res'; res.mkdir(); out=td/'out'; out.mkdir()
        cases=res/'prompts'; fichas=res/'fichas'/'INTRO'; cases.mkdir(parents=True); fichas.mkdir(parents=True)
        (cases/'PROMPT_01_PLAN_FIJO_MAS_TRANSCRIPCION_A_ALFA_R6.txt').write_text('BASE PROMPT',encoding='utf-8')
        (fichas/'FICHA_INTRO_ALFA_CINEMATIC_R6.json').write_text('{"schemaVersion":"R6","pieces":[]}',encoding='utf-8')
        (res/'ONE_FILE_CONTEXT_R6.txt').write_text('CANON CONTEXT',encoding='utf-8')
        (res/'libraries').mkdir(); (res/'libraries'/'XR_FAMILIES_R6.json').write_text('{"schemaVersion":"R6"}',encoding='utf-8')
        request={'requestId':'INTRO_AMANDA','projectId':'JOC55_AMANDA','projectTitle':'JOC55','workflowMode':'fixed_plan','stage':'ALFA','contentType':'intro','editProfile':'XR_FULL','timingQuality':'exact','transcript':'TRANSCRIPT','editorialPlan':'PLAN','projectConfig':{'projectId':'JOC55_AMANDA'},'brandAdapter':{'brandId':'JOC'},'specialRules':'NO CHANGE ORDER'}
        result=build_content_ai_package(request,out,res)
        folder=Path(result['folder'])
        required={'00_START_HERE.txt','01_QUE_SUBIR_A_CHATGPT.txt','02_PROMPT_FINAL.txt','03_REQUEST.json','04_TRANSCRIPCION.txt','05_PLAN_EDITORIAL.txt','06_PROJECT_CONFIG.json','07_BRAND_ADAPTER.json','08_FICHA_TARGET.json','09_CANON_CONTEXT.txt','11_SPECIAL_RULES.txt','package_manifest.json'}
        assert required.issubset({p.name for p in folder.iterdir()})
        manifest=json.loads((folder/'package_manifest.json').read_text(encoding='utf-8'))
        assert manifest['caseId']=='01'
        assert all(len(f['sha256'])==64 for f in manifest['files'])
        assert (folder/'CANON_LIBRARIES'/'XR_FAMILIES_R6.json').exists()
        assert Path(result['zip']).exists()
