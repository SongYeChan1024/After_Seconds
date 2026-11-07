"""Corridor-only wayfinding baseline and specification. Author 송예찬."""
from pathlib import Path
import json,hashlib
H=Path(__file__).resolve().parent;R=H.parents[1];D=R/'Docs/검수/2026-11-08_B5_CorridorOnlyGuidance';D.mkdir(parents=True,exist_ok=True)
src=R/'SourceAssets/B5_OperationalDetail'
s=(src/'Inspect.cs').read_text(encoding='utf-8').replace('B5_OperationalDetail','B5_CorridorOnlyGuidance').replace('OperationalInspect','CorridorInspect').replace('AfterSeconds_Operational_','AfterSeconds_CorridorOnly_');(H/'Inspect.cs').write_text(s,encoding='utf-8')
A=R/'Unity/After_Seconds_Build_V0.01/Assets'
if not (H/'assets_before.json').exists():(H/'assets_before.json').write_text(json.dumps({str(p.relative_to(A)):hashlib.sha256(p.read_bytes()).hexdigest() for p in A.rglob('*') if p.is_file()},indent=2),encoding='utf-8')
(H/'plan.json').write_text((R/'SourceAssets/B5_SpatialRefinement/plan.json').read_text(encoding='utf-8'),encoding='utf-8')
f=R/'Docs/AfterSeconds_메인기획서.md';s=f.read_text(encoding='utf-8');note='2026-11-08 사용자 확정: 바닥 이동 안내선은 복도에만 배치한다. 돔과 계단/승강기 코어 내부의 목적지 선·화살표·바닥 목적지 문자·범례, C01 내부 R1/S1/M1 이동선은 제거한다. 복도에서는 기존 목적지별 색·문자·방향을 유지하고 양 끝을 돔 외곽/출입 전환부에서 마감한다. 장비의 작업 표식·적재 경계·문턱 안전 표시는 이동 안내선과 구분해 유지한다. 이전 돔 내부 연결 방식보다 이 결정을 우선한다. 작성자 송예찬.'
if note not in s:
 s=s.replace('메인 기획서 V0.46','메인 기획서 V0.47',1);head,body=s.split('\n',1);s=head+'\n\n'+note+'\n\n'+body.lstrip();s=s.replace('| V0.46 |','| V0.47 | 2026-11-08 | 송예찬 | 이동 안내선을 복도에만 유지하고 돔/코어 내부 노선·목적지 문자·범례를 제거하도록 변경. |\n| V0.46 |',1);f.write_text(s,encoding='utf-8')
(H/'README.md').write_text('# B5 복도 전용 안내선 V0.01\n\n작성자 송예찬 · 2026-11-08\n\n'+note+'\n\nUnity Editor API로 기존 안내 메시의 복도 영역만 UV/재질을 보존해 복제한다. 기존 메시 원본은 보존하며 씬의 기존 안내 렌더러를 비활성화한다. 새 CG_ 메시와 검수 자료는 이 작업 전용이다. 게임 코드/충돌/조명 변경 없음.\n',encoding='utf-8')
print('Baseline and design prepared')
