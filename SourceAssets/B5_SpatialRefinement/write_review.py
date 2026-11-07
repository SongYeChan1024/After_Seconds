"""Local delivery record. Author 송예찬."""
from pathlib import Path
import json,html,re
H=Path(__file__).resolve().parent;R=H.parents[1];D=R/'Docs/검수/2026-11-08_B5_SpatialRefinement';A=R/'Unity/After_Seconds_Build_V0.01/Assets'
load=lambda p:json.loads(p.read_text(encoding='utf8'))
p=load(H/'plan.json');g=load(H/'guidance.json');m=load(H/'models.json');v=load(D/'verification.json');w=load(D/'walk.json');a=load(D/'audit.json');pres=load(D/'preservation.json');spacing=load(H/'guide_spacing.json')
labels=['security','cooling','utility','living','isolation','medical','receiving','meal','decon','control','testcell','staira','stairs','lift','corridor'];play={k:load(D/('play_'+k+'.json')) for k in labels}
assert all(r['passed'] for r in w['results']);assert all(not r['blocked'] and not r['missing'] for r in v['routes']);assert all(r['complete'] and r['displacement']>.2 and not r['errors'] for r in play.values());assert not a['overlaps'] and not a['missingMaterials']
names={c:x['name'] for c,x in g['destinations'].items()}
changes={
'C02':'관제실과 사건 검토 자리를 유리 구획으로 분리하고 서버·무전·교대 장비를 재배치했다. 사건 검토실 입구를 넓혀 의자 옆으로 출입할 수 있다.',
'C03':'중앙 냉각 설비4기·전용 기초·배관 헤더와 제어실을 구성했다. 펌프 배출구와 열교환기 플랜지에 연결 배관, 압력계·밸브·체결부를 추가했다.',
'C04':'전기 설비와 공조 설비 사이에 점검 통로를 두고 전기측 차폐벽·상부 설비 프레임을 추가했다.',
'W01':'생활실4개를 독립 구획하고 중앙 간호 자리와 공용 통로를 구성했다. 침대 서비스 레일·위생 가림벽·천장·환기구를 추가했다.',
'W02':'생활실4개와 중앙 관찰 자리, 물품 반납·배식 동선을 분리했다. 침대·개인 수납·세면 공간을 각 생활실 안으로 재배치했다.',
'W03':'진료실2개와 검사·대기/분류 공간을 구분했다. 침대·이동형 모니터·가스 설비·커튼의 위치와 출입 간섭을 보수했다.',
'E01':'중앙 보관열 두 줄과 입고 검수대를 중심으로 배치했다. 선반 간 통로와 운반 장비 접근 공간, 입고 작업 프레임을 구성했다.',
'E02':'중앙 배식 작업대·조리·세척/회수·냉장 보관을 분리했다. 추출 후드·세척 칸막이·실제로 파인 세면 볼과 배수관을 추가했다.',
'E03':'오염측·제염 구역·청결측을 칸막이로 구분하고 중앙 통로 양쪽에 샤워 부스를 배치했다. 분사 노즐·호스·감지기·배수판을 보강했다.',
'N01':'6석 관제실·측면 서버 통로·협의 자리를 구분했다. 좌석 앞과 뒤로 이동 가능한 통로를 확보하고12개 모니터의 정적 표시 내용을 달리했다.',
'S01':'시험 장치를 중앙 시험 셀 안에 두고 별도 관찰실과 장비 보관 공간을 구성했다. 관찰실 입구를 공용 통로 방향으로 돌렸다.',
'VA':'기존96단 계단을 보존하고 구조 접합부·벽체 설비 패널·층별 서비스 링을 보강했다.',
'VB':'기존96단 계단을 보존하고 기둥 접합부·설비 패널·서비스 링을 보강했다.',
'VL':'기존 승강로를 보존하고 문 가이드·랜딩 트랙·정비 캐비닛과 외곽 설비 패널을 보강했다.'}
order=['C02','C03','C04','W01','W02','W03','E01','E02','E03','N01','S01','VA','VB','VL']
def figure(src,caption):
 assert (D/src).exists(),src
 return f'<figure><a href="{html.escape(src)}"><img loading="lazy" src="{html.escape(src)}" alt="{html.escape(caption)}"></a><figcaption>{html.escape(caption)}</figcaption></figure>'
parts=[]
for c in order:
 old='../2026-11-08_B5_RemainingDomes/'+c+'_0.png'
 if not (D/old).exists():old='../2026-11-08_C02_Refine/After_FromLab.png' if c=='C02' else '../2026-11-08_T02_StairA/After_VA_Entry.png'
 pair=figure(old,'이전 배치')+figure(c+'_0.png','현재 배치')
 extra=''.join(figure(n,c+' / '+title) for n,title in [(c+'_1.png','다른 출입 방향'),(c+'_inside.png','내부 공간'),(c+'_detail.png','설비 상세')] if (D/n).exists())
 parts.append(f'<section id="{c}"><h2>{c} · {names[c]}</h2><p>{changes[c]}</p><div class="grid">{pair}</div><details><summary>추가 시야와 상세 보기</summary><div class="grid">{extra}</div></details></section>')
close=''.join(figure(n+'.png',caption) for n,caption in [('Close_Sink','오목한 세면 볼·수전·배수'),('Close_Bed','침대 기구·캐스터·레일'),('Close_Pump','펌프 플랜지·계기·밸브'),('Close_Desk','모니터·입력 장치·연결부')])
doc='''<!doctype html><html lang="ko"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>B5 공간·프랍 재검수 V0.01</title><style>
:root{color-scheme:dark}*{box-sizing:border-box}body{margin:0;background:#111921;color:#dde5e8;font:16px/1.7 system-ui,sans-serif}main{max-width:1440px;margin:auto;padding:32px 24px}h1{font-size:32px}h2{font-size:24px;color:#a5dce2}a{color:#9bcfdb}nav{position:sticky;top:0;padding:12px;background:#17212cf2;display:flex;gap:14px;flex-wrap:wrap;z-index:2}section{scroll-margin-top:90px;border-top:1px solid #35414d;margin:38px 0;padding-top:20px}.grid{display:grid;grid-template-columns:1fr 1fr;gap:16px}figure{margin:0 0 14px}img{width:100%;display:block;background:#090e14}figcaption{padding:8px;background:#202c36;color:#bfcdd1}summary{cursor:pointer;padding:12px;background:#202d37}details[open] summary{margin-bottom:16px}.info{padding:18px;border-left:3px solid #8dbfc8;background:#1b2731}table{border-collapse:collapse;width:100%}td,th{padding:8px;border:1px solid #35414d;text-align:left}@media(max-width:850px){.grid{grid-template-columns:1fr}main{padding:18px}h1{font-size:25px}}</style><main>'''
doc+=f'<h1>B5 공간 구조·프랍 재제작</h1><p>V0.01 · 2026-11-08 · 송예찬 · 로컬 저장</p><div class="info">실험동 C01은 보존했다. 나머지11개 돔의 기능별 구획과3개 수직 코어를 보강하고, 상세 프랍171개를 재배치했다. 외곽 돔과 복도 연결 위치는 유지했다. 전체 조명·색감 조정과 사용자 최종 외형 판정은 다음 단계다.</div>'
doc+='<p>같은 출입 방향의 이전/현재 화면을 나란히 비교한다. C02·VA의 이전 이미지는 앞선 검수 자료이므로 시점이 다를 수 있다. 이미지를 누르면 원본으로 열린다.</p><nav>'+''.join(f'<a href="#{c}">{c}</a>' for c in order)+'<a href="#details">프랍 확대</a><a href="#checks">검수</a></nav>'+''.join(parts)
doc+='<section id="details"><h2>프랍 상세</h2><div class="grid">'+close+'</div></section><section id="checks"><h2>검수 결과</h2>'
doc+=f'<p>Controller 90/90 · 안내선 {v["samples"]:,}표본 막힘0 · 서로 다른 안내선 교차0 · 누락 재질0 · 기존 Light203개 설정 보존</p><p>Play14구역과 복도에서 실제 W 입력을 확인했다. 아래 수치는 현재 Editor/1920×1080/구역별8초 표본이며 출시 빌드의 성능 보증 수치가 아니다.</p><table><tr><th>구역</th><th>이동(m)</th><th>중앙값(ms)</th><th>P95(ms)</th><th>새 게임 로그</th></tr>'
for k,r in play.items():doc+=f'<tr><td>{k}</td><td>{r["displacement"]:.2f}</td><td>{r["medianMs"]:.2f}</td><td>{r["p95Ms"]:.2f}</td><td>{len(r["errors"])}</td></tr>'
doc+='</table><p><a href="검수결과.md">기술 검수 기록</a> · <a href="preservation.json">기존 작업 보존 대조</a></p></section></main></html>'
(D/'review.html').write_text(doc,encoding='utf8')
report=f'''# B5 공간 구조·프랍 재검수 V0.01

작성자 송예찬 · 2026-11-08

사용자가 지적한 외벽 나열과 단순한 방 구조를 보수했다. 실험동 C01을 보존하고 나머지11개 돔의 내부 공간과3개 수직 코어를 재제작했다. 대상은 `Assets/Afrer_Seconds/01.Scenes/Stage/Level_B5_Circular.unity`이며 새 배치는 `B5_Spatial_Refinement` 아래에 있다. 이전 가구는 비활성 상태로 보관했다. [변경 전후와 확대 화면](review.html)을 사용자 일괄 검수에 사용한다.

## 변경

'''+''.join(f'- **{c} {names[c]}**: {changes[c]}\n' for c in order)+f'''
새 모델76종(실내 구조14·상세 프랍62), 기능별 구조39개, 활성 상세 프랍171개(계획154+C02교체17)를 반영했다. 새 모델은 기존 `.blend` 원본에서 형상을 보강해 별도 `SF_` 파일로 제작했으며 기존 모델 파일은 덮어쓰지 않았다. 베벨·판금 이음·체결부·캐스터 브레이크·침대 구동부/침구·연결 케이블·실제로 파인 세면 볼·배관 트랩·계기·밸브·얇은 UV 인쇄 라벨을 보강했다. PBR Base/Normal/MetalSmooth9장과 장비 라벨 아틀라스1장을 제작했다. 모니터 화면은 정적이다.

## 검증

- 실제 CharacterController **{len(w['results'])}/{len(w['results'])}** 경로 통과. 돔 출입구 사이,8개 생활실·2개 진료실·관찰/제어/검토실 내부와 중앙관제실 뒤 통로, VA/VB96단 계단 왕복을 포함한다.
- 목적지15색·19복도·38안내 경로, 표본 **{v['samples']:,}**개 막힘0·바닥 누락0. 샤워 트레이 위로 지나가던 표본을 수정했다.
- 서로 다른 선·화살표 간 최소 여백 **{spacing['minMarkerClearance']*100:.2f}cm**, 방향 글자 영역까지 **{spacing['minLabelClearance']*100:.2f}cm**. C01 내부의 기존 안내 메시796tri와 재질·UV를 복제해 보존했다.
- 활성 새 아트 고유 메시 {a['uniqueMeshes']}개, {a['triangles']:,}tri. 재질 누락0. 면적0 수준 퇴화삼각형0(교차곱 제곱 `<1e-22 m⁴`). 나사/베벨의 유효 미세 삼각형은 제거하지 않았다.
- BoxCollider가 포함된 충돌쌍의2.5cm 초과 침투0. MeshCollider끼리는 자동 침투 계산 대상에서 제외했고 실제 통행 및 구역/설비 렌더로 보완했다. 배관 접속부의 의도된 맞물림은 유지한다.
- Play14구역+복도, 실제 기존 키보드 W 입력/수평 카메라/구역별8초 검증. 모두 실제 이동하고 새 게임 경고·오류0. 화면/JSON은 `Play_*.png`, `play_*.json`에 있다. 별도 생활동 비가림 비교 표본도 저장했다.
- 기존 외곽 구조만 가림막으로 사용해 가림 데이터를 다시 계산했다. 유리가 섞인 새 실내 모델 전체를 불투명 가림막으로 지정하지 않았다.

| 구역 | 이동 m | 프레임 중앙값 ms | P95 ms | 새 게임 로그 |
|---|---:|---:|---:|---:|
'''+''.join(f'| {k} | {r["displacement"]:.3f} | {r["medianMs"]:.2f} | {r["p95Ms"]:.2f} | {len(r["errors"])} |\n' for k,r in play.items())+f'''
성능 수치는 현재 Editor/1920×1080의 짧은 구역별 표본이다. 전체 조명 조정·최종 빌드 성능 판정은 별도다.

## 보존과 다음 단계

작업 전 Assets {pres['baselineFiles']:,}파일을 해시로 대조했다. {pres['unchangedFiles']:,}파일 동일, 변경 파일은 {', '.join('`'+x+'`' for x in pres['changedFiles'])}이다. 누락/예상 밖 변경0. C01 Transform {pres['protectedC01Transforms']}개 동일, 기존203개 Light의 위치·회전·설정 동일이다. 새 등기구와 맞춘 작업등44개를 추가했다. 전체 조명·색감의 최종 조정은 아직 하지 않았다.

게임 C#/Animator 변경0. 문·승강기 동작과 B4 실제 씬 연결은 기존 미구현 상태이며 이번 작업은 정적 외형과 충돌/통행 보수다. 씬을 Edit 모드로 저장했다. 커밋·push 미실시. 사용자 일괄 외형 검수 → 필요한 보수 → B5 전체 조명·색감 조정 순서다. 아트 최종 판정0/34는 사용자 확인 전까지 유지한다.
'''
(D/'검수결과.md').write_text(report,encoding='utf8')
record=dict(version='V0.01',author='송예찬',date='2026-11-08',scene=v['scene'],source='SourceAssets/B5_SpatialRefinement',review='Docs/검수/2026-11-08_B5_SpatialRefinement/review.html',scope='C01 preserved; 11 domes and 3 vertical cores',models={k:{**val,'asset':str(Path(val['asset']).relative_to(R)).replace('\\','/')} for k,val in m.items()},activeProps=171,structures=39,existingLightsPreserved=203,newFixtureLights=44,pbrMaps=9,printedAtlas=1,controllerPaths=90,guideSamples=v['samples'],playAreas=15,userArtReview='pending',globalLightingReview='pending',gameplayCodeChanged=False)
(A/'Afrer_Seconds/06.Data/AssetSources/B5_SpatialRefinement_20261108.json').write_text(json.dumps(record,ensure_ascii=False,indent=2),encoding='utf8')
readme=(H/'README.md').read_text(encoding='utf8').replace('V0.01','V0.02',1)
readme+='''

## 저장 결과 / V0.02

76종 모델(구조14/프랍62),39개 기능별 구조,171개 상세 프랍 배치. [검수 페이지](../../Docs/검수/2026-11-08_B5_SpatialRefinement/review.html) · [검증과 남은 범위](../../Docs/검수/2026-11-08_B5_SpatialRefinement/검수결과.md).

제작 원본은 `SF_*.blend`, 모델 원본 연결은 `prop_sources.json`, 확정 배치는 `plan.json`, 안내 경로는 `guidance.json`이다. Blender 실행 순서는 `plan.py → interiors.py / props.py → textures.py`다. Unity 최초 반영은 `Apply.cs`, 이후 구조 재임포트·최종 배치 보수는 `Fix.cs`를 사용했다. `Grid.cs → guides.py → GuideApply.cs → Finish.cs`는 안내 재생성 절차이며 `Finish.cs`는 실험동의 기존 안내 메시를 보존하고 관제 화면 역할을 구분한다. 새 모델은 `05.Model/Props/B5` 또는 `Environment/B5`, 텍스처와 재질은 그 아래 전용 폴더, 출처 JSON은 `06.Data/AssetSources`에 있다.

`prepare_*.py`는 이번 제작 중 검수 도구를 파생시킨 이력이다. 최종 파일을 덮어쓸 수 있으므로 재실행하지 않는다. `Apply.cs`는 중복 반영을 막는다. 씬을 바꾸기 전 미저장 편집을 백업하고, 재생성은 본 작업의 `SF_` 자산과 소유 그룹만 대상으로 한다.

`Verify.cs`, `Audit.cs`, `Walk.cs`, `run_play.py`, `preservation.py`가 최종 검수 도구다. 런타임/Editor 게임 C# 파일을 Assets에 추가하지 않았다. 사용자 아트 승인과 전체 조명 마감은 남아 있다. 작성자 송예찬.
'''
(H/'README.md').write_text(readme,encoding='utf8')
summary=f'2026-11-08 공간·프랍 재검수: 사용자 요청에 따라 C01 실험동을 보존하고 나머지11돔·3코어를 재제작했다. 개별생활실8개·진료실2개·관제/검토/제어/관찰실·중앙 설비/보관/조리/제염 구획, 모델76종·상세 프랍171개·구조39개를 반영했다. 안내38경로 재계산, {v["samples"]:,}표본 막힘0·Controller90/90·Play14구역+복도 새 게임 로그0. C01 Transform과 기존203 Light 설정 보존, 새 작업등44개 추가. 이전 모델·가구는 원본/비활성 보관, 게임 C#/Animator 변경0. **다음은 사용자 일괄 외형 검수 → 보수 → B5 전체 조명·색감 조정**. 문/승강기 기능·B4 실제 연결 미구현, 아트 최종 판정0/34 유지. 로컬 저장, 커밋·push 미실시. 작성자 송예찬.'
versions=[('AGENTS.md','0.55','0.56'),('CLAUDE.md','0.55','0.56'),('Docs/AfterSeconds_메인기획서.md','0.44','0.45'),('Docs/이어하기_2026-11-06.md','0.39','0.40'),('Docs/회사_작업목록_2026-11-06.md','0.37','0.38')]
for file,old,new in versions:
 path=R/file;s=path.read_text(encoding='utf8');head,rest=s.split('\n',1);assert 'V'+old in head,file;head=head.replace('V'+old,'V'+new);prefix='Docs/' if '/' not in file else '';link=f' [{"검수 화면"}]({prefix}검수/2026-11-08_B5_SpatialRefinement/review.html) · [검수 결과]({prefix}검수/2026-11-08_B5_SpatialRefinement/검수결과.md).';s=head+'\n\n'+summary+link+'\n\n이전 단계 기록:\n'+rest.lstrip()
 if file.endswith('메인기획서.md'):s=s.replace('| V0.44 |','| V0.45 | 2026-11-08 | 송예찬 | C01 보존, 나머지11돔·3코어 기능별 내부 구조/상세 프랍 재제작, 안내·통행·Play 재검수. |\n| V0.44 |',1)
 path.write_text(s,encoding='utf8')
path=R/'Docs/도면/Decision/원형공동/B5_안내체계/README.md';s=path.read_text(encoding='utf8');head,rest=s.split('\n',1);assert 'V0.07' in head;head=head.replace('V0.07','V0.08');s=head+f'\n\n2026-11-08 내부 구조 재편에 맞춰38경로를 다시 배치했다. 목적지15색/19복도 유지, 선·화살표 여백 최소{spacing["minMarkerClearance"]*100:.2f}cm·글자45cm, 실제 통행{v["samples"]:,}표본 막힘0·Controller90/90. C01 실험동의 기존 안내 메시·화살표·재질은 보존했다. 새 좌표 기준은 [B5_SpatialRefinement](../../../../../SourceAssets/B5_SpatialRefinement/README.md)다. 전체 조명 마감과 사용자 외형 판정은 남는다. 작성자 송예찬.\n\n이전 단계 기록:\n'+rest.lstrip();path.write_text(s,encoding='utf8')
print('Gallery, report, source record, source README and six handoff documents written.')
