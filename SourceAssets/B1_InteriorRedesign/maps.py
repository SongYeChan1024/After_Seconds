"""Actual plan: meters, native scene placement, public routes and occupied zones."""
from pathlib import Path
import json,math,html
H=Path(__file__).resolve().parent;R=H.parents[1];O=R/'Docs/Review/2026-11-12_B1_Interior'
p=json.loads((H/'layout.json').read_text(encoding='utf8'))
public=json.loads((O/'public_routes.json').read_text(encoding='utf8'))
labels={'C01':'자료 열람 · 대조','C02':'기록 인계 · 정리','C03':'기록 보관','C04':'직원 의무실','C05':'8인 회의실','W01':'직원 사무실','W02':'조리 · 식당 · 휴게','W03':'직원 침실 · 위생','E01':'출입 보안 업무','E02':'기밀 기록 보관','E03':'경비 침실 · 교대','N01':'연구 데이터 분석','S01':'백업 · 서버','VA':'계단 A','VB':'계단 B','VL':'화물 코어'}
def rect(x,z,w,d,fill,stroke='#758391',sw=.025):return f'<rect x="{x-w/2:.4f}" y="{-z-d/2:.4f}" width="{w:.4f}" height="{d:.4f}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>'
def room(r,overview=False):
 code=r['id'];out=[f'<circle r="{r["r"]}" fill="#f5f3ec" stroke="#384d60" stroke-width=".16"/>']
 for z in p['interior']['zones']:
  if z['room']==code:
   x0,z0,x1,z1=z['bounds'];out.append(rect((x0+x1)/2,(z0+z1)/2,x1-x0,z1-z0,'#d8e9e4','#92b7aa'))
 if not overview:
  for c in p['interior']['ceilings']:
   if c['room']==code:
    x0,z0,x1,z1=c['bounds'];out.append(f'<rect x="{x0}" y="{-z1}" width="{x1-x0}" height="{z1-z0}" fill="none" stroke="#aac0ca" stroke-width=".04" stroke-dasharray=".18 .12"/>')
 for q in p['placements']:
  if q['room']!=code or q['model']=='BL_HandheldRecorder':continue
  x,y,z=q['position'];cx,cy,cz=q['center'];w,h,d=q['size'];a=math.radians(q['yaw']);xx=x+cx*math.cos(a)+cz*math.sin(a);zz=z-cx*math.sin(a)+cz*math.cos(a)
  fill='#a9bdc2' if 'Chair' in q['model'] else '#b9a887' if 'Bunk' in q['model'] else '#c3c8cc'
  out.append(f'<g transform="translate({xx:.3f},{-zz:.3f}) rotate({q["yaw"]})"><title>{html.escape(q["name"])}</title>'+rect(0,0,w,d,fill)+f'<path d="M -.16 {-d/2-.02:.3f} L .16 {-d/2-.02:.3f}" stroke="#336878" stroke-width=".055"/></g>')
 for w in p['interior']['walls']:
  if w['room']==code:out.append(f'<line x1="{w["a"][0]}" y1="{-w["a"][1]}" x2="{w["b"][0]}" y2="{-w["b"][1]}" stroke="{"#668da2" if w.get("glazed") else "#344d5a"}" stroke-width="{w["th"]}"/>')
 for route in public:
  if route['id'].startswith(code+'_'):
   pts=' '.join(f'{v[0]-r["x"]:.2f},{-(v[2]+r["v"]):.2f}' for v in route['points'])
   out.append(f'<polyline points="{pts}" fill="none" stroke="#dc8a36" stroke-opacity=".7" stroke-width=".07"/>')
 for d in r['doors']:
  out.append(f'<circle cx="{d["x"]}" cy="{-d["z"]}" r=".22" fill="#e58d29"/>')
  if not overview:out.append(f'<text x="{d["x"]*.87}" y="{-d["z"]*.87}" font-size=".32" fill="#99591a" text-anchor="middle">{d["id"].replace("B1-","")}</text>')
 return ''.join(out)
base='<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" style="font-family:Malgun Gothic,Arial,sans-serif" '
out=[base+'viewBox="-143 -96 286 195" width="1716" height="1170"><rect x="-143" y="-96" width="286" height="195" fill="#f7f8fa"/><text x="-137" y="-89" font-size="4" fill="#213b4d">B1 · 연구 데이터와 직원 생활 / 실내 구획 V0.01</text><text x="-137" y="-83" font-size="2.3" fill="#536a78">송예찬 · 2026-11-12 · 기존 13공동 / 3코어 / 22통로 · 주황선: 체류 구획을 피하는 검증 통과 경로</text>']
for t in p['tunnels']:
 pts=' '.join(f'{v[0]:.2f},{v[1]:.2f}' for v in t['path']);out.append(f'<polyline points="{pts}" fill="none" stroke="#ccd8dc" stroke-width="4.2"/>')
for r in p['rooms']:
 out.append(f'<a xlink:href="{r["id"]}_plan.svg"><g transform="translate({r["x"]},{r["v"]})">'+room(r,True)+f'<text y="{r["r"]+2.5}" text-anchor="middle" fill="#193c50" font-size="2">{r["id"]} · {labels[r["id"]]}</text></g></a>')
out.append('<text x="-137" y="94" font-size="2.3" fill="#536a78">연녹색: 체류 구획 · 짙은 선: 칸막이 · 청회색 선: 창 구간 · 가구 사각형: 실제 배치 외곽 / 기존 복도는 유지</text></svg>')
(O/'B1_interior_plan.svg').write_text(''.join(out),encoding='utf8')
for r in p['rooms']:
 rad=r['r']+1.5
 s=base+f'viewBox="{-rad} {-rad-2} {rad*2} {rad*2+4}" width="900" height="1000"><rect x="{-rad}" y="{-rad-2}" width="{rad*2}" height="{rad*2+4}" fill="#f7f8fa"/><text x="0" y="{-rad-.7}" text-anchor="middle" font-size=".6" fill="#193c50">{r["id"]} · {labels[r["id"]]}</text>'+room(r)+f'<text x="0" y="{rad+1}" text-anchor="middle" font-size=".34" fill="#536a78">반지름 {r["r"]}m · 주황: 공용 통과 경로 · 점선: 부분 천장 · 가구 위에 올리면 이름 표시</text></svg>'
 (O/(r['id']+'_plan.svg')).write_text(s,encoding='utf8')
print('Saved overview and 16 room/core SVG plans')
