from pathlib import Path
import json,sys,math,hashlib,html,collections
H=Path(__file__).resolve().parent;R=H.parents[1];U=R/'Unity/After_Seconds_Build_V0.01';A=U/'Assets/Afrer_Seconds';O=R/'Docs/Review/2026-11-11_B1_FullFloor';sys.path.insert(0,str(U/'Temp/ZFightingReview/deps'))
from PIL import Image,ImageDraw,ImageFont
f=lambda n:ImageFont.truetype('C:/Windows/Fonts/malgun.ttf',n)
plan=json.loads((H/'layout.json').read_text(encoding='utf8'));audit=json.loads((O/'audit.json').read_text());walk=json.loads((O/'walk.json').read_text());geo=json.loads((H/'geometry_verified/Level_B1_Circular.json').read_text());play=[json.loads(p.read_text()) for p in sorted(O.glob('before_play_*.json'))]
before=json.loads((H/'protected_before.json').read_text());changed=[name for name,sha in before.items() if not (R/name).exists() or hashlib.sha256((R/name).read_bytes()).hexdigest()!=sha]
assert not changed,changed
assert not audit['errors'] and all(x['passed'] for x in walk['results']) and not walk['planningFailures']
assert not geo['patches'] and all(p['complete'] and p['framesAdvanced']>10 and p['displacement']>.3 and not p['errors'] for p in play)
newassets=[p for folder in [A/'05.Model/Environment/B1',A/'05.Model/Props/B1'] for p in folder.rglob('*') if p.is_file() and p.name.startswith(('BL_','B1M_'))]
newassets += [p for p in (A/'01.Scenes/Stage').glob('Level_B1_Circular*') if p.is_file()]
newassets += [p for p in (A/'01.Scenes/Stage/Level_B1_Circular').rglob('*') if p.is_file()]
newfbx=[p for p in newassets if p.suffix=='.fbx']; resources=dict(fbx=len(newfbx),fbxMiB=round(sum(p.stat().st_size for p in newfbx)/2**20,2),newAssetMiB=round(sum(p.stat().st_size for p in newassets)/2**20,2),sourceMiB=round(sum(p.stat().st_size for p in H.rglob('*') if p.is_file())/2**20,2),protectedFiles=len(before),changedProtected=changed)
(O/'preservation.json').write_text(json.dumps(dict(protected=len(before),changed=changed,errors=[]),indent=2));(O/'resources.json').write_text(json.dumps(resources,indent=2));(O/'play_summary.json').write_text(json.dumps(play,indent=2))
geo_summary=dict(initialInternal=46,initialOverlapCandidates=355,finalInternal=0,finalDuplicates=0,residualQuantizedCandidates=16,verifiedCoplanarOverlapPairs=geo['overlapPairs'],verifiedRemovedArea=geo['projectedRemovedArea'],toleranceM=.00005,smallSurfaceLimitM2=.005,scope='Opaque planar surfaces; mutually exclusive LODs excluded from cross-renderer checks. Not a dynamic-lighting or all-angle runtime artifact guarantee.')
(O/'geometry_summary.json').write_text(json.dumps(geo_summary,indent=2))
# As-built geometry drawing, using the actual B1 room/tunnel/prop transforms.
im=Image.new('RGB',(2200,1560),(20,27,31));dr=ImageDraw.Draw(im);scale=7.1;ox=1100;oy=810
def xy(x,v):return (ox+x*scale,oy+v*scale)
dr.text((48,26),'AFTER SECONDS · B1 · 제작 배치도 V0.01',font=f(38),fill=(227,229,218));dr.text((50,88),'13개 공동 / 3개 코어 / 22개 통로 / 174개 주요 프랍 · 2026-11-11 · 송예찬',font=f(22),fill=(160,180,178))
for t in plan['tunnels']:
 points=[xy(*p) for p in t['path']];dr.line(points,fill=(91,105,110),width=31);dr.line(points,fill=(39,51,56),width=26);mid=points[len(points)//2] if len(points)>2 else ((points[0][0]+points[-1][0])/2,(points[0][1]+points[-1][1])/2);dr.text(mid,t['id'].split('-')[1],font=f(13),fill=(172,181,174),anchor='mm')
for r in plan['rooms']:
 x,y=xy(r['x'],r['v']);rad=r['r']*scale;warm=r['id'].startswith('W') or r['id'] in ['E02','E03'];color=(94,80,62) if warm else (52,79,89);dr.ellipse((x-rad,y-rad,x+rad,y+rad),fill=color,outline=(185,195,184),width=2)
 for p in plan['placements']:
  if p['room']!=r['id'] or p['role']=='Accessory':continue
  w,h,d=p['size'];cx,cy,cz=p['center'];yaw=math.radians(p['yaw']);points=[]
  for dx,dz in [(-w/2,-d/2),(w/2,-d/2),(w/2,d/2),(-w/2,d/2)]:
   a,b=cx+dx,cz+dz;xx=p['position'][0]+a*math.cos(yaw)+b*math.sin(yaw);zz=p['position'][2]-a*math.sin(yaw)+b*math.cos(yaw);points.append(xy(r['x']+xx,r['v']-zz))
  dr.polygon(points,fill=(148,158,143),outline=(31,43,45))
 dr.text((x,y-7),r['id'],font=f(24),anchor='mm',fill=(247,238,208));dr.text((x,y+rad+20),r['name'],font=f(18),anchor='mm',fill=(221,223,213))
dr.text((48,1500),'T08 북측 곡선 진입: 방 위치·연결 관계 유지 / VA·VB 상행18m / VL 정적 승강기 / 층 전환·AI·상호작용은 후속',font=f(21),fill=(177,193,188));im.save(O/'B1_as_built.png')
# Compact review contact sheet of the sixteen room and core views.
sheet=Image.new('RGB',(1600,1120),(22,28,31));draw=ImageDraw.Draw(sheet)
for i,r in enumerate(plan['rooms']):
 tile=Image.open(O/(r['id']+'_overview.jpg')).resize((400,250));x=(i%4)*400;y=(i//4)*280;sheet.paste(tile,(x,y));draw.text((x+10,y+254),r['id']+' '+r['name'],font=f(17),fill=(226,227,216))
sheet.save(O/'contact.jpg',quality=90)
roomlinks=''.join(f'<figure><a href="{r["id"]}_room.jpg"><img loading="lazy" src="{r["id"]}_overview.jpg"></a><figcaption>{r["id"]} · {html.escape(r["name"])}</figcaption></figure>' for r in plan['rooms'])
detail=''.join(f'<figure><a href="{p.name}"><img loading="lazy" src="{p.name}"></a><figcaption>{p.stem.removeprefix("detail_")}</figcaption></figure>' for p in sorted(O.glob('detail_*.jpg')))
page=f'''<!doctype html><html lang="ko"><meta charset="utf-8"><meta name="viewport" content="width=device-width"><title>B1 제작 검수 V0.01</title><style>body{{margin:36px auto;max-width:1400px;padding:0 24px;background:#141b20;color:#dfe5df;font:16px/1.7 system-ui}}a{{color:#a8d7ce}}h1,h2{{font-weight:600}}.grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(320px,1fr));gap:18px}}figure{{margin:0;background:#253037;padding:10px;border-radius:8px}}img{{width:100%;height:auto}}figcaption{{padding:6px}}.facts{{padding:18px;background:#293b40;border-radius:10px}}</style><h1>After Seconds · 지하 1층 제작 검수 V0.01</h1><p>송예찬 · 2026-11-11 · 전체 정적 외형과 통행 검수 완료 / 사용자 외형 확인 대기</p><div class="facts">13개 공동 + 3개 코어 · 통로22 · 주요 프랍174 · 신규/보정 FBX{resources['fbx']}개 ({resources['fbxMiB']}MiB)<br>CharacterController 250/250 · 실제 Play8구간 · 신규 게임 오류0 · 보호 파일{len(before)}개 변경0<br>중복 삼각형0 · 내부 겹침0 · 0.05mm 기준 잔여 평면 겹침0 · LOD{audit['lodGroups']}그룹 · 반사16 · 가림 베이크</div><p>씬: <b>Level_B1_Circular</b>. 문은 열린 외형이며, AI·CCTV 작동·승강기 이동·층 전환·소품 획득 기능은 구현하지 않았습니다. 기존 Player와 게임 코드, B2 냉각 펌프 보수를 보존했습니다. Play 측정은 에디터의 짧은 구간 확인이며 빌드 권장사양 보증이 아닙니다.</p><h2>실제 배치</h2><a href="B1_as_built.png"><img src="B1_as_built.png"></a><h2>공동·이동 코어</h2><div class="grid">{roomlinks}</div><h2>근접 외형</h2><div class="grid">{detail}</div><h2>검수 기록</h2><p><a href="Review.md">결과와 후속 범위</a> · <a href="audit.json">씬 구조</a> · <a href="walk.json">통행250경로</a> · <a href="play_summary.json">실제 Play</a> · <a href="geometry_summary.json">깊이 충돌 범위</a> · <a href="preservation.json">기존 작업 보존</a> · <a href="resources.json">용량</a></p></html>'''
(O/'review.html').write_text(page,encoding='utf8')
text=f'''# B1 전체 정적 외형 제작·검수 V0.01

작성자: 송예찬 · 2026-11-11

사용자의 B1 제작 요청에 따라 `Level_B1_Circular.unity`를 새로 제작했다. 최신 Decision의13공동·3코어·22연결을 유지하고, T08의 진입을 북측 곡선으로 바꾸어 관찰 공동 접합 겹침을 제거했다. 옛 B1 실험 씬과 다른 층은 변경하지 않았다.

174개 주요 프랍을 배치했다. C01/N01 시험 설비, C02 준비, C03 기록, C04 의료, C05 관찰, W01 연구·회의, W02 조리→배식→식사, W03 직원 숙소, E01 감독·보안, E02 기밀 기록, E03 경비 숙소, S01 백업 서버를 구분했다. 직원 이층침대8개·경비 이층침대4개와 위생/세탁 시설, 업무 자리와 연결한 의자, R1 직원 이중 안내선·불투명 출입 표지를 반영했다. 생활부는 따뜻한 회색/아이보리, 연구부는 중성 작업광이다.

## 검증 결과

- 실제 CharacterController 통행250/250: 통로22개 왕복, 공동 출입/작업 접근, 두 계단18m 왕복. 바닥·충돌 누락과 접근 계획 실패0.
- 실제 Play8구간: C01·W03·W02·E01·N01·C04·복도·계단. 프레임 진행과 키보드 이동, 새 경고/오류0을 확인. 최종 계단/복도는 보수 후 재검사. 마우스·키보드 장치를 비활성화하지 않았다.
- FBX{resources['fbx']}개 {resources['fbxMiB']}MiB, 신규 Unity 에셋 합계 약{resources['newAssetMiB']}MiB. 공용 텍스처/설비 재사용, 큰 Unity YAML 메시 파생본0개. 신규 메시 Read/Write 해제. LOD{audit['lodGroups']}그룹, 반사16개, 활성 광원{audit['lights']}개 중 그림자{audit['shadowLights']}개.
- 단면·접합 면 보수: 계단 챌판/디딤판 겹침, 터널/돔 벽 두께 이음, 공용 프랍8메시의 내부 면을 보정. 보정 FBX8개를319렌더러가 공유하며 공용 원본은 보존. CCTV 고정 가스켓13개 간격과 싱크 지지대12개 보완.
- 최종 평면 검사: 중복 삼각형0, 내부 겹침0. 1mm 양자화 후보16개는 실제0.05mm 평면 거리 조건에서 모두 제외. 검사 표본은 면적0.005m² 이상 불투명 평면을 중심으로 하며 모든 작은 면·조명 조건의 무결성을 보장하지 않는다.
- 보호 파일{len(before)}개 해시 일치. 기존 씬·게임 C#·Animator와 B2 VARCO/냉각 펌프 보수 보존. 새 씬의 메시/재질/스크립트 누락0,174개 배치 좌표/회전 일치.

## 남은 범위와 검수 순서

사용자 외형 검수는 C01 → W02 → W03 → E01 → C04 → N01 순서가 적합하다. 방별 밀도·조명 취향과 근접 디테일은 사용자 확인 후 해당 구역만 보수한다. 전체 Apply를 재실행하지 않는다.

현재 결과는 정적 레벨 아트다. VA/VB18m 계단과 VL 캐빈 및 도착/전환 마커만 준비했고, 실제1F 씬 연결·승강기 이동·문/CCTV 동작·경비 AI·소품 획득은 미구현이다. 게임 기능은 사용자 직접 구현 방침을 유지한다. 에디터 Play의 짧은 샘플을 출시 빌드 FPS나 권장사양으로 해석하지 않는다.

[화면 검수](review.html) · [실제 배치도](B1_as_built.png) · [제작 원본](../../../SourceAssets/B1_FullFloor/README.md)
'''
(O/'Review.md').write_text(text,encoding='utf8')
print(json.dumps(resources,ensure_ascii=False));print('Report and as-built drawing written')
