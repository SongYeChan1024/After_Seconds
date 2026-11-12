"""Write the local art review and handoff after the native checks have passed."""
from pathlib import Path
import json,html,math,re,hashlib
H=Path(__file__).resolve().parent;R=H.parents[1];O=R/'Docs/Review/2026-11-12_1F_FullFloor';U=R/'Unity/After_Seconds_Build_V0.01'
def read(n):return json.loads((O/n).read_text(encoding='utf8'))
p=json.loads((H/'resolved.json').read_text(encoding='utf8'));quality=read('quality.json');walk=read('walk.json');geo=read('geometry.json');protected=read('protected.json');look=read('look_test.json');audit=read('audit.json');occ=read('occlusion.json');plays=[read('play_'+n+'.json') for n in ['VA','VB','VL','C01','C02','C03','C04','OUT']]
assert not quality['errors'] and not audit['errors'] and not walk['failed'] and not walk['planningFailures'] and not geo['patches'] and not protected['changed'] and not protected['missing']
assert all(q['complete'] and q['framesAdvanced']>10 and q['displacement']>.3 and not q['errors'] for q in plays)
assert look['complete'] and look['events']>0 and look['yawChange']>.1 and look['pitchChange']>.1 and not look['errors']

# A true-scale, static review drawing. Diagram labels are not added to the game scene.
scale=8.5
def xy(x,z):return(55+(x+71)*scale,75+(38-z)*scale)
svg=['<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="820" viewBox="0 0 1200 820">','<rect width="1200" height="820" fill="#121b20"/>','<g font-family="Malgun Gothic, sans-serif" fill="#e6e9dc">','<text x="40" y="38" font-size="24">AFTER SECONDS · 1F 폐공장 실제 배치</text>','<text x="40" y="63" font-size="13" fill="#a6b4ad">4구역 + 3코어 + 외부 마당 · Y=0 · 85기물 · 연결 7개 · 송예찬 / 2026-11-12</text>']
for tri in p['floorTriangles']:
 pts=' '.join(f'{xy(x,z)[0]:.1f},{xy(x,z)[1]:.1f}' for x,z in tri);svg.append(f'<polygon points="{pts}" fill="#34403d"/>')
for t in p['tunnels']:
 pts=' '.join(f'{xy(x,z)[0]:.1f},{xy(x,z)[1]:.1f}' for x,z in t['path']);svg.append(f'<polyline points="{pts}" stroke="#d8c98c" stroke-width="2" fill="none" stroke-dasharray="5 4"/>')
for q in p['placements']:
 if q['model'] in ['HardHat','HandRadio','ShippingRecord']:continue
 x,y=xy(q['position'][0],q['position'][2]);w=q['size'][0]*scale;d=q['size'][2]*scale;svg.append(f'<rect x="{x-w/2:.1f}" y="{y-d/2:.1f}" width="{w:.1f}" height="{d:.1f}" fill="#81917a" stroke="#c0c6a6" stroke-width=".6" transform="rotate({q["yaw"]} {x} {y})"><title>{html.escape(q["name"])}</title></rect>')
for wall in p['walls']:
 a=xy(*wall['a']);b=xy(*wall['b']);svg.append(f'<path d="M{a[0]},{a[1]} L{b[0]},{b[1]}" stroke="#d4d8c9" stroke-width="2"/>')
names={'C01':'폐생산동','C02':'하역 / 승강기 전실','C03':'출구 검문','C04':'옛 사무 / 휴게','VA':'계단 A','VB':'계단 B','VL':'화물 승강기'}
for room in p['rooms']:
 x,y=xy(room['x'],room['z']+room['d']/2+1.4);svg.append(f'<text x="{x}" y="{y}" text-anchor="middle" font-size="14">{room["id"]} · {names[room["id"]]}</text>')
for arrival in p['arrivals']:
 x,y=xy(arrival['position'][0],arrival['position'][2]);svg.append(f'<circle cx="{x}" cy="{y}" r="5" fill="#7dd5ba"/><text x="{x+8}" y="{y+5}" font-size="10">B1 도착</text>')
x,y=xy(-58,-28);svg.append(f'<text x="{x}" y="{y-8}" text-anchor="middle" font-size="15">← 외부 마당</text>');svg+=['<text x="40" y="770" font-size="13" fill="#a6b4ad">실선: 구조 벽 · 녹색: 기물 · 점선: 연결 관계(실제 보행 경로는 장애물을 우회) · 10m</text>','<path d="M40 790H125" stroke="#d4d8c9" stroke-width="3"/>','</g></svg>'];(O/'1F_plan.svg').write_text('\n'.join(svg),encoding='utf8')

labels={'overview':'전체 배치','Exterior_factory':'지상 공장 외관','C01_production':'폐생산동','C01_press':'프레스와 정비 구역','C02_loading':'하역·출하 공간','C04_office':'직원 사무·휴게','C04_desks':'책상 기물 근접','C03_checkpoint':'검문·물품 검사','OUT_gate':'외부 출구','VA_arrival':'계단 A 도착','VB_arrival':'계단 B 도착','VL_arrival':'승강기 도착'}
for id in ['C01','C02','C03','C04','VA','VB','VL']:labels[id+'_overview']=id+' 구획'
for i in range(1,8):labels[f'T{i:02}_link']=f'T{i:02} 연결 통로'
cards=''.join(f'<figure><a href="{n}.jpg" target="_blank"><img src="{n}.jpg" loading="lazy" alt="{label}"></a><figcaption>{label}</figcaption></figure>' for n,label in labels.items())
playcards=''.join(f'<figure><a href="play_{q["label"]}.png" target="_blank"><img src="play_{q["label"]}.png" loading="lazy" alt="{q["label"]} 실제 Play"></a><figcaption>{q["label"]} 실제 Play · {q["framesAdvanced"]}프레임 · {q["displacement"]:.2f}m 이동 · 경고/오류 0</figcaption></figure>' for q in plays)
page=f'''<!doctype html><html lang="ko"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>After Seconds 1F 전체 검수</title><style>body{{margin:0;background:#121b20;color:#e7ebdf;font:16px/1.7 "Malgun Gothic",sans-serif}}main{{max-width:1420px;margin:auto;padding:40px}}h1{{font-size:32px;margin:0}}p{{color:#b6c1ba;max-width:1000px}}a{{color:#a7d8be}}.grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(440px,1fr));gap:18px}}figure{{margin:0;background:#25322e;border-radius:6px;overflow:hidden}}img{{width:100%;display:block}}figcaption{{padding:10px 16px}}.facts{{display:flex;gap:18px;flex-wrap:wrap;margin:25px 0}}.facts span{{background:#263b33;padding:12px 18px;border-radius:5px}}nav{{margin:20px 0}}@media(max-width:600px){{main{{padding:18px}}.grid{{grid-template-columns:1fr}}}}</style><main><h1>지상 1층 · 폐공장</h1><p>송예찬 · 2026-11-12 · Unity 6000.4.0f1 · Level_1F_Factory</p><p>세 코어에서 올라와 옛 사무동과 하역장을 거쳐 생산동·출구 검문·외부 마당으로 이어지는 지상층이다. 직선 공장 건물, 철골 지붕, 높은 창, 녹슨 운반·생산 설비와 직원 공간을 구성했다.</p><div class="facts"><span>4구역 + 3코어 + 마당</span><span>연결 7개 · 기물 85배치</span><span>통행 84/84</span><span>Play 8곳 · Look 통과</span><span>LOD 82 · 조명 37 · 반사 7</span></div><nav><a href="1F_plan.svg">실제 배치도</a> · <a href="Review.md">검수 기록</a> · <a href="quality.json">모델 검사</a> · <a href="walk.json">보행 결과</a> · <a href="geometry.json">깊이 충돌 결과</a></nav><figure><img src="1F_plan.svg" alt="1F 실제 배치도"></figure><h2>구역별 화면</h2><div class="grid">{cards}</div><h2>실제 플레이</h2><p>기존 Player의 키보드 입력으로 이동했고 프레임 진행·위치 변화·경고/오류를 함께 기록했다. 아래 화면은 실제 Game 뷰 캡처다. 배포 빌드 성능 측정과 권장 사양 확정 자료는 아니다.</p><div class="grid">{playcards}</div><p>이번 범위는 공간·아트·충돌과 보행 검수다. 층 전환, 승강기·보안문 작동, AI, 아이템 사용과 결말 연출은 후속 게임 구현 범위다. 기존 층과 공유 에셋 {protected['unchanged']:,}파일의 SHA-256을 보존했다.</p></main></html>'''
(O/'review.html').write_text(page,encoding='utf8')

review=f'''# 지상 1층 전체 제작 검수 V0.01

작성자 송예찬 · 2026-11-12

사용자 요청에 따라 `Level_1F_Factory.unity`를 새로 제작하고 저장했다. [전체 화면](review.html) · [실제 배치도](1F_plan.svg).

## 공간 구성

| 구역 | 구현 내용 |
|---|---|
| C01 폐생산동 | 프레스, 롤러 컨베이어2종, 지게차, 케이블 릴, 자재 선반, 정비대·제어함, 작업/운반 통로 |
| C02 폐하역장 | 팔레트·출하 적재물, 팔레트 잭·핸드트럭, 화물 케이지, 출하 업무석 |
| C04 옛 사무동 | 배치가 다른 업무석3곳, 우측 마우스·키보드 세부, 서류/무전기, 파일함·사물함, 식탁·싱크대와 휴게 구획 |
| C03 출구 검문 | 경비 업무석, 화물 검사기, 검사 카운터, 열쇠 보관·무전기 충전, 대기 벤치 |
| VA/VB/VL | B1 도착 좌표에 맞춘 두 계단 전실과 열린 화물 승강기 객실, 출구 안내 |
| OUT | 열린 차단기, 볼라드, 울타리, 외부 마당과 도로 |

직선 외벽·철골 트러스·박공지붕/낮은 지붕·창·부분 칸막이로 공간을 구분했다. 낡은 녹색 도장과 콘크리트, 외광과 작업등을 사용한다. 업무석은 앞서 개선한 B1 모델을 서로 다르게 재사용하며 화면/서류 재질만 1F 출하·근무 기록으로 바꿨다. 공용 원본은 수정하지 않았다.

## 설계 기준과 연결

최신 Decision 1F의 4구역·3코어·외부 출구, 중심 좌표와7연결을 유지했다. 원형 점유 반경은 조감도의 직선 산업 건축 외곽 크기로 해석했으며, 문이 모서리와 겹치지 않도록 연결선의 끝점·굴곡을 조정했다. 실제 좌표는 [resolved.json](../../../SourceAssets/F1_FullFloor/resolved.json)과 `Docs/도면/Decision/원형공동/1F_제작현황/as_built_layout.json`이 기준이다.

- VA→C04→C01→C03→OUT.
- VB→C02→C01→C03→OUT.
- VL→C02→C01→C03→OUT.
- B1 VA/VB 도착은 각각(-44,0,24.2)/(44,0,-31.8), VL은 평면(44,26.8)을 유지하고 지상 객실 바닥 Y=.075에 맞췄다.

실험체의 정상 활동 범위 B5/B4와 B4→B3 상행 제한은 유지한다. 지상층에 능력 실험 도구를 넣지 않았다. 과거1F의 강제 교환 구덩이나 미확정 마지막 교환 연출도 적용하지 않았다.

## 검수

- 실제 CharacterController 통행 **{walk['tested']}/{walk['tested']}**: 7연결 양방향, 내부 출입구 연결, 작업 전면/지게차 운전석 접근, 세 진입점→외부 출구 왕복. 계획 실패0, 바닥 낙하/끼임0. [walk.json](walk.json), [routes.json](routes.json).
- 실제 Play **8곳**: VA/VB/VL/C01/C02/C03/C04/OUT. 각 장소 프레임 진행·키보드 이동 확인, 경고/오류0. 별도 마우스 Look 입력 확인. [look_test.json](look_test.json).
- 새 모델 **{quality['models']}FBX·{quality['meshCount']}메쉬**, 비정상 수치·면적0 면·뒤집힌 노멀0, Read/Write꺼짐. [quality.json](quality.json).
- 전체 활성 메쉬의 깊이 충돌 정밀 잔여0: 불투명 평면0.005m² 이상 후보, 실제면 거리0.05mm와 같은 방향 조건으로 확인. 단순 후보7건은 정밀 조건을 통과하지 않는 근접/평행 면이다. 모든 곡면·모든 거리의 픽셀 현상을 수학적으로 보장하는 검사는 아니다. [geometry.json](geometry.json).
- 새 모델 파일 합계 **{quality['modelBytes']/1024**2:.2f}MiB**, 재사용 기물8종과 조명기구1종, 기물85배치, LOD82그룹, 조명37개/그림자5개, 반사7개128px. 가림 데이터{occ['bytes']:,}bytes. 이 수치로 전체 게임의 권장 사양을 확정하지 않는다.
- 기존 Unity 파일 **{protected['unchanged']:,}/{protected['checked']:,} SHA-256 일치**. B1 기물 보수·다른 층·기존1F·공유 모델·.meta·게임 C#·Player·Animator·빌드 설정 보존. [protected.json](protected.json).

## 저장 상태와 다음 작업

새1F 씬을 저장한 편집 상태로 열어 둔다. 기존 Player로 계단A 도착점부터 걸어볼 수 있다. 먼저 C04→C01→C02→C03→OUT의 공간과 외형을 사용자 확인한다. 후속 수정은 현재 저장본의 지정 구역만 다루고 제작기 전체를 재실행하지 않는다.

층 전환·AI·문/CCTV·승강기 작동·물품 사용·결말은 이번 정적 공간 제작의 완료 범위에 포함하지 않는다. 본편 기능은 기존 사용자 주도 구현 방침을 따른다. 커밋·push·블로그 게시는 이번에 요청되지 않아 수행하지 않았다.
'''
(O/'Review.md').write_text(review,encoding='utf8')

decision=R/'Docs/도면/Decision/원형공동/1F_제작현황';decision.mkdir(parents=True,exist_ok=True)
asbuilt=dict(version='V0.01',author='송예찬',date='2026-11-12',scene='Assets/Afrer_Seconds/01.Scenes/Stage/Level_1F_Factory.unity',floor='1F',coordinates='Unity X,Y,Z in metres, ground Y=0',rooms=p['rooms'],tunnels=p['tunnels'],walls=p['walls'],placements=p['placements'],arrivals=p['arrivals'],out=p['out'],notes=p['notes']);(decision/'as_built_layout.json').write_text(json.dumps(asbuilt,ensure_ascii=False,indent=2),encoding='utf8')
(decision/'README.md').write_text('''# 1F 현재 제작 배치 V0.01

작성자 송예찬 · 2026-11-12

`Level_1F_Factory`의 실제 좌표·배치·건축 외곽은 `as_built_layout.json`을 따른다. 최신 Decision의4구역·3코어·OUT와7연결, 중심 좌표는 유지했다. 조감도처럼 직선 공장 건물을 사용했고 문과 벽 모서리를 피해 통로 끝점·굴곡을 조정했다.

폐생산동·하역·옛 직원 사무/휴게·출구 검문·외부 마당과85기물, 철골/창/천장/안내를 구성했다. [검수](../../../../Review/2026-11-12_1F_FullFloor/Review.md) · [화면](../../../../Review/2026-11-12_1F_FullFloor/review.html) · [배치도](../../../../Review/2026-11-12_1F_FullFloor/1F_plan.svg).

전체84/84통행·실제Play8곳·Look·깊이 충돌 검수를 완료했다. 세 코어는 B1 도착 좌표와 대응하지만 실제 층 전환·문/승강기/AI/결말은 후속 게임 기능이다. 과거 구덩이 강제 교환 씬은 현행 설계가 아니며 변경하지 않았다. 사용자 외형 검수 뒤 지정 범위만 보수한다.
''',encoding='utf8')
provenance=dict(version='V0.01',author='송예찬',date='2026-11-12',source='SourceAssets/F1_FullFloor',method='Local Blender hard-surface meshes, generated wear/concrete/records textures; native Unity import, materials, scene editing, verified coplanar clipping; no runtime code changes',scene=asbuilt['scene'],newAssets=quality['assets'],reuse={k:v for k,v in p['models'].items() if v.get('reuse')},newTextureAssets=['Assets/Afrer_Seconds/05.Model/Environment/1F/Textures/F1_SurfaceWear.png','Assets/Afrer_Seconds/05.Model/Environment/1F/Textures/F1_Concrete.png','Assets/Afrer_Seconds/05.Model/Props/1F/Textures/F1_WorkRecords.png'],review='Docs/Review/2026-11-12_1F_FullFloor/Review.md')
(U/'Assets/Afrer_Seconds/06.Data/AssetSources/1F_Factory_20261112.json').write_text(json.dumps(provenance,ensure_ascii=False,indent=2),encoding='utf8')

summary='''2026-11-12 최신: 사용자가 마지막 지상1층 제작을 요청해 `Level_1F_Factory.unity`를 새로 저장했다. 폐생산동·하역장·옛 사무/휴게·출구 검문,3코어·외부 마당과7연결·85기물. B1의 실제 도착 위치와 대응한다. 통행84/84·실제Play8곳·Look·깊이 충돌 잔여0, 새74FBX 약7.66MiB·LOD82·조명37·반사7·가림 베이크. 기존Unity13171파일 해시 보존, B1·다른층·게임C#/Player/Animator·빌드 설정 미변경. **다음은 사용자 전체1F 외형/공간 검수와 지정 범위 보수**다. 층 전환·AI·문/승강기·결말은 후속 기능. [현재 검수](Docs/Review/2026-11-12_1F_FullFloor/Review.md) · [화면](Docs/Review/2026-11-12_1F_FullFloor/review.html) · [제작 원본](SourceAssets/F1_FullFloor/README.md) · [이어하기](Docs/이어하기_2026-11-12.md)를 먼저 읽는다. 저장된1F 편집 상태, C01 프레스 선택. 현재/이전 제작기를 후속 편집 뒤 일괄 재실행하지 않는다. 커밋·push 미실행. 작성자 송예찬.'''
def prepend(file,old,new,text):
 path=R/file;s=path.read_text(encoding='utf8');assert old in s.splitlines()[0];s=s.replace(old,new,1);head,body=s.split('\n',1);path.write_text(head+'\n\n'+text+'\n\n이전 단계 기록:\n'+body,encoding='utf8')
for file in ['AGENTS.md','CLAUDE.md']:prepend(file,'V1.03','V1.04',summary)
prepend('Unity/README.md','V0.59','V0.60',summary.replace('(Docs/','(../Docs/').replace('(SourceAssets/','(../SourceAssets/'))
prepend('Docs/AfterSeconds_메인기획서.md','V0.81','V0.82','**2026-11-12 지상1F 전체 제작.** 사용자가 마지막 지상층 제작을 요청해 폐공장4구역·3코어·OUT·7연결·85기물의 `Level_1F_Factory`를 저장했다. 통행84/84·실제Play8곳·Look·깊이 충돌 검수 완료. 기존 B1과 다른 층은 보존했다. [현재 검수](Review/2026-11-12_1F_FullFloor/Review.md) · [전체 화면](Review/2026-11-12_1F_FullFloor/review.html) · [실제 배치](도면/Decision/원형공동/1F_제작현황/README.md). 다음은 사용자 전체1F 공간·외형 검수다. 본편 층 전환·AI·보안문/승강기·결말은 후속 게임 구현이며, 과거 강제 교환 구덩이나 미확정 엔딩은 적용하지 않았다.')
main=R/'Docs/AfterSeconds_메인기획서.md';s=main.read_text(encoding='utf8');old='B5·B4·B3·B2·B1에 각각 원형 공동과 통로를 갖춘 Unity 씬이 있고, 플레이어는 걷고 달리고 앉아서 통과할 수 있다. 다섯 층의 보행과 공간 검수 기록이 있다.';new='B5·B4·B3·B2·B1의 원형 공동 씬과 지상 폐공장 `Level_1F_Factory` 씬이 있으며, 기존 플레이어로 각 씬에서 걷고 달리고 앉아서 통과할 수 있다. 여섯 층의 개별 보행과 공간 검수 기록이 있다.';assert old in s;s=s.replace(old,new).replace('1F는 최신 도면으로 설명한다.','1F는 최신 실제 배치와 검수 기록을 따른다.');main.write_text(s,encoding='utf8')
prepend('Docs/이어하기_2026-11-12.md','V0.02','V0.03','''## 최신 상태 — 지상1층

사용자가 마지막 지상1층 제작을 요청해 `Level_1F_Factory.unity`를 새로 만들었다. 폐생산동·하역·옛 직원 사무/휴게·출구 검문,3코어·외부 마당을7통로로 연결했다. 기물85배치, 통행84/84·실제Play8곳·Look·깊이 충돌 검수 통과. 새74FBX 약7.66MiB, LOD82·조명37·반사7·가림 베이크. 기존Unity13171파일 해시 일치.

- [현재 검수](Review/2026-11-12_1F_FullFloor/Review.md) · [전체 화면](Review/2026-11-12_1F_FullFloor/review.html) · [배치도](Review/2026-11-12_1F_FullFloor/1F_plan.svg) · [실제 배치](도면/Decision/원형공동/1F_제작현황/README.md).
- Unity6000.4.0f1의 새1F 저장·편집 상태, C01 프레스 선택. Play 시작점은 계단A의 B1 도착 자리다. 게임 입력과 임시검수 설정을 복구했다.
- B1의 데스크/기물 보수와 다른 층·기존1F·공유 원본·.meta·게임C#·Player·Animator·빌드 설정은 보존했다. Git main HEAD는 `f663ea07010dc1f40698a55431f9db9ccf286e12`, 이전 B1과 이번1F 작업은 로컬 변경으로 남아 있다.
- 다음은 사용자 전체1F 외형과 체감 규모 검수다. C04→C01→C02→C03→OUT 순서와 VA/VB/VL 진입을 보고 지정 구역만 수정한다. 게임 기능은 사용자 주도 방침을 유지한다.
- 실제 층 전환·보안문/CCTV·AI·승강기·물품 사용·결말은 후속이다. 여섯 층 정적 공간이 있다는 사실은 본편 연속 플레이가 완성됐다는 뜻이 아니다.
- 이번 커밋·push·블로그 게시는 미실행. 현재/이전 제작기를 후속 사용자 편집 뒤 재실행하지 않는다. 새 제작 원본은 `SourceAssets/F1_FullFloor/README.md`.

작성자 송예찬 · 2026-11-12''')
src=(H/'README.md').read_text(encoding='utf8').replace('V0.01','V0.02',1).replace('현재 작업 중이며 검수 전 완료로 해석하지 않는다.','새1F 씬을 저장했고84/84통행·실제Play8곳·Look·깊이 충돌·모델 품질 검수를 통과했다. 전체 아트 최종 수용은 사용자 검수 뒤 결정한다.');src+='''

## 적용 결과와 재현 자료

74새FBX·85기물·LOD82·조명37/그림자5·반사7·가림 베이크. 기존Unity13171파일 해시 보존. [검수](../../Docs/Review/2026-11-12_1F_FullFloor/Review.md)와 [화면](../../Docs/Review/2026-11-12_1F_FullFloor/review.html)을 따른다.

`plan.py`→`plan.json`은 원도면 연결을 실제 직선 건물로 해석한 초기 계획이다. `resolve.py`→`resolved.json`이 최종 배치/재사용 모델과 접근 위치의 기준이다. `common.py`·`props.py`·`architecture.py`·`textures.py`는 제작 원본, `floor_fix.py`·`detail_geometry.py`·`wayfinding.py`는 적용한 구조/표지 후속 단계다. `clean.py`는 native Unity 원본 채널을 보존하며 정밀 계획의 중복 면만 잘라 FBX에 다시 저장했다. 마지막 노멀/미세 퇴화면 보수도 반영했다. 현재FBX가 저장된 최종 산출물이며 원시 생성기를 덮어 실행하면 후속 면 정리가 사라진다.

`Apply.cs`는 새 씬 생성 전용이다. 이후 `Polish/Detail/Wayfinding/Finish`를 이미 적용했다. 일부 후속 도구는 반복 실행 시 조명 값을 다시 바꾸므로 재실행하지 않는다. `Review/Walk/Quality/GeometryExport/Play/Look`가 외부 검수 도구이며 Assets 안에 게임 C#을 추가하지 않았다. `Inspect.cs`와 `baseline.py`의 원래 기준선은 덮어쓰지 않는다. `protected_before.json`은 작업 전13171파일, `protected.json`은 작업 뒤 대조 결과다.

현재 저장본에서 새 수정이 필요하면 먼저 조사한 뒤 지정 오브젝트만 수정한다. B1·다른 층의 이전 제작기를 실행하지 않는다. 작성자 송예찬.
''';(H/'README.md').write_text(src,encoding='utf8')
resources=dict(newModels=quality['models'],modelBytes=quality['modelBytes'],newMeshCount=quality['meshCount'],placements=85,lodGroups=82,lights=37,shadowLights=5,reflectionProbes=7,occlusionBytes=occ['bytes'],newTextureSizes=[[1024,1024],[1024,1024],[2048,2048]],reusedPropModels=8,reusedFixtureModels=1,scene='Level_1F_Factory',note='Editor art validation, not a standalone build hardware recommendation');(O/'resources.json').write_text(json.dumps(resources,indent=2),encoding='utf8')
print('Reports, provenance, as-built layout, and handoff updated',flush=True)
