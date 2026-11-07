from pathlib import Path
import json,re
H=Path(__file__).resolve().parent;R=H.parents[1];D=R/'Docs/검수/2026-11-08_T02_StairA'
read=lambda n:json.loads((D/n).read_text(encoding='utf-8'))
a,p,w,g,f,st=[read(n) for n in ['audit.json','probe.json','walk.json','route_walk.json','file_preservation.json','final_state.json']]
spacing=read('spacing.json');inside=read('play_inside.json');stairs=read('play_stairs.json');collar=read('collar_cleanup.json')
assert not any([a['degenerate'],a['missingMaterials'],a['protectedTransformChanges'],a['badLightSettings'],a['newGameplayBehaviours'],p['blocked'],p['missingFloor'],f['unexpected'],f['missing'],st['dirty'],st['playing'],st['runInBackground'],st['legendBlocked']])
assert all(x['passed'] for x in w['results']) and all(x['passed'] for x in g['routes']) and a['minHeadroom']>3
assert len(a['oldLightChanges'])==2 and a['currentLights']==195
assert all(x['complete'] and x['framesAdvanced']>10 and x['displacement']>.2 and not x['errors'] for x in [inside,stairs]) and stairs['rise']>.2
report=f'''# T02 복도·계단 A 제작 검수 V0.01

작성자 송예찬 · 2026-11-08

다음 구역 제작 요청에 따라 T02 복도와 VA 계단 A를 제작했다. 기존 도면의 C02–VA 연결과 반경5m 원형 코어 위치를 유지하고, B5 -82m에서 B4 -66m 높이까지 실제로 걸어 오르는 계단을 배치했다. **상부 도착참과 닫힌 문까지 구현했으며 B4 공간/씬 전환 연결은 미구현**이다. 로컬 저장 상태이며 이번 변경을 커밋·push하지 않았다.

## 반영 내용

- T02는 길이13.766m·폭4.2m·높이3.4m다. 곡면/하부 패널, 카트 보호 레일, 배수 홈·바닥, 케이블과 벽 연결, 문 전원/가압 제어함1개, 닫힌 뒤판이 있는 환기구2개를 제작했다.
- VA의 빈 반구형 셸을 같은 위치/반경의 수직 계단 코어로 교체했다. 기존 셸 원본은 남겨 두고 해당 Renderer/Collider만 비활성화했다. 계단8구간·96단·상승16m, 단높이1/6m·단너비28cm·유효 계단 폭1.5m다. 중간참, 미끄럼 방지 면·노란 코끝, 지지보·기둥4개·기초 볼트, 연속 난간과 벽 배관을 포함한다. 상부 전실/방화문은 정적 외형이다.
- 소방 설비함과 인터폰을 곡면 벽 방향으로 맞추고 실제 벽 고정대를 연결했다. 새 모델11종은 편집 가능한 bevel 원본과 UV를 보존하며 기존 TC 도장/강철/바닥의 색·노멀·금속/거칠기 맵을 공유한다. 모델 합계500,152tri, 안내/표기 포함 검수 고유 메시20개 {a['triangles']:,}tri다.
- VA 쪽 T02/T08/T16 문3개를 Clinical Portal로 통일하고 기존 문은 비활성 보관했다. 이전 반구에 맞춘 VA 접합 장식5,076tri는 새 파생 메시에서만 제외했다. 다른 문 장식59,220tri와 원본 FBX는 유지했다. 제거 범위의 VA 중심 최대 반경4.80m를 확인했다.
- 기존 목적지 방식에 따라 C01 청록·C02 파랑을 유지하고 **새로 연결된 VA 녹색**을 추가했다. C01–T01–C02–T02–VA 계단 시작점까지 세 색의 네 방향 경로를 연결했다. 목적지 색은 출발 돔과 무관하게 일정하며 C04/다른 미제작 돔 안내는 추가하지 않았다. T02 바닥 코드4개·T01 통과 표기1개와 C01/C02/VA 바닥 색상 안내를 갱신했다. 실험동 내부 R1 순환선/S1/M1 국소 표기는 유지한다.
- 기존 Light187개의 색·밝기·범위 등 설정을 보존했다. 그중 VA_Work_1/3의 위치만 계단참 보행 공간에서 벽 등기구로 옮겼다. 새 상부 등기구8개에는 대응하는 Light8개를 두어 총195개다. 전체 조명·색감 조정은 B5 전체 제작 후 진행한다.
- 관제 정적 화면4장도 현재 안내선으로 갱신했다. 새 게임 C#/Animator는 없다. 새 MonoBehaviour8개는 URP의 UniversalAdditionalLightData이며 게임 동작이 아니다. 새 Collider12개는 계단/난간/셸/설비/문 및 지지 기둥·복도 보호 레일용이다.

## 검증

| 검사 | 결과 |
| --- | --- |
| 메시 퇴화·재질 누락 | 0 / 0 |
| 계단 머리 위 여유 | 96지점, 최소 {a['minHeadroom']:.2f}m |
| CharacterController | 16m 계단 왕복·T02 왕복·T08/T16 접근, 6/6통과 |
| 목적지 경로 | {p['samples']:,}표본, 막힘·바닥 누락0 / Controller4/4통과 |
| 서로 다른 색 선 최소 여백 | {spacing['minLineClearance']*100:.2f}cm |
| 모양/화살표 폭 포함 보수적 여백 | {spacing['minMarkerClearance']*100:.2f}cm |
| 기존/새 바닥 표기와 여백 | {spacing['minLabelClearance']*100:.2f}cm |
| 바닥 색상 안내 프랍 간섭 | {st['legendSamples']}표본, 막힘0 |
| 대상 외 기존 Transform | 변경0 |
| 기존 파일 | {f['baselineFiles']:,}개 중 대상14개 변경, 나머지{f['preservedFiles']:,}개 SHA256동일 |
| Play T02 | {inside['framesAdvanced']}프레임, W 입력 {inside['displacement']:.3f}m 이동, 새 경고/오류0 |
| Play 계단 | {stairs['framesAdvanced']}프레임, {stairs['displacement']:.3f}m 전진·{stairs['rise']:.3f}m 상승, 새 경고/오류0 |
| 최종 상태 | Edit 저장 완료, 플레이어 시작 위치/백그라운드 설정복구 |

1920×1080 Editor 관측 중앙값은 T02 {inside['medianMs']:.2f}ms/p95 {inside['p95Ms']:.2f}ms, 계단 {stairs['medianMs']:.2f}ms/p95 {stairs['p95Ms']:.2f}ms였다. 해당 시야의 짧은 측정이며 빌드 성능이나 전체 최적화 완료를 뜻하지 않는다.

Play 시작 중 Domain Reload/Hold on 진행 창은 로드 완료를 기다려 재접속했다. 첫 실제 입력 검사는235프레임 이동0으로 실패 처리했다. Game View 입력 전달 설정을 임시 적용한 재검사에서 이동을 확인하고 원래 설정을 복구했다. 화면 캡처는 서버가 반환한 Assets/Temp 경로에서 검수 폴더로 복사했고 임시 이미지 에셋을 삭제했다. Play 종료 후 남은 편집 dirty 상태도 별도 사본에 백업한 뒤 저장했으며 대상 외 변경이 없는지 재검사했다. 검수 도구의 초기 실패와 성공한 게임 검사를 구분한다.

## 보기와 남은 범위

- [계단실 진입](After_VA_Entry.png) · [아래에서 본 계단](After_VA_South.png)
- [T02 연결 복도](After_T02.png) · [실제 계단 Play](Play_stairs.png)
- [B4 높이 도착참](After_VA_B4Landing.png) · [위쪽 구조](After_VA_Up.png)

작업 전 씬/에셋 백업은 `%TEMP%/AfterSeconds_StairA_20261108_013839`, Play 후 편집 백업은 `%TEMP%/AfterSeconds_StairA_PostPlay_20261108_015326`이다. 검수 원문은 `audit.json`, `walk.json`, `probe.json`, `route_walk.json`, `spacing.json`, `play_inside.json`, `play_stairs.json`, `file_preservation.json`, `final_state.json`이다. [제작 원본](../../../SourceAssets/T02_StairA/README.md)을 우선한다.

다음 후보는 VA 외형 확인 후 T08→W01 제1격리생활동이다. T08/T16 본체는 이번 제작 범위가 아니며 그 끝의 돔도 아직 세부 제작 전이다. B4 실제 공간/층 전환·문 개폐는 후속 범위다. 사용자 전체 아트 최종 판정0/34는 유지한다.
'''
(D/'검수결과.md').write_text(report,encoding='utf-8')
(H/'README.md').write_text('''# T02 복도·계단 A 제작 V0.01

작성자 송예찬 · 2026-11-08

현재 T02/VA 건축과 C01–T01–C02–T02–VA 목적지 안내의 기준 원본이다. 도면은 `Docs/도면/Decision/원형공동/facility_layout.json`, 실제 계단 치수는 `geometry.json`, 안내 좌표는 `plan.json`이다. B5 -82m→B4 -66m의16m를8구간96단으로 연결하지만 B4 공간/씬 전환은 구현하지 않았다. 닫힌 상부문은 정적 외형이다.

## 제작과 적용

`build.py`는 기존 제작기의 함수 정의만 재사용해 TA_ 모델11종을 만들며 원래 제작 본문을 실행하지 않는다. 각 `.blend`에 편집용 bevel이 남고 FBX는 삼각화한 결과다. `refine_build.py`/`detail_build.py`는 이번 후속 보강 기록이다. 최종 `build.py`에 동일 보강을 반영했다. 모델11종500,152tri이며 TC PBR 텍스처3세트를 공유한다.

Unity 명령은 `python SourceAssets/B4_StealthLayout/unity_task.py script run <C# 절대경로> --entry <클래스.메서드>`를 사용한다. 먼저 현재 사용자 편집/씬/에셋을 별도 백업한다. `StairAApply.Run`은 자기 건축 그룹과 VA 셸/VA측 문3개, VA 하부 Light2개 위치만 갱신한다. 기존 문은 비활성 보관한다. 원본 전체 층이나 C01/C02/T01 제작기는 재실행하지 않는다.

`build_guides.py` → `verify_plan.py` → `textures.py` → `StairAGuideApply.Run`은 C01 청록/C02 파랑/VA 녹색의 목적지 안내를 만든다. numpy/Pillow는 `%TEMP%/as_art_tools/Scripts/python.exe`에 있다. `StairALabels.Run`으로 T02 표기4개와 T01 VA표기1개를 반영한다. `prepare_guides.py`는 초기 도구 복제 기록으로, 최종 수정된 검수/출처 코드를 덮어쓰지 않도록 재실행하지 않는다.

`StairACollarCleanup.Run`은 원본 전체 문 접합 메시에서 VA 영역만 제외한 `TA_PortalCollars_VAReplaced.asset`를 생성한다. 다른 문 장식/원본 FBX는 보존한다. 이미 적용된 씬에서 재생성하지 않는다. `CollisionFinish.cs`는 마지막에 추가한 기둥4개/보호 레일2개 Collider의 기록이며 같은 내용은 최종 Apply에 포함한다.

`Walk.cs`는 계단 전체 왕복과 세 문 접근, `GuideProbe.cs`/`GuideWalk.cs`는 안내 경로를 검사한다. `Audit.cs`는 메시·보호 Transform·기존 Light 설정·머리 위 여유를 확인한다. `Play.cs`/`run_play.py`는 기존 키보드 입력과 프레임/실제 이동으로 검증하고 설정을 복구한다. `fix_play_focus.py`는 포커스 처리 보강 기록이다. Play 도구 재생성 시 이를 반영하며 게임 C#을 바꾸지 않는다.

`Capture.cs`는 외형 검수, `Feeds.cs`/`refresh_feeds.py`는 관제 정적 화면 갱신이다. `PostPlay.cs`는 편집 상태를 백업/보존하고 임시 캡처를 정리한다. `RecordSource.cs`는 제작 좌표·모델·최종 상태 기록, `finalize_assets.py`는 기존 파일 보존 대조, `finish_documents.py`는 검수 문서 작성용이다. baseline/Prepare/Inspect는 작업 시작 기준이므로 덮어쓰지 않는다.

모델/재질/텍스처는 `Assets/Afrer_Seconds/05.Model/Environment/B5`, 출처는 `06.Data/AssetSources/T02_StairA_20261108.json`이다. 새 Light8개는 새 등기구에만 대응한다. 기존187 Light는 위치2개 외 설정을 보존했다. URP 조명 데이터8개 외 새 게임 Behaviour/Animator는 없다. 최종 조명은 B5 전체 후 조정한다.

[최신 검수](../../Docs/검수/2026-11-08_T02_StairA/검수결과.md). 로컬 저장, 이번 변경 커밋·push 미실시. 다음 후보는 T08/W01이다.
''',encoding='utf-8')
note='2026-11-08 T02/계단A 제작: T02 곡면 패널·보호 레일·배수·배선/제어함·환기구와 VA 원형 수직 코어를 제작했다. B5 -82m→B4 -66m 높이까지8구간96단·16m, 지지 기둥/중간참/난간/소방함/인터폰/등기구와 VA측 문3개를 마감했다. B4 실제 공간/씬 전환은 미연결, 상부 문은 닫힌 정적 외형이다. 새 모델11종500,152tri, 안내 포함 고유 검수504,664tri. 안내는 C01청록/C02파랑에 새 VA녹색을 더한3목적지4경로이며 다른 돔 안내는 해당 구역 제작 때 추가한다. 경로1,959표본 막힘0·Controller4/4, 계단 왕복/문 접근6/6, 머리 위 최소3.10m, Play 복도1.204m/계단0.682m상승·새 게임 로그0. 기존 Light187개의 설정은 보존하고 VA2개 위치만 등기구에 맞췄으며 상부 Light8개를 추가했다. 대상 외 기존 파일3,988개와 Transform 보존, 게임 C#/Animator변경0. 다음 후보는 T08→W01 제1격리생활동이며 VA 외형의 사용자 확인은 남는다. 전체 B5 후 조명 조정·아트 판정0/34 유지. 로컬 저장, 이번 변경 커밋·push 미실시. 작성자 송예찬.'
for rel,version in [('AGENTS.md','V0.54'),('CLAUDE.md','V0.54'),('Docs/이어하기_2026-11-06.md','V0.38'),('Docs/회사_작업목록_2026-11-06.md','V0.36'),('Docs/AfterSeconds_메인기획서.md','V0.43')]:
    path=R/rel;t=path.read_text(encoding='utf-8')
    if note not in t:
        head,rest=t.split('\n',1);prefix='Docs/' if '/' not in rel else ''
        t=re.sub(r'V0\.\d+',version,head)+'\n\n'+note+f' [최신 검수]({prefix}검수/2026-11-08_T02_StairA/검수결과.md).\n\n이전 단계 기록:\n'+rest.lstrip()
    if rel.endswith('메인기획서.md') and '| V0.43 |' not in t:
        assert '| V0.42 |' in t
        t=t.replace('| V0.42 |','| V0.43 | 2026-11-08 | 송예찬 | T02/VA 16m 계단 코어 제작, 목적지3색 확장, 통행/실제 Play 검수, B4 연결 미완료 범위 구분. |\n| V0.42 |',1)
    path.write_text(t,encoding='utf-8')
for rel,version,target in [('SourceAssets/B5_TwoDomeGuidance/README.md','V0.02','../T02_StairA/README.md'),('Docs/도면/Decision/원형공동/B5_안내체계/README.md','V0.06','../../../../../SourceAssets/T02_StairA/README.md')]:
    path=R/rel;t=path.read_text(encoding='utf-8');marker='2026-11-08 계단 A 제작 후 안내 확장'
    if marker not in t:
        head,rest=t.split('\n',1);t=re.sub(r'V0\.\d+',version,head)+f'\n\n{marker}: 새 T02/VA 구역이 제작되어 C01청록/C02파랑에 VA녹색을 추가했다. 현재 범위는3목적지4경로이며 [현재 제작 좌표/검수]({target})를 우선한다. 아래 두 돔만의 기록은 이전 단계다. 도달할 목적지별 안내와 새 돔 제작 시 확장이라는 사용자 방침은 유지한다. 작성자 송예찬.\n\n이전 단계 기록:\n'+rest.lstrip()
        if '## Revision History' in t:t+='\n| V0.06 | 2026-11-08 | 송예찬 | T02/VA 제작에 따른3목적지4경로 현장 확장. |\n'
        path.write_text(t,encoding='utf-8')
print(json.dumps({'validated':True,'models':11,'routeSamples':p['samples'],'controller':10,'playRise':stairs['rise'],'preserved':f['preservedFiles']},ensure_ascii=True))
