"""B5 전체 안내체계 배치안과 인수인계를 기록한다. 작성자 송예찬."""
from pathlib import Path
import json,csv,hashlib,base64
R=Path(__file__).resolve().parents[2];H=Path(__file__).resolve().parent
O=R/'Docs/도면/Decision/원형공동/B5_안내체계'
p=json.loads((O/'wayfinding_plan.json').read_text(encoding='utf-8'))
v=json.loads((O/'geometry_validation.json').read_text(encoding='utf-8'))
u=json.loads((O/'unity_probe.json').read_text(encoding='utf-8'))
s=json.loads((H/'survey.json').read_text(encoding='utf-8'))
scene=R/'Unity/After_Seconds_Build_V0.01'/s['scene']
scene_same=base64.b64encode(hashlib.sha256(scene.read_bytes()).digest()).decode()==s['sceneFileHash']
assert scene_same and not u['badPaths'] and not u['badLabels']
with (O/'목적지_목록.csv').open('w',encoding='utf-8-sig',newline='') as f:
 w=csv.writer(f);w.writerow(['층','섹터','목적지 코드','표시 이름','Unity X','Unity Z','상태'])
 for d in p['destinations']:w.writerow(['B5',d['sector'],d['code'],d['name'],*d['position'],'폐쇄·입구 종단' if d['restricted'] else '배치안'])
destrows='\n'.join(f"| {d['sector']} | {d['code']} | {d['name']} | {'폐쇄 입구 종단' if d['restricted'] else '일반 목적지' if d['kind']=='cavern' else '공용 이동 목적지'} |" for d in p['destinations'])
corridorrows='\n'.join(f"| {e['code']} | {e['a']} ↔ {e['b']} | {' / '.join(e['lanes'])} | {', '.join(f'{k}: {x:+.2f}m' for k,x in e['lanes'].items())} |" for e in p['corridors'])
report=f'''# B5 구역·목적지·전체 안내체계 배치안 V0.01

작성자 송예찬 · 2026-11-07

사용자가 승인한 5섹터 구분을 작업 기준으로 삼아 15개 목적지 이름과 19개 복도의 전체 배치안을 정리했다. 목적지 이름은 바닥 안내선 옆에 표기한다. 별도 구역 명판은 만들지 않는다.

이번 산출물은 **기존 R1/S1/M1 용도별 선을 유지하는 검토안**이다. 사용자에게 용도별 유지/돔별 전용선 중 구분 기준을 물었으며 응답 전에는 기존 체계를 기준으로 설계를 진행했다. 선 구분 방식에 대한 새 답이 오면 이 배치안을 조정한다. 아직 Unity 바닥 메시·텍스처를 교체하지 않았다.

## 바로 보기

- [전체 안내선 PNG](B5_전체안내선.png) · [SVG](B5_전체안내선.svg)
- [확대·노선 표시·목적지 선택이 가능한 검토용 HTML](B5_안내선_검토.html)
- [C04 세 노선 분리 상세](C04_분기상세.png)
- [목적지 표 CSV](목적지_목록.csv) · [좌표/노선/글자 영역 JSON](wayfinding_plan.json)

HTML은 파일을 브라우저에서 열면 동작한다. 외부 서비스·CDN·게임 UI를 사용하지 않는다. 전체도는 선을 굵게 표시한 검토용 표현이고, 상세도와 JSON은 실제 선 폭을 기준으로 한다.

## 구역과 이름

| 섹터 | 목적지 코드 | 표시 이름 | 구분 |
| --- | --- | --- | --- |
{destrows}

상위 구분은 C 중앙 실험·운영, W 격리·의료, E 생활지원, N 중앙관제, S 폐쇄시험이다. 기존 관리 코드와 돔 위치를 유지했다. 내부 설계의 ‘의료 안정’ 등 세부 기능은 이름을 간결하게 줄여도 유지한다.

## 노선 의미와 목적지

- **R1 직원 이동:** 일반 직원 접근 네트워크. C01에서 T01→C02→T02→VA 계단 A로 이어지는 기존 주 경로를 유지하고, 서·동·북측 공동과 VB/VL로 접근하는 연결을 포함한다. 모든 R1 가지가 지상 출구를 뜻하지 않으며 목적지 이름을 보고 분기한다. 계단 A/B는 현재 B5의 이동 목적지이고 지상까지의 완성된 층간 연결을 가정하지 않는다.
- **S1 시료 이송:** W03 의료검사동→T11→C01 실험동→T03→C03 냉각설비동→T04→C04 유틸리티동→T06→VL 화물 인계 구역. C03/C04는 현 평면에서의 통과 구역이다. 시료 수거·인계 설비의 구체적인 프랍은 해당 구역 아트에서 별도 배치한다.
- **M1 설비 정비:** VL→T06→C04 유틸리티동→T04→C03 냉각설비동. S1과 함께 쓰는 구간은 나란히 분리한다. 실험동 점검함 앞 기존 M1은 국소 작업공간 표시로 별도 유지 여부를 검토하며 이 전체 설비 노선의 출발점으로 연결하지 않는다.
- **S01 폐쇄시험동:** T18/T19 양쪽 접근선은 해당 입구에서 끝난다. 두 입구를 실내 선으로 연결하지 않고 다른 구역으로 가는 통과 경로로 사용하지 않는다. 문 잠금·출입 제한의 게임 기능을 새로 구현한 것은 아니다.

같은 용도의 가지가 만나는 접속점은 하나의 노선 연결로 취급한다. 서로 다른 노선을 같은 자리에 포개거나 색으로 덮지 않는다. 기존 C01 T11 쪽 R1 연장은 이 배치안에서 의료/시료 동선을 읽기 쉽도록 S1으로 재분류할 대상이다.

## 복도별 배치

오프셋은 JSON의 p→q 진행 방향에 대한 오른쪽(+)·왼쪽(-)이다. 양 끝에서 이 기준을 뒤집지 않아야 선 순서가 유지된다. 모든 복도는 설계 폭 4.2m다.

| 복도 | 연결 목적지 | 사용하는 선 | 중앙선 기준 오프셋 |
| --- | --- | --- | --- |
{corridorrows}

R1은 선 폭 5cm 두 줄·중심 간격 24cm(전체 폭 29cm), S1은 9cm 선, M1은 7.5cm 점선의 표면 제작 기준을 사용했다. T04는 중심 간격 60cm의 두 줄, T06은 -60/0/+60cm 세 노선으로 분리했다. 이 치수는 이번 배치안의 검증 값이며 실제 메시 마감 후 다시 대조한다.

목적지 표기 영역은 각 복도의 양쪽 진행 방향에 대해 출발·도착 쪽에 한 번씩, 총 76곳이다. `목적지 코드 / 구역·이름 / 방향`을 넣을 0.60×1.40m 영역을 이동 방향 오른쪽 1.15m, 문 경계에서 복도 안쪽 2.5m 위치에 확보했다. 안내선 자체와 글자가 겹치지 않는다. 같은 복도에서 R1/S1/M1이 같은 목적지로 향하면 목적지 글자를 세 번 중복 인쇄하지 않고 해당 방향의 공통 목적지 표기로 읽는다.

## 실제 검사

| 항목 | 결과 |
| --- | --- |
| 공간·복도 | 15개 목적지 / 19개 복도 |
| 다른 용도 선의 교차·중첩 | 0 |
| 서로 다른 선 가장자리 최소 간격 | {v['minimumDifferentRouteEdgeGapM']*100:.2f}cm |
| 글자 영역끼리 / 글자 영역과 선 간섭 | 0 / 0 |
| 글자 영역과 선 최소 간격 | {v['minimumLineLabelGapM']*100:.2f}cm |
| 닫힌 S01 내부를 경유하지 않는 목적지 도달성 | 방향별 210조합 연결 |
| Unity 경로 캡슐/바닥 검사 | {u['pathSamples']:,}표본, 막힘·바닥 누락 0 |
| Unity 표기 영역 바닥 검사 | {u['labelSamples']:,}표본, 막힘·바닥 누락 0 |
| Editor/씬 상태 | 읽기 전용, dirty false→false, 저장 씬 SHA-256 동일 |
| 문서 | SVG XML 유효, HTML 실행·목적지 연결 목록 표시 확인 |

목적지 도달성은 연결 그래프 검사이고, 표시된 바닥 경로와 텍스트 영역은 현재 씬의 Collider에 대조했다. 새 도장 메시·실제 글꼴의 가독성·곡선 마감·Play 화면은 아직 검수하지 않았다. 다른 돔의 프랍을 추가한 뒤에도 배치 충돌을 다시 검사해야 한다.

## 현장 반영 순서

1. 이 JSON을 기준으로 전체 바닥 도장과 목적지 글자를 만든다. 꺾임을 둥글게 처리한 실제 메시와 글자 경계로 겹침 검사를 다시 수행한다.
2. 기존 `Facility_Floor_Guidance_R1`과 `C01_Workplace_Wayfinding`의 이동 안내 부분을 백업 후 새 네트워크로 교체한다. 기존 선 위에 새 선을 중복 배치하지 않는다. 점검함 접근 공간·문턱 표시의 유지 항목은 이동 안내선과 구분한다.
3. 기존 C01 문 옆 임시 R1/S1 코드판은 바닥 목적지·용도 표기로 정리한다. 문틀·리브·승인된 프랍과 조명은 보존한다.
4. 분기점의 실제 시야·목적지 문자 가독성·문 통행과 Play 이동을 검수한다. 이후 T01→C02 아트를 이어간다.

현재는 도면과 제작 데이터만 로컬 저장했다. Unity 새 안내선 적용·커밋·push는 하지 않았다. B5 전체 제작 후 조명·색감을 일괄 조정한다는 사용자 방침을 유지한다.

## Revision History

| 버전 | 날짜 | 작성자 | 변경 |
| --- | --- | --- | --- |
| V0.01 | 2026-11-07 | 송예찬 | 5섹터·15목적지·19복도 노선 및 76표기 영역 배치안, 겹침·씬 바닥 대조, 검토 도면 |
'''
(O/'README.md').write_text(report,encoding='utf-8')
(H/'README.md').write_text('''# B5 전체 안내체계 배치안 제작 V0.01

작성자 송예찬 · 2026-11-07

결과는 [도면과 검수 기록](../../Docs/도면/Decision/원형공동/B5_안내체계/README.md)을 따른다. 이번 소스는 읽기 전용 씬 조사와 전체 안내선 설계용이다. Unity에 새 메시·컴포넌트를 추가하지 않는다.

재현 순서: `Survey.cs` → `build_plan.py` → `verify_plan.py` → `ProbePlan.cs` → `render_plan.py`. C#은 기존 `SourceAssets/B4_StealthLayout/unity_task.py script run <절대경로> --entry <클래스.Run>`으로 호출한다. 기존 JSON의 설계 좌표를 Unity 월드 X/Z로 변환하고 실제 바닥/충돌 격자를 조사한 뒤 경로를 계산한다. 바닥 표면 후보의 전체 폭·다른 노선 간격·목적지 글자 영역을 따로 검사한다.

R1은 직원 접근 네트워크, S1은 의료검사–실험–화물 인계, M1은 화물–유틸리티–냉각 설비 연결이라는 현행 용도별 제안이다. 노선 구분 방식에 대한 사용자 답이 오면 이를 우선한다. 목적지 이름은 JSON/CSV와 도면에 같이 보관한다.

SVG와 자체 HTML은 코드로 생성한 실제 설계 데이터 시각화다. PNG는 Chrome headless로 SVG를 렌더링한다. 게임 화면·게임 UI가 아니다. `finish_documents.py`는 이번 작업의 문서 정리용이며 인수인계 버전 갱신은 별도 수행한다. 기존 `SourceAssets/C01_Wayfinding`의 Apply나 전체 레벨 제작기를 재실행하지 않는다.
''',encoding='utf-8')
proof=dict(scene=s['scene'],before=s['sceneFileHash'],after=base64.b64encode(hashlib.sha256(scene.read_bytes()).digest()).decode(),unchanged=scene_same,dirtyBefore=u['dirtyBefore'],dirtyAfter=u['dirtyAfter'])
(O/'scene_preservation.json').write_text(json.dumps(proof,ensure_ascii=False,indent=2),encoding='utf-8')
print('Destination CSV, plan README, source README and preservation evidence saved.')
