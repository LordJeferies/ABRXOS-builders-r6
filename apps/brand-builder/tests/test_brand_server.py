import json, tempfile, threading, urllib.request, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from app import make_server


def req(url, method="GET", data=None):
    body = None if data is None else json.dumps(data).encode("utf-8")
    r = urllib.request.Request(url, data=body, method=method, headers={"Content-Type":"application/json"})
    with urllib.request.urlopen(r, timeout=5) as res:
        return res.status, json.loads(res.read().decode("utf-8"))


def test_health_and_brand_save_export_api():
    with tempfile.TemporaryDirectory() as td:
        root=Path(td); data=root/"data"; out=root/"out"; res=root/"resources"; web=root/"web"
        for p in (data,out,res,web): p.mkdir()
        (res/"brand_adapter_template.json").write_text('{"schemaVersion":"abrxos.brand-adapter.r6"}',encoding="utf-8")
        (web/"index.html").write_text("ok",encoding="utf-8")
        server=make_server("127.0.0.1",0,data,out,res,web)
        th=threading.Thread(target=server.serve_forever,daemon=True); th.start()
        base=f"http://127.0.0.1:{server.server_address[1]}"
        try:
            status,obj=req(base+"/api/health")
            assert status==200 and obj["ok"] is True
            project={"brandId":"JOC","brandName":"JOC","rawContext":"hello","brandAdapterDraft":{"schemaVersion":"abrxos.brand-adapter.r6"},"method":{"summary":{"ego":{"buyer":"x"}}}}
            _, saved=req(base+"/api/brand/save","POST",project)
            assert saved["ok"] and saved["slug"]=="joc"
            _, brands=req(base+"/api/brands")
            assert brands["brands"][0]["brandId"]=="JOC"
            _, exported=req(base+"/api/export","POST",project)
            assert exported["ok"]
            assert Path(exported["folder"]).exists()
            assert Path(exported["zip"]).exists()
        finally:
            server.shutdown(); server.server_close(); th.join(timeout=3)
