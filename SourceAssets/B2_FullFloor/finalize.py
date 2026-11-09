from pathlib import Path
import json,hashlib,shutil,re,html
H=Path(__file__).resolve().parent;R=H.parents[1];O=R/'Docs/Review/2026-11-09_B2_FullFloor';D=R/'Docs/도면/Decision/원형공동';A=R/'Unity/After_Seconds_Build_V0.01/Assets/Afrer_Seconds'
read=lambda p:json.loads(p.read_text(encoding='utf8'))
plan=read(H/'layout.json');walk=read(O/'corridors.json');access=read(O/'access.json');stairs=read(O/'stairs.json');play=read(O/'play.json');look=read(O/'look_test.json');audit=read(O/'audit.json');state=read(O/'final_state.json');lod=read(H/'lod_applied.json')
assert all(x['passed'] for x in walk['controller']+walk['clearance']+stairs)
assert all(t['reachable'] for r in access for t in r['targets'])
assert play['complete'] and not play['errors'] and all(r['distance']>.3 and r['grounded'] and r['frames']>20 for r in play['results'])
assert look['complete'] and look['events']>0 and look['yawChange']>0 and look['pitchChange']>0 and not look['errors']
assert not audit['missingMeshes'] and not audit['missingMaterials'] and not audit['missingScripts'] and not audit['meshIssues']
assert not state['C02Missing'] and all(p['positionError']<.001 and p['yawError']<.01 for p in state['newPlacements'])
baseline=read(H/'protected_before.json');changed=[];unchanged=[]
for path,digest in baseline.items():
 p=R/path
 (unchanged if p.exists() and hashlib.sha256(p.read_bytes()).hexdigest()==digest else changed).append(path)
allowed=[p for p in changed if p.replace('\\','/').endswith('/Level_B2_Circular.unity')]
concurrent=[p for p in changed if p.replace('\\','/').endswith('/02.Scripts/C.System/Player/PlayerMotorSettings.cs')]
unexpected=[p for p in changed if p not in allowed and p not in concurrent]
assert not unexpected,unexpected
protection={'unchanged':len(unchanged),'expectedChanges':allowed,'observedConcurrentChanges':concurrent,'concurrentNote':'PlayerMotorSettings.cs에서 작업 중 별도 변경을 관측했다. 이 제작 도구에서는 수정하지 않았으며 현 내용을 보존했다.','unexpectedChanges':unexpected};(O/'protection.json').write_text(json.dumps(protection,ensure_ascii=False,indent=2),encoding='utf8')
# Draw the verified geometry at readable scale, keeping all room identities.
from PIL import Image,ImageDraw,ImageFont
im=Image.new('RGB',(1800,1350),'#121b22');pen=ImageDraw.Draw(im);font=ImageFont.truetype('C:/Windows/Fonts/malgunbd.ttf',23);small=ImageFont.truetype('C:/Windows/Fonts/malgun.ttf',17);xy=lambda x,v:(900+x*5.8,650+v*5.8)
for t in plan['tunnels']:
 col='#b57863' if t.get('routing') else '#647d87';pts=[xy(*p) for p in t['path']];pen.line(pts,fill=col,width=31,joint='curve')
 for x,y in pts:pen.ellipse((x-15,y-15,x+15,y+15),fill=col)
for r in plan['rooms']:
 x,y=xy(r['x'],r['v']);rr=r['r']*5.8;pen.ellipse((x-rr,y-rr,x+rr,y+rr),fill='#33444e',outline='#9bb7c0',width=2);pen.text((x,y-12),r['id'],font=font,fill='white',anchor='mm');pen.text((x,y+15),r['name'].replace(' 공동','').replace('·',' / '),font=small,fill='#dae3e5',anchor='mm')
for t in plan['tunnels']:
 ps=t['path'];p=ps[len(ps)//2] if len(ps)>2 else [(ps[0][0]+ps[-1][0])/2,(ps[0][1]+ps[-1][1])/2];pen.text(xy(*p),t['id'].split('-')[1],font=small,fill='#f6e2ce',anchor='mm')
pen.text((50,35),'After Seconds B2 기계층 연결도 V0.01',font=font,fill='white');pen.text((50,80),'공동 12 / 이동 코어 3 / 원형 배관 통로 21     작성자 송예찬',font=small,fill='#c8d0d4');pen.text((50,1210),'내경 5.0m / 평탄 바닥 폭 4.2m / 천장 3.85m / C02 그레이팅 높이 3.6m',font=font,fill='#d4dadc');pen.text((50,1260),'구리색 5개 통로: 출입부 겹침 방지를 위한 곡선 진입. 공동 위치와 연결 관계는 유지.',font=small,fill='#cfa48b');im.save(H/'connection_plan.png')
folder=D/'B2_배관통로';folder.mkdir(exist_ok=True);shutil.copy2(H/'connection_plan.png',folder/'B2_연결도.png');shutil.copy2(H/'layout.json',folder/'as_built_layout.json');shutil.copy2(O/'final_state.json',folder/'unity_final_state.json')
master=read(D/'facility_layout.json');floor=next(f for f in master['floors'] if f['id']=='B2');floor['tunnels']=plan['tunnels'];floor['rooms']=plan['rooms'];floor['pipeSection']=plan['pipeSection'];floor['tunnelClearance']=plan['tunnelClearance']
byid={t['id']:t for t in plan['tunnels']}
for t in master['tunnels']:
 if t.get('id') in byid:t.update(byid[t['id']])
for r in master['rooms']:
 if r.get('floor')=='B2':
  code=r.get('room',r.get('id','')).replace('B2-','');rr=next((q for q in plan['rooms'] if q['id']==code),None)
  if rr:r['doors']=rr['doors']
master.update(title='After Seconds 원형 공동 제작 설계 V0.06',version='V0.06',status='B5/B4 역할 및 B3 보수 유지 / B2 전체 연결과 원형 배관 통로 실제 배치 반영')
master['revision_history'].append({'version':'V0.06','date':'2026-11-09','author':'송예찬','change':'B2 공동12·코어3·통로21 연결. T01/T07/T08/T19/T20 곡선 진입, 내경5m 배관 단면, 실제 장비144배치 별도 명세. 게임 기능 미구현.'})
master['production_status']['B2_FullFloor']={'date':'2026-11-09','scene':'Level_B2_Circular.unity','status':'전체 연결 및 정적 외형 1차 / 사용자 분위기·밀도 검수 대기','as_built':'B2_배관통로/as_built_layout.json','review':'../../../Review/2026-11-09_B2_FullFloor/Review.md','runtime_added':False}
(D/'facility_layout.json').write_text(json.dumps(master,ensure_ascii=False,indent=2),encoding='utf8')
naccess=sum(len(r['targets']) for r in access);samples=sum(r['tested'] for r in walk['clearance'])
summary=f'''2026-11-09 B2 전체 연결: `Level_B2_Circular.unity`에 공동12·이동 코어3·원형 통로21을 연결했다. 내경5m·바닥4.2m·천장3.85m, 금속 플랜지/볼트·측면 배관·붉은 보조등·목적지 바닥 안내선을 반영했다. 출입 겹침4곳은 통로5개의 곡선 진입으로 해소했다. 신규 설비144배치·벽 소방/CCTV 각11개, VARCO 비상 발전기18,000tri와 Blender 전용 설비6종. 기존 C02 메자닌/설비는 유지하고 문/개구부를 연결했으며 소방1개를 이동했다. Controller21/21·폭/높이{samples:,}표본·접근{naccess}/{naccess}·계단왕복4/4·Play4곳·OnLook 통과. 신규 LOD{len(lod)}그룹, 정적 반사35개 추가·가림 베이크. **전체 연결과 정적 외형 1차 완료이며 다음은 사용자 통로 형태·공동 밀도·밝기 검수 후 지적 구역 보수**. B1 연결 로딩·문/승강기·설비·CCTV 동작은 미구현이며 게임 C#/Animator를 추가하지 않았다. 저장된 B2 편집 모드, 마우스/키보드 활성. 커밋·push 미실시. 작성자 송예찬. [검수](Docs/Review/2026-11-09_B2_FullFloor/Review.md).'''
for path,old,new in [(R/'AGENTS.md','V0.75','V0.76'),(R/'CLAUDE.md','V0.75','V0.76'),(R/'Unity/README.md','V0.55','V0.56')]:
 text=path.read_text(encoding='utf8');line,rest=text.split('\n',1);s=summary.replace('](Docs/','](../Docs/') if path.parent.name=='Unity' else summary;text=line.replace(old,new)+'\n\n'+s+'\n\n이전 단계 기록:\n'+rest
 if path.name=='CLAUDE.md':text+='\n- V0.76 (2026-11-09): B2 전체 연결·배관 통로 외형과 실제 이동 검수. 송예찬.\n'
 path.write_text(text,encoding='utf8')
text=(D/'README.md').read_text(encoding='utf8');first,rest=text.split('\n',1);(D/'README.md').write_text(first.replace('V0.12','V0.13')+'\n\n2026-11-09 B2 전체 연결: [현재 연결도와 실제 배치](B2_배관통로/README.md)를 우선한다. `facility_layout.json` V0.06에 통로5개 곡선 진입과 원형 단면을 반영했다. 공동 위치·연결 관계는 유지했다. 기존 Excel/PDF/SVG는 초기 수급·설계 이력이며 B2 실제 배치는 새 as_built_layout.json을 따른다. 작성자 송예찬.\n\n이전 단계 기록:\n'+rest,encoding='utf8')
(folder/'README.md').write_text('''# After Seconds B2 배관 통로와 실제 배치 V0.01

작성자 송예찬 · 2026-11-09

[연결도](B2_연결도.png)와 [실제 배치 명세](as_built_layout.json)를 기준으로 Level_B2_Circular 씬을 연결했다. 공동12개·계단/승강기 코어3개·통로21개다. 공동 중심과 연결 관계는 유지하고 T01/T07/T08/T19/T20의 진입부를 곡선으로 조정했다.

통로는 내경5m 원형 금속 외피, 두께0.18m, 바닥4.2m, 천장3.85m다. 구조 플랜지/볼트와 측면 설비 배관, 중성 작업등과 약한 붉은 보조등을 사용한다. C02의 3.6m 그레이팅 복층은 유지한다.

신규 장비144배치와 C02 기존 장비는 구분한다. 실제 Unity 좌표는 [native 검수 결과](unity_final_state.json), 통행/입력/성능 검수와 남은 일은 [검수 기록](../../../../Review/2026-11-09_B2_FullFloor/Review.md)을 따른다. 기존 Excel·PDF·SVG는 이번 배치와 다를 수 있다.
''',encoding='utf8')
(O/'Review.md').write_text(f'''# After Seconds B2 전체 연결과 배관 통로 검수 V0.01

작성자 송예찬 · 2026-11-09

`Level_B2_Circular.unity`에 공동12개·이동 코어3개·통로21개를 연결했다. 통로 내부가 큰 배관으로 읽히도록 원형 금속 벽체, 체결 플랜지와 볼트, 측면 배관, 평평한 보행면을 적용했다. [화면 모음](review.html), [연결도](../../도면/Decision/원형공동/B2_배관통로/B2_연결도.png).

## 구현 범위

- 내경5m, 외피0.18m, 보행면4.2m, 천장3.85m. 진입부가 겹치던4곳을 통로5개의 곡선으로 조정했다.
- 신규 장비144배치. 원심분리·배전·관제·주/예비 전력·정비·급수·공조·폐수·환기·감시/정비 구역을 구분했다.
- 지정 VARCO 플로우에서 비상 발전기를 생성하고18,000tri로 리메시했다. Blender 전용 설비6종은 변압기·필터 설비·송풍기·수처리·밀폐 탱크·정비 부품 랙이다. 제작 모서리에 베벨을 적용했다.
- 기존 C02 그레이팅·계단·냉각 설비 배치는 보존했다. 닫힌 문/이전 문틀과 외피는 비활성 보관하고 새 원형 개구부를 연결했다. 출입 폭 확보를 위해 소방 설비1개만 이동했다.
- 신규 소방11개·CCTV 외형11개, 신규 정적 반사35개, LOD{len(lod)}그룹. 가림 데이터 {state['occlusionBytes']:,}bytes. 바닥선은 목적지별 시설 안내이며 예상 플레이 경로 디버그 표시는 없다.

## 검수

| 항목 | 결과 |
|---|---|
| CharacterController 통로 이동 | 21/21 통과 |
| 폭·높이·바닥 표본 | {samples:,}개, 막힘·바닥 누락0 |
| 공동 출입/장비 전면 접근 | {naccess}/{naccess} 연결 |
| VA/VB 16m 계단 | 상승/하강4/4 통과 |
| 실제 Play | 4구역 프레임 진행·이동·접지, 새 게임 오류0 |
| OnLook | {look['events']}이벤트, 좌우{look['yawChange']:.2f}°/상하{look['pitchChange']:.2f}° 회전 |
| 메시/재질/스크립트 누락 | 0/0/0 |
| 메시 퇴화면 | 검수 대상0 |
| 실제 신규 배치 | 144/144 좌표·각도 일치 |
| 보호 파일 | {len(unchanged)}개 동일, B2 씬 변경·별도 스크립트 변경1개 관측 |

측정 파일은 corridors.json, access.json, stairs.json, play.json, look_test.json, audit.json, final_state.json, protection.json이다. Play 프레임 시간은 에디터 검수값이며 빌드 성능 수치가 아니다. 새 LOD114개 중5개의 법선 방향 검사 실패는 원거리 메시의 면 법선 재계산으로 수정한 후 적용했다.

## 다음 작업

1. 사용자가 T01 원형 통로의 배관 느낌과 밝기, C01/W02/N01의 설비 규모·밀도를 확인한다.
2. 지적한 구역부터 근접 디테일·배관 연결·소품 밀도를 조정한다. 전체 연결은 완료했지만 최종 아트 승인으로 취급하지 않는다.
3. B1 제작 및 실제 층 전환은 별도 작업이다. 문/승강기/설비/CCTV 동작과 AI·UI는 사용자가 게임 스크립트로 구현한다.

게임 C#/Animator·다른 층·Player 씬은 이번 제작 도구에서 변경하지 않았다. 작업 도중 PlayerMotorSettings.cs에 앉기 속도 관련 주석이 별도로 추가된 상태를 관측했고 이를 그대로 보존했다. 커밋·push하지 않았다. 제작 원본은 SourceAssets/B2_FullFloor이며 Apply/Repair/Safety/LodApply/Probes를 현재 씬에 그대로 재실행하지 않는다.
''',encoding='utf8')
shots=[('01_pipe_tunnel','T01 원형 배관 통로'),('02_centrifuge','C01 원심분리 공동'),('03_cooling_connected','C02 기존 복층과 연결'),('04_freight_junction','VL 화물 승강기 연결부'),('room_W02','W02 예비 전력'),('room_E01','E01 급수 설비'),('room_E02','E02 공조 필터'),('room_N01','N01 환기 설비'),('room_C04','C04 관제')]
page='<!doctype html><html lang="ko"><meta charset="utf-8"><meta name="viewport" content="width=device-width"><title>B2 전체 연결 검수 V0.01</title><style>body{background:#111a20;color:#e2e8eb;font:16px system-ui;margin:32px auto;max-width:1440px}img{width:100%;display:block}figure{margin:36px 0}figcaption{padding:12px;background:#20313b}p{line-height:1.8}</style><h1>B2 전체 연결 검수 V0.01</h1><p>작성자 송예찬 · 공동12 / 코어3 / 원형 통로21. 정적 외형과 통행 검수 결과.</p><p><a style="color:#9ad7e1" href="Review.md">검수 범위와 다음 작업</a></p>'
for file,label in shots:page+=f'<figure><img src="{file}.png" alt="{html.escape(label)}"><figcaption>{html.escape(label)}</figcaption></figure>'
(O/'review.html').write_text(page+'</html>',encoding='utf8')
(H/'README.md').write_text('''# B2 전체 연결 제작 원본 V0.01

작성자 송예찬 · 2026-11-09

현재 씬은 Level_B2_Circular.unity. 기존 B2_C02_CoolingSector와 신규 B2_MachineryNetwork를 함께 사용한다. 공동12·코어3·통로21의 연결/정적 외형 1차를 적용했고 사용자 아트 검수가 다음이다.

layout.json과 Docs/Review/2026-11-09_B2_FullFloor/Review.md를 먼저 읽는다. Apply.cs, Repair.cs, Safety, LodApply, Probes는 일회성 적용 도구다. 현재 씬에 전체 적용을 다시 실행하지 않는다. 부분 보수는 최신 저장 씬과 실제 Transform을 기준으로 한다.

architecture.py/common.py는 원형 통로와 공동, equipment.py는 베벨을 포함한 전용 기계 설비6종을 제작한다. Blender 원본과 생성 전 GLB를 보존한다. models.json과 Equipment/models.json을 함께 참조한다. LOD는 근접 원본을 보존한 거리별 파생 모델이다.

Play.cs/Look.cs는 검수용 외부 도구다. Mouse/Keyboard를 비활성화하지 않는다. Play 종료 후 Restore를 실행하고 마우스/키보드 활성 및 runInBackground 복원을 확인한다. 게임 내부 C#/Animator는 사용자가 작성한다.
''',encoding='utf8')
metadata={'title':'B2 기계층 전체 연결 에셋 기록 V0.01','author':'송예찬','date':'2026-11-09','scene':'Level_B2_Circular.unity','source':'SourceAssets/B2_FullFloor','varco':{'flow':'8f7100a4-a7df-488b-81ee-0c2ac6ae60d8','flowName':'After_Second_Env_and_Props_Ver0.03','task':'62d539b2-2962-4bdc-838f-825a6cb2384b','node':'cf409293-b38d-4953-98c3-e62ac942a75e','asset':'B2_EmergencyGenerator','remeshTriangles':18000,'pbrTextureSize':2048,'glbSha256':hashlib.sha256((H/'B2_EmergencyGenerator.glb').read_bytes()).hexdigest()},'models':{**read(H/'models.json'),**read(H/'Equipment/models.json')},'lodModels':read(H/'lod_models.json'),'runtimeScriptsAdded':0}
(A/'06.Data/AssetSources/B2_MachineryNetwork_V001.json').write_text(json.dumps(metadata,ensure_ascii=False,indent=2),encoding='utf8')
print(json.dumps({'protected':len(unchanged),'equipment':144,'access':naccess,'samples':samples,'lodGroups':len(lod),'docs':'written'},ensure_ascii=False))
