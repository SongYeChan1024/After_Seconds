from pathlib import Path
from decimal import Decimal
import json,re,hashlib,shutil
R=Path(__file__).resolve().parents[2];H=R/'SourceAssets/B5_FullLayout';O=R/'Docs/검수/2026-11-06_B5_FullLayout';D=R/'Docs/도면/Decision/원형공동';S=R/'SourceAssets/B5_Sector01'
def read(p):return json.loads(p.read_text('utf-8'))
def write(p,v):p.write_text(json.dumps(v,ensure_ascii=False,indent=2),encoding='utf-8')
if (H/'record_finalized.json').exists():raise SystemExit('Already recorded; do not duplicate version updates.')
audit=read(O/'audit.json');walk=read(O/'controller_walk.json');doors=read(O/'door_validation.json');imp=read(O/'implementation.json')
assert len(audit['domes'])==15 and len(audit['tunnels'])==19 and not audit['blocked'] and not audit['groundMissing']
assert len(walk)==38 and all(r['passed'] for r in walk)
assert len(doors)==38 and all(r['openClear'] and r['closedBlocks'] for r in doors)
assert not read(O/'clinical_prop_check.json') and not read(O/'outer_prop_check.json')
for label in ('inside','tunnel'):
    p=read(O/f'play_{label}.json');assert p['complete'] and p['framesAdvanced']>100 and p['displacement']>.5 and not p['errors']
baseline=read(H/'protected_before.json');changed=[name for name,sha in baseline.items() if not (R/name).exists() or hashlib.sha256((R/name).read_bytes()).hexdigest()!=sha]
assert len(changed)==1 and Path(changed[0]).name=='Level_B5_Circular.unity',changed
write(O/'protection.json',dict(protected=len(baseline),unchanged=len(baseline)-1,changed=changed,runtime_code_changes=0))
if read(D/'B5_섹터/sector_plan.json')['title'].endswith('V0.04'):
    archive=R/'Docs/도면/Old/원형공동/B5_섹터/V0.04';archive.mkdir(parents=True,exist_ok=True)
    for name in ('sector_plan.json','scene_reference.json','B5_섹터구분도.svg','B5_섹터구분도.png'):
        if not (archive/name).exists():shutil.copy2(D/'B5_섹터'/name,archive/name)
write(D/'B5_섹터/scene_reference.json',dict(scene=audit['scene'],dirty=False,playing=False,domes=audit['domes'],tunnels=audit['tunnels'],evidence='Docs/검수/2026-11-06_B5_FullLayout/audit.json'))
plan=read(D/'B5_섹터/sector_plan.json')
for u in plan['sectors']+plan['cores']+plan['corridor_area']['segments']:
    u['structure_present']=True;u['complete']=False
    u['evidence']='Docs/검수/2026-11-06_B5_FullLayout/검수결과.md'
    if u.get('kind')=='core':u['status']='외피·평면 접속 / 층간 계단·승강로 미완료'
    elif u.get('room_id')=='C01':
        u['status']='실험 배치·곡면 패널·3출입구 반영 / 세부 아트 미완료';u['checks']['구조·문 접합']=True
        u['review_note']='이번 실험 배치와 T11 연결 검수는 새 검수 기록을 따른다. 이전 생활실 검사는 과거 이력이다.'
    elif u.get('room_id') in ('W01','W02'):u['status']='기본 구조·생활 가구 4모듈 / 세부 마감 미완료'
    elif u.get('room_id'):u['status']='기본 구조 / 프랍·세부 마감 미완료'
    else:u['status']='구조·문·왕복 통행 검수 / 세부 마감 미완료';u['checks']['구조·문 접합']=True
write(D/'B5_섹터/sector_plan.json',plan)
old=read(S/'latest_scope.json')['decision']
new='2026-11-06 Unity 반영: 조감도의 B5 일반 공동12개·이동 코어3개·연결 복도19개 전체 평면 구조를 Level_B5_Circular 씬에 제작·저장했다. 문38세트, C01의 T01·T03·T11 출입 연결, 실험 계측 포드·관찰 콘솔·곡면 벽 패널을 반영했다. C01 생활 배치는 비활성 보관하고 W01·W02에 생활 가구 각4모듈을 배치했다. 복도4854표본 막힘·바닥 누락0, CharacterController 왕복38회 및 문38세트 검수 통과. Play 두 구간 실제 이동·프레임 진행·새 경고/오류0을 확인했다. 전체 기본 구조 반영과 아트 완성은 구분한다. 외곽 프랍24배치의 에셋, 층간 계단·승강로, C01 세부 마감이 남아 아트 완료는0/34다. 최신 기록은 Docs/검수/2026-11-06_B5_FullLayout/검수결과.md, 제작 원본은 SourceAssets/B5_FullLayout이다.'
for name in ['AGENTS.md','CLAUDE.md','Docs/AfterSeconds_메인기획서.md','Docs/이어하기_2026-11-06.md','Docs/회사_작업목록_2026-11-06.md','Docs/도면/Decision/원형공동/README.md','SourceAssets/B5_Sector01/README.md']:
    p=R/name;text=p.read_text('utf-8');assert old in text,name;head,body=text.split('\n',1);head=re.sub(r'V(\d+\.\d+)',lambda m:f'V{Decimal(m[1])+Decimal("0.01"):.2f}',head);p.write_text((head+'\n'+body).replace(old,new,1),encoding='utf-8')
with (R/'Docs/AfterSeconds_메인기획서.md').open('a',encoding='utf-8') as f:f.write('\n- V0.34 (2026-11-06): B5 전체12공동·3코어·19복도와 C01 실험 배치를 Unity에 반영. 통행·문·Play 검수, 외곽 세부 아트와 층간 구조의 미완료 범위를 구분. 송예찬.\n')
p=R/'Docs/회사_작업목록_2026-11-06.md';text=p.read_text('utf-8');start=text.index('## 최신 우선 작업:');end=text.index('아래는 이번 구분 이전의 작업 기록이다.',start)
block='## 최신 우선 작업: B5 전체 평면 구현 이후\n\n작성자 송예찬 · 2026-11-06. [Unity 구현·검수 기록](검수/2026-11-06_B5_FullLayout/검수결과.md), [섹터도 V0.05](도면/Decision/원형공동/B5_섹터/B5_섹터구분도.png)를 따른다. 전체 평면이 실제 씬에 있으며, 아트 완료 판정은0/34다.\n\n| 구역 | 현재 상태 |\n| --- | --- |\n'
for u in plan['sectors']+plan['cores']:block+=f'| {u["room_id"]} {u["name"]} | {u["status"]} |\n'
block+='\nT01~T19 전체: 기본 구조·문38세트·4,854표본·양방향38회 통행 검수 완료. 복도별 배선·안내선·재질·조명 세부 마감은 남는다.\n\n- [x] 외곽 공동8개·복도12개와 기존 공동의 새 출입부를 실제 Unity에 연결.\n- [x] C01 생활 배치를 실험 계측·관찰 용도로 변경하고 W01·W02에 생활 가구 배치.\n- [x] T11을 막던 기존 벽면 설비 이동, 새 프랍의 BoxCollider 간섭 검사.\n- [x] C01/T11 Play 입력·프레임 진행 확인, 편집 상태·시작 위치 복구.\n- [ ] C01 장비 배선·단자·실험 소품과 조명·표면 마감.\n- [ ] 외곽 부족 프랍24배치에 필요한 에셋 제작 및 각 공동의 세부 마감.\n- [ ] VA/VB 실제 층간 계단·참과 VL 승강로 연결.\n- [ ] 공동별 실제 잠입 동선·시야·성능 검수 및 사용자 아트 검수.\n\nAI·문·스위치·미니맵 동작은 사용자 직접 구현 범위를 유지한다.\n\n'
p.write_text(text[:start]+block+text[end:],encoding='utf-8')
scope=read(S/'latest_scope.json');scope.update(version='V0.04',decision=new,scene_role_update_pending=False,basic_structure_implemented=True,complete=False);write(S/'latest_scope.json',scope)
decision=read(S/'decision.json');decision.update(decision=new,scene_role_update_pending=False);write(S/'decision.json',decision)
catalog={c['code']:c['name'] for c in read(D/'facility_layout.json')['catalog']}
missing='\n'.join('- '+x+' — '+catalog.get(x.split()[-1],'') for x in imp['missingOuterPropAssets'])
perf=[read(O/f'play_{x}.json') for x in ('inside','tunnel')]
report=f'''# B5 전체 평면 구현 검수 V0.01

작성자 송예찬 · 2026-11-06

`Level_B5_Circular.unity`에 조감도의 일반 공동12개, 이동 코어3개, 연결 복도19개를 실제 메시·충돌·문과 함께 반영했다. 새 공동8개·복도12개 및 기존 공동의 연결 구멍을 추가했고, 전체 문은38세트다. 구조만 존재하던 이전 상태에서 전체 평면 통행이 가능한 상태로 확장했다.

C01은 침상·위생·개인 책상 배치를 비활성 보관하고 실험 계측 포드, 관찰 콘솔2개, 기록장·밀폐 폐기함, 곡면 벽 패널·보강 리브를 반영했다. 서쪽 T11 출입부 주변의 기존 설비6개를 옮겼다. W01·W02에는 기존 VARCO/Blender 에셋으로 생활 가구 각4모듈을 배치했다. 새 건축·패널·리브·계측 장치는 Blender 편집 원본에 베벨을 남기고 명시 삼각화해 반입했다.

## 확인한 결과

| 검사 | 결과 |
| --- | --- |
| 활성 돔/코어 외피 | 15개 = 일반 공동12 + 코어3 |
| 활성 터널 | 19개, 도면 연결 일치 |
| 복도 중앙·좌우 캡슐 검사 | 4,854표본, 막힘0·바닥 누락0 |
| 실제 CharacterController 왕복 | 38/38 통과, 도착 오차0.06m 미만 |
| 문 열린/닫힌 정적 충돌 | 38/38 통과, 검사 후 열린 상태 복구 |
| 신규 임상 설비4개 및 외곽 BoxCollider27개 | 35mm 초과 관통0 |
| 메시·재질 누락 | 0 |
| 모델 반입 경고·오류 | 0 |
| Play 입력·프레임 | C01 {perf[0]['framesAdvanced']}프레임 / T11 {perf[1]['framesAdvanced']}프레임 진행 |
| W 입력 이동 | C01 {perf[0]['displacement']:.2f}m / T11 {perf[1]['displacement']:.2f}m |
| 5초 Editor 측정 중앙값 / p95 | C01 {perf[0]['medianMs']:.2f}/{perf[0]['p95Ms']:.2f}ms, T11 {perf[1]['medianMs']:.2f}/{perf[1]['p95Ms']:.2f}ms |
| Play 새 경고·오류 | 0 |
| 보호 파일 | {len(baseline)-1}/{len(baseline)} 동일, 승인된 B5 씬만 변경 |

프레임 수가1만 증가했던 최초 비활성 창 측정은 폐기하고, 백그라운드 실행을 켠 뒤 실제 프레임 진행과 이동을 재측정했다. 위 성능은 이 PC의 Editor 1920×1080 두 구간5초 측정이며 전체 게임 성능 보장은 아니다. CharacterController의 약0.08m 스킨 접지 오차는 기존 설정 범위다. 임의의 프랍 MeshCollider끼리 모든 면 관통이나 층간 이동을 검수한 결과는 아니다.

## 실제 Unity 화면

- [전체 평면 절개 검수 화면](B5_AllCaverns_Cutaway.png): 촬영 때만 지붕 상부를 숨겼으며 저장 씬의 지붕은 유지한다.
- [C01 실험 공동 입구](C01_Entrance.png), [서쪽 T11 출입부](C01_New_WestExit.png)
- [W01 생활 가구](W01_Living.png), [T11 터널](T11_Corridor.png)
- [C01 실제 Play](B5_Full_Play_C01.png), [T11 실제 Play](B5_Full_Play_Tunnel.png)

## 남은 제작

아트 완료는0/34로 유지한다. C01 장비의 세부 배선·단자·소품, 외곽 공동의 설비와 표면 마감, 구역별 안내선·조명 마감, 코어의 실제 층간 계단·승강로가 남는다. 기존 프랍 목록에서 연결된 에셋이 없는 외곽24배치는 아래에 기록했다. 이 목록은 프랍 종류24종이 아니라 배치24개다. 문·AI·키패드·스위치·미니맵의 게임 동작은 사용자 직접 구현 범위다.

{missing}

검사 원본은 `audit.json`, `controller_walk.json`, `door_validation.json`, `clinical_prop_check.json`, `outer_prop_check.json`, `play_inside.json`, `play_tunnel.json`, `protection.json`이다. 제작기는 `SourceAssets/B5_FullLayout`에 있으며 이전7공동 생성기나 생활실 완료 처리기를 다시 실행하지 않는다.
'''
(O/'검수결과.md').write_text(report,encoding='utf-8')
(H/'README.md').write_text('''# B5 전체 평면 제작 원본 V0.01

작성자 송예찬 · 2026-11-06

Decision 조감도의12공동·3코어·19복도를 기존 B5 씬에 반영한 원본이다. [검수 기록](../../Docs/검수/2026-11-06_B5_FullLayout/검수결과.md)을 따른다. 기본 평면 구현 완료와 세부 아트·층간 구조 완성을 구분한다.

- `build_layout.py`: 기존 CF/S1의 형상 제작 함수만 읽어 새 AF 모델5개를 생성한다. 기존 모델 원본은 덮어쓰지 않는다. AF 모델의 후속 수정을 확인한 뒤 실행한다.
- `ApplyFullLayout.cs`: 반입과 최초 씬 반영. Apply는 이미 반영한 그룹이 있으면 중단한다. 사용자의 후속 편집을 지우기 위해 이 방어를 제거하지 않는다.
- `RepairFullLayout.cs`: T11 주변 설비6개 위치 보정. 이후 사용자 배치가 있으면 자동 재실행하지 않는다.
- `VerifyFullLayout.cs`, `WalkFullLayout.cs`, `DetailAudit.cs`: 저장된 B5 편집 상태에서 구조·문·프랍·왕복 검수. Capture는 촬영용 절개를 일시 적용하고 저장 씬을 다시 연다.
- `PlayFullLayout.cs`: Play에서 현재 플레이어를 두 검수 위치로 일시 이동하여5초간 입력·프레임·오류를 검사한다. 백그라운드 실행과 자동 tick을 먼저 확인하고, 검사 뒤 Play를 종료해 저장 위치로 복구한다.
- `before.unity`, `protected_before.json`: 반영 전 기록. 자동 덮어쓰기·복구를 하지 않는다.
- 모든 C#은 Assets 밖의 Editor 제작/검수 도구다. 게임 런타임 코드는 추가하지 않았다.
''',encoding='utf-8')
asset=R/'Unity/After_Seconds_Build_V0.01/Assets/Afrer_Seconds/06.Data/AssetSources/B5_FullLayout.json'
write(asset,dict(version='V0.01',author='송예찬',scene=imp['scene'],basic_structure=dict(caverns=12,cores=3,tunnels=19,doors=38),geometry=read(H/'geometry_manifest.json'),report='Docs/검수/2026-11-06_B5_FullLayout/검수결과.md',missing_outer_placements=imp['missingOuterPropAssets'],art_complete=False,runtime_code_added=False))
write(H/'record_finalized.json',dict(verified=True,art_complete=False,changed_protected_files=changed))
print(json.dumps(dict(recorded=True,protected_unchanged=len(baseline)-1,changed=changed),ensure_ascii=False))
