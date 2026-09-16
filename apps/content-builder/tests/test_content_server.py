import json,tempfile,threading,urllib.request,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from app import make_server

def req(url,method='GET',data=None):
    body=None if data is None else json.dumps(data).encode()
    r=urllib.request.Request(url,data=body,method=method,headers={'Content-Type':'application/json'})
    with urllib.request.urlopen(r,timeout=5) as res:return res.status,json.loads(res.read().decode())

def test_content_api_health_save_library_and_export():
    with tempfile.TemporaryDirectory() as td:
        td=Path(td); data=td/'data'; out=td/'out'; res=td/'res'; web=td/'web'
        (res/'prompts').mkdir(parents=True); (res/'fichas'/'INTRO').mkdir(parents=True); web.mkdir(); out.mkdir(); data.mkdir()
        (res/'prompts'/'PROMPT_01_PLAN_FIJO_MAS_TRANSCRIPCION_A_ALFA_R6.txt').write_text('PROMPT',encoding='utf-8')
        (res/'fichas'/'INTRO'/'FICHA_INTRO_ALFA_CINEMATIC_R6.json').write_text('{"schemaVersion":"R6"}',encoding='utf-8')
        (res/'ONE_FILE_CONTEXT_R6.txt').write_text('CANON',encoding='utf-8')
        (web/'index.html').write_text('ok',encoding='utf-8')
        server=make_server('127.0.0.1',0,data,out,res,web); th=threading.Thread(target=server.serve_forever,daemon=True); th.start(); base=f'http://127.0.0.1:{server.server_address[1]}'
        try:
            _,h=req(base+'/api/health'); assert h['ok']
            draft={'requestId':'R1','projectId':'JOC','workflowMode':'fixed_plan','stage':'ALFA','contentType':'intro','editProfile':'XR_FULL','timingQuality':'exact','transcript':'t','editorialPlan':'p'}
            _,s=req(base+'/api/draft/save','POST',draft); assert s['slug']=='r1'
            _,lst=req(base+'/api/drafts'); assert lst['drafts'][0]['requestId']=='R1'
            _,lb=req(base+'/api/library/brand','POST',{'brandId':'JOC','schemaVersion':'abrxos.brand-adapter.r6'}); assert lb['ok']
            _,cases=req(base+'/api/cases'); assert '01' in cases['cases'] and '14' in cases['cases']
            _,ex=req(base+'/api/export','POST',draft); assert Path(ex['folder']).exists() and Path(ex['zip']).exists()
        finally:
            server.shutdown();server.server_close();th.join(timeout=3)
