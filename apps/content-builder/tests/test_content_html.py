from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
HTML=ROOT/'ABRXOS_CONTENT_BUILDER_V1.html'

def test_content_html_has_required_workspaces():
    text=HTML.read_text(encoding='utf-8')
    for token in [
      'ABRXOS Content Builder','workflowMode','contentType','stageSelect','editProfile','transcriptText','editorialPlan','currentFichaText',
      'projectConfigText','brandAdapterText','allProjectPanel','xrRule','Build AI Package','/api/export','/api/draft/save',
      'Cinematic Edit','Dynamic Edit','Clean Edit','carousel','full_episode','multi_source'
    ]:
        assert token in text, token
    assert 'localStorage' in text
