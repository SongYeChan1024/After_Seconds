"""검수 결과와 다음 작업 인수인계. 작성자 송예찬."""
from pathlib import Path
import hashlib,json,re
H=Path(__file__).resolve().parent;R=H.parents[1];O=R/'Docs/검수/2026-11-07_T01_Corridor'
audit=json.loads((O/'audit.json').read_text(encoding='utf-8'))
inside=json.loads((O/'play_inside.json').read_text(encoding='utf-8'));door=json.loads((O/'play_tunnel.json').read_text(encoding='utf-8'))
walk=json.loads((O/'controller_walk.json').read_text(encoding='utf-8'));scope=json.loads((O/'guide_scope.json').read_text(encoding='utf-8'))
baseline=json.loads((H/'baseline.json').read_text(encoding='utf-8'));changed=[];missing=[]
for rel,sha in baseline['protected'].items():
    p=R/rel
    if not p.exists():missing.append(rel)
    elif hashlib.sha256(p.read_bytes()).hexdigest()!=sha:changed.append(rel)
preserved=dict(baselineFiles=len(baseline['protected']),changed=changed,missing=missing,sceneOnly=changed==[baseline['scene']],backup=baseline['backup'])
(O/'file_preservation.json').write_text(json.dumps(preserved,indent=2),encoding='utf-8')
assert preserved['sceneOnly'] and not missing
assert audit['degenerateTriangles']==audit['missingMaterials']==audit['newBehaviours']==audit['newLights']==0
assert not audit['blocked'] and not audit['missingFloor'] and not audit['lightChanges'] and not audit['protectedTransformChanges']
assert audit['labelGuideOverlapSamples']==0 and scope['passed'] and all(x['passed'] for x in walk)
assert all(p['complete'] and p['framesAdvanced']>100 and p['displacement']>.5 and not p['errors'] for p in [inside,door])
assert not audit['runInBackground'] and audit['playerPosition']==[-9.2,-81.36,-10.0]
report=f'''# T01 실험동–보안관제동 연결 복도 검수 V0.01

작성자 송예찬 · 2026-11-07

T01 복도 아트 마감을 `Level_B5_Circular.unity`에 저장했다. C02 돔 본체 제작과 전체 B5 안내선 일괄 적용은 다음 작업으로 남는다. 사용자의 최종 외형 확인 전이며 전체 아트 최종 판정0/34는 유지한다.

## 제작 결과

길이13.46m·폭4.2m·천장3.4m의 기존 구조 안에 곡면 패널·하부 패널·카트 보호 레일·금속 킥·배수 그레이팅·미끄럼 방지 바닥을 제작했다. 기존 리브4개의 씬 재질만 전용 금속으로 바꾸고 빈 천장 트레이에 케이블과 벽 인입·전원 배선을 연결했다. 점검 장치는 도어 전원함1개, 환기구2개, 보안 카메라 외형1개다. 패널/캐비닛/루버/카메라에 베벨·고정 나사·힌지·손잡이·렌즈/차광부를 반영했다. 카메라 회전·감지와 문 작동은 사용자 구현 범위다.

보안관제동 쪽 구형 문은 비활성 자식으로 보존하고 실험동에서 검수한 Clinical Portal을 반대 방향으로 배치했다. 아치 상부와 문턱을 마감하고 열린 통행 폭2.4m를 유지한다. 기존 실험동 문과 승인된 프랍은 그대로다.

새 FBX5종144,164tri, PBR9장(Base/Normal/Metallic-Smoothness)과 바닥 표기2장, 전용 재질10개를 추가했다. 바닥 표기4개와 R1 파생 메시2개를 포함한 이번 검수 고유 메시8개는 {audit['uniqueTriangles']:,}tri다. 기존 문 모델은 공유하며 복제 파일을 만들지 않았다. 새 구역 Renderer9개와 전원함 충돌1개가 추가됐다.

## 안내선

C01 실험동과 C02 보안관제동 표기는 각 진행 방향의 우측 바닥, 문에서2.5m 떨어진 출발/도착 위치에 총4개 배치했다. 화살표·SECTOR C·목적지 코드·한글 이름·B5/R1을 함께 표시했다. 별도 구역 명판은 추가하지 않았다.

기존 R1 흰 이중선은 새 선을 겹쳐 얹지 않고 `TC_R1_Continuous_L/R.asset`로 참조를 교체했다. T01 구간만 중앙 정렬하고 양 끝1.25m에서 기존 노선으로 부드럽게 연결한다. 바깥 평면 경로는288개 정점 표본에서 최대 {scope['maxOutsideXZChange']*1000:.4f}mm 오차로 유지했다. 문턱 주변±0.8m에서는 도장이 바닥에 묻히지 않도록 실제 표면 위3.5mm로 높이만 맞췄다. 바깥 나머지 높이 변경0.

바닥 글자 영역과 양쪽 안내선 가장자리 간 최소 여백은 {audit['labelGuideMinClearance']*100:.2f}cm, 겹침0이다. B5 전체 노선48개·76표기의 일괄 적용을 완료한 것은 아니며, 이 단계에서는 T01 표기4개만 반영했다.

## 검증

| 항목 | 결과 |
| --- | --- |
| 복도 중앙/좌우0.8m 통행477표본 | 막힘0, 바닥 누락0 |
| 실제 CharacterController 전체 복도 왕복 | 2/2, 각각163회 이동, 목적점 도달 |
| 메시 퇴화/재질 누락 | 0/0 |
| 기존187 Light 설정·활성·위치 | 변경0 |
| 기존 Transform·활성 보존 | 허용한 C02 문 보관 구조 외 변경0 |
| 사전 기존 에셋3,764개 | 대상 씬 외 기존 파일3,763개 해시 동일, 누락0 |
| 새 Light/런타임 MonoBehaviour | 0/0 |
| 바닥 표기/안내선 겹침 | 0 |

실제 Play에서 기존 키보드 Input System으로 W를 눌렀다. 복도 내부는 {inside['framesAdvanced']}프레임 진행·{inside['displacement']:.3f}m 이동, C02 문 바깥에서 복도 안으로 들어오는 검사는 {door['framesAdvanced']}프레임 진행·{door['displacement']:.3f}m 이동했다. 두5초 검사 동안 새 경고/오류0건이다. 1920×1080에서 중앙값 {inside['medianMs']:.2f}/{door['medianMs']:.2f}ms, p95 {inside['p95Ms']:.2f}/{door['p95Ms']:.2f}ms였으며 Editor의 짧은 표본이므로 빌드 성능 보증 수치로 쓰지 않는다. 기존 Unity AI 패키지의 모델 조회 메시지는 이 Play 표본의 결과와 구분한다.

Play 종료 후 저장된 편집 씬을 다시 열어 플레이어 시작 위치(-9.2,-81.36,-10), 회전(0,0,0), Run In Background=false를 복구했다. 마지막 변경은 충돌 없는 안내선에서 중복 샘플이 만든 면적0 삼각형20개 정리이며, 최종 메시 검사를 다시 통과했다. 씬 YAML은 Unity가 저장했다. Git 공백 검사에서 Unity의 빈 문자열 직렬화 `value: ` / `m_Name: `가 표시되지만 YAML을 수작업으로 고치지 않았다.

## 화면과 원본

- [보안관제동 방향](After_ToSecurity.png) · [실험동 방향](After_ToLab.png)
- [설비 상세](After_ServiceWall.png) · [천장 배선](After_Ceiling.png)
- [보안관제동 문 접합](After_SecurityPortal.png) · [바닥 표기](After_FloorDetail.png)
- [실제 Play 화면](Play_Threshold.png)
- [제작 원본](../../../SourceAssets/T01_CorridorFinish/README.md)
- audit.json / controller_walk.json / guide_scope.json / play_inside.json / play_tunnel.json / file_preservation.json

기존 씬 백업: `{baseline['backup']}`. 제작 변경은 로컬 저장이며 커밋·push하지 않았다. 다음은 T01 사용자 외형 확인과 C02 보안관제동 본체 제작이다. 조명·색감 최종 조정은 B5 전체 제작 후 일괄 진행한다.
'''
(O/'검수결과.md').write_text(report,encoding='utf-8')
note='''2026-11-07 T01 연결 복도 마감 완료: 사용자 다음 구역 제작 요청에 따라 곡면/하부 패널·보호 레일·바닥/배수·트레이 케이블·도어 전원함1개·환기구2개·정적 카메라 외형1개를 제작했다. C02 쪽 문을 Clinical Portal로 맞추고 T01 바닥 목적지 표기4개와 R1 중앙 정렬을 반영했다. 글자/선 겹침0·최소 여백70.49cm, 통행477표본·Controller 왕복2/2 통과. Play 내부483프레임/1.223m·문 통과457프레임/0.917m·새 경고/오류0. 기존187 Light와 승인된 프랍·대상 씬 외 기존 에셋3,763개를 보존했다. **다음 제작은 C02 보안관제동 본체**이며 T01 최종 외형은 사용자 확인을 기다린다. B5 전체 안내선 일괄 적용은 아직 남아 있고 T01 표기4개만 현장 반영했다. 최종 조명·색감은 B5 전체 제작 후 조정, 게임 C#/Animator는 사용자 직접 구현, 전체 아트 최종 판정0/34 유지. 로컬 저장, 커밋·push 미실시. 작성자 송예찬.'''
for rel,version in [('AGENTS.md','V0.49'),('CLAUDE.md','V0.49'),('Docs/이어하기_2026-11-06.md','V0.33'),('Docs/회사_작업목록_2026-11-06.md','V0.31')]:
    p=R/rel;s=p.read_text(encoding='utf-8');head,rest=s.split('\n',1);head=re.sub(r'V0\.\d+',version,head)
    if note in s:continue
    prefix='Docs/' if '/' not in rel else ''
    links=f' [최신 검수]({prefix}검수/2026-11-07_T01_Corridor/검수결과.md)와 [제작 원본]({"" if "/" not in rel else "../"}SourceAssets/T01_CorridorFinish/README.md)을 따른다.'
    p.write_text(head+'\n\n'+note+links+'\n\n이전 단계 기록:\n'+rest.lstrip(),encoding='utf-8')
p=R/'Docs/AfterSeconds_메인기획서.md';s=p.read_text(encoding='utf-8');start=s.index('2026-11-07 다음 구역 제작:');end=s.index('\n\n',start);s=s[:start]+note+' [최신 검수](검수/2026-11-07_T01_Corridor/검수결과.md).'+s[end:]
s=s.replace('사용자 다음 구역 요청에 따른 T01 연결 복도 아트 마감 범위·목적지 바닥 표기·Light/게임 코드 보존 기준 기록.','T01 복도 마감·C02 문 교체·목적지 바닥 표기4개·안내선 정렬 구현, 통행/Play/기존 자산 보존 검증 및 C02 후속 범위 기록.')
p.write_text(s,encoding='utf-8')
p=H/'README.md';s=p.read_text(encoding='utf-8').replace('마감 V0.01','마감 V0.02').replace('현재 제작 단계이며 완료/검증 수치는 최종 검수 기록에서 확정한다.','제작·검수 완료: 모델5종144,164tri, 새 재질10개·텍스처11장·바닥 표기4개. 통행477표본/왕복2회 통과, 실제 Play 내부483프레임·문 통과457프레임에서 새 경고/오류0. 최종 메시 퇴화0·재질 누락0·기존187 Light 변경0. 사용자 외형 검수는 남는다. 문턱 주변±0.8m의 안내선 높이는 표면에 맞추며 바깥 평면 노선은 보존했다.')
s+='''

## 다시 확인할 파일

- `textures.py`: PBR9장과 한글 목적지 스텐실2장.
- `build.py`: 기존 좌표/베벨 도우미의 함수만 불러와 새 TC 모델5종 생성. 구형 제작 본문은 실행하지 않는다. 케이블 내보내기는 결합 후 기준점을 원점으로 확정한다.
- `Apply.cs`: 저장된 B5 편집 씬에서 자기 그룹/자산·T01 리브 재질·C02 문·R1 참조만 편집. 실행 전 현재 사용자 변경 확인이 필요하다. 이전 문은 비활성 보관한다.
- `Audit.cs`, `GuideScope.cs`, `Walk.cs`: 메시·통행·기존 배치/Light·외부 노선 보존 확인.
- `Play.cs`: 기존 키보드 W 입력으로 복도 내부/새 문 통과 측정. Play 종료 후 `Restore.cs`로 저장 편집 씬 복원.
- `Capture.cs`: 최종6시점, `PlayCapture.cs`: 실제 Game 화면.
- [최종 검수](../../Docs/검수/2026-11-07_T01_Corridor/검수결과.md).

씬 그룹 `B5_Circular_Core_V0.03/T01_Corridor_Finish`. 새 파일은 Environment/B5 직하 TC_* 및 Materials/Textures에 있으며 Blender 원본은 이 폴더에 둔다. 전체 안내선 적용 도구가 기존 CF_R1 대신 TC_R1 참조를 덮어쓸 경우 T01 문턱 높이와 표기 간격을 다시 확인해야 한다.

로컬 저장이며 커밋·push하지 않았다. 다음 제작은 C02 보안관제동 본체다.
'''
p.write_text(s,encoding='utf-8')
p=R/'Docs/도면/Decision/원형공동/B5_안내체계/README.md';s=p.read_text(encoding='utf-8').replace('배치안 V0.01','배치안 V0.02').replace('아직 Unity 바닥 메시·텍스처를 교체하지 않았다.','전체 안내체계의 Unity 일괄 적용은 아직 남아 있다. 후속 T01 마감에서는 이 계획의 C01/C02 바닥 표기4곳만 적용하고 기존 R1의 T01 구간을 중앙 정렬했다. 자세한 구현/검수는 [T01 검수](../../../../검수/2026-11-07_T01_Corridor/검수결과.md)를 따른다. T01 외 다른 구간은 이 배치안 단계이며, 전체 현장 적용 완료로 해석하지 않는다.')
p.write_text(s,encoding='utf-8')
print(json.dumps({'validation':'passed','report':str(O/'검수결과.md'),'protectedFiles':len(baseline['protected'])-1,'next':'C02'},ensure_ascii=True))
