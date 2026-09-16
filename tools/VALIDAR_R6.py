#!/usr/bin/env python3
from __future__ import annotations
import json, sys
from pathlib import Path
from collections import Counter

VIDEO={'intro','vertical','horizontal','full_episode'}
STATIC={'carousel','quote','thread','note','pdf','script'}
WORKFLOW={'PENDIENTE','REVISADO','HACIENDO','LISTO','PROGRAMADO','PUBLICADO'}
STAGES={'BETA','ALFA','OMEGA'}
XR_FAMILIES={'COMIC_INFO','COMIC_CC','TYPO','PHOTOS','OBJECTS','PHOTO_OBJECT','NO_XR'}
CINE_TYPES={'CINE01_BLACK_HOLD','CINE02_FREEZE_HOLD','CINE03_PUNCH_CUT'}
SFX_IDS={'SFX_CLICK','SFX_KEYBOARD','SFX_WHOOSH','SFX_CAMERA','SFX_GOOD','SFX_WRONG','SFX_LOW_BOOM','SFX_EMPHASIS','SFX_SUSPENSE','SFX_TENSION','SFX_RISER','SFX_IMPACT','SFX_CLICK_DEEP'}


def num(v):
    try:return float(v)
    except:return None

def main(path:str)->int:
    p=Path(path).expanduser()
    try: obj=json.loads(p.read_text(encoding='utf-8'))
    except Exception as e:
        print('CRITICAL JSON:',e);return 2
    critical=[];warn=[]
    pieces=obj.get('pieces')
    if not obj.get('projectId'): critical.append('projectId faltante')
    if not isinstance(pieces,list): critical.append('pieces debe ser lista'); pieces=[]
    ids=[]
    for pi,x in enumerate(pieces,1):
        if not isinstance(x,dict): critical.append(f'piece[{pi}] no objeto');continue
        pid=x.get('canonicalId') or x.get('id') or f'piece[{pi}]';ids.append(pid)
        typ=x.get('type');stage=x.get('stage');wf=x.get('workflowStatus')
        if typ not in VIDEO|STATIC: critical.append(f'{pid}: type inválido {typ}')
        if stage not in STAGES: critical.append(f'{pid}: stage inválido')
        if wf not in WORKFLOW: critical.append(f'{pid}: workflowStatus inválido')
        if not isinstance(x.get('schedule'),dict): warn.append(f'{pid}: schedule faltante')
        if typ in VIDEO:
            ranges=x.get('sourceRanges') or []
            if stage in {'ALFA','OMEGA'} and typ!='full_episode' and not ranges:
                warn.append(f'{pid}: video {stage} sin sourceRanges; no Cutter-ready')
            for ri,r in enumerate(ranges,1):
                a=num(r.get('start'));b=num(r.get('end'))
                if a is None or b is None: critical.append(f'{pid}: sourceRange {ri} no numérico')
                elif b<=a: critical.append(f'{pid}: sourceRange {ri} end<=start')
            tl=x.get('timeline') or []
            tids=[]
            xrs=[];caps=[]
            for ei,e in enumerate(tl,1):
                if not isinstance(e,dict): critical.append(f'{pid}: timeline[{ei}] no objeto');continue
                eid=e.get('id');
                if eid:tids.append(eid)
                a=num(e.get('start'));b=num(e.get('end'))
                if a is None or b is None: critical.append(f'{pid}: {eid or ei} start/end no numérico')
                elif b<=a: critical.append(f'{pid}: {eid or ei} end<=start')
                if e.get('track')=='xr': xrs.append(e)
                if e.get('track')=='captions': caps.append(e)
                if e.get('track')=='broll' and e.get('type')=='cine' and e.get('cineType') not in CINE_TYPES:
                    critical.append(f'{pid}: cineType inválido {e.get("cineType")}')
                if e.get('track')=='sfx':
                    sid=(e.get('sfx') or {}).get('libraryId') or e.get('libraryId')
                    if sid and sid not in SFX_IDS: warn.append(f'{pid}: SFX fuera de librería {sid}')
            if len(tids)!=len(set(tids)): critical.append(f'{pid}: timeline ids repetidos')
            # XR density/diversity only when XR_FULL
            prof=(x.get('editProfile') or {}).get('code')
            visual_xrs=[e for e in xrs if e.get('xrFamily')!='NO_XR']
            if prof=='XR_FULL':
                if typ=='intro' and len(visual_xrs)!=6: warn.append(f'{pid}: intro XR_FULL tiene {len(visual_xrs)} XR; canon pide 6')
                if typ=='vertical' and not (2<=len(visual_xrs)<=4): warn.append(f'{pid}: vertical XR_FULL tiene {len(visual_xrs)} XR; canon pide 2-4')
                fam=[e.get('xrFamily') for e in visual_xrs]
                for a,b in zip(fam,fam[1:]):
                    if a and a==b: warn.append(f'{pid}: XR consecutivos de misma familia {a}')
            # Family rules
            for e in visual_xrs:
                fam=e.get('xrFamily');dur=(num(e.get('end')) or 0)-(num(e.get('start')) or 0)
                if fam not in XR_FAMILIES: critical.append(f'{pid}: XR family inválida {fam}');continue
                assets=e.get('assets') or [];states=e.get('states') or []
                if fam=='COMIC_INFO':
                    if len(assets)!=1: critical.append(f'{pid}/{e.get("id")}: COMIC_INFO debe tener 1 asset')
                    if len(states)!=5: critical.append(f'{pid}/{e.get("id")}: COMIC_INFO debe tener 5 states')
                    if not 12<=dur<=20: warn.append(f'{pid}/{e.get("id")}: COMIC_INFO duración {dur:.2f}s fuera 12-20')
                elif fam=='COMIC_CC':
                    if len(assets)!=3: critical.append(f'{pid}/{e.get("id")}: COMIC_CC debe tener 3 assets')
                    if e.get('captionPolicy') not in {'HIDE','hide'}: warn.append(f'{pid}/{e.get("id")}: COMIC_CC debe ocultar captions')
                elif fam=='TYPO':
                    if len(states)!=3: critical.append(f'{pid}/{e.get("id")}: TYPO debe tener 3 states')
                    if not 6<=dur<=12: warn.append(f'{pid}/{e.get("id")}: TYPO duración fuera 6-12')
                elif fam=='PHOTOS':
                    if len(assets)!=3: critical.append(f'{pid}/{e.get("id")}: PHOTOS debe tener 3 assets')
                    if not 6<=dur<=12: warn.append(f'{pid}/{e.get("id")}: PHOTOS duración fuera 6-12')
                elif fam=='OBJECTS':
                    if len(assets)!=3: critical.append(f'{pid}/{e.get("id")}: OBJECTS debe tener 3 assets')
                    for a in assets:
                        if len(a.get('emojiFallback') or [])!=2: warn.append(f'{pid}/{e.get("id")}/{a.get("assetId")}: necesita 2 emoji fallback')
                    if not 6<=dur<=12: warn.append(f'{pid}/{e.get("id")}: OBJECTS duración fuera 6-12')
                elif fam=='PHOTO_OBJECT':
                    if len(assets)!=3: critical.append(f'{pid}/{e.get("id")}: PHOTO_OBJECT = 1 foto + 2 objetos')
                    if not 8<=dur<=12: warn.append(f'{pid}/{e.get("id")}: PHOTO_OBJECT duración fuera 8-12')
            # Captions
            for e in caps:
                text=str(e.get('sourceText') or e.get('text') or '').strip(); wc=len(text.split())
                mode=e.get('displayMode')
                if mode=='hero_word':
                    if len(str(e.get('highlightWord') or e.get('text') or '').split())!=1: warn.append(f'{pid}/{e.get("id")}: hero_word debería ser una palabra')
                elif wc and not 6<=wc<=17: warn.append(f'{pid}/{e.get("id")}: caption group tiene {wc} palabras; soft range 6-17')
                if not e.get('partId'): warn.append(f'{pid}/{e.get("id")}: caption sin partId')
                if e.get('suppressedBy') and e.get('visibility')!='hidden': warn.append(f'{pid}/{e.get("id")}: suppressedBy pero visibility no hidden')
        elif typ in STATIC:
            sp=x.get('staticProduction')
            if stage in {'ALFA','OMEGA'} and (not isinstance(sp,dict) or not sp.get('items')):
                critical.append(f'{pid}: estático {stage} sin staticProduction.items')
    if len(ids)!=len(set(ids)): critical.append('canonicalId/id de piezas repetidos')
    print('PROJECT:',obj.get('projectId','?'))
    print('PIECES:',len(pieces))
    print('CRITICAL:',len(critical))
    for x in critical:print('  ✗',x)
    print('WARNINGS:',len(warn))
    for x in warn:print('  ⚠',x)
    if not critical:print('RESULT: PASS estructural R6')
    return 1 if critical else 0

if __name__=='__main__':
    if len(sys.argv)!=2:
        print('Uso: python3 VALIDAR_R6.py archivo.json');raise SystemExit(2)
    raise SystemExit(main(sys.argv[1]))
