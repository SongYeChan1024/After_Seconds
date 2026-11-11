from pathlib import Path
import json,sys,hashlib,html,re,math
H=Path(__file__).resolve().parent;R=H.parents[1];U=R/'Unity/After_Seconds_Build_V0.01';O=R/'Docs/Review/2026-11-11_B1_StaffData'
sys.path.insert(0,str(U/'Temp/ZFightingReview/deps'))
from PIL import Image,ImageDraw,ImageFont
def read(p):return json.loads(p.read_text(encoding='utf8'))
def write(p,j):p.write_text(json.dumps(j,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
plan=read(H/'layout.json');audit=read(O/'audit.json');walk=read(O/'walk.json');play=[read(p) for p in sorted(O.glob('before_play_*.json'))];geo=[read(H/'geometry_verified'/n) for n in ['Level_B1_Circular.json','Level_B1_Circular_C05.json']]
before=read(H/'protected_before.json');changed=[p for p,sha in before.items() if not (R/p).exists() or hashlib.sha256((R/p).read_bytes()).hexdigest()!=sha]
assert not changed,changed
assert not audit['errors'] and not audit['forbiddenObjects'] and not audit['missingScripts']
assert all(q['passed'] for q in walk['results']) and not walk['planningFailures']
assert len(play)==4 and all(p['complete'] and p['framesAdvanced']>10 and p['displacement']>.3 and not p['errors'] for p in play)
assert all(not q['patches'] for q in geo)
models=read(H/'models_props.json');size=sum((U/q['asset']).stat().st_size for q in models.values());write(O/'preservation.json',dict(protectedFiles=len(before),changed=changed,retainedPlacementTransforms=136));write(O/'play_summary.json',play);write(O/'geometry_summary.json',dict(fullFloorBeforeConference=dict(exactOverlapPairs=geo[0]['overlapPairs'],patches=len(geo[0]['patches'])),finalConference=dict(exactOverlapPairs=geo[1]['overlapPairs'],patches=len(geo[1]['patches'])),toleranceM=.00005,scope='Opaque planar surfaces >=0.005m2, exclusive LODs excluded across renderers. Final C05 checked after conference extension; other rooms unchanged.'));write(O/'resources.json',dict(newFBX=2,newFBXMiB=round(size/2**20,3),newRuntimeCode=0,placements=len(plan['placements']),lodGroups=audit['lodGroups']))
oldoc=R/'Docs/Review/2026-11-11_B1_FullFloor/occlusion.json';write(O/'occlusion.json',read(oldoc))
# Reuse the tested floor drawing layout; all labels and footprints come from current plan.
f=lambda n:ImageFont.truetype('C:/Windows/Fonts/malgun.ttf',n)
source=(R/'SourceAssets/B1_FullFloor/write_report.py').read_text(encoding='utf8');drawing=source[source.index('# As-built geometry drawing'):source.index("roomlinks=''.join")]
drawing=drawing.replace('V0.01','V0.02').replace('174개 주요 프랍','198개 주요 프랍');exec(drawing)
cards=''.join(f'<figure><a href="{r["id"]}_room.jpg"><img loading="lazy" src="{r["id"]}_overview.jpg"></a><figcaption>{r["id"]} · {html.escape(r["name"])}</figcaption></figure>' for r in plan['rooms'])
page=f'''<!doctype html><html lang="ko"><meta charset="utf-8"><meta name="viewport" content="width=device-width"><title>B1 연구 데이터·직원 생활 검수 V0.01</title><style>body{{margin:36px auto;max-width:1400px;padding:0 24px;background:#141b20;color:#dfe5df;font:16px/1.7 system-ui}}a{{color:#a8d7ce}}.grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(330px,1fr));gap:18px}}figure{{margin:0;background:#253037;padding:10px;border-radius:8px}}img{{width:100%}}.facts{{padding:20px;background:#293b40}}</style><h1>B1 · 연구 데이터와 직원 생활</h1><p>송예찬 · 2026-11-11 · 용도 정정과 회의장 제작 V0.01</p><div class="facts">실험체 정상 활동: B5·B4 / B4→B3 상행 경계에서 출입 제한<br>B1 현장 능력 시험 없음 · 연구 자료 인계·열람·분석·보관 + 직원 생활<br>13공동·3코어·22통로·198프랍 · C05 8인 회의장<br>통행 {len(walk['results'])}/{len(walk['results'])} · 변경4구역 실제 Play · 기존 보호파일{len(before)}개 동일</div><h2>C05 연구 보고·직원 회의장</h2><a href="C05_room.jpg"><img src="C05_room.jpg"></a><p>4.2m 회의 테이블, 의자8개, 2.9m 자료 발표 화면, 발표 공간, 기록 보관장. 신규 FBX2개 합계 {size/2**20:.3f}MiB, 두 LOD 포함.</p><h2>용도 정정</h2><p>C01 자료 열람·대조 / C02 기록 인계·정리 / N01 데이터 분석. 시험 표적·센서·전극 준비·실험 카트리지 등 이전38배치를 제거했습니다. 기존136배치 위치를 보존했습니다. C04는 직원 의무실이며 숙소·식당·위생시설을 유지합니다.</p><p>출입 보안 화면은 B4 상층 경계를 확인하는 업무 맥락입니다. 직원 통제나 B1 실험체 관찰 시설을 의미하지 않습니다. 화면은 정적 아트이며 보안문·AI·실제 층 전환 동작은 후속입니다.</p><h2>현재 배치도</h2><img src="B1_as_built.png"><h2>공동별 화면</h2><div class="grid">{cards}</div><p><a href="Review.md">검수 결과</a> · <a href="walk.json">통행</a> · <a href="play_summary.json">Play</a> · <a href="geometry_summary.json">깊이 충돌 검수 범위</a> · <a href="preservation.json">기존 작업 보존</a></p></html>'''
(O/'review.html').write_text(page,encoding='utf8')
summary=f'''# B1 연구 데이터·직원 생활 용도 정정 V0.01

작성자 송예찬 · 2026-11-11

사용자 정정: 실험체는 정상 운영에서 B5·B4에 머물며 B4→B3부터 상행을 막는다. B3·B2·B1·1F는 정상 실험체 구역이 아니다. 플레이어의 상행은 이 경계를 뚫는 탈출이다. B1은 연구 데이터 업무와 직원 생활 공간이며 현장 능력 시험이나 직원 통제 공간이 아니다.

- C01: 연구 자료 열람·대조, 6개 업무석과 기록 보관/대조 테이블.
- C02: 연구 기록 인계·정리. 시료·전극·카트리지 준비대 제거.
- C05: 사용자 추가 요청의 8인 연구 보고·직원 회의장. 4.2m 테이블·2.9m 발표 화면·발표 공간·기록 보관장.
- N01: 연구 데이터 분석, 6개 업무석과 보관장.
- C04 직원 의무실, W01 사무실, W02 식당/조리, W03 숙소/위생, E02 기밀 기록, E03 경비 숙소/교대, S01 백업 보존. E01은 출입 보안 업무이며 실험체 현장 통제 시설이 아님.

## 변경과 검증

이전 시험 관련38배치 제거. 첫 직원/데이터 가구57배치 뒤 회의장5배치를10배치로 확장하여 총198개. 기존136배치의 위치·회전·크기는 유지했다. 새 3D는 회의 테이블/화면2종 {size/2**20:.3f}MiB, LOD0 합계8,222tri·LOD1 합계3,450tri. 나머지는 기존 씬의 보수된 메시·재질·LOD를 재사용했다.

- CharacterController {len(walk['results'])}/{len(walk['results'])}, 접근 계획 실패0. 전체 통로 왕복·방 출입·업무/회의 좌석 접근·18m 계단 왕복.
- 실제 Play C01·C02·C05·N01: 입력 이동·프레임 진행·새 경고/오류0. C05는 최종8인 회의장 배치 뒤 재검사.
- 메시·재질·스크립트 누락0, 금지된 현장 시험장비 이름0,198개 배치 계획과 저장 씬 일치.
- 깊이 충돌: 전체 직원/데이터 수정 후 중복0·내부 겹침0·0.05mm 정밀 평면 겹침0. 후속 회의장 C05도 중복0·내부0·정밀 겹침0. 면적0.005m² 이상 불투명 평면과 상호 배타적 LOD 구분 범위이며 모든 작은 면·모든 런타임 조명의 보증은 아님.
- 반사16개 갱신·가림 베이크 갱신, LOD328그룹·활성 광원209개.
- 기존 보호파일{len(before)}개 해시 동일. 다른 층·B2 펌프·게임 C#·Player·Animator 보존.

기획 V0.78·AI V0.06·코어 V0.08·획득 명세 V0.05·Decision V0.10에 역할과 경계를 동기화했다. 기존 이미지/PDF/엑셀은 이전 설계 이력임을 명시하고 현재 B1 제작 배치를 우선하도록 연결했다. 메인 규칙은 문서 확정이며 실제 보안문·AI·층간 전환은 미구현. 커밋·push 미요청/미실시.

[화면](review.html) · [현재 배치](B1_as_built.png) · [제작 원본](../../../SourceAssets/B1_StaffDataRevision/README.md)
'''
(O/'Review.md').write_text(summary,encoding='utf8')
(H/'README.md').write_text('''# B1 직원·연구 데이터 용도 보수 V0.01

작성자 송예찬 · 2026-11-11

사용자 정정의 B5/B4 실험체 구역·B4→B3 상행 경계와 B1 연구 데이터/직원 생활을 반영했다. C05는 후속 요청으로 8인 회의장이 됐다. [검수](../../Docs/Review/2026-11-11_B1_StaffData/Review.md)를 따른다.

현재 씬에 Apply/Conference/prepare/docs/conference_plan을 재실행하지 않는다. 이미 저장됐고 사용자 후속 편집을 덮어쓸 수 있다. 전체 B1_FullFloor 제작기도 재실행 금지다.

- before_layout.json / before_design_B1.json: 정정 전 배치·설계 이력. 현재 기준으로 복원하지 않는다.
- layout.json: 최종198배치. B1_FullFloor/layout.json과 Decision/B1_제작현황/as_built_layout.json에도 동일하게 저장.
- Apply.cs: 38배치 제거·57가구 복제·화면/빛 정정 및 회의장 확장 이력. 기존 보수 메시/LOD를 복제하고136개 잔여 배치 Transform 보존.
- conference_models.py: 회의 테이블/발표 화면 FBX2종 제작. 이전 공용 모델·meta를 덮어쓰지 않음. conference_plan.py는 초기4인 회의석을8인으로 바꾼 일회성 기록.
- Review/Play/ConferenceExport.cs, geometry.py: 외부 검수. Assets에 C# 추가하지 않음. geometry_scan/verified의 전체 결과는 회의장 확장 직전, C05 결과는 최종 확장 뒤. 두 결과를 함께 사용.
- run_play.py: 실제 입력/프레임/새 오류 검사, Play 종료·Run In Background 원상복구. 최종 C05 재검사 결과가 최신.
- finish.py: 검수 증거 확인 후 보고서/현재 배치도 생성 및 현행 문서 연결.

정상 운영의 실험체 출입 금지를 플레이어의 상행 불가로 바꾸지 않는다. 보안문·AI·층 전환·사용 가능한 발표 UI는 미구현. 다음은 사용자 C05 회의장 및 C01/N01 업무 공간 외형 확인. 커밋·push하지 않았다.
''',encoding='utf8')
(H/'.gitignore').write_text('__pycache__/\n*.log\n',encoding='utf8')
# Current status links: retain old reports as dated evidence, not current scene truth.
status='2026-11-11 B1 용도 보수 완료: 실험체 정상 활동은 B5/B4, B4→B3부터 상행 출입 제한. B1은 연구 데이터/직원 생활이며 현장 시험설비38배치 제거. C01 열람·C02 기록 인계·N01 분석, C05 사용자 요청8인 회의장. 현재198배치·260/260 통행·실제 Play4구역·최종 C05 재검사 통과. [현재 검수](Docs/Review/2026-11-11_B1_StaffData/Review.md)와 `SourceAssets/B1_StaffDataRevision/README.md`를 우선한다. 기존136배치 Transform·보호178파일 보존. 게임 기능/다른 층/Animator 미변경, 커밋·push 미실시. 이전 B1 전체 제작 기록과 도구는 현행 씬에 재실행하지 않는다. 다음은 사용자 C05/C01/N01 외형 검수다. 작성자 송예찬.'
for name in ['AGENTS.md','CLAUDE.md']:
 p=R/name;s=p.read_text(encoding='utf8');s=s.replace('\n\n','\n\n'+status+'\n\n',1);s=s.replace('B1·1F 최신 원형 씬 제작 및 층간 전환은 후속','B1 연구 데이터·직원 생활과8인 회의장 보수 완료.1F 제작 및 층간 전환은 후속');p.write_text(s,encoding='utf8')
p=R/'Docs/AfterSeconds_메인기획서.md';s=p.read_text(encoding='utf8');row=next(line for line in s.splitlines() if line.startswith('| V0.78 |'));s=s.replace(row+'\n\n','',1);s=s.replace('| --- | --- | --- | --- |\n| V0.77 |','| --- | --- | --- | --- |\n'+row+'\n| V0.77 |',1);s=s.replace('**2026-11-11 B1 최초 제작 이력','**2026-11-11 B1 현재 제작.** 연구 데이터·직원 생활 용도로198배치와 C05 8인 회의장을 완성했다. 전체260경로·변경4구역 실제 Play·최종 회의장 겹침 검수를 통과했다. [현재 화면/검수](Review/2026-11-11_B1_StaffData/review.html). 보안문·AI·층 전환은 후속이다.\n\n**2026-11-11 B1 최초 제작 이력',1);p.write_text(s,encoding='utf8')
p=R/'Docs/층별_획득오브젝트_명세.md';s=p.read_text(encoding='utf8').replace('**38종의 휴대 오브젝트와 55개 층별 등장 항목**','**현행35종·55개 층별 등장 항목** (기존38종 정의 중 B1 시험 소품3종은 배치 제외 이력으로 보관)');p.write_text(s,encoding='utf8')
p=R/'Docs/도면/Decision/원형공동/B1_제작현황/README.md';p.write_text('''# B1 현재 제작 배치 V0.02

작성자 송예찬 · 2026-11-11

B1은 연구 데이터 업무와 직원 생활층이다. 실험체 정상 활동은 B5/B4이며 B4→B3부터 상행 출입을 막는다. B1 현장 능력 실험은 없다.

`as_built_layout.json`은 현재198배치·13공동·3코어·22통로다. C01 자료 열람·대조, C02 기록 인계, C05 연구 보고·직원 회의장8석, N01 데이터 분석으로 정정했다. 직원 의무실·식당·숙소·위생과 백업/기밀 기록을 유지한다. 방 위치·연결과 T08 보수 유지.

[현재 배치도](../../../../Review/2026-11-11_B1_StaffData/B1_as_built.png) · [현재 화면](../../../../Review/2026-11-11_B1_StaffData/review.html) · [검수](../../../../Review/2026-11-11_B1_StaffData/Review.md)

260/260 통행·실제 Play4구역·회의장 최종 재검수. 정적 아트 단계이며 실제 보안문·AI·층 전환·장비 UI 동작은 미구현. 기존174배치/실험층 자료는 정정 전 이력이다. 제작기 재실행 금지.

- V0.02: 사용자 용도 정정과8인 회의장/현재198배치 반영. 송예찬.
''',encoding='utf8')
p=R/'SourceAssets/B1_FullFloor/README.md';s=p.read_text(encoding='utf8').replace('V0.01','V0.02',1);s=s.replace('\n\n','\n\n현재는 [B1 용도 보수](../B1_StaffDataRevision/README.md)가 최신이다.198배치와8인 회의장, B5/B4 실험체 경계가 현행이다. 아래174배치·시험 설비 설명은 초기 제작 이력이며 초기 생성기는 재실행하지 않는다. `layout.json`만 최종 배치로 동기화했다.\n\n',1);p.write_text(s,encoding='utf8')
for rel in ['Docs/Review/2026-11-11_B1_FullFloor/Review.md']:
 p=R/rel;s=p.read_text(encoding='utf8');s=s.replace('\n\n','\n\n이 문서는 용도 정정 전 제작 이력이다. 현재198배치·직원/연구 데이터·8인 회의장은 [후속 검수](../2026-11-11_B1_StaffData/Review.md)를 따른다.\n\n',1);p.write_text(s,encoding='utf8')
p=R/'Docs/Review/2026-11-11_B1_FullFloor/review.html';s=p.read_text(encoding='utf8');s=s.replace('<h1>','<p><b>이전 제작 이력입니다.</b> <a href="../2026-11-11_B1_StaffData/review.html">현재 직원·연구 데이터/8인 회의장 검수</a></p><h1>',1);p.write_text(s,encoding='utf8')
p=R/'Docs/도면/Decision/원형공동/facility_layout.json';j=read(p);b=next(x for x in j['floors'] if x['id']=='B1');next(x for x in b['rooms'] if x['id']=='C05')['name']='연구 보고·직원 회의장';next(x for x in j['rooms'] if x['floor']=='B1' and x['id']=='C05')['name']='연구 보고·직원 회의장';j['production_status']['B1_StaffData'].update(status='용도 정정과8인 회의장 제작/검수 완료',placements=198,conference_seats=8,walk_routes=260,play_regions=4);write(p,j)
p=U/'Assets/Afrer_Seconds/06.Data/AssetSources/B1_FullFloor.json';j=read(p);j['title']=j['title'].replace('V0.01','V0.02');j['current_revision']=dict(source='SourceAssets/B1_StaffDataRevision',review='Docs/Review/2026-11-11_B1_StaffData/Review.md',placements=198,role='연구 데이터·직원 생활',conference_seats=8,boundary='B4->B3',unused_trial_models=['BL_TrialTargetRail','BL_PredictiveSensorFrame','BL_ExperimentCartridges']);j['models'].extend(models.values());write(p,j)
print(json.dumps(dict(placements=len(plan['placements']),walk=len(walk['results']),play=len(play),protected=len(before),newFBXMiB=round(size/2**20,3)),ensure_ascii=False))
