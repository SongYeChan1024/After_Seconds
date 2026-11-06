from pathlib import Path
import json,hashlib,shutil,re
R=Path(__file__).resolve().parents[2];S=R/'SourceAssets/B5_Sector01';O=R/'Docs/검수/2026-11-06_B5_Sector01';D=R/'Docs/도면/Decision/원형공동'
def read(p):return json.loads(p.read_text('utf-8'))
def write(p,obj):p.write_text(json.dumps(obj,ensure_ascii=False,indent=2),encoding='utf-8')
raise RuntimeError('이전 생활실 초안의 완료 도구는 사용 종료했습니다. C01 실험 공동과 전체 34개 작업 단위를 새로 검수해야 합니다.')
before=read(S/'protected_before.json');changed=[]
for name,sha in before.items():
 p=R/name
 if not p.exists() or hashlib.sha256(p.read_bytes()).hexdigest()!=sha:changed.append(name)
assert len(changed)==1 and changed[0].endswith('Level_B5_Circular.unity'),changed
audit=read(O/'audit.json');walk=read(O/'controller_walk.json');state=read(O/'final_state.json')
assert not audit['blocks'] and not audit['overlaps'] and not audit['missing'] and not audit['matMissing']
assert all(x['passed'] for x in walk)
assert all(x['openClear'] and x['closedBlocks'] for x in state['doors']) and len(state['doors'])==2
assert all(read(O/f'play_{x}.json')['framesAdvanced']>100 and not read(O/f'play_{x}.json')['errors'] for x in ['inside','outside'])
oldprops={x['name']:x for x in read(O/'before.json')['props']};moved=[]
for p in state['oldProps']:
 if p['position']!=oldprops[p['name']]['position'] or p['rotation']!=oldprops[p['name']]['rotation']:moved.append(p['name'])
assert set(moved)<=set(['B5-03_P03','B5-06_P09','B5-07_P13']),moved
write(O/'protection.json',dict(protected_files=len(before),unchanged=len(before)-len(changed),changed=changed,old_props_moved=moved,game_code_changed=False,other_scenes_unchanged=True))
decision='사용자 확인: 새 Decision 전체 조감도는 참고용이다. C01 내부 배치는 현재 Unity의 포드 내부 생활시설·외부 관찰/진료 구획을 유지한다.'
write(S/'decision.json',dict(date='2026-11-06',decision=decision,reference='Docs/도면/Decision/원형공동/층별조감도/B5_실내조감도.png',reference_only=True,layout_source_sha256=hashlib.sha256((D/'facility_layout.json').read_bytes()).hexdigest()))
source=dict(version='V0.01',author='송예찬',sector='B5 C01',decision=decision,varco=read(S/'varco_record.json'),blender=read(S/'detail_manifest.json'),placements=state['instances'],scene=state['scene'],runtime_code_added=False)
ap=R/'Unity/After_Seconds_Build_V0.01/Assets/Afrer_Seconds/06.Data/AssetSources/B5_Sector01.json';write(ap,source)
planfile=D/'B5_섹터/sector_plan.json';plan=read(planfile);archive=R/'Docs/도면/Old/원형공동/B5_섹터/V0.01';archive.mkdir(parents=True,exist_ok=True)
for f in ['sector_plan.json','B5_섹터구분도.png','B5_섹터구분도.svg']:
 target=archive/f
 if not target.exists():shutil.copy2(planfile.parent/f,target)
plan['title']='B5 현재 제작 구역 섹터도 V0.02';one=plan['sectors'][0];one['complete']=True;one['status']='레벨·아트 제작 및 기술 검수 완료 / 사용자 시야 확인';one['checks']={k:True for k in one['checks']};one['evidence']='Docs/검수/2026-11-06_B5_Sector01/검수결과.md';one['review_note']='AI·교환·배식구·문 동작은 사용자 직접 코딩 범위. 닫힌 포드의 탈출 기능을 구현한 상태가 아님.';plan['next']='B5-T01';plan['latest_decision']=decision;write(planfile,plan)
report='''# B5 1섹터 레벨 아트 검수 V0.01

작성자 송예찬 · 2026-11-06

`Level_B5_Circular`의 C01 피험체 격리 구역을 제작하고 레벨·아트 검수를 마쳤다. 포드 내부는 생활시설, 바깥은 관찰·진료·보급 공간이다. 새 Decision 조감도는 사용자 확인에 따라 분위기 참고로 사용하며, 그림 속 포드 밖 생활가구 배치를 적용하지 않는다.

## 제작 결과

- 기존 8m급 포드와 돔·출입구·배식구를 보존했다. 포드 안에 성인용 침상, 책상과 스툴, 개인 사물함, 개인 상자, 세면·변기 일체형 설비, 낮은 위생 칸막이, 거울·호출 패널·수건·세면도구·독서/배식 소품을 배치했다.
- 바깥에는 생체신호 기록기·진료 카트·보급장을 두고 시계와 기록판에 지지대를 추가했다. 회전 분리 CCTV 외형을 고정 지지대에 설치했다. CCTV 감지·회전은 미구현이다.
- 곡면 보강 리브, 곡면 기단, 두 출입구 접합 칼라, 바닥 이음새와 사용 흔적, 벽 작업등 4개와 포드 조명을 마감했다. 금속과 도장 재질을 구분하고 새 가공부에 베벨을 적용했다.
- VARCO에서 침상·위생 유닛·생체신호 기록기 3종을 생성·리메시했다. Blender에서 치수·베벨·3단계 LOD·PBR를 정리했고, 건축과 세부 가구/소품 20종을 Blender 원본으로 보관했다. 신규 그룹은 조명 2개를 포함한 29개 직계 오브젝트다.

## 검수

| 검사 | 결과 |
| --- | --- |
| B5 주 경로·우회 경로 | 690표본, 새 막힘 0 |
| 실제 CharacterController 이동 | 내부 생활·침상·위생·책상, 바깥 동서·직원 통로·북측 입구 8경로 통과 |
| 두 출입구 | 열린 상태 통과·닫힌 문 충돌 확인, 원래 열린 위치 복구 |
| 신규 주요 프랍 | 박스 충돌 중첩 검사 0, 누락 메시·재질 0, VARCO 3종 LOD 각 3단계 |
| 실제 Input System W 입력 | 내부 516프레임·외부 634프레임 진행, 각각 이동 확인 |
| 1920×1080 에디터 성능 | 내부 중앙값 9.04ms·95백분위 10.79ms, 외부 중앙값 7.69ms·95백분위 8.95ms |
| 신규 그룹 최고 LOD | 167,917 삼각형; 전체 씬과 구분 |
| 보호 검사 | 게임 C#·Controller·다른 씬 불변, 기존 시작 위치 복구 |

성능은 이 PC의 짧은 Play 측정이며 최종 빌드 성능 보증은 아니다. 각 입력 측정 구간에서 새 경고·오류는 0건이었다. 캡처 경로와 검수용 카메라 조회의 도구 오류는 수정했으며 게임 코드 오류와 구분한다. 문·포드 탈출·교환·AI·UI를 구현하거나 플레이 퍼즐을 완성한 결과가 아니다. 다른 6섹터와 복도 7구역은 미완료다. 닫힌 사물함 내부 소품까지 가시 모델로 제작한 것은 아니다.

## 화면과 근거

- [포드 생활공간](S1_Inside_Living.png), [책상과 출입구](S1_Inside_Desk.png), [위생 구획](S1_Hygiene.png)
- [입구 전경](S1_Entrance.png), [진료·보급 공간](S1_Staff_Arc.png), [배식구](S1_Hatch.png)
- [실제 Play 내부](S1_Play_Inside.png), [실제 Play 외부](S1_Play_Outside.png)
- [경로·에셋 검사](audit.json), [Controller 이동](controller_walk.json), [Play 내부](play_inside.json), [Play 외부](play_outside.json), [최종 배치](final_state.json), [보호 파일 비교](protection.json)

제작 원본은 `SourceAssets/B5_Sector01`, 반입·배치 명세는 `06.Data/AssetSources/B5_Sector01.json`이다. 엑셀 V0.03과 전체 배치 JSON은 기존 가안을 유지하므로 C01의 실제 배치는 이 반입 기록과 최종 배치 기록을 우선한다. 다음 작업 단위는 T01이며 그 다음이 2섹터다. 로컬 저장 상태이며 커밋·push하지 않았다.
'''
(O/'검수결과.md').write_text(report,encoding='utf-8')
(S/'README.md').write_text('''# B5 1섹터 제작 원본 V0.01

작성자 송예찬 · 2026-11-06

현재 씬의 C01 레벨·아트 마감 원본이다. [검수 결과](../../Docs/검수/2026-11-06_B5_Sector01/검수결과.md)를 먼저 읽는다. 새 Decision 조감도는 분위기 참고이며 포드 안 생활시설 배치는 사용자 확인대로 유지한다.

VARCO 3종과 Blender 20종의 편집 원본·생성/반입 기록을 보관한다. 모든 C#은 Assets 밖의 제작·검수 도구이며 게임 런타임 스크립트가 아니다. `start.py`·`InspectSector.Read`는 작업 전 스냅샷이므로 재실행하지 않는다. `ApplySector.Apply`는 현재 그룹을 재생성하므로 후속 사용자 편집을 확인하지 않고 다시 실행하지 않는다. 현재 최종 배치는 검수 폴더의 `final_state.json`과 Unity 씬을 우선한다.

원본 제작 순서는 prepare_varco.py → build_details.py/make_textures.py → Import → Apply → RefineSector → PolishSector → DeskSector → FinishSector → CollarSector였다. 이후 추가 보수와 명시 재반입을 수행했으므로 이 순서를 자동 재실행하는 것은 복구 절차가 아니다. `AuditSector`, `WalkSector`, `FinalCheck`는 저장된 Edit 씬에서 사용하며 `PlaySector`는 기존 입력·이동 코드를 실제 Play에서 검수하고 일시 설정을 복구한다.
''',encoding='utf-8')
def update_header(path,new_version,paragraph):
 text=path.read_text('utf-8');lines=text.splitlines();lines[0]=re.sub(r'V\d+\.\d+',new_version,lines[0]);path.write_text(lines[0]+'\n\n'+paragraph+'\n\n'+'\n'.join(lines[1:]).lstrip()+'\n',encoding='utf-8')
summary='2026-11-06 1섹터 레벨·아트 제작 및 기술 검수 완료: [검수 기록](Docs/검수/2026-11-06_B5_Sector01/검수결과.md), [제작 원본](SourceAssets/B5_Sector01/README.md)을 우선한다. 현재 1/14단위이며 다음은 T01 → 2섹터다. 새 Decision 전체 조감도는 참고용이고 포드 내부 생활시설·외부 진료/관찰 배치를 유지한다는 사용자 확인을 받았다. 게임 C#·Controller·다른 씬과 기존 플레이어 시작 위치를 보존했다. 게임 기능은 사용자 직접 구현 범위다. 아래 0/14·1섹터 대기는 이전 이력이다.'
for name in ['AGENTS.md','CLAUDE.md']:update_header(R/name,'V0.34',summary)
update_header(R/'Docs/이어하기_2026-11-06.md','V0.18',summary.replace('(Docs/','(').replace('(SourceAssets/','(../SourceAssets/'))
mp=R/'Docs/AfterSeconds_메인기획서.md';update_header(mp,'V0.31','2026-11-06 사용자 확인: 새 Decision 전체 조감도는 분위기·구성 참고용이다. C01은 현재 Unity 제작처럼 포드 내부에 생활시설을 두고 바깥에 관찰·진료·보급 장비를 둔다. 1섹터 레벨·아트와 통행·Play 검수를 마쳤고 현재 1/14단위다. [검수](검수/2026-11-06_B5_Sector01/검수결과.md)를 따른다. 다음은 T01이며 게임 기능은 별도 구현한다. 아래 문단은 제작 시작 당시 이력이다.')
with mp.open('a',encoding='utf-8') as f:f.write('\n- V0.31 (2026-11-06): Decision 조감도의 참고 범위와 C01 내부 생활 배치 유지 확인. 1섹터 레벨·아트 검수 완료, T01로 다음 단위 이동. 송예찬.\n')
wl=R/'Docs/회사_작업목록_2026-11-06.md';text=wl.read_text('utf-8').replace('작업 목록 V0.15','작업 목록 V0.16',1).replace('부분 제작, 다음 작업','레벨·아트 검수 완료',1).replace('현재 완료0/14단위이며 기존 일부 제작 진행은 유지한다.','현재 완료1/14단위이며 [1섹터 검수 기록](검수/2026-11-06_B5_Sector01/검수결과.md)을 따른다. 다음은 T01이다.',1).replace('현재 실제 씬을 읽어 돔7개·터널7개와 위치를 대조했고, Unity 씬은 변경하지 않았다.','현재 1섹터의 Unity 레벨·아트 제작과 이동·성능 검수를 마쳤다. 새 조감도는 참고이며 포드 안 생활시설 배치를 유지한다.',1);wl.write_text(text,encoding='utf-8')
print(json.dumps(dict(protected=len(before),changed=changed,completion='1/14',next='B5-T01',source=ap.as_posix()),ensure_ascii=False))
