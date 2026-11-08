from pathlib import Path
import json,hashlib,shutil
H=Path(__file__).resolve().parent;R=H.parents[1];P=R/'Unity/After_Seconds_Build_V0.01';O=R/'Docs/검수/2026-11-08_EnglishNaming'
def read(p):return json.loads(p.read_text(encoding='utf8'))
results=read(H/'result.json');plan=read(H/'rename_plan.json');inventory=read(H/'scene_inventory.json');baseline=read(H/'baseline.json')
assert sum(r['renamed'] for r in results)==1799 and all(not r['nonNameChanges'] and r['remainingKoreanNames']==0 for r in results)
expected={'Assets/Afrer_Seconds/01.Scenes/Stage/Level_B4_Circular.unity','Assets/Afrer_Seconds/01.Scenes/Stage/Level_B5_Circular.unity'};changed=[];missing=[]
for f,h in baseline.items():
 p=P/f
 if not p.exists():missing.append(f)
 elif hashlib.sha256(p.read_bytes()).hexdigest()!=h:changed.append(f)
assert not missing and set(changed)==expected,changed
new={(r['scene'],r['id']):r['new'] for r in plan};nonascii=[];objects=0
for s in inventory:
 for row in read(H/(Path(s['path']).stem+'_before.json')):
  name=new.get((s['path'],row['id']),row['name']);objects+=1
  if not name.isascii():nonascii.append(name)
assert not nonascii,nonascii
plays=[read(O/f'play_{n}.json') for n in ['C01','B5']];assert all(p['complete'] and not p['errors'] and p['displacement']>.1 and p['framesAdvanced']>0 for p in plays)
preserve={'protectedFiles':len(baseline),'unchanged':len(baseline)-len(changed),'changed':changed,'missing':missing,'scenesScanned':len(inventory),'sceneObjects':objects,'nonAsciiNames':nonascii,'serializedObjectsCompared':sum(r['comparedObjects'] for r in results),'nonNameChanges':0}
(O/'preservation.json').write_text(json.dumps(preserve,ensure_ascii=False,indent=2)+'\n',encoding='utf8');shutil.copy2(H/'result.json',O/'rename_result.json')
shutil.copy2(R/'Docs/검수/2026-11-08_B4_ExperimentOperations/final_state.json',O/'final_state.json')
table='\n'.join(f"| {p['label']} | {p['displacement']:.3f}m | {p['framesAdvanced']} | {len(p['errors'])} |" for p in plays)
(O/'review.md').write_text(f'''# Unity 영문 이름 정리 V0.01

작성자 송예찬 · 2026-11-08

사용자가 프로젝트 내부의 한글 이름을 짧고 알아보기 쉬운 영어로 변경하도록 요청했다. Unity 전체13씬을 조사하고 **B4 1,577개·B5 222개, 총1,799개 하이라키 이름**을 변경했다. 한글 이름1,778개와 화살표 기호가 있던 복도 이름21개를 정리했다. 에셋·폴더 경로의 한글은 처음부터0개였다. 문서/블로그 본문은 한국어로 유지한다.

## 규칙과 예시

- 구역 코드 + 간결한 기능 + 필요한 번호. ASCII 영문·숫자·밑줄을 기본으로 한다.
- `B4_ResearchFloor_V0.03` → `B4_ExperimentEquipment` → `B4_W01_Equipment` → `B4_W01_ObservationBooth_01`.
- `B5_CeilingLights` → `C01_CeilingLights` → `C01_CeilingLight_01` → `Light`.
- 복도 목적지 `B4_T01_To_C02_GuideLine`, 화면 표기 `B4_T01_To_C02_FloorLabel`.
- 영어 이름의 복도 연결 기호 `↔`21개를 밑줄로 바꿨으며 그 외 기존 영어 이름은 유지했다. 같은 부모 아래 반복된 LightRig3개만 번호를 붙여 중복을 풀었다.

## 보존과 검증

- Unity 네이티브 API로 GameObject.name과 프리팹 인스턴스 이름 오버라이드만 변경했다. 파일 이동·GUID 변경·수동 YAML 편집은 하지 않았다.
- 이름을 원래 값으로 정규화한 Editor 직렬화 데이터 **{preserve['serializedObjectsCompared']:,}개**를 전후 비교해 차이0을 확인했다. 위치·회전·크기·활성·태그·레이어·재질/메시·광원·Collider·스크립트/Animator 설정과 직렬화 참조가 유지됐다.
- 전체13씬 **{objects:,}개 오브젝트**의 최종 이름이 ASCII 범위다. 나머지11씬은 이름 변경이 필요하지 않았고 파일도 그대로다.
- 기존 Assets/Packages/ProjectSettings {len(baseline):,}파일 중 대상 B4/B5 씬2개만 변경, 나머지{preserve['unchanged']:,}파일 SHA-256 동일. 기존 모든.meta와 모델·재질·텍스처·게임 C#·Animator·사용자 설정 보존.
- 게임 C#에서 한글 이름을 직접 찾는 조회는 발견되지 않았다. 변경 대상에 영향을 받는 Animator 클립 경로는 없었다. 현재 B4/B5 검수 도구와 최신 배치 JSON의 객체 이름/경로는 영문으로 갱신했다.

| 이름 변경 후 실제 키보드 Play | 이동 | 진행 프레임 | 새 게임 경고·오류 |
|---|---:|---:|---:|
{table}

두 씬에서 각8초간 프레임 진행과 입력 이동을 다시 확인하고 B4 편집 모드로 돌아왔다. 원래 플레이어 위치·입력 설정·백그라운드 실행 설정 복원, 씬 저장 완료. B4 설비320경로/16구역 검수는 명칭 변경 전 외형 검수이며, 이번에는 이름 보존 비교와 두 씬 대표 Play를 추가했다.

## 기록

SourceAssets/EnglishNaming의 rename_plan.json은 GlobalObjectId별 전후 이름, name_map.json은 이전/현재 이름 대응표다. 원래 씬은 *_before.unity로 백업했다. 처음 비교에서 GameObject JSON의 래핑 구조 때문에 이름 자체를 차이로 세던 검수기를 보수했으며, 최종 결과는 실제 이름 외 차이0이다. 이 문제는 게임 코드 오류가 아니다.

과거 일회성 생성·Apply 도구와 before 스냅샷은 당시 이름을 가진 제작 이력으로 보존한다. 최신 씬에 그대로 재실행하지 않는다. 새 제작은 영어 이름을 사용하고 최신 검수 도구를 따른다.

[이름 변경](rename_result.json) · [파일 보존](preservation.json) · [최종 씬](final_state.json)

- V0.01 (2026-11-08): 한글 하이라키 영문화, 이름 외 속성·기존 파일·실제 Play 검증. 송예찬.
''',encoding='utf8')
(H/'README.md').write_text('''# English Naming Migration V0.01

작성자 송예찬 · 2026-11-08

User-requested ASCII English hierarchy names. Scene filenames and asset GUIDs were already English and are unchanged.

inventory.py performs a read-only path/serialized-name scan. Survey.cs recorded all13 native scenes and saved backups of the two affected scenes. prepare.py saved6,541 file hashes and the naming policy. plan.py produced1,778 ID-based renames; append_ascii.py added21 corridor names containing arrow symbols, for1,799 total. Apply.cs edits through Unity, checks animation bindings, saves/reloads and compares22,473 serialized object/component snapshots with GameObject names normalized to their original values.

Do not rerun Survey, prepare or plan against the final state; they describe the original baseline. Apply accepts only the recorded old/new names. update_tools.py is one-time: it migrated current review paths/layout names while retaining historical snapshots and one-shot generation sources. Previous generators must not be reapplied to the current scene without adapting their naming rules.

Play.cs/Scenes.cs provide the two-scene smoke check and restore saved editor state. report.py verifies file preservation and writes the review. Current report: Docs/검수/2026-11-08_EnglishNaming/review.md.

- V0.01 (2026-11-08): Naming migration and preservation/Play validation. 송예찬.
''',encoding='utf8')
for folder in ['B4_Observation','B5_CeilingLighting']:
 p=R/'SourceAssets'/folder/'README.md';s=p.read_text(encoding='utf8');title,body=s.split('\n',1);assert 'V0.02' in title
 p.write_text(title.replace('V0.02','V0.03')+'\n'+body+'\n- V0.03 (2026-11-08): 영문 명칭 전환과 최신 검수 경로 반영. 송예찬.\n',encoding='utf8')
print(json.dumps(preserve,ensure_ascii=False))
