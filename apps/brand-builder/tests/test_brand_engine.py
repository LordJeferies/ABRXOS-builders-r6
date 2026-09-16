import json, tempfile, zipfile, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from brand_engine import safe_slug, deep_merge, BrandStore, build_brand_ai_package


def test_safe_slug_blocks_paths_and_keeps_identity():
    assert safe_slug("JOC / Amanda Vicari") == "joc-amanda-vicari"
    assert ".." not in safe_slug("../../evil")
    assert "/" not in safe_slug("a/b")


def test_deep_merge_preserves_unknown_fields():
    base = {"voice": {"tone": ["clear"], "unknownNested": {"x": 1}}, "unknownTop": 9}
    patch = {"voice": {"tone": ["warm"]}}
    got = deep_merge(base, patch)
    assert got["voice"]["tone"] == ["warm"]
    assert got["voice"]["unknownNested"] == {"x": 1}
    assert got["unknownTop"] == 9


def test_store_roundtrip_preserves_project():
    with tempfile.TemporaryDirectory() as td:
        store = BrandStore(Path(td))
        project = {"brandId": "JOC", "brandName": "JOC", "rawContext": "literal\ntext", "unknown": {"ok": True}}
        saved = store.save(project)
        loaded = store.load(saved["slug"])
        assert loaded["rawContext"] == "literal\ntext"
        assert loaded["unknown"]["ok"] is True
        assert loaded["brandId"] == "JOC"


def test_package_contains_required_files_and_hashes():
    with tempfile.TemporaryDirectory() as td:
        td = Path(td)
        resources = td / "resources"; resources.mkdir()
        (resources / "brand_adapter_template.json").write_text('{"schemaVersion":"abrxos.brand-adapter.r6"}', encoding="utf-8")
        (resources / "branding_method_registry.json").write_text('{"drivers":[]}', encoding="utf-8")
        (resources / "BRANDING_METHOD_SOURCE_NOTE.txt").write_text('attach original method pdf', encoding="utf-8")
        ref = td / "ref.txt"; ref.write_text('REFERENCE', encoding='utf-8')
        project = {
            "brandId": "JOC", "brandName": "JOC", "rawContext": "RAW EXACT",
            "brandForm": {"sector": "podcast"}, "method": {"summary": {"ego": {"buyer":"dentists"}}},
            "references": [{"filename":"ref.txt","path":str(ref)}], "brandAdapterDraft": {"schemaVersion":"abrxos.brand-adapter.r6","brandId":"JOC"},
            "canonVersion": "R6"
        }
        result = build_brand_ai_package(project, td / "out", resources)
        folder = Path(result["folder"])
        required = {
            "00_START_HERE.txt","01_QUE_SUBIR_A_CHATGPT.txt","02_PROMPT_FINAL.txt",
            "03_RAW_BRAND_CONTEXT.txt","04_BRAND_FORM.json","05_BRANDING_METHOD_INPUT.json",
            "06_BRAND_ADAPTER_TEMPLATE_R6.json","07_EXPECTED_OUTPUT_SCHEMA.json",
            "08_SOURCE_REFERENCES.json","09_BRAND_DRAFT.json","10_BRANDING_METHOD_REGISTRY.json","11_BRANDING_METHOD_SOURCE_NOTE.txt","package_manifest.json"
        }
        assert required.issubset({p.name for p in folder.iterdir()})
        manifest = json.loads((folder / "package_manifest.json").read_text(encoding="utf-8"))
        assert manifest["canonVersion"] == "R6"
        assert manifest["files"]
        assert all(len(x["sha256"]) == 64 for x in manifest["files"])
        upload=(folder/'01_QUE_SUBIR_A_CHATGPT.txt').read_text(encoding='utf-8')
        assert '10_BRANDING_METHOD_REGISTRY.json' in upload and '11_BRANDING_METHOD_SOURCE_NOTE.txt' in upload
        assert (folder / "REFERENCES" / "ref.txt").read_text(encoding="utf-8") == "REFERENCE"
        assert Path(result["zip"]).exists()
        with zipfile.ZipFile(result["zip"]) as zf:
            assert "00_START_HERE.txt" in zf.namelist()
