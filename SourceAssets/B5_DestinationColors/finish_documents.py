from pathlib import Path
import json
import re

H = Path(__file__).resolve().parent
R = H.parents[1]
D = R / 'Docs/검수/2026-11-08_B5_DestinationColors'
read = lambda name: json.loads((D / name).read_text(encoding='utf-8'))
a, p, w = read('audit.json'), read('probe.json'), read('route_walk.json')
s, f, state = read('spacing.json'), read('file_preservation.json'), read('final_state.json')
assert not any([a['degenerate'], a['downward'], a['missingMaterials'], a['oldMainGuidesActive'], a['oldC04GuideActive'], a['protectedTransformChanges'], a['lightChanges'], a['newColliders'], a['newBehaviours'], p['blocked'], p['missingFloor'], f['missing'], f['unexpected'], state['dirty'], state['playing'], state['legendBlocked']])
assert a['lightCount'] == 187 and len(w['routes']) == 6 and all(t['passed'] for t in w['routes'])
assert s['minMarkerClearance'] > .10 and s['minLabelClearance'] > .04 and s['minS1Clearance'] > .08

palette = '''| 목적지 | 색 | 식별 모양 |
| --- | --- | --- |
| C01 실험동 | 청록 `#39C8E3` | 원 |
| C02 보안관제동 | 파랑 `#4F8CFF` | 사각 |
| C04 유틸리티동 | 보라 `#C27FFF` | 마름모 |
| VA 계단 A | 녹색 `#70D692` | 이중 막대 |'''

(D / '검수결과.md').write_text(f'''# B5 목적지별 안내선 색 구분 검수 V0.01

작성자 송예찬 · 2026-11-08

기존 흰 R1 주 안내선을 목적지별 네 색으로 교체했다. 현재 연결 범위는 C01–T01–C02–T02–VA 및 C02–T05–C04다. 전체 15목적지·19복도의 일괄 적용은 아니다. 로컬 씬을 저장했으며 이번 변경을 커밋·push하지 않았다.

{palette}

## 실제 반영

- 방향이 있는 경로6개: VA→C01, C01→VA, C01→C02, C01→C04, VA→C02, C04→C02. 목적지 색은 출발 구역과 무관하게 일정하다. T01에서는 네 색을 평행 배치하고 C02에서 각각 관제석·계단A·유틸리티동 방향으로 분기한다. C04 안내는 입구 안쪽2m까지 연결했다.
- 선 폭10cm, T01 중심 간격32cm. 화살표와 식별 모양으로 방향·목적지를 보조하고 기존 바닥 목적지7곳도 해당 색으로 맞췄다. C01/C02 바닥에 각각 네 목적지 색상 안내를 추가했다. 구역명 벽 명판은 추가하지 않았다.
- 이전 `R1_Continuous` 렌더러2개와 `SC_R1_T05_ToC04` 렌더러를 비활성화했다. 원본 메시·계층은 보존했다. 실험동 내부의 흰 R1 순환선/코드, 국소 S1 시료선과 M1 정비 표기는 유지했다. 청록 목적지 도착선만 기존 실험동 내부 순환선에 연결했다.
- T01 실험동 입구에서 기존 선이 문 중심을 벗어난 구간을 실제 문 중심으로 정렬했다. 새 안내는 `Destination_Colour_Guidance` 그룹이다. 메시9개/{a['triangles']:,}tri, 재질10개, 텍스처6개. 재질은 비발광 바닥 도장이다.
- 관제 감시 피드01–04를 새 색 안내선이 보이는 현재 씬으로 갱신했다. 화면은 정적이다. 기존 C02 텍스처 제작기도 최신 피드가 있으면 이를 우선하도록 연결했다.

## 검증

| 검사 | 결과 |
| --- | --- |
| 서로 다른 목적지 선 가장자리 최소 여백 | {s['minLineClearance']*100:.2f}cm |
| 화살표/모양 최대 폭을 포함한 보수적 여백 | {s['minMarkerClearance']*100:.2f}cm |
| 기존 바닥 표기·새 색상 안내와의 최소 여백 | {s['minLabelClearance']*100:.2f}cm |
| 유지한 S1과 최소 여백 | {s['minS1Clearance']*100:.2f}cm |
| 통행·바닥 검사 | {p['samples']:,}표본, 막힘·바닥 누락0 |
| CharacterController | 반경28cm, 경로6/6 통과 |
| 두 바닥 색상 안내 주변 프랍 검사 | {state['legendSamples']}표본, 막힘0 |
| 메시 퇴화·뒤집힌 면·재질 누락 | 0 / 0 / 0 |
| 기존 Transform / Light187개 | 변경0 / 변경0 |
| 기존 파일 보존 | {f['baselineFiles']:,}개 중 씬·화면4장만 변경, 나머지{f['preservedFiles']:,}개 SHA256동일 |
| 최종 상태 | Edit, 저장 완료, 플레이어 위치와 백그라운드 설정 유지 |

같은 C02 파란 노선이 관제석 앞에서 합류하는 것은 의도한 연결이다. 서로 다른 색의 교차는 없다. 통행 검사는 기존 CharacterController를 편집 도구로 이동시킨 결과이며, 이번 바닥 도장 변경에서 새 키보드 Play 검사를 수행한 것은 아니다. 런타임 코드·Animator 변경0, 새 Collider/Light0. 전체 조명·색감 조정은 B5 완성 후 진행한다.

## 보기와 이어하기

- [실험동 출발 지점](C01/After_NorthJunction.png)
- [T01 복도](T01/After_ToSecurity.png)
- [관제동 분기](After_FromLab.png) · [전체 배치](After_Overview.png)
- [업데이트된 감시 화면](After_WallDetail.png)

실측/검수 원문은 `spacing.json`, `probe.json`, `route_walk.json`, `audit.json`, `file_preservation.json`, `final_state.json`이다. 작업 전 씬과 기존 감시 텍스처는 `%TEMP%/AfterSeconds_DestinationColors_20261108_011926`에 보존했다. 제작 좌표·색상은 [제작 원본](../../../SourceAssets/B5_DestinationColors/README.md)을 우선한다.

다음은 T02/계단A 연결부 제작과 이후 돔별 안내 확장이다. 나머지 목적지의 색·노선은 미확정이며, 새 구역 연결 시 기존 네 색 및 국소 S1/M1과의 중첩을 다시 확인한다. 현재 네 색의 시각 확인과 전체 아트 최종 판정은 사용자 검수 대상으로 남는다. 전체 아트 판정0/34 유지.
''', encoding='utf-8')

(H / 'README.md').write_text(f'''# B5 목적지별 색 안내선 제작 V0.01

작성자 송예찬 · 2026-11-08

현재 C01/T01/C02/T02/VA/T05/C04의 안내선은 이 폴더의 `plan.json`과 [최신 검수](../../Docs/검수/2026-11-08_B5_DestinationColors/검수결과.md)를 우선한다. 이전 B5_WayfindingNetwork의 R1/S1/M1 전역 배치안은 참고 자료이며 현재 반영 구간 위에 그대로 적용하지 않는다.

{palette}

## 원본과 실행 범위

`Survey.cs`는 기존 선·표기/포털을 읽는다. `build_plan.py`는 실제 T01 문 중심과 C02 분기를 따라 여섯 경로를 만든다. `verify_plan.py`는 선/모양/표기/S1 간격을 검사하며 numpy가 필요하다. `textures.py`는 Pillow로 목적지 스텐실4장과 바닥 색상 안내2장을 만든다. 현재 도구 환경은 `%TEMP%/as_art_tools/Scripts/python.exe`다.

Unity 호출은 `python SourceAssets/B4_StealthLayout/unity_task.py script run <C# 절대경로> --entry <클래스.메서드>`를 사용한다. `Apply.cs`의 `DestinationApply.Run`은 전용 메시·재질·안내 그룹과 명시된 기존 표기/렌더러만 갱신한다. 기존 C01 내부 순환선·S1/M1은 보존하며 이전 전체 C01/C02/층 Apply는 재실행하지 않는다. 재적용 전 현재 사용자 편집과 씬을 별도로 백업한다.

`Probe.cs`, `RouteWalk.cs`, `Audit.cs`로 물리 통행/실제 Controller/보호 상태를 검사한다. `Capture.cs`, `T01Capture.cs`, `LabCapture.cs`는 편집 카메라 검수다. `Feeds.cs` → `refresh_feeds.py`는 SC_Display_01–04의 정적 화면을 갱신한다. `RecordSource.cs`는 두 바닥 색상 안내의 프랍 간섭을 검사하고 출처 JSON을 저장한다. `record_preservation.py`는 원래 파일의 SHA256을 대조한다. `finish_documents.py`는 검수 결과를 확인한 뒤 문서를 갱신한다.

모델/재질/텍스처는 `Assets/Afrer_Seconds/05.Model/Environment/B5` 및 Materials/Textures, 출처는 `06.Data/AssetSources/B5_DestinationColors_20261108.json`이다. `prepare.py`/`Prepare.cs`와 `baseline.json`은 이번 작업 시작 시점 기록이므로 후속 작업에서 기존 기준을 덮어쓰도록 재실행하지 않는다.

적용은 네 목적지·여섯 경로에 한정된다. 나머지11목적지와 다른 복도 확장은 별도 설계/간격 검수가 필요하다. 게임 C#/Animator는 추가하지 않으며 최종 조명은 B5 전체 제작 후 조정한다.
''', encoding='utf-8')

note = '2026-11-08 목적지 색 안내선 반영: C01 실험동 청록(#39C8E3), C02 보안관제동 파랑(#4F8CFF), C04 유틸리티동 보라(#C27FFF), VA 계단A 녹색(#70D692). T01 네 평행선과 C02 분기를 포함한6경로를 구현하고 목적지 바닥 표기7곳·색상 안내2곳·정적 감시 피드4장을 갱신했다. 서로 다른 색 교차0, 모양 포함 최소 여백11.96cm, 통행3,051표본 막힘0·Controller6/6 통과. 기존 Transform/Light187개 및 대상 외 기존 파일3,941개 보존, 게임 코드 변경0. 실험동 내부 흰 R1 순환선·S1/M1 국소 표기는 유지했다. 전체15목적지/19복도 적용 완료는 아니며 이전 용도별 전역 배치안을 현재 구간에 중복 적용하지 않는다. 다음은 T02/계단A 연결부와 이후 목적지별 확장, 현재 외형은 사용자 확인 대상이다. 전체 B5 후 조명 조정·아트 판정0/34 유지. 로컬 저장, 이번 변경 커밋·push 미실시. 작성자 송예찬.'
for rel, version in [('AGENTS.md','V0.52'), ('CLAUDE.md','V0.52'), ('Docs/이어하기_2026-11-06.md','V0.36'), ('Docs/회사_작업목록_2026-11-06.md','V0.34'), ('Docs/AfterSeconds_메인기획서.md','V0.41')]:
    path = R / rel
    body = path.read_text(encoding='utf-8')
    if note not in body:
        head, rest = body.split('\n', 1)
        head = re.sub(r'V0\.\d+', version, head)
        prefix = 'Docs/' if '/' not in rel else ''
        body = head + '\n\n' + note + f' [최신 검수]({prefix}검수/2026-11-08_B5_DestinationColors/검수결과.md).\n\n이전 단계 기록:\n' + rest.lstrip()
    if rel.endswith('메인기획서.md') and '| V0.41 |' not in body:
        assert '| V0.40 |' in body
        body = body.replace('| V0.40 |', '| V0.41 | 2026-11-08 | 송예찬 | 네 목적지 색 안내선6경로·바닥 표기·정적 피드 갱신, 간격/통행 검수와 전체 확장 미완료 범위 기록. |\n| V0.40 |', 1)
    path.write_text(body, encoding='utf-8')

updates = [
    ('Docs/도면/Decision/원형공동/B5_안내체계/README.md', 'V0.04', '../../../../../SourceAssets/B5_DestinationColors/README.md'),
    ('SourceAssets/B5_WayfindingNetwork/README.md', 'V0.02', '../B5_DestinationColors/README.md'),
]
for rel, version, target in updates:
    path = R / rel
    body = path.read_text(encoding='utf-8')
    marker = '2026-11-08 목적지별 색상 적용 우선'
    if marker not in body:
        head, rest = body.split('\n', 1)
        body = re.sub(r'V0\.\d+', version, head) + f'\n\n{marker}: C01 청록·C02 파랑·C04 보라·VA 녹색의6방향 경로가 현장 반영됐다. 현재 연결 구간은 [최신 제작 좌표와 검수]({target})를 따른다. 아래 R1/S1/M1 전체 배치도는 이전 가안이며 현재 구간 위에 중복 적용하지 않는다. 실험동 내부의 국소 R1/S1/M1은 유지했다. 전체15목적지·19복도 색 안내 적용은 남는다. 작성자 송예찬.\n\n이전 단계 기록:\n' + rest.lstrip()
        if '## Revision History' in body:
            body += '\n| V0.04 | 2026-11-08 | 송예찬 | 네 목적지 색상6경로 현장 반영을 우선하고 기존 전체 배치안의 참고 범위 구분. |\n'
        path.write_text(body, encoding='utf-8')
print(json.dumps({'validated': True, 'triangles': a['triangles'], 'paths': len(w['routes']), 'preserved': f['preservedFiles']}, ensure_ascii=True))
