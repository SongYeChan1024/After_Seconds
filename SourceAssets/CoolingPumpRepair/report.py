"""냉각 펌프 보수 기록 V0.01 · 송예찬."""
from pathlib import Path
import json,sys,html
H=Path(__file__).resolve().parent;R=H.parents[1];P=R/'Unity/After_Seconds_Build_V0.01';O=R/'Docs/Review/2026-11-11_CoolingPump'
sys.path.insert(0,str(P/'Temp/ZFightingReview/deps'))
from PIL import Image,ImageDraw
models=json.loads((H/'repair_models.json').read_text());checks=json.loads((H/'validation.json').read_text());applied=json.loads((H/'applied_save.json').read_text());asset_bytes=(P/models[0]['asset']).stat().st_size
canvas=Image.new('RGB',(1280,684),(30,36,43));d=ImageDraw.Draw(canvas)
for j,side in enumerate([0,1]):
 for i,phase in enumerate(['before','after']):
  im=Image.open(O/f'{phase}_BM_CoolingPump_{side}.png').convert('RGB').resize((320,320))
  # Four evenly sized panels, before/after for opposite sides.
  x=(j*2+i)*320;canvas.paste(im,(x,0));d.text((x+8,322),f'{phase} | side {side}',fill='white')
for i,phase in enumerate(['tilt_before','tilt_after','after','lod1']):
 side=2 if i<2 else 0;im=Image.open(O/f'{phase}_BM_CoolingPump_{side}.png').convert('RGB').resize((320,320));canvas.paste(im,(i*320,342));d.text((i*320+8,664),phase,fill='white')
canvas.save(O/'comparison.jpg',quality=90)
manifest={'title':'B2 냉각 펌프 형상·정렬 보수 V0.01','author':'송예찬','date':'2026-11-11','scene':checks['scene'],'assetName':'Props_CoolingPump','models':models,'placements':checks['repairedPlacements'],'changes':['찢어져 보이던 모터 뒤 덮개의 면 방향/노멀을 복구하고 축 기준 반경을 정렬','뒤틀린 스키드를 수평 상판·I형 레일·가로 보강·체결부로 교체','C02 PumpTrainA_03의 LOD0만 기울었던 약2도를 바로잡고 LOD0/1 자세 일치','본체 원본 UV/재질을 유지하며 새 받침대는 기존 B2 금속 텍스처를 재사용'],'triangles':[10000,4000],'newModelBytes':asset_bytes,'newTextureCount':0,'newMaterialCount':1,'readWriteEnabled':False,'validation':{'placements':194,'colliders':194,'repairedPumps':10,'errors':checks['errors']},'scope':'B2 C02 5개/E01 3개/E03 2개. 다른 층·원본 모델·이전 프랍3종 보수는 유지. 에디터 형상/배치/LOD 검수이며 빌드 FPS 검증은 아님.'}
(P/'Assets/Afrer_Seconds/06.Data/AssetSources/B2_CoolingPumpRepair_20261111.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8')
parts=['<!doctype html><html lang="ko"><meta charset="utf-8"><title>냉각 펌프 보수 V0.01</title><style>body{max-width:1100px;margin:40px auto;padding:0 24px;background:#121a22;color:#e8edf2;font:16px/1.7 system-ui}img{width:100%;height:auto}a{color:#8ecbff}table{border-collapse:collapse;width:100%}td,th{padding:10px;border-bottom:1px solid #46515a;text-align:left}.pair{display:grid;grid-template-columns:1fr 1fr;gap:12px}</style><h1>Props_CoolingPump 형상·정렬 보수 V0.01</h1><p>2026-11-11 · 송예찬</p><p>앞선 검수에서 펌프의 회전 방향만 확인하고 보수에서 제외한 판단을 정정한다. 사용자 지적 후 선택된 E01 펌프를 확인해 모터 뒤 덮개 갈라짐과 받침대 뒤틀림을 보수했다. C02 세 번째 펌프의 LOD0만 약2도 기울었던 별도 문제도 확인해 바로잡았다.</p><p><strong>B2 C02 5개·E01 3개·E03 2개, 총10개에 적용·저장.</strong> 원본 본체와 UV/재질은 유지하고 받침대를 수평 상판·레일·보강재·체결부로 제작했다. 모터 덮개를 중심축에 맞추고 면 방향·노멀을 정리했다.</p><h2>전후와 LOD 비교</h2><p>위: 양쪽 면의 수정 전/후. 아래: C02 기울기 수정 전/후, E01 LOD0/LOD1. 검수용 임시 조명.</p><img src="comparison.jpg" alt="냉각 펌프 전후 및 LOD 비교"><h2>선택했던 E01 펌프</h2><div class="pair"><div>수정 전<img src="before_BM_CoolingPump_0.png"></div><div>수정 후<img src="after_BM_CoolingPump_0.png"></div></div><h2>씬 내 배치</h2><p>주변 설비·기존 서비스 배관과 함께 본 수정 후 화면. 편집 검수용 조명을 사용했다.</p><img src="context_BM_CoolingPump_0.png"><h2>검증</h2><table><tr><th>항목</th><th>결과</th></tr><tr><td>루트 위치·회전·크기 / 충돌체</td><td>194 / 194 보존</td></tr><tr><td>수정 펌프 LOD 참조</td><td>10개 × 2단계 정상, 회전 차이0도</td></tr><tr><td>접지</td><td>모델 하단 Y=-34.000m, C02 기울기 때문에 내려갔던 약36mm 복구</td></tr><tr><td>메시</td><td>정점 접합 기준 열린 경계·과잉 연결·퇴화 면0, Unity 반입 후 빈 메시0</td></tr><tr><td>삼각형</td><td>LOD0 10,000 / LOD1 4,000 — 기존 수량 유지</td></tr>']
parts.append(f'<tr><td>추가 파일</td><td>공유 FBX1개 {asset_bytes/1024/1024:.2f}MiB, 재질1개. 신규 텍스처0, Read/Write 꺼짐</td></tr></table>')
parts.append('<p>받침대에 별도 재질 슬롯1개를 사용하므로 펌프당 재질 패스가1개 증가한다. 런타임 스크립트는 추가하지 않았다. 보호 파일100개 중 B2 씬만 변경됐으며 다른 층·Player·Animator·이전3종 보수와 원본 모델/GUID는 유지했다. 커밋·push는 하지 않았다. 전체 다른 층의 펌프 검수나 빌드 성능 검증 완료를 의미하지 않는다.</p><p>제작·적용·검증 원본은 <code>SourceAssets/CoolingPumpRepair/</code>. Apply는 이미 적용되어 재실행하지 않는다. 보수 직전 씬 백업은 Documents/Codex/Backups/AfterSeconds_CoolingPump_20261111에 있다.</p></html>')
(O/'review.html').write_text(''.join(parts),encoding='utf-8')
old=R/'Docs/Review/2026-11-11_VarcoPropAlignment/review.html';text=old.read_text(encoding='utf-8')
if '냉각 펌프 후속 보수' not in text:
 text=text.replace('V0.01','V0.02').replace('</h1>','</h1><p><strong>냉각 펌프 후속 보수:</strong> 이 기록에서 펌프를 제외했던 판단은 후속 검수로 정정했다. <a href="../2026-11-11_CoolingPump/review.html">펌프10개 형상·LOD 정렬 보수 결과</a>를 함께 확인한다.</p>',1);old.write_text(text,encoding='utf-8')
note='2026-11-11 냉각 펌프 후속 보수: 사용자 지적한 `Props_CoolingPump`를 이전3종 보수에서 제외했던 판단을 정정했다. B2 C02 5개/E01 3개/E03 2개 총10개의 모터 덮개 갈라짐·노멀/축 정렬, 뒤틀린 받침대 재제작을 적용했다. C02 PumpTrainA_03의 LOD0만 약2도 기울어져 약36mm 내려가던 문제도 복구했다. 기존194루트/194충돌체·원본 본체 UV/재질·다른 층/Player/Animator·이전 프랍3종 보수 보존. LOD0 10,000/LOD1 4,000tri 유지, 새FBX1개0.58MiB·재질1개·새텍스처0, 검증오류0. [전후 기록](Docs/Review/2026-11-11_CoolingPump/review.html)과 `SourceAssets/CoolingPumpRepair/`를 따른다. Apply 재실행 금지. 저장된 B2 편집 씬이며 사용자 선택했던 E01 펌프를 다시 선택했다. 전체 다른 층/빌드 성능 검증 완료가 아니다. 로컬 저장, 커밋/push 미실시. 작성자 송예찬.'
for file in ['AGENTS.md','CLAUDE.md']:
 p=R/file;text=p.read_text(encoding='utf-8')
 if '냉각 펌프 후속 보수: 사용자' not in text:
  head,rest=text.split('\n',1);p.write_text(head.replace('V0.95','V0.96')+'\n\n'+note+'\n\n이전 단계 기록:\n'+rest+'\n- V0.96 (2026-11-11): 냉각 펌프10배치 받침대/모터 덮개와 LOD 자세 보수. 송예찬.\n',encoding='utf-8')
print(json.dumps({'report':str(O/'review.html'),'assetMiB':asset_bytes/1024/1024},ensure_ascii=False))
