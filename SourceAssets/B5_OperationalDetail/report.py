"""Evidence-backed local handoff and review gallery. Author 송예찬."""
from pathlib import Path
import json,html,re
H=Path(__file__).resolve().parent;R=H.parents[1];D=R/'Docs/검수/2026-11-08_B5_OperationalDetail'
read=lambda n:json.loads((D/n).read_text(encoding='utf-8'))
a=read('audit.json');v=read('verification.json');w=read('walk.json');pres=read('preservation.json');post=read('post_play.json');layout=json.loads((H/'layout.json').read_text(encoding='utf-8'));manifest=json.loads((H/'models.json').read_text(encoding='utf-8'));access=json.loads((H/'equipment_access.json').read_text(encoding='utf-8'))
plays={n:read('play_'+n+'.json') for n in ['cooling','utility','receiving','meal','decon','testcell','lift']}
assert len(manifest)==25 and len(layout['placements'])==41 and len(w['results'])==128
assert all(x['passed'] for x in w['results']) and all(not x['blocked'] and not x['missing'] for x in v['routes'])
assert a['degenerate']==0 and not a['missingMaterials'] and not access['failures']
assert all(x['complete'] and x['framesAdvanced']>10 and x['displacement']>.2 and not x['errors'] for x in plays.values())
assert not pres['lightRemovedOrChanged'] and not pres['protectedTransformsChanged'] and not post['dirty'] and not post['runInBackground']
sections=[('S01 폐쇄시험동','교환 현상의 위치·자세 변화를 측정하는 계측 시험실. 임시 흰 표적을 분절형 계측 더미, 추적 마커, 데이터 하네스, 고정 발판, 기준 격자로 교체했다. 관찰실에서 정적 상태 화면을 확인한다.',['S01_detail_InstrumentedTestRig','S01_inside','Play_testcell']),('E03 제염동','오염 보호구 회수·밀봉 → 장화 세척·샤워 → 건조·청결 보호구 착용/출구 확인. 회수함·실러·발 세척기·개별 보호구 디스펜서·확인대, 상부 급수/바닥 배수 접점과 국소 바닥 작업 표기를 반영했다.',['E03_dirty_return','E03_wash_step','E03_clean_issue','E03_detail_PipedDeconShower','E03_detail_CleanPPEDispenser','Play_decon']),('E02 급식지원동','직원용 외부 공급 밀봉 식품을 저온/상온 보관하고 재가열·검수·분배한다. 직접 요리하는 주방이나 식당이 아니다. 피험체용 영양팩/투약 소모품은 별도 잠금 서랍과 인계 카트로 구분했다.',['E02_inside','E02_detail_SealedMealInspection','E02_detail_MealRegenerationCabinet','E02_detail_ControlledNutritionBank','E02_detail_NutritionTransferCart','Play_meal']),('E01 물자보급동','중앙 6개와 벽면 8개, 총 14개 적재 선반. 상자·재사용 용기·밀봉 드럼·장비 케이스 네 적재 유형, 묶음 팔레트 두 종류, 수동 팔레트 트럭, 스캐너/저울/라벨 프린터를 배치했다. 작업대 폭과 적재 위치를 조정해 선반 접근을 확보했다.',['E01_inside','E01_warehouse','E01_detail_WarehouseRack_0','E01_detail_ReceivingInspection','E01_detail_PalletTruck','Play_receiving']),('VL 화물승강기','강재 보강 문짝, 분리된 문틈, 발판 보호 철판, 문턱 레일, 고무 충돌 방지대, 층/적재 정보 화면과 호출 조작부를 반영했다. 상단 중복 화면과 호출 패널 가림을 제거했다. 문 개폐와 층간 운행은 정적 외형 이후의 기능 작업이다.',['VL_freight','Play_lift']),('C03·C04 제어 설비','C04 배전반뿐 아니라 C03·S01의 같은 장비도 교체했다. 곡면 렌즈·패킹·금속 베젤·켜짐/꺼짐 재질·밀착 기능 인쇄를 적용했다. 공정 제어반의 평면 초록 점, 화면을 가리던 나사, 부자연스러운 추가 조작판을 정리했다.',['C04_indicators','C04_detail_ElectricalSwitchgear','C03_detail_ProcessControlBay','Play_cooling','Play_utility'])]
cards=[];nav=[];imagecount=0
for i,(title,desc,imgs) in enumerate(sections):
 nav.append(f'<a href="#s{i}">{html.escape(title)}</a>');fig=[]
 for name in imgs:
  assert (D/(name+'.png')).exists(),name
  fig.append(f'<figure><button class="image" data-src="{name}.png" aria-label="{html.escape(title)} 확대"><img src="{name}.png" loading="lazy" alt="{html.escape(name)}"></button><figcaption>{html.escape(name)}</figcaption></figure>');imagecount+=1
 cards.append(f'<section id="s{i}"><h2>{html.escape(title)}</h2><p>{html.escape(desc)}</p><div class="grid">'+''.join(fig)+'</div></section>')
page='''<!doctype html><html lang="ko"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>B5 운용 목적·장비 상세 검수 V0.01</title><style>body{margin:0;background:#131d23;color:#e5eceb;font:16px/1.65 system-ui,sans-serif}header,main{max-width:1440px;margin:auto;padding:28px}header{border-bottom:1px solid #43535b}h1{font-size:30px}nav{display:flex;gap:10px;flex-wrap:wrap}a{color:#99d8d5}nav a{padding:6px 12px;border:1px solid #45606c;border-radius:6px;text-decoration:none}.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(380px,1fr));gap:18px}figure{margin:0;background:#1d2a32;border:1px solid #344750;border-radius:8px;overflow:hidden}figure button{padding:0;border:0;display:block;background:transparent;width:100%;cursor:zoom-in}img{width:100%;display:block}figcaption{padding:8px;font:12px monospace;color:#b8c8cb}section{margin:24px 0 50px;scroll-margin-top:20px}section p{max-width:1080px}aside{background:#21343b;padding:18px;border-radius:8px}dialog{max-width:94vw;max-height:94vh;border:1px solid #45606c;padding:8px;background:#111b20;color:white}dialog::backdrop{background:#000c}dialog img{max-height:85vh;width:auto;max-width:90vw}dialog button{float:right;padding:8px 20px;cursor:pointer} @media(max-width:500px){.grid{grid-template-columns:1fr}}</style><header><h1>B5 운용 목적·장비 상세 검수 V0.01</h1><p>송예찬 · 2026-11-08 · 로컬 씬 반영 / 사용자 검수 대기</p><aside>새 모델 25종 · 배치 41개 · 장비 접근 포함 Controller 128/128 통과 · 안내선 38경로 막힘 0 · Play 7구역 새 게임 로그 0<br>화면과 설비는 정적 아트다. 전체 조명·색감 및 게임 기능은 별도 단계이며, 이 화면은 외형 확인용이다.</aside><p><a href="검수결과.md">검수 결과</a> · 이미지를 누르면 확대할 수 있다.</p><nav>'''+''.join(nav)+'</nav></header><main>'+''.join(cards)+'''</main><dialog id="viewer"><button onclick="this.parentNode.close()">닫기</button><img alt="확대 검수 이미지"></dialog><script>const d=document.querySelector('dialog');document.querySelectorAll('[data-src]').forEach(b=>b.onclick=()=>{d.querySelector('img').src=b.dataset.src;d.showModal()});d.addEventListener('click',e=>{if(e.target===d)d.close()});</script></html>'''
(D/'review.html').write_text(page,encoding='utf-8')
rows='\n'.join(f'| {n} | {p["framesAdvanced"]} | {p["displacement"]:.3f} m | {len(p["errors"])} |' for n,p in plays.items())
report=f'''# B5 운용 목적·장비 상세 검수 V0.01

작성자 송예찬 · 2026-11-08 · 사용자 세부 판단 위임에 따른 제작안. 외형 최종 판정 대기.

[검수 화면 {imagecount}장](review.html) · [제작 원본](../../../SourceAssets/B5_OperationalDetail/README.md)

## 반영 내용

'''+ '\n\n'.join('### '+t+'\n\n'+desc for t,desc,_ in sections)+f'''

## 검증

- OD_ 모델25종, 배치41개(장비40·국소 바닥 표기1). 고유 메시 {a['triangles']:,}tri, 정확한 면적 0 삼각형0·재질 누락0. 전체 메시의 수밀성 보증은 아니다.
- 공용 PBR9장·장비 인쇄 atlas1장·정적 화면7장. 원본 Blender와 제작 스크립트, 출처 JSON 보관.
- 기존38 안내 경로 {v['samples']:,}개 표본의 막힘/바닥 누락0. 노선/색상/선 자산은 변경하지 않았다.
- 실제 CharacterController 이동128/128 통과: 기존90경로 + 새 장비 앞 접근38경로. 작업대와 선반 사이로 실제 캐릭터가 진입하는지 검사했다. 팔레트 운반 차량의 회전 반경 시뮬레이션은 아니다.
- 씬 점유 그리드는 반경0.38m, 실제 Controller 검사는 씬의 기존 반경 {w['radius']:.2f}m로 수행했다.
- 경계 상자 간섭 후보4건은 샤워 상부 배관/캐노피 접점2건과 승강기 외피·레일을 하나의 상자로 감싼 후보2건이다. 전체 메시 교차가 0이라고 해석하지 않는다. 실제 렌더와 통행을 함께 확인했다.
- Play7구역에서 실제 W 입력 이동, 프레임 증가, 새 경고/오류 로그를 확인했다. 아래 수치는 이 PC의 Editor 검사이며 배포 빌드 성능 보증이 아니다.

| 구역 | 진행 프레임 | 실제 이동 | 새 게임 경고/오류 |
| --- | ---: | ---: | ---: |
{rows}

## 보존과 현재 상태

- 작업 시작 시점 기존 Assets {pres['baselineAssets']:,}개 중 {pres['unchanged']:,}개 동일. 변경된 기존 파일은 대상 B5 씬1개다. 기존 모델·재질·안내선·가림 데이터 보존.
- C01 실험동 및 기존 C01/T01 아트의 보호 Transform {pres['protectedTransforms']}개 동일. 기존 Light {pres['lightsBefore']}개 전체 설정 동일, 새 Light0개.
- 교체 전 가구는 비활성 보관. 게임 C#/Animator 변경0. 문 개폐·화물승강기 층간 이동·장비 UI 갱신은 미구현.
- Edit 모드 저장 완료, 시작 위치 {post['player']} 보존, runInBackground 원상 복구. 커밋·push는 하지 않았다.
- 다음: 사용자 공간 용도/외형 검수 → 지적 사항 보수 → B5 전체 조명·색감 조정. 아트 최종 판정0/34 유지.

근거: [메시/배치](audit.json), [안내선](verification.json), [이동](walk.json), [보존](preservation.json), [종료 상태](post_play.json).
'''
(D/'검수결과.md').write_text(report,encoding='utf-8')
summary='2026-11-08 운용 목적·장비 보강: 사용자 위임에 따라 S01 흰 표적을 계측 더미/고정대/추적 마커로, E03을 오염 보호구 회수·밀봉→세정→청결 착용 흐름으로 보강했다. E02는 직원용 외부 공급 밀봉식의 보관·재가열·분배와 피험체용 영양/투약 물품의 잠금 인계로 구분했다. E01 중앙6·벽면8 선반, 팔레트/수동 운반/입고 검사 장비, VL 화물 문·문턱·호출부, C03/C04/S01 표시등·제어부를 상세화했다. 새 모델25종·배치41개, 안내38경로 막힘0·Controller128/128·Play7구역 새 게임 로그0. C01 및 기존247 Light·대상 씬 외 기존 Assets 보존, 게임 C#/Animator 변경0. **다음은 사용자 용도·외형 검수 → 보수 → B5 전체 조명·색감 조정**. 정적 아트이며 문/승강기 기능과 B4 연결 미구현, 아트 최종 판정0/34 유지. 로컬 저장, 커밋·push 미실시. 작성자 송예찬.'
for rel,oldver,newver in [('AGENTS.md','V0.56','V0.57'),('CLAUDE.md','V0.56','V0.57'),('Docs/이어하기_2026-11-06.md','V0.40','V0.41'),('Docs/회사_작업목록_2026-11-06.md','V0.38','V0.39')]:
 f=R/rel;s=f.read_text(encoding='utf-8');head,body=s.split('\n',1)
 if '2026-11-08 운용 목적·장비 보강:' in body[:1400]:continue
 assert oldver in head,(rel,head)
 prefix='검수/' if rel.startswith('Docs/') else 'Docs/검수/'
 note=summary+f' [검수 화면]({prefix}2026-11-08_B5_OperationalDetail/review.html) · [검수 결과]({prefix}2026-11-08_B5_OperationalDetail/검수결과.md).'
 f.write_text(head.replace(oldver,newver)+'\n\n'+note+'\n\n이전 단계 기록:\n'+body.lstrip(),encoding='utf-8')
f=R/'Docs/AfterSeconds_메인기획서.md';s=f.read_text(encoding='utf-8');head,body=s.split('\n',1)
if '2026-11-08 운용 목적·장비 보강:' not in body[:1400]:f.write_text(head+'\n\n'+summary+' [검수 화면](검수/2026-11-08_B5_OperationalDetail/review.html).\n\n'+body.lstrip(),encoding='utf-8')
f=H/'README.md';s=f.read_text(encoding='utf-8');head,body=s.split('\n',1)
if '최종 반영:' not in body: f.write_text(head.replace('V0.01','V0.02')+'\n\n최종 반영: 모델25종·장비40개와 바닥 표기1개, PBR9장·인쇄1장·정적LCD7장. 128개 실제 Controller 경로 및 Play7구역 통과. [검수 결과](../../Docs/검수/2026-11-08_B5_OperationalDetail/검수결과.md).\n\n'+body.lstrip()+'\n\n재현 순서: textures.py → Blender build.py → layout.py → Apply.cs(최초만) / Refresh.cs·Fix.cs(보수) → Grid.cs·FunctionalAccess.py·Walk.cs·Verify.cs → run_play.py → PostPlay.cs·Audit.cs·preservation.py·report.py. 모든 C#은 Editor 검사 도구로 이 폴더에서만 실행한다. 기존 baseline/보고서를 새 작업에 덮어쓰지 않는다.\n',encoding='utf-8')
(D/'review_manifest.json').write_text(json.dumps(dict(author='송예찬',images=imagecount,sections=len(sections),models=len(manifest),placements=len(layout['placements']),triangles=a['triangles'],controllerPaths=len(w['results'])),ensure_ascii=False,indent=2),encoding='utf-8')
print('Gallery',imagecount,'images; report and handoff updated')
