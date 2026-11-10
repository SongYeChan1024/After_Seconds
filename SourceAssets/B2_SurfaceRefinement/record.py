from pathlib import Path
import json,hashlib,re,html
H=Path(__file__).resolve().parent;R=H.parents[1];O=R/'Docs/Review/2026-11-10_B2_SurfaceRefinement';D=R/'Docs/도면/Decision/원형공동'
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
def write(p,x):p.parent.mkdir(exist_ok=True,parents=True);p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
ground=read(O/'ground.json');upper=read(O/'upper.json');play=read(O/'play.json');bay=read(O/'play_bay.json');state=read(O/'final_state.json');plan=read(H/'plan.json');applied=read(O/'applied.json');models=read(H/'models.json')
assert all(t['reachable'] and (not t.get('move') or t['move']['passed']) for r in ground for t in r['targets'])
assert all(m['passed'] for r in upper for m in r['moves'])
assert play['complete'] and bay['complete'] and not play['errors'] and not bay['errors'] and all(p['passed'] for p in play['results']+bay['results'])
assert state['saved'] and not state['missingOriginal'] and not state['missingMeshes'] and not state['missingMats'] and not state['activeGuidance']
assert all(f['verticesUnchanged'] and f['trianglesUnchanged'] for f in state['floors'])
assert all(m['degenerate']==0 for m in state['newModels']) and all(m['emission'] for m in state['lcd'])
protected=read(H/'protected_before.json');different=[p for p,sha in protected.items() if not (R/p).exists() or hashlib.sha256((R/p).read_bytes()).hexdigest()!=sha];assert not different,different
write(O/'protected.json',dict(files=len(protected),changed=different))
frames=sum(r['frames'] for r in play['results']);summary=dict(version='V0.01',date='2026-11-10',author='송예찬',scope='B2 사용자 피드백 후속 보수',placements=plan['placements'],floor_surfaces=read(H/'floors.json'),floor_guidance=False,models=models,verification=state,review='../../../Review/2026-11-10_B2_SurfaceRefinement/Review.md')
write(D/'B2_운영동선_재설계/as_built_surface_refinement.json',summary)
facility=read(D/'facility_layout.json');facility['version']='V0.11'
facility['floor_art_direction']['B2'].update(dict(description='어두운 붉은 보조등과 철색 설비. 하부는 사용감 있는 산업용 콘크리트, 상부는 개방 철제 그레이팅. 조작부는 비교적 관리되고 바닥·계단·가장자리는 먼지·기름때·마모가 남는다.',ground_finish='industrial concrete / aggregate, old oil marks, edge dust, sparse boot smears',upper_finish='open steel grating / scuffed stair centres, oxidised edges',floor_guidance=False))
facility['wayfinding']['rule']='안내선을 사용하는 층에서는 같은 의미를 유지한다. B2 기계층은 2026-11-10 사용자 결정으로 바닥 안내선을 표시하지 않는다. 도면 예상 경로와 월드 업무 안내선을 구분하며 게임 UI 경로 표시는 별도다.'
facility['wayfinding'].setdefault('floor_exceptions',{})['B2']=dict(enabled=False,reason='기계층 바닥에는 이동 안내선·색상 경계 도색을 표시하지 않는다. 콘크리트 시공 줄눈과 계단 미끄럼 방지면은 재질/구조 표현이다.',date='2026-11-10')
facility['production_status']['B2']='12공동 운영 배치188개(기존186+윤활 설비/모터 받침), 콘솔8교체, 바닥15·통로21·계단/데크 사용감. B2 바닥 안내선 비활성. 정적 외형 및 이동 검수 완료, 사용자 외형 확인 단계.'
facility['production_status']['B2_SurfaceRefinement']=dict(date='2026-11-10',as_built='B2_운영동선_재설계/as_built_surface_refinement.json',review='../../../Review/2026-11-10_B2_SurfaceRefinement/Review.md',runtime_added=False)
if not any(v.get('version')=='V0.11' for v in facility['revision_history'] if isinstance(v,dict)):facility['revision_history'].append(dict(version='V0.11',date='2026-11-10',author='송예찬',change='B2 적치 배치·콘솔 근접 마감과 산업용 바닥/계단 사용감. B2 바닥 안내선 미표시 사용자 결정.'))
write(D/'facility_layout.json',facility)
ab=read(D/'B2_운영동선_재설계/as_built_operations.json');ab['surface_refinement']=dict(path='as_built_surface_refinement.json',note='C02 적치물2개 위치/방향과 새 설비2개, 콘솔8·바닥·데크 재질은 이 후속 참조가 최신.');write(D/'B2_운영동선_재설계/as_built_operations.json',ab)
asset=R/'Unity/After_Seconds_Build_V0.01/Assets/Afrer_Seconds/06.Data/AssetSources/B2_SurfaceRefinement.json'
write(asset,dict(version='V0.01',author='송예찬',date='2026-11-10',source='SourceAssets/B2_SurfaceRefinement',models=models,method='Blender manual construction with bevels and distance LOD; procedural PBR/legible static display textures. Original VARCO console preserved inactive in this scene; no new VARCO generation.',floor_guidance=False,screen_runtime=False,inspection_images='detail_* use temporary inspection lighting; no additional scene lights saved.'))
review=f'''# B2 적치·콘솔·바닥 마감 보수 V0.01

작성자 송예찬 · 2026-11-10

사용자가 지적한 C02 적치물, C01 콘솔과 빈 공간, 기계층 하부/상부 바닥의 불일치와 과하게 깨끗한 마감을 보수했다. `Level_B2_Circular.unity`에 저장했다. 게임 코드·Player 씬·Animator는 보존했다.

- `B2_C02_Ops_PartsStaging_13`: 정비대 옆 로컬(-4, 0.185, -5.3)의 전용 모터 받침 위로 이동했다. 받침과 모터 접지 높이를 맞췄다.
- `B2_C02_Ops_PartsStaging_14`: 로컬(-6.55, 0, -5.9), Y회전180도로 배치해 공구 카트의 접근 면이 작업 구역 바깥쪽을 향한다.
- 기존 VARCO 콘솔은 비활성/숨김 보존하고 **C01·C04·E03·S01의8개**를 Blender 새 모델로 교체했다. 읽을 수 있는 공정/추세 화면, E-stop·Run/Stop·선택 스위치, 도어 씰·힌지·래치·통풍구·후면 케이블 글랜드를 만들었다. 명판은 문짝 한쪽에 고정하고 곡선 호스와 감지 배관을 정리했다. 모든 화면은 정적 아트다.
- C01 동쪽 빈 구역에 윤활·씰 정비 설비를 추가해 서쪽 제어/기록 공간과 역할을 나눴다. 중앙 두 공정열과 다섯 출입구는 유지한다.
- 공동12·코어3의 바닥15개를 산업용 콘크리트로, 통로21개의 바닥도 같은 계열로 바꿨다. 설비 주변 오래된 기름 얼룩, 가장자리 먼지, 흩어진 보행 흔적을 방별로 배치했다. **B2 바닥 안내선은 끄고 기존 C02 도색 경계도 제거**했다. 남은 가는 선은 콘크리트 시공 줄눈이다.
- 부분 데크4개·복층 통로19개의 금속과 계단을 보수했다. 계단 윗면에는 중앙 마모/가장자리 오염이 구분되는 표면을 적용했다. 바닥/발판의 실제 형상과 충돌을 바꾸지 않고 시각 메시의 UV·재질만 분리했다. 조작부 도장면은 바닥보다 관리된 인상을 유지한다.

검증: 하부 출입구/조작면 **220/220**, 상부 Controller 왕복 **34/34** 통과. 실제 Play6경로 **{frames}프레임**, C02 받침 가장자리를 피하는 정비 통로 별도 재검사 **{bay['results'][0]['frames']}프레임** 통과. 새 게임 오류0, Mouse/Keyboard 활성 복구. 기존 Transform {state['originalTransforms']}개 누락0, 보호 파일 {len(protected)}개 동일, 메시·재질 누락0, 새 모델6개 퇴화 삼각형0. 광원158개 유지. 반사37개와 가림 정보는 최종 배치로 갱신했다.

[변경 전후 및 근접 화면](review.html) · [실배치](../../도면/Decision/원형공동/B2_운영동선_재설계/as_built_surface_refinement.json) · [제작 원본](../../../SourceAssets/B2_SurfaceRefinement/README.md)

`before_*`/`after_*`는 실제 씬 조명이다. `detail_*`는 마감 검수를 위해 촬영 때만 임시 점검등을 켠 이미지이며 씬에는 저장하지 않았다. 어두운 붉은 실제 조명과 구분한다. 최종 외형 수용은 사용자 확인 대상이며, 설비 기능/AI 구현이나 전체 레벨 완성을 의미하지 않는다. 로컬 저장, 커밋·push 미요청.

## 변경 기록

- V0.01: 사용자 피드백에 따른 B2 적치·콘솔·산업용 바닥·계단 마감 및 검수. 송예찬.
'''
(O/'Review.md').write_text(review,encoding='utf8')
labels={'console':'C01 제어 콘솔','C01':'C01 공정 공간','C02_parts':'C02 정비·부품 적치','C02':'C02 하부와 상부','C02_upper':'C02 상부 데크','C04':'C04 관제 공동','floor':'하부 바닥'}
cards=''.join(f'<section><h2>{html.escape(label)}</h2><div class="pair"><figure><img loading="lazy" src="before_{key}.png"><figcaption>이전</figcaption></figure><figure><img loading="lazy" src="after_{key}.png"><figcaption>보수 후</figcaption></figure></div></section>' for key,label in labels.items())
details=''.join(f'<figure><img loading="lazy" src="detail_{key}.png"><figcaption>{label} · 임시 점검등 촬영</figcaption></figure>' for key,label in [('console','콘솔 근접'),('lubrication','윤활·씰 정비 설비'),('floor','콘크리트 마감'),('stair','계단 마모')])
(O/'review.html').write_text(f'''<!doctype html><html lang="ko"><meta charset="utf-8"><meta name="viewport" content="width=device-width"><title>B2 사용자 피드백 보수</title><style>body{{margin:30px auto;max-width:1600px;background:#171a1b;color:#ddd;font:16px system-ui;line-height:1.65}}header,section{{padding:20px}}h1{{font-size:28px}}h2{{font-size:20px}}.pair{{display:grid;grid-template-columns:1fr 1fr;gap:14px}}figure{{margin:0}}img{{display:block;width:100%;height:auto}}figcaption{{padding:8px;color:#aaa}}a{{color:#b9d2cd}}@media(max-width:800px){{.pair{{grid-template-columns:1fr}}}}</style><header><h1>B2 적치·콘솔·산업용 바닥 보수</h1><p>2026-11-10 · 콘솔8 / 바닥15 / 통로21 / 기존 붉은 조명 유지</p><p>아래 전후 비교는 같은 위치·실제 씬 조명이다. 하단 근접 화면만 임시 점검등을 사용했다.</p><a href="Review.md">검수 기록</a></header>{cards}<section><h2>근접 마감 검수 — 임시 점검등</h2><p>조명은 촬영 후 제거했으며 실제 레벨 밝기를 올리지 않았다.</p><div class="pair">{details}</div></section></html>''',encoding='utf8')
source='''# B2 사용자 피드백 마감 제작 원본 V0.01

작성자 송예찬 · 2026-11-10

이 폴더가 B2 적치물·콘솔·바닥·계단 마감의 최신 후속 원본이다. `plan.json`은 기존 운영 배치186개에 윤활 설비와 모터 받침을 추가한188개, 적치물2개 위치/방향을 포함한다. 기존 전체 Apply/plan 생성기를 현재 씬에 재실행하지 않는다.

`build.py`는 Blender 콘솔·모터 받침·윤활 정비 설비3종과 거리 LOD3종, 베벨 원본을 만든다. 신규 VARCO 생성 없이 기존 품질 부족 콘솔을 수작업 교체했다. `textures.py`는 방별 실제 설비 위치에 따른 콘크리트 PBR·금속 타일·정적 화면을 생성한다. `treads.py`는 발판 중앙 마모/끝 오염 표면이다. `BR_ONLY_TILES=1`은 바닥 지도를 재생성하지 않고 공용 마감만 갱신한다.

`Apply.Import`는 초기 반입, `Apply.Run`은 한 번만 실행하는 씬 적용이다. `Refine.Run`은 LCD 발광 플래그, 오래된 C02 바닥 줄눈 제거, 카트 방향을 마감한다. `Treads.Run`은 시각 메시만 파생하고 원래 충돌을 유지한다. 현재 씬에 재실행할 경우 기존 후속 수정을 반드시 대조한다. 계단의 파생 메시를 다시 생성하지 않는다.

`Audit.Ground/Upper`와 `Play`/`PlayBay`, `Verify`가 통행·실제 프레임·참조를 검사한다. 실제 Mouse/Keyboard 장치는 비활성화하지 않는다. 외부 C#은 일시 실행용이며 게임 스크립트를 추가하지 않는다. `Finish.Reflections/Occlusion/Complete`는 최종 반사·가림 갱신이다. `Capture`의 `detail_*`만 임시 점검등이며 다른 비교 사진은 실제 조명이다.

`record.py`는 검사 통과 후 출처·실배치·최신 안내를 기록한다. 원본 씬 백업은 `C:/Users/503-26/Documents/Codex/Backups/AfterSeconds_B2_Surface_20261110/`에 있다. 기존 모델·.meta는 보존했다.

[검수](../../Docs/Review/2026-11-10_B2_SurfaceRefinement/Review.md) · [전후 비교](../../Docs/Review/2026-11-10_B2_SurfaceRefinement/review.html)
'''
(H/'README.md').write_text(source,encoding='utf8')
note='2026-11-10 B2 사용자 피드백 마감: C02 모터/카트를 정비대 옆 받침·카트 자리로 묶고 C01 동쪽 윤활·씰 정비 설비를 추가했다. 품질 부족 VARCO 콘솔8곳을 Blender 베벨/도어/버튼/읽을 수 있는 정적 화면 모델로 교체했다. 하부 바닥15·통로21은 산업용 콘크리트 사용감, 상부 데크/계단은 닳은 철색으로 정리했다. **B2는 바닥 안내선과 도색 경계를 표시하지 않는다.** 다른 층 안내선 규칙은 유지한다. 하부220/220·상부34/34·Play6경로 및 정비 통로 추가 검수 통과. 게임 코드/Player 씬/Animator·광원158개 보존. [최신 검수](Docs/Review/2026-11-10_B2_SurfaceRefinement/Review.md)와 [제작 원본](SourceAssets/B2_SurfaceRefinement/README.md)을 우선하며 이전 Apply를 현재 씬에 재실행하지 않는다. 다음은 C02 적치·C01 콘솔/윤활 구역·바닥/계단의 사용자 근접 검수다. 로컬 저장, 이번 커밋·push 미요청. 작성자 송예찬.'
for name in ['AGENTS.md','CLAUDE.md']:
 p=R/name;text=p.read_text(encoding='utf8');lines=text.splitlines();lines[0]=re.sub(r'V0\.\d+','V0.90',lines[0]);text='\n'.join(lines)+'\n'
 if note not in text:text=text.replace('\n\n','\n\n'+note+'\n\n이전 단계 기록:\n\n',1);text+='\n- V0.90 (2026-11-10): B2 사용자 피드백 적치·콘솔·바닥·계단 마감. 송예찬.\n'
 p.write_text(text,encoding='utf8')
p=D/'B2_운영동선_재설계/README.md';text=p.read_text(encoding='utf8');msg='최신 후속 마감: [B2 적치·콘솔·바닥 보수](../../../Review/2026-11-10_B2_SurfaceRefinement/Review.md). 적치물2개 이동, 윤활 설비/받침 추가, 콘솔8 교체, 바닥·계단 사용감과 B2 안내선 미표시는 `as_built_surface_refinement.json`이 최신이다.'
if msg not in text:text=text.replace('\n\n','\n\n'+msg+'\n\n',1);p.write_text(text,encoding='utf8')
print(json.dumps(dict(protected=len(protected),ground=220,upper=34,frames=frames,consoles=8,placements=len(plan['placements']))))
