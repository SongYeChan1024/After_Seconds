"""Record the verified B1-only tabletop refinement without publishing or committing."""
from pathlib import Path
import json,gzip,html,re
H=Path(__file__).resolve().parent;R=H.parents[1];U=R/'Unity/After_Seconds_Build_V0.01';O=R/'Docs/Review/2026-11-12_B1_DeskProps'
def read(p):return json.loads(p.read_text(encoding='utf8'))
p=read(H/'plan.json');models=read(H/'models.json');audit=read(O/'audit.json');quality=read(O/'quality.json');geo=read(O/'geometry.json');pres=read(O/'preservation.json');walk=read(O/'walk.json');occ=read(O/'occlusion.json');end=read(O/'final_state.json');look=read(O/'look_test.json');plays=[read(f) for f in O.glob('play_*.json')]
assert not audit['errors'] and not quality['errors'] and not geo['patches'] and not pres['errors']
assert all(m['reversedNormals']==0 and m['zeroArea']==0 for m in quality['meshes'])
assert len(plays)==5 and all(t['complete'] and t['framesAdvanced']>10 and t['displacement']>.3 and not t['errors'] for t in plays)
assert not walk['planningFailures'] and all(q['passed'] for q in walk['results'])
assert look['complete'] and look['events']>0 and look['yawChange']>.1 and look['pitchChange']>.1 and not look['errors']
assert end['saved'] and not end['playing'] and not occ['running'] and end['keyboardEnabled'] and end['mouseEnabled']
with gzip.open(H/'source_geometry.json.gz','rt',encoding='utf8') as f:source=json.load(f)
old_tri=sum(sum(len(a) for a in source[t['source']][0]['submeshes'])//3 for t in p['targets']);new_tri=sum(models[t['variant']]['triangles'][0] for t in p['targets'])
metrics={'surveyedPlacements':53,'changedPlacements':51,'researchDesks':24,'researchDeskVariants':12,'rightHandedStations':28,'newModels':30,'lodMeshes':90,'modelBytes':quality['modelBytes'],'newTextures':1,'textureSize':[2048,2048],'newMaterials':2,'activeLodGroups':audit['activeLodGroups'],'activeLights':audit['activeLights'],'changedPlacementLod0TrianglesBefore':old_tri,'changedPlacementLod0TrianglesAfter':new_tri,'deltaLod0Triangles':new_tri-old_tri,'protectedTransforms':audit['protectedTransforms'],'protectedColliders':audit['protectedColliders'],'protectedFiles':pres['checked'],'walkPass':len(walk['results']),'playRooms':len(plays)}
(O/'resources.json').write_text(json.dumps(metrics,indent=2),encoding='utf8')
report=f'''# B1 데스크·기물 근접 보수 검수 V0.01

작성자 송예찬 · 2026-11-12

사용자 지적한 동일한 상판 구성·낮은 입력 장치 디테일·왼쪽 마우스를 보수했다. **현재 B1의 관련53배치를 조사하고51배치에 적용**했다. 전체 프로젝트의 모든 층 프랍 보수 완료를 뜻하지 않는다. 다른 층에 쓰이는 공유 원본은 보존하고 B1 파생 모델로 적용했다.

[전후 비교와 전체 목록](review.html) · [키보드 확대](close_keyboard.jpg) · [마우스 확대](close_mouse.jpg) · [제작 원본](../../../SourceAssets/B1_DeskPropRefinement/README.md)

## 수정

- 일반 연구용 데스크24개를12가지 상판 구성으로 나눴다. C01/W01/N01의 각6개 업무석은 같은 구성을 반복하지 않는다. 펼친 기록·인계 트레이·2단 트레이·문서 받침·파일 정리함·전화·메모·컵·필기구를 업무 흐름과 손이 닿는 범위에 맞췄다.
- 일반24·보안2·기록 검토2의 **28개 업무석**은 작업자 기준 오른손 마우스다. 제작 축과 앉아서 보는 좌우를 혼동했던 배치를 바로잡았다.
- 키보드는 엇갈린84키 배열·넓은 Shift/Enter/Space·분리된 기능/방향 키·각인·상태등·받침을 구현했다. 기존 키 각인 아틀라스를 재사용한다.
- 마우스는 곡면 몸체·좌우 클릭 영역/분할선·홈이 있는 스크롤 휠·엄지 버튼·패드·USB 배선으로 바꿨다. 확대 검사에서 발견한 버튼/몸체 겹침과 전화 수화기 곡면 노멀을 추가 보수했다.
- 검토 테이블4·8인 회의 테이블1·식탁4는 자료·컵·식기·비운 자리와 방향을 구분했다. 컵은 속이 빈 입구·벽 두께, 접시는 테두리와 오목한 면을 갖는다.
- 보안 업무석2·기록 검토석2·무전 인계대2의 기물·조작면·충전 자리·인계 기록을 구분했다. 보안의 의미는 실험체 B4→B3 상행 출입 제한이다.
- 의무실 카트2종은 직원 건강 확인/초음파 대기 화면으로 교체하고 조작부·트랙볼·프로브·혈압 커프를 구분했다. 이전 실험 타이머 문구를 제거했다. 녹음기10개는 화면·버튼·단자를 보강하고 상판 뒤쪽의 독립 자리로 이동했다.
- 배식대·조리대2배치는 함께 살펴봤으며 이번 기물 교체 대상에는 포함하지 않았다.

## 보존·검증

- 기존 방/책상/의자 배치와 통행 구조 보존: **{audit['protectedTransforms']}Transform·{audit['protectedColliders']}충돌체** 대조 통과. 별도 녹음기10개의 위치/회전만 계획대로 변경했다.
- **{pres['checked']}기존 파일 SHA-256 일치**. 다른 층·원본 공유FBX/재질·게임 C#·Player·Animator 보존. 씬 GUID와 기존 .meta 유지.
- 새30모델·90LOD메시: 비유한 좌표0·면적0삼각형0·반대 노멀0·Read/Write꺼짐·재질/스크립트 누락0. 마우스 오른손 배치28/28.
- 전체 B1 통행 **{len(walk['results'])}/{len(walk['results'])}**, 계획 실패0. 기존 Collider를 보존한 상태에서 검사했다.
- 실제 Play5구역(C01/C04/W01/W02/E01): 키보드 입력 이동·프레임 진행 확인, 새 경고/오류0. 실제 마우스 Look 이벤트{look['events']}회·시점 좌우/상하 회전 확인. 임시 조작/포커스 설정 복구.
- 전체 B1 깊이 충돌 검사: 중복 메시0·내부 겹침0, 1mm 후보는0.05mm 정밀 검사에서 실제 겹침0. 불투명 평면0.005m² 이상과 배타적 LOD를 구분한 검사다. 작은 장치 접합은 별도 확대 화면으로 확인했다.
- 기존 반사16개 갱신, 가림 데이터{occ['bytes']:,}bytes 갱신·최소 구멍 크기0.05m 유지. 근접 전후69시점과 키보드/마우스 확대, 대표3모델의 LOD0/1/2를 비교했다.

## 비용과 남은 범위

새FBX30개 **{quality['modelBytes']/1048576:.2f}MiB**, 새2048아틀라스1장·재질2개. 기존 키 인쇄·가구 재질과 텍스처를 재사용한다. 교체51배치의 최고LOD 삼각형은{old_tri:,}→{new_tri:,}(+{new_tri-old_tri:,})이다. 새 형상은3단계LOD를 적용했다. 광원209개 유지, 새 광원0. 파일 크기와 이 검수로 빌드 FPS·권장 사양을 확정하지 않는다.

최신 배치와 보수 이력은 `Docs/도면/Decision/원형공동/B1_제작현황/`을 따른다. 사용자 전체 B1 외형·공간 검수는 계속 진행하며, 다음 층 제작은 그 뒤 결정한다. 게임 기능은 추가하지 않았다. 로컬 저장이며 이번 보수의 커밋·push·블로그 게시는 하지 않았다.
'''
(O/'Review.md').write_text(report,encoding='utf8')
css='body{margin:0;background:#edf1f3;color:#203746;font:16px/1.7 system-ui,"Malgun Gothic",sans-serif}main{max-width:1300px;margin:auto;padding:32px 24px}h1{font-size:30px}h2{border-top:1px solid #becbd2;padding-top:26px}a{color:#176b83}figure{margin:12px 0;background:white;padding:12px;border-radius:7px}img{display:block;width:100%;height:auto}figcaption{font-size:14px;color:#526a76}.pair{display:grid;grid-template-columns:1fr 1fr;gap:16px}nav{display:flex;gap:10px;flex-wrap:wrap}nav a{padding:6px 12px;background:white;text-decoration:none}details{background:white;padding:12px;margin:12px 0}@media(max-width:800px){.pair{grid-template-columns:1fr}}'
page=['<!doctype html><html lang="ko"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>B1 데스크·기물 보수 V0.01</title><style>'+css+'</style><main><small>AFTER SECONDS · 2026-11-12 · 송예찬</small><h1>B1 데스크·기물 근접 보수</h1><p>업무석마다 다른 기록·도구 구성, 올바른 오른손 마우스 배치, 읽을 수 있는 키보드 각인과 실제 기물 형태.</p><p>관련53배치 조사 · 51배치 보수 · 28업무석 오른손 배치 · 통행297/297 · 실제 Play5구역</p><p><a href="Review.md">검수 보고서</a> · <a href="resources.json">리소스 변화</a></p><nav>']
for room in sorted({t['room'] for t in p['targets']}):page.append(f'<a href="#{room}">{room}</a>')
page.append('</nav><div class="pair"><figure><img src="close_keyboard.jpg" alt="84키 배열과 각인 확대"><figcaption>키 배열·각인·기능/방향 키</figcaption></figure><figure><img src="close_mouse_top.jpg" alt="오른손 마우스 곡면과 클릭 영역 확대"><figcaption>곡면 몸체·클릭 분할·휠·엄지 버튼</figcaption></figure></div>')
for room in sorted({t['room'] for t in p['targets']}):
 page.append(f'<section id="{room}"><h2>{room}</h2>')
 for t in [t for t in p['targets'] if t['room']==room and t['source']!='BL_HandheldRecorder']:
  name=t['name'];page.append(f'<details><summary>{html.escape(name)} · {t["variant"]}</summary><div class="pair"><figure><img loading="lazy" src="before_{name}.jpg" alt="{name} 수정 전"><figcaption>수정 전</figcaption></figure><figure><img loading="lazy" src="after_{name}.jpg" alt="{name} 수정 후"><figcaption>수정 후 · 기존 씬 조명</figcaption></figure></div></details>')
 page.append('</section>')
page.append('<h2>LOD 비교</h2><p>검수 시 강제한 단계이며 실제 거리 전환은 LODGroup이 처리한다.</p>')
for name in ['B1_C01_Data_ResearchDesk_01','B1_E01_SC_OperatorDesk_A_02','B1_W02_DiningSet_01']:
 page.append(f'<details><summary>{name}</summary>')
 for i in range(3):page.append(f'<figure><img loading="lazy" src="lod{i}_{name}.jpg" alt="{name} LOD{i}"><figcaption>LOD{i}</figcaption></figure>')
 page.append('</details>')
page.append('</main></html>');(O/'review.html').write_text(''.join(page),encoding='utf8')
(H/'README.md').write_text('''# B1 데스크·기물 보수 원본 V0.01

작성자 송예찬 · 2026-11-12

현재 B1의 최신 기물 보수다. [검수](../../Docs/Review/2026-11-12_B1_DeskProps/Review.md) · [전후 화면](../../Docs/Review/2026-11-12_B1_DeskProps/review.html).

**사용자 후속 편집 뒤 제작기·Apply를 일괄 재실행하지 않는다.** 현재 씬부터 확인해 지적 범위만 보수한다. B1_InteriorRedesign의 layout은 실내 구조 제작 당시 기록이며 녹음기10개의 최신 위치는 이 폴더 plan과 Decision 현재 배치를 따른다.

- Inspect.cs / before.json / protected_files.json: 작업 전 씬53관련 배치·전체Transform/Collider/Light와 기존13041파일 기준. Inspect 재실행으로 덮어쓰지 않는다.
- source_geometry.json.gz: 당시 저장 씬에서 읽은 원본 메시·UV·노멀·재질. 원본의 하부 가구 형상을 유지하기 위한 압축 원본. mesh_export와 before.unity는 PC 임시 사본으로 Git 제외.
- plan.py / plan.json: 51시각 교체와 녹음기10자리 변경. 24연구 데스크12구성, 각6석 방 안에서 중복 없음.
- models.py / models.json: Blender 네이티브30FBX·3LOD. 기존 하부 가구 보존, 키/마우스·기물·배선 재제작. DP_ONLY로 지정 모델만 만들 수 있지만 후속 작업에서 자동 적용하지 않는다.
- textures.py / atlas.json: 2048공유 업무 화면·인쇄 기록 아틀라스1장. 기존 PD_KeyLegend 재사용.
- Apply.cs: Unity 네이티브 적용·Undo·저장·보존 감사. 공유 원본FBX나 게임 C#을 수정하지 않는다. 이전 렌더러는 비표시 보존하고 새 B1 모델을 연결한다.
- Quality.cs / GeometryExport.cs / geometry.py: 메시·LOD·오른손 배치·전체B1 깊이 충돌 검사. 이전 가림 데이터용 메시 캐시는 같은 파일을 중복해서 덮어쓰지 않는다.
- Capture.cs / Walk.cs / Play.cs / Look.cs / run_play.py: 전후 확대·LOD·통행·실제 입력/시점 검수. 실제 입력 장치를 비활성화하지 않고 임시 설정을 복구한다.
- Finish.cs / report.py: 반사/가림 갱신·편집 상태 복귀·로컬 기록. Assets 안에 게임 스크립트를 추가하지 않는다.

다음은 사용자 전체 B1 외형 검수와 지정 범위 보수다. 다른 층·게임 C#·Player·Animator 보존, 커밋·push 미실시.
''',encoding='utf8')
provenance={'version':'V0.01','date':'2026-11-12','author':'송예찬','source':'SourceAssets/B1_DeskPropRefinement/models.py','method':'Saved Unity mesh lower furniture preserved; Blender tabletop geometry; one generated records atlas; existing key legends reused','plan':p,'models':models,'metrics':metrics}
(U/'Assets/Afrer_Seconds/06.Data/AssetSources/B1_Desk_Prop_Refinement.json').write_text(json.dumps(provenance,ensure_ascii=False,indent=2),encoding='utf8')
decision=next((R/'Docs').glob('**/Decision/*/B1_제작현황'));layout=read(decision/'as_built_layout.json');targets={q['name']:q for q in p['targets']};reloc={q['name']:q for q in p['relocations']}
for q in layout['placements']:
 if q['name'] in targets:q['visualVariant']=targets[q['name']]['variant'];q['visualAsset']=models[q['visualVariant']]['asset']
 if q['name'] in reloc:q['position']=reloc[q['name']]['position'];q['yaw']=reloc[q['name']]['yaw']
layout['desktopRefinement']={'date':'2026-11-12','source':'SourceAssets/B1_DeskPropRefinement/plan.json','targets':51,'note':'Furniture roots retained; recorder positions updated; visualVariant/visualAsset are the current B1 visual models.'}
(decision/'as_built_layout.json').write_text(json.dumps(layout,ensure_ascii=False,indent=2),encoding='utf8')
f=decision/'README.md';s=f.read_text(encoding='utf8').replace('V0.03','V0.04',1);lines=s.splitlines(keepends=True);lines.insert(2,'2026-11-12 후속: 데스크 반복·입력 장치·상판 기물51배치를 보수했다. 주요 배치203개와 실내 구조는 유지한다. visualVariant/visualAsset이 현재 시각 모델이며 녹음기10개 위치를 갱신했다. [최신 기물 검수](../../../../Review/2026-11-12_B1_DeskProps/Review.md) · [전후 화면](../../../../Review/2026-11-12_B1_DeskProps/review.html). 아래 실내 구획 검수는 선행 기록이다.\n\n');f.write_text(''.join(lines)+'\n- V0.04: 데스크·기물51배치 보수와 최신 시각 모델/녹음기 위치 연결. 송예찬.\n',encoding='utf8')
print(json.dumps(metrics,ensure_ascii=False,indent=2))
