from pathlib import Path
import json,html,re,hashlib
H=Path(__file__).resolve().parent;R=H.parents[1];O=R/'Docs/Review/2026-11-09_B3_FullFloor'
plan=json.loads((H/'layout.json').read_text(encoding='utf-8'))
body=['<!doctype html><html lang="ko"><meta charset="utf-8"><title>B3 시료층 검수 V0.01</title><style>body{margin:32px;background:#111820;color:#dbe6ed;font:16px system-ui}h1{font-size:26px}img{width:100%;height:auto}section{margin:38px 0}article{display:grid;grid-template-columns:1fr 1fr;gap:14px}figure{margin:0}figcaption{padding:8px}a{color:#a9cbdc}summary{cursor:pointer;padding:12px;background:#263441}</style><h1>B3 시료층 전체 외형 V0.01</h1><p>작성자 송예찬 · 2026-11-09</p><p>왼쪽은 저장된 기본 조명, 오른쪽은 외형 확인용으로 작업등을 임시 점등한 화면입니다. 실제 스위치 동작은 미구현이며 기본 소등 상태를 저장했습니다.</p><p><a href="Review.md">검수 결과·남은 작업</a></p>']
def fig(file,label):return '<figure><a href="'+file+'"><img loading="lazy" src="'+file+'"></a><figcaption>'+html.escape(label)+'</figcaption></figure>'
for r in plan['rooms']:
 code=r['id'];body.append('<section><h2>'+code+' · '+html.escape(r['name'])+'</h2><article>');body.append(fig(code+'_room.png','기본 조명'))
 f='reviewlit_'+code+'.png';body.append(fig(f,'작업등 임시 점등') if (O/f).exists() else fig(code+'_overview.png','상부/구조 검수'));body.append('</article></section>')
body.append('<section><h2>근접 검수 — 작업등 임시 점등</h2>')
for p in sorted(O.glob('detail_*.png')):body.append('<details><summary>'+html.escape(p.stem)+'</summary>'+fig(p.name,p.stem)+'</details>')
body.append('</section><section><h2>실제 Play 카메라</h2>'+fig('play_game_camera.png','Main Camera · 프레임 진행 후 캡처')+'</section><section><h2>연결 복도</h2>')
for t in plan['tunnels']:body.append('<details><summary>'+t['id']+' '+t['a']+' → '+t['b']+'</summary>'+fig(t['id']+'.png','기본 조명')+'</details>')
body.append('</section></html>');(O/'review.html').write_text(''.join(body),encoding='utf-8')
plays=[json.loads(p.read_text()) for p in sorted(O.glob('before_play_*.json'))];assert len(plays)>=6 and all(x['complete'] and x['framesAdvanced']>100 and x['displacement']>.30 and not x['errors'] for x in plays)
(O/'play_summary.json').write_text(json.dumps({'tests':plays,'allPassed':True,'note':'Existing keyboard input; temporary focus/look settings restored. Editor timings are not standalone build guarantees.'},indent=2))
old=R/'Docs/Review/2026-11-09_B4_Finish';parts=['<!doctype html><html lang="ko"><meta charset="utf-8"><title>B5/B4 표면 마감 V0.01</title><style>body{margin:32px;background:#111820;color:#dbe6ed;font:16px system-ui}img{width:100%;height:auto}article{display:grid;grid-template-columns:1fr 1fr;gap:12px}figure{margin:0}figcaption{padding:8px}section{margin:32px 0}a{color:#a9cbdc}</style><h1>B5/B4 표면 · B4 조명/LOD V0.01</h1><p>작성자 송예찬 · 2026-11-09</p><p><a href="Review.md">검수 범위와 제한</a></p>']
for stem in ['B4_E02','B4_CargoDetail','B5_CargoDetail','B5_C04','E03','C01','W02']:
 parts.append('<section><h2>'+stem+'</h2><article>')
 for phase,label in [('before','변경 전'),('after','변경 후')]:
  n=phase+'_'+stem+'.png'
  if (old/n).exists():parts.append(fig(n,label))
 parts.append('</article></section>')
for p in sorted(old.glob('wall_*.png'))+sorted(old.glob('close_*.png')):parts.append('<section><h2>'+p.stem+'</h2>'+fig(p.name,p.stem)+'</section>')
(old/'review.html').write_text(''.join(parts),encoding='utf-8')
for folder in [old,O]:
 page=(folder/'review.html').read_text(encoding='utf-8');missing=[n for n in re.findall(r'src="([^"]+)"',page) if not (folder/n).exists()];assert not missing,missing
note=(H/'status.md').read_text(encoding='utf-8');history=(R/'SourceAssets/B4_Finish/history_v069.md').read_text(encoding='utf-8')
for file in ['AGENTS.md','CLAUDE.md']:
 p=R/file;s=p.read_text(encoding='utf-8');title,body=s.split('\n',1);assert 'V0.70' in title
 if not body.lstrip().startswith('2026-11-09 B4 실험') and '2026-11-09 B4 실험 시설·1인칭 디테일:' not in body:body=body.replace('아래는 이전 단계 기록이다.',history+'\n아래는 이전 단계 기록이다.',1)
 p.write_text(title.replace('V0.70','V0.71')+'\n\n'+note+'\n'+body.lstrip()+'\n- V0.71 (2026-11-09): B3 전체 정적 외형·통행·Play 검수와 사용자 검수 단계. 송예찬.\n',encoding='utf-8')
p=R/'Unity/README.md';s=p.read_text(encoding='utf-8');title,body=s.split('\n',1);p.write_text(title.replace('V0.51','V0.52')+'\n\n'+note.replace('(Docs/','(../Docs/')+'\n'+body.lstrip(),encoding='utf-8')
source=R/'Unity/After_Seconds_Build_V0.01/Assets/Afrer_Seconds/06.Data/AssetSources';source.mkdir(exist_ok=True)
varco=json.loads((H/'varco_candidates.json').read_text(encoding='utf-8'));varco.update(author='송예찬',date='2026-11-09',flowName='After_Second_Env_and_Props_Ver0.03',meshExecution='bb462333-f275-478c-b10b-5adac7c3f9f7',remeshTasks={'B3_CryogenicDewar':'1c9b006f-9f4b-4a20-9ed9-a0fa401fc836','B3_SealedSampleCarrier':'be984510-4b41-42ee-b37f-e993182e1421'},actualPoints={'image':100,'meshAndRemesh':400},outputTrianglesEach=10000,visibility='PRIVATE',processedAssets=json.loads((H/'varco_assets.json').read_text()))
(source/'B3_FullFloor_VARCO.json').write_text(json.dumps(varco,ensure_ascii=False,indent=2),encoding='utf-8')
(source/'B3_FullFloor.json').write_text(json.dumps({'version':'V0.01','author':'송예찬','scene':'Assets/Afrer_Seconds/01.Scenes/Stage/Level_B3_Circular.unity','source':'SourceAssets/B3_FullFloor','designSource':'Docs/도면/Decision/원형공동/facility_layout.json','models':json.loads((H/'models.json').read_text()),'review':'Docs/Review/2026-11-09_B3_FullFloor/Review.md','runtimeScriptsAdded':0},ensure_ascii=False,indent=2),encoding='utf-8')
(source/'B4_Finish.json').write_text(json.dumps({'version':'V0.01','author':'송예찬','source':'SourceAssets/B4_Finish','textures':'Procedural PBR surfaces.py and walls.py, 2048px; new derivatives preserve original geometry/collision','review':'Docs/Review/2026-11-09_B4_Finish/Review.md','runtimeScriptsAdded':0},ensure_ascii=False,indent=2),encoding='utf-8')
print('Reviews, verified Play summary, provenance and handoff saved')
