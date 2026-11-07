"""C02 결과와 인수인계 갱신. 작성자 송예찬."""
from pathlib import Path
import json,re,math
H=Path(__file__).resolve().parent;R=H.parents[1];O=R/'Docs/검수/2026-11-08_C02_Security'
load=lambda n:json.loads((O/n).read_text(encoding='utf-8'))
a=load('audit.json');walk=load('controller_walk.json');inside=load('play_inside.json');door=load('play_tunnel.json');pres=load('file_preservation.json');state=load('final_state.json');backup=load('backup.json');models=json.loads((H/'model_manifest.json').read_text(encoding='utf-8'))
assert a['degenerateTriangles']==a['missingMaterials']==a['labelGuideOverlapSamples']==a['newLights']==a['newBehaviours']==0
assert not a['blocked'] and not a['missingFloor'] and not a['lightChanges'] and not a['protectedTransformChanges']
assert all(w['passed'] for w in walk) and pres['sceneOnly'] and not pres['missing']
assert all(p['complete'] and p['framesAdvanced']>100 and p['displacement']>.5 and not p['errors'] for p in [inside,door])
assert not state['dirty'] and not state['playing'] and not state['runInBackground']
tri=sum(v['triangles'] for v in models.values())
report=f'''# C02 보안관제동 제작·검수 V0.01

작성자 송예찬 · 2026-11-08

사용자가 T01 외형을 좋다고 확인하고 보안관제동 본체 제작을 요청했다. `Level_B5_Circular.unity`의 `B5_Circular_Core_V0.03/C02_Security_Art`에 제작·저장했다. 지름14m 돔과 기존 출입3곳을 유지했다. 현재 C02 외형은 사용자 확인 전이며, B5 전체 조명·색감과 최종 아트 판정은 후속 단계다.

## 공간 구성

| 구역 | 구성 |
| --- | --- |
| 북측 관제 | 6분할 감시 화면, 2인 관제석/모니터4대, 키보드·마우스·유선 전화, 의자2개 |
| 북동 전산 | 네트워크 패치 랙, 드라이브 녹화 랙, 별도 UPS 배터리 장치 |
| 남서 교대 | 무전기5대 충전·채널 선택·마이크, 장비 로커, 별도 사건 검토 책상과 의자 |
| 남동 기록 | 잠금 기록 보관장10서랍·얕은 인덱스 창 |
| 건축·설비 | 곡면 패널·연속 리브/구조 링·바닥·점검 해치·북측 전원 버스/인입·매달린 등기구4개 |

새 모델14종(환경3·프랍11), 모델 배치16곳, 전용 재질23개, 텍스처13장이다. 고유 FBX 삼각형은 {tri:,}개이며 바닥 표기/안내선까지 포함한 검수 고유 메시16개는 {a['uniqueTriangles']:,}tri다. Renderer20개, 프랍용 단순 충돌13개를 추가했다. 의자3개는 같은 자산을 공유한다.

하드웨어는 베벨·얕은 틈·힌지/손잡이·실제 키캡·무전기 안테나/충전 받침·패치 케이블·드라이브 트레이·캐스터로 구성했다. 서버 유리 뒤에는 장치와 불투명 후면이 있어 벽이 바로 관통해 보이지 않는다. 기록 인덱스와 봉투는 얇은 표면이다. 광택이 화면 내용을 가리지 않도록 활성 LCD의 정반사를 낮췄다.

기존 TC 도장/금속/바닥 PBR9장을 공유해 중복 파일을 만들지 않았다. 새 화면10장은 실제 실험동/T01 씬 캡처, 출입 기록, 전산 상태, 보안 노드 도식으로 구성했다. 물리 화면15곳에 적용했으며 전부 정적 아트다. 카메라 실시간 송출·로그 갱신·문 개폐·경비 AI는 구현하지 않았다.

## 연결과 안내

C02 쪽 T02·T05 구형 문2개는 비활성 하위 그룹으로 보존하고 기존 Clinical Portal을 출입 방향에 맞춰 재사용했다. 승인된 T01 문과 복도는 그대로 보존했다. 새 문은 통행 폭2.4m를 유지하며 상부 아치를 마감한다.

기존 T01–C02–T02 R1을 유지하고 C02 중앙 분기에서 T05를 따라 C04 유틸리티동 입구까지 약32.85m의 흰 이중선을 연결했다. 문턱은 실제 표면 위3.5mm 이상으로 맞췄다. 복도 중간에서 끝나는 안내선은 만들지 않았다. C02 안의 세 출구에 C01 실험동·VA 계단A·C04 유틸리티동 목적지를 바닥으로 표시했다. 별도 구역 명판은 추가하지 않았다.

표기 영역과 기존/새 R1 가장자리의 최소 여백은 {a['labelGuideMinClearance']*100:.2f}cm이고 겹침0이다. R1끼리 중앙에서 만나는 곳은 한 노선의 의도한 분기다. 다른 목적의 선을 겹쳐 놓지 않았다. 전체 B5 안내체계는 아직 일괄 적용하지 않았다. [실제 반영 좌표](../../../SourceAssets/C02_Security/as_built_wayfinding.json)를 우선하며 전체 적용 때 `SC_R1_T05_ToC04`를 다시 중복 생성하지 않는다.

## 검수

| 항목 | 결과 |
| --- | --- |
| 출입·T05·장비 접근 경로 | {a['samples']:,}표본, 막힘0·바닥 누락0 |
| 실제 CharacterController | 출입3곳 사이 방향별6회 + T05 전체1회 = 7/7 도달 |
| 메시 퇴화·재질 누락 | 0 / 0 |
| 기존 Light187개의 설정·활성·Transform | 변경0 |
| 기존 Transform·활성 | 허용한 구형 문 보관/초기 소품2개 외 변경0 |
| 기존 파일 해시 | {pres['baselineFiles']:,}개 중 대상 씬 외 {pres['baselineFiles']-1:,}개 동일, 누락0 |
| 새 Light / 런타임 MonoBehaviour | 0 / 0 |

Play에서 기존 키보드 Input System으로 W를 눌렀다. 내부는 {inside['framesAdvanced']}프레임·{inside['displacement']:.3f}m 이동, T02 문 바깥에서 안쪽으로 통과한 검사는 {door['framesAdvanced']}프레임·{door['displacement']:.3f}m 이동했다. 두5초 표본 모두 새 경고·오류0이다. 1920×1080 중앙값 {inside['medianMs']:.2f}/{door['medianMs']:.2f}ms, p95 {inside['p95Ms']:.2f}/{door['p95Ms']:.2f}ms였다. 이는 현재 Editor의 짧은 표본이며 전체 B5 빌드 최적화 완료를 의미하지 않는다.

검수 중 LCD 단면의 앞면/UV 방향을 고쳤고, 얇은 인쇄/바닥 경계와 돔 꼭대기에서 생긴 미세 베벨 삼각형을 정리했다. 검토 자리/의자를 통과하던 단순 직선 검사 대신 장비 뒤로 실제 걸어가는 접근 경로를 검증했다. 주 출입 동선과 프랍 위치를 검사 통과 목적으로 삭제하지 않았다.

## 보존·현재 상태

작업 시작 시 미저장 편집이 있었다. `{backup['backup']}`에 기존 디스크 씬과 현재 편집 씬을 따로 백업한 뒤 사용자 편집을 저장하고 기준으로 삼았다. C02 초기 `B5-12_P14`·`B5-15_P11`은 비활성 상태로 남겼다. 모델·게임 C#·기존 공유 재질은 덮어쓰지 않았다.

Play 종료 후 현재 편집 상태도 같은 백업 폴더에 보관하고 저장했다. 플레이어 시작 위치 {state['playerPosition']}, 회전 {state['playerRotation']}, Run In Background=false, 저장된 Edit 상태다. 기존 광원4곳에는 발광 등기구 외형을 대응시켰으며 Light 수치·위치·색은 바꾸지 않았다.

로컬 저장, 커밋·push 미실시. 다음은 사용자 C02 외형 확인이며 후속 제작 후보는 T02 복도와 계단A 연결부다. B5 전체 제작 뒤 최종 조명·색감 검수를 진행한다.

## 확인 자료

- [입구 전체](After_FromLab.png) · [관제석](After_Operations.png) · [교대/보관](After_SouthServices.png)
- [화면 상세](After_WallDetail.png) · [전체 배치](After_Overview.png) · [T01 접합](After_EntryBack.png)
- [실제 Play 화면](Play_Operations.png)
- [제작 원본](../../../SourceAssets/C02_Security/README.md)
- audit.json, controller_walk.json, play_inside.json, play_tunnel.json, file_preservation.json, final_state.json, apply.json
'''
(O/'검수결과.md').write_text(report,encoding='utf-8')
labels=[]
for code,x,z in [('C01',1.503721,-6.014883),('VA',-5.644272,2.565578),('C04',6.19143,.325865)]:
 n=math.hypot(x,z);fx,fz=x/n,z/n;labels.append(dict(code=code,world_xz=[-22+x-2.4*fx+1.15*fz,18+z-2.4*fz-1.15*fx],forward=[fx,fz],width=.6,length=1.4))
asbuilt=dict(title='C02 반영 안내선 V0.01',author='송예찬',date='2026-11-08',preserved='Facility_Floor_Guidance_R1 with TC_R1 mesh references',new_route=dict(code='R1',object='C02_Security_Art/SC_R1_T05_ToC04',world_xz=[[-22,18],[10.807187,19.726694]],line_width=.05,line_offsets=[-.12,.12],end='C04 side T05 threshold'),labels=labels,note='전체 안내선 적용 시 이 분기/표기와 중복 생성하지 않는다. 바닥 높이는 Unity 실제 표면 기준.')
(H/'as_built_wayfinding.json').write_text(json.dumps(asbuilt,ensure_ascii=False,indent=2),encoding='utf-8')
note=f'''2026-11-08 C02 보안관제동 본체 제작 완료: 사용자 T01 외형 확인 후 C02의 2인 관제석·6분할 감시 화면·네트워크/녹화/UPS·무전/교대·장비/기록 보관·사건 검토 자리와 돔 패널/리브/바닥/배선을 제작했다. C02 쪽 T02/T05 문을 통일하고 C02 중앙에서 C04 입구까지 R1 분기·바닥 목적지3개를 반영했다. 모델14종·고유 검수239,928tri, 통행1,721표본 막힘0·Controller7/7·메시 퇴화/재질 누락0. Play 내부434프레임/1.216m·T02 문 통과377프레임/0.914m·새 경고/오류0. 기존187 Light와 대상 씬 외 기존 파일3,821개를 보존했다. 미저장 사용자 편집은 작업 전/후 각각 백업하고 보존했다. **화면은 정적이며 게임 C#/Animator·문/감시 기능은 미구현**이다. 다음은 C02 사용자 외형 확인, 후속 후보는 T02 복도/계단A 연결부다. 전체 안내체계 일괄 적용과 B5 완성 후 조명·색감 검수는 남는다. 전체 아트 최종 판정0/34 유지. 로컬 저장, 커밋·push 미실시. 작성자 송예찬.'''
for rel,version in [('AGENTS.md','V0.50'),('CLAUDE.md','V0.50'),('Docs/이어하기_2026-11-06.md','V0.34'),('Docs/회사_작업목록_2026-11-06.md','V0.32')]:
 p=R/rel;s=p.read_text(encoding='utf-8');head,rest=s.split('\n',1);head=re.sub(r'V0\.\d+',version,head)
 prefix='Docs/' if '/' not in rel else '';link=f' [최신 검수]({prefix}검수/2026-11-08_C02_Security/검수결과.md)를 따른다.'
 if note not in s:p.write_text(head+'\n\n'+note+link+'\n\n이전 단계 기록:\n'+rest.lstrip(),encoding='utf-8')
p=R/'Docs/AfterSeconds_메인기획서.md';s=p.read_text(encoding='utf-8');start=s.index('2026-11-08 C02 보안관제동 제작 시작:');end=s.index('\n\n',start);s=s[:start]+note+' [검수](검수/2026-11-08_C02_Security/검수결과.md).'+s[end:];s=s.replace('T01 사용자 확인 및 C02 관제동 본체 제작 범위·관제/교대 역할·통행/조명 보존 기준.','T01 사용자 확인, C02 관제동 모델14종·문2세트·C04 안내선 연결 구현 및 통행/Play/기존 편집 보존 검증.');p.write_text(s,encoding='utf-8')
p=H/'README.md';s=p.read_text(encoding='utf-8').replace('제작 V0.01','제작 V0.02',1).replace('완료 여부와 검수 수치는 최종 기록에 남긴다.','제작·기술 검수를 완료했으며 사용자 외형 확인은 남는다. 아래 최종 기록을 따른다.')
s+='''

## 최종 결과

모델14종·배치16곳·재질23개·텍스처13장, 고유 검수 메시239,928tri. 화면15곳은 정적이다. 실제 감시/로그·문·AI 코드가 없다. 새로운 광원 없이 기존187 Light를 보존했다. 출입/설비 접근1,721표본, 전체 출입 왕복6회와 T05 전체1회 통과. Play 두 구간 새 경고/오류0. 바닥 글자/선 최소 여백55.21cm.

- `build.py`, `textures.py`: 새 모델과 정적 장비 화면 제작. 기존 좌표 도우미의 함수만 재사용한다. 기존 제작 스크립트 본문은 실행하지 않는다. `.blend`는 편집 원본이다.
- `Apply.cs`: C02 자기 그룹과 해당 문2개·초기 소품2개의 활성·C02 셸 재질만 변경한다. 변경 전 사용자의 현재 편집을 백업/보존한다.
- `Inspect.cs`, `Prepare.cs`, `baseline.json`: 변경 전 실제 씬·사용자 미저장 편집·기존 파일 해시 기록. 최초 기준을 덮어쓰지 않는다.
- `Audit.cs`, `Walk.cs`: 메시·기존 배치/Light·바닥 표기·실제 통행 검사.
- `Play.cs`, `PlayCapture.cs`: 실제 키보드 입력/프레임·Game 화면 확인. `Restore.cs`는 Play 후 현재 편집도 백업하고 저장하며 사용자 변경을 버리지 않는다.
- `Capture.cs`: 편집 검수6시점. `RecordSource.cs`: 06.Data/AssetSources에 반입 기록.
- `as_built_wayfinding.json`: C02/C04 연결의 현장 반영 좌표. 전체 안내체계 적용 시 현재 SC_R1 분기를 중복 생성하지 않는다.
- [최종 검수](../../Docs/검수/2026-11-08_C02_Security/검수결과.md).

모델은 Environment/B5·Props/B5 직하 SC_*이고 재질/텍스처는 해당 Materials/Textures에 둔다. 기존 TC PBR를 공유한다. 승인된 C01/T01 에셋을 다시 생성하거나 덮어쓰지 않는다. 사용자가 요청하기 전 커밋·push하지 않는다.
'''
p.write_text(s,encoding='utf-8')
p=R/'Docs/도면/Decision/원형공동/B5_안내체계/README.md';s=p.read_text(encoding='utf-8').replace('배치안 V0.02','배치안 V0.03',1);head,rest=s.split('\n',1);p.write_text(head+'\n\n2026-11-08 현장 반영: C02 내부에는 기존 T01–T02 R1을 보존하고 중앙에서 T05를 거쳐 C04 입구까지 분기1개, C02 안쪽 출입 목적지3개를 추가했다. 전체 계획의 일괄 구현은 아니다. [C02 실제 좌표](../../../../../SourceAssets/C02_Security/as_built_wayfinding.json)와 [검수](../../../../검수/2026-11-08_C02_Security/검수결과.md)를 우선하며 후속 일괄 적용 시 기존 TC_R1/새 SC_R1 분기 및 바닥 글자를 중복 생성하지 않는다. 작성자 송예찬.\n'+rest,encoding='utf-8')
p=R/'Docs/검수/2026-11-07_T01_Corridor/검수결과.md';s=p.read_text(encoding='utf-8').replace('복도 검수 V0.01','복도 검수 V0.02',1).replace('사용자의 최종 외형 확인 전이며 전체 아트 최종 판정0/34는 유지한다.','2026-11-08 사용자가 T01 외형을 좋다고 확인하고 C02 본체 제작을 요청했다. B5 전체 조명·색감 최종 검수와 전체 아트 판정0/34는 유지한다.');p.write_text(s,encoding='utf-8')
print(json.dumps(dict(validation='passed',models=len(models),modelTriangles=tri,uniqueTriangles=a['uniqueTriangles'],report=str(O/'검수결과.md')),ensure_ascii=True))
