"""Save verified corridor-only guidance handoff. Author 송예찬."""
from pathlib import Path
import json,html
H=Path(__file__).resolve().parent;R=H.parents[1];D=R/'Docs/검수/2026-11-08_B5_CorridorOnlyGuidance'
v=json.loads((D/'verification.json').read_text(encoding='utf-8'));p=json.loads((D/'preservation.json').read_text(encoding='utf-8'));a=json.loads((D/'apply.json').read_text(encoding='utf-8'))
assert v['domeInteriorVertices']==0 and v['outsideCorridorVertices']==0 and v['sourceStillVisible']==0 and p['lightsUnchanged'] and a['collidersSame']
note='2026-11-08 안내선 복도 한정 완료: 사용자 요청에 따라 돔·계단/승강기 코어 내부의 이동선·화살표·목적지 문자·범례와 실험동 R1/S1/M1 바닥 이동 표기를 제거했다. 19개 복도의 목적지별 색·방향·문자는 유지하고 선 끝은 돔 외곽에서 복도 쪽 20cm에 정렬했다. 기존 안내 Renderer152개를 보존/비활성화하고 복도 구간 메시120개를 적용했다. 저장 씬 재로드 후 정점89,463개를 검사해 돔 내부/복도 밖 안내 정점0, 이전 안내 재노출0. 기존247 Light·Collider·Transform3,582개·대상 씬 외 기존 Assets5,511개 동일. 장비 작업/적재 안전 표시는 유지. **안내선은 앞으로도 복도에만 두며 이전 돔 내부 안내 유지 기록보다 이 결정을 우선한다.** 사용자 외형 검수와 B5 전체 조명 마감은 남음. 로컬 저장, 커밋·push 미실시. 작성자 송예찬.'
for rel,old,new in [('AGENTS.md','0.57','0.58'),('CLAUDE.md','0.57','0.58'),('Docs/이어하기_2026-11-06.md','0.41','0.42'),('Docs/회사_작업목록_2026-11-06.md','0.39','0.40'),('Docs/도면/Decision/원형공동/B5_안내체계/README.md','0.08','0.09')]:
 f=R/rel;s=f.read_text(encoding='utf-8')
 if note in s:continue
 head,body=s.split('\n',1);assert 'V'+old in head,head;head=head.replace('V'+old,'V'+new)
 prefix='../../../../' if 'B5_안내체계' in rel else '' if rel.startswith('Docs/') else 'Docs/'
 links=f' [검수 화면]({prefix}검수/2026-11-08_B5_CorridorOnlyGuidance/review.html) · [검수 결과]({prefix}검수/2026-11-08_B5_CorridorOnlyGuidance/검수결과.md).'
 s=head+'\n\n'+note+links+'\n\n이전 단계 기록:\n'+body.lstrip()
 if 'B5_안내체계' in rel:s+='\n| V0.09 | 2026-11-08 | 송예찬 | 돔 내부 안내 제거, 19복도만 유지하는 최종 배치 기준과 검수 추가. |\n'
 f.write_text(s,encoding='utf-8')
f=R/'Docs/AfterSeconds_메인기획서.md';s=f.read_text(encoding='utf-8')
if note not in s:
 head,body=s.split('\n',1);f.write_text(head+'\n\n'+note+' [검수](검수/2026-11-08_B5_CorridorOnlyGuidance/review.html).\n\n'+body.lstrip(),encoding='utf-8')
(H/'README.md').write_text('# B5 복도 전용 안내선 V0.01\n\n작성자 송예찬 · 2026-11-08\n\n'+note+'\n\n`Apply.cs`는 Unity Editor에서 기존 안내 메시를 복도 사각 영역으로 잘라 UV/재질을 보존한 `CG_` 메시를 생성한다. 텍스트는 전체가 복도 안에 들어오는 경우만 유지한다. 원본 파일과 GameObject는 보존하고 이전 Renderer만 비활성화한다. 재실행 방지 가드가 있다. `Verify.cs`는 저장 후 모든 정점의 복도/돔 경계를 검사한다. 새 Collider/MonoBehaviour 없음.\n\n기준 좌표: `plan.json`, 실제 절단 경계: 검수 폴더 `apply.json`. 이전 안내 생성기를 그대로 재적용하지 않는다. `Capture.cs`의 `Run` 후 가려진 두 공간은 `FloorOverview`로 보완한다. 보고서는 `report.py`, 보존 검사는 `preservation.py`.\n',encoding='utf-8')
report=f'''# B5 복도 전용 안내선 검수 V0.01

작성자 송예찬 · 2026-11-08

사용자 결정: 이동 안내선은 복도에만 둔다. 돔 내부의 선·방향 화살표·바닥 목적지 문자·색 범례, 실험동의 R1/S1/M1 바닥 이동 안내를 함께 제거했다. 장비 작업 표식·적재 경계·안전 표시는 유지했다.

- 19개 복도에 목적지 색·방향·문자 유지. 끝은 돔 평면 외곽에서 복도 쪽 20cm에 정렬했다.
- 기존 안내 Renderer {a['sources']}개 보존/비활성화, 복도 부분 메시 {a['meshes']}개, {a['triangles']:,}삼각형. 기존 원본 메시/재질 수정 없음.
- 저장 씬 재로드 후 {v['vertices']:,}정점 검사: 돔 내부0·복도 밖0·이전 안내 재노출0. 문자 중간 절단 방지. 퇴화 삼각형/누락 재질0.
- 기존 Assets {p['baselineAssets']:,}개 중 대상 B5 씬만 변경. 기존 조명247개, 충돌체, 기존 Transform {p['oldTransforms']:,}개 보존. 새 Collider/MonoBehaviour0.
- 37개 화면으로 복도19·돔/코어15·입구3곳 확인. C04/VL은 설비 가림을 피한 별도 구도로 보완. 조명 후처리 없는 Editor 임시 카메라 캡처이며 Play 이동 검증은 이번 변경에서 재실시하지 않았다.

씬: `Assets/Afrer_Seconds/01.Scenes/Stage/Level_B5_Circular.unity`.
활성 안내 그룹: `B5_CorridorOnly_Guidance`.
기존 그룹이 활성 상태여도 해당 안내 Renderer는 비활성화되어 있다. 이전 제작 도구를 재실행해 돔 내부 선을 복구하지 않는다.

[검수 화면](review.html) · [형상 검사](verification.json) · [보존 비교](preservation.json) · [적용 상세](apply.json).

로컬 저장. 커밋·push 미실시. 사용자 외형 검수 및 전체 조명·색감 마감은 별도이며 게임 기능 구현 범위를 늘리지 않았다.
'''
(D/'검수결과.md').write_text(report,encoding='utf-8')
groups=[('입구 마감',sorted(D.glob('*_threshold.png'))),('돔 내부',sorted(D.glob('*_dome.png'))),('복도 안내선',sorted(D.glob('*_corridor.png')))]
parts=[]
for title,files in groups:
 parts.append('<h2>'+title+'</h2><div class="grid">')
 for f in files:parts.append(f'<figure><a href="{f.name}"><img loading="lazy" src="{f.name}" alt="{html.escape(f.stem)}"></a><figcaption>{html.escape(f.stem)}</figcaption></figure>')
 parts.append('</div>')
(D/'review.html').write_text('<!doctype html><html lang="ko"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>B5 복도 전용 안내선</title><style>body{background:#121820;color:#e4ebf2;font:16px/1.6 system-ui;margin:auto;padding:32px;max-width:1600px}a{color:#7ed6ed}.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(360px,1fr));gap:18px}figure{margin:0;background:#1c2733}img{width:100%;display:block}figcaption{padding:10px}h2{margin-top:40px}</style><h1>B5 복도 전용 안내선</h1><p>2026-11-08 · 작성자 송예찬 · 로컬 검수 자료</p><p>돔 내부 이동 안내를 제거하고 19개 복도의 목적지 색·방향·문자는 유지했습니다. 장비 작업·안전 표시는 유지합니다. 입구의 선 끝과 실내 바닥을 확인할 수 있습니다.</p><p><a href="검수결과.md">검수 결과</a> · 이미지를 클릭하면 원본을 엽니다.</p>'+''.join(parts)+'</html>',encoding='utf-8')
record={'author':'송예찬','date':'2026-11-08','task':'B5 복도 전용 안내선','source':'기존 프로젝트 안내 메시에서 복도 영역을 절단한 파생 메시. 외부 생성/다운로드 없음.','meshes':120,'assetPattern':'Assets/Afrer_Seconds/05.Model/Environment/B5/CG_*.asset','script':'SourceAssets/B5_CorridorOnlyGuidance/Apply.cs','report':'Docs/검수/2026-11-08_B5_CorridorOnlyGuidance/검수결과.md','originalsPreserved':True}
(R/'Unity/After_Seconds_Build_V0.01/Assets/Afrer_Seconds/06.Data/AssetSources/B5_CorridorOnlyGuidance_20261108.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
src=(R/'SourceAssets/B5_OperationalDetail/SourceRecord.cs').read_text(encoding='utf-8').replace('OperationalSourceRecord','CorridorSourceRecord').replace('B5_OperationalDetail_20261108','B5_CorridorOnlyGuidance_20261108')
(H/'SourceRecord.cs').write_text(src,encoding='utf-8')
print('Handoff, review gallery, and source record saved')
