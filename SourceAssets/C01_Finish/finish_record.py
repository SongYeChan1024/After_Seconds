from pathlib import Path
import hashlib,json,re
R=Path(__file__).resolve().parents[2];H=Path(__file__).resolve().parent;O=R/'Docs/검수/2026-11-07_C01_Finish'
baseline=json.loads((H/'protected_before.json').read_text('utf-8'))
changed=[p for p,digest in baseline.items() if not (R/p).exists() or hashlib.sha256((R/p).read_bytes()).hexdigest()!=digest]
assert not changed,changed
play=json.loads((O/'play_inside.json').read_text('utf-8'))
audit=json.loads((O/'rib_and_prop_audit.json').read_text('utf-8'))
walk=json.loads((O/'controller_walk.json').read_text('utf-8'))
doors=json.loads((O/'door_validation.json').read_text('utf-8'))
assert play['complete'] and play['framesAdvanced']>0 and play['displacement']>.1 and not play['errors']
assert not audit['gaps'] and not audit['propIssues'] and not audit['ribIntersections'] and audit['badTriangles']==0
assert audit['maximumEightWayRadiusDifferenceMeters']<.0001 and all(x['passed'] for x in walk)
assert all(d['openClear'] and d['closedBlocks'] for d in doors)
(O/'protected_files.json').write_text(json.dumps({'checked':len(baseline),'changed':changed},indent=2),encoding='utf-8')

# Keep an intentional full rebuild consistent with the targeted corrected rib source.
p=R/'SourceAssets/B5_FullLayout/build_layout.py';s=p.read_text('utf-8')
old=s[s.index('for deg in range(0,360,30):'):s.index("export2('AF_C01_ThreePortalRibs')")+len("export2('AF_C01_ThreePortalRibs')")]
assert "seg*10.7" in old
s=s.replace(old,"# C01 ribs now use continuous, eight-way symmetric geometry.\n# The targeted tool also preserves the original AF model name and output path.\nimport runpy\nrunpy.run_path(str(R/'SourceAssets/C01_Finish/build_ribs.py'),run_name='__main__')\nde['manifest']['AF_C01_ThreePortalRibs']=json.loads((R/'SourceAssets/C01_Finish/rib_geometry.json').read_text('utf-8'))")
p.write_text(s,encoding='utf-8')

report='''# C01 리브 보수와 실험 소품 보강 V0.01

작성자 송예찬 · 2026-11-07

`Level_B5_Circular`의 `C01_Experiment_Art`를 수정했다. 사용자가 지적한 `AF_C01_ThreePortalRibs`의 마디 단절·비대칭·벽과 같은 재질을 보수하고 실험 소품을 추가했다. 로컬 저장 상태이며 이번 변경은 커밋·push하지 않았다.

## 반영한 내용

- 리브의 기존 8조각 분할과 출입구 방향 통째 생략을 없애고, **32.5° 기준 45° 간격의 연속 리브 8개**로 교체했다. 맞은편 리브와 마디 높이가 대응하며 세 출입구는 유지한다.
- 폭 28cm, 벽 내측보다 약 29.6cm 돌출되는 곡선 단면이다. 바닥 받침·앵커, 닫힌 이음 덮개, 천장 연결 링을 추가했다. 8mm 베벨을 적용했고 최종 32,480tri다. FBX 이름·GUID와 씬 Transform은 유지했다.
- 벽용 S1_Coat와 분리한 청회색 무광 금속 3재질을 사용한다. 본체 metallic .64 / smoothness .43, 이음 .68 / .50, 앵커 .80 / .60이다. 다른 벽과 공용 재질은 수정하지 않았다.
- 기존 에셋으로 시료 카트 2대, 분석 장비 1대, 보호구 스테이션 1대를 배치했다. 분석 장비는 기존 수납장과의 겹침을 피한 위치로 옮겼다.
- 콘솔 2곳에 벽면 단자함·소켓·고정대와 케이블 6가닥을 추가했다. 전용 연결 메시 4,704tri이며 통행로를 가로지르지 않는다. 작은 케이블에는 별도 충돌체를 넣지 않았다.
- C01 내부 보조 작업등 intensity를 16에서 12로 조정했다. 조명 전체 재설계나 천장 발광체 교체는 아니다.

## 확인 결과

- 리브 표면 1,368 ray 표본: 빈 마디 0. 여덟 대응 단면의 반경 차이 최대 0.00000763m. 삼각형 공유 경계에 정확히 닿는 수치 오차를 피하도록 동일하게 0.05° 치우친 표본을 사용했다.
- 리브 주변 BoxCollider 15개 및 새 프랍 4개: 35mm 초과 관통 0. 모든 메시 간 정밀 교차 검사를 뜻하지 않는다.
- 전체 복도 4,854 capsule 표본: 막힘·바닥 누락 0. T01/T03/T11 CharacterController 왕복 6/6 통과.
- 문 38세트: 열린 상태 통행·닫힌 상태 충돌 38/38. 문 작동 런타임 코드를 구현한 것은 아니다.
- 누락 메시/재질·퇴화 삼각형 0. 리브 강제 반입 경고/오류 0.
- 1920×1080 Editor Play 5초: 458프레임 진행, 실제 W 입력 이동 1.226m, 관찰 중 새 경고/오류 0. 프레임 median 10.61ms/p95 12.14ms이며 전체 게임 성능을 보증하는 수치는 아니다.
- 작업 전부터 있던 Unity AI Assistant 계정 API 대기 경고 1건은 아트 반입 오류와 구분한다.
- 게임 C#·Animator와 다른 씬의 보호 파일 21개 해시 동일. 플레이어 저장 위치 (-9.2,-81.36,-10)와 회전 (0,0,0) 유지. Play 종료 후 백그라운드 실행 override를 해제했다.

## 시각 자료

- [수정 전](Before_Observation.png) / [수정 후](After_Observation.png)
- [벽과 리브](After_Wall.png), [서쪽 출입구](After_WestExit.png), [천장](After_Crown.png)
- [콘솔 A와 카트·단자함](After_ConsoleA.png), [콘솔 B](After_ConsoleB.png), [분석 장비](After_Analyzer.png)

## 남은 범위

이번 보수로 C01 전체 아트나 B5 전체를 완료 처리하지 않는다. 출입구 상부 곡면과 사각 문틀 사이 마감, 벽 표면 반복과 광원 확산, 문 포켓 외형·바닥 안내선 연결은 계속 확인한다. 외곽 공동의 부족 24배치는 이번 C01 소품 4개와 별도 목록이다. 전체 아트 완료 0/34 유지. 층간 계단·승강로와 게임 기능도 기존 미완료 범위다.

원본과 재현 도구는 [SourceAssets/C01_Finish](../../../SourceAssets/C01_Finish/README.md)에 있다. 기존 전체 Apply/Repair를 재실행하지 않는다.
'''
(O/'검수결과.md').write_text(report,encoding='utf-8')

note='2026-11-07 집 보수: `AF_C01_ThreePortalRibs`를 45° 간격 연속 리브 8개·약30cm 돌출·별도 무광 금속으로 수정했다. C01 시료 카트2·분석기1·보호구 스테이션1과 단자함2·케이블6을 반영했다. [최신 검수](검수/2026-11-07_C01_Finish/검수결과.md), [제작 도구](../SourceAssets/C01_Finish/README.md)를 따른다. 리브1368표본 끊김0, 복도4854표본 막힘0, 세 복도 왕복6/6, 문38/38, Play458프레임·1.226m·새 경고/오류0. 이번 변경은 로컬 저장이며 커밋·push하지 않았다. 다음은 사용자 시야 확인 후 출입구 상부·문 포켓 외형·벽 표면/광원·바닥 안내선 마감이다. 외곽 부족24배치와 구역별 완성은 별도이며 전체 아트0/34 유지.'
for rel,oldver,newver in [('Docs/이어하기_2026-11-06.md','V0.22','V0.23'),('Docs/회사_작업목록_2026-11-06.md','V0.20','V0.21')]:
    p=R/rel;s=p.read_text('utf-8');head,rest=s.split('\n',1);assert oldver in head;head=head.replace(oldver,newver)
    p.write_text(head+'\n\n'+note+'\n'+rest,encoding='utf-8')
for rel in ['AGENTS.md','CLAUDE.md']:
    p=R/rel;s=p.read_text('utf-8');head,rest=s.split('\n',1);assert 'V0.38' in head
    lead='2026-11-07 최신: C01 연속·대칭 리브8개, 전용 금속, 소품4개와 콘솔 배선을 반영했다. [이어하기 V0.23](Docs/이어하기_2026-11-06.md), [검수 기록](Docs/검수/2026-11-07_C01_Finish/검수결과.md), [전용 제작 도구](SourceAssets/C01_Finish/README.md)를 우선한다. 게임 코드·다른 씬·플레이어 저장 위치를 보존했고 로컬 저장 상태다. 이번 변경의 커밋·push는 하지 않았다. C01 전체/외곽24배치/전체층 완료가 아니며 아트0/34 유지. 아래 11월6일 커밋·push 승인 문구는 회사 작업 이력이다.'
    p.write_text(head.replace('V0.38','V0.39')+'\n\n'+lead+'\n'+rest,encoding='utf-8')
p=R/'SourceAssets/B5_FullLayout/README.md';s=p.read_text('utf-8').replace('V0.01','V0.02',1);line='\n2026-11-07: `AF_C01_ThreePortalRibs.blend`/FBX는 [C01 전용 보수 도구](../C01_Finish/README.md)의 연속 리브8개 버전이다. `build_layout.py`도 리브 생성만 새 원본으로 위임한다. 이 문서의 나머지 전체 Apply/Repair를 현재 씬에 재실행하지 않는다.\n'
head,rest=s.split('\n',1);p.write_text(head+'\n'+line+rest,encoding='utf-8')
print(json.dumps({'protected':len(baseline),'changed':changed,'reportsWritten':True},ensure_ascii=False))
