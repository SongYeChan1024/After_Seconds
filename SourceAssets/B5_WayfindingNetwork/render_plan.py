"""검토용 SVG/오프라인 HTML 도면. 게임 UI가 아니다. 작성자 송예찬."""
from pathlib import Path
import json,html,math
OUT=Path(__file__).resolve().parents[2]/'Docs/도면/Decision/원형공동/B5_안내체계'
P=json.loads((OUT/'wayfinding_plan.json').read_text(encoding='utf-8'))
validation=json.loads((OUT/'geometry_validation.json').read_text(encoding='utf-8'))
probe=json.loads((OUT/'unity_probe.json').read_text(encoding='utf-8'))
D={r['code']:r for r in P['destinations']}
esc=lambda t:html.escape(str(t))
SCALE=6.2
def point(p):return [940+p[0]*SCALE,810-p[1]*SCALE]
def pts(p):return ' '.join(f'{x:.2f},{y:.2f}' for x,y in map(point,p))
def text(x,y,value,size=19,color='#d9e5ea',weight=400,extra=''):
 return f'<text x="{x}" y="{y}" font-size="{size}" font-weight="{weight}" fill="{color}" {extra}>{esc(value)}</text>'
def card(x,y,w,h):return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="12" fill="#14232d" stroke="#2b414f"/>'

parts=['<svg id="planMap" xmlns="http://www.w3.org/2000/svg" width="2400" height="1600" viewBox="0 0 2400 1600" role="img" aria-label="B5 전체 구역과 안내선 배치안">', '<style>text{font-family:Malgun Gothic,Arial,sans-serif} .destination{cursor:pointer}.destination:hover circle{stroke:#fff;stroke-width:3}.route{pointer-events:none}.floor-label{cursor:help}</style>','<rect width="2400" height="1600" fill="#0c171e"/>']
parts += [text(80,65,'AFTER SECONDS  /  ENVIRONMENT PLANNING',19,'#8faab9',600),text(80,130,'B5 구역·목적지·전체 안내선',46,'#f0f4f5',700),text(80,174,'V0.01  ·  5개 섹터 / 15개 목적지 / 19개 복도  ·  용도별 선 유지 배치안  ·  Unity 미반영',21,'#a8bdc8')]
parts += [f'<line x1="80" y1="205" x2="2320" y2="205" stroke="#2e424d"/>']
parts += [text(86,258,'N ↑',23,'#9eb8c8',700),text(86,286,'좌표·공간 크기는 기존 B5 설계 기준',15,'#7892a1')]
for e in P['corridors']:
 a=point(e['p']);b=point(e['q'])
 parts.append(f'<line x1="{a[0]}" y1="{a[1]}" x2="{b[0]}" y2="{b[1]}" stroke="#273b47" stroke-width="{e["width"]*SCALE:.2f}"/>')
for r in P['destinations']:
 x,y=point(r['position']);radius=r['radius']*SCALE
 parts.append(f'<circle cx="{x}" cy="{y}" r="{radius}" fill="#14252f" stroke="#466171" stroke-width="2"/>')
for code,meta in P['route_codes'].items():
 parts.append(f'<g class="route route-{code}" data-route="{code}">')
 for path in P['paths']:
  if path['code']!=code:continue
  dash='stroke-dasharray="7 4"' if code=='M1' else ''
  parts.append(f'<polyline points="{pts(path["points"])}" fill="none" stroke="{meta["color"]}" stroke-width="2.4" stroke-linejoin="round" {dash}><title>{esc(path["id"])}</title></polyline>')
 parts.append('</g>')
for l in P['labels']:
 x,y=point(l['position']);f=l['forward'];rotation=-math.degrees(math.atan2(f[1],f[0]))
 parts.append(f'<g class="floor-label"><rect x="{-l["length"]*SCALE/2}" y="{-l["width"]*SCALE/2}" width="{l["length"]*SCALE}" height="{l["width"]*SCALE}" transform="translate({x} {y}) rotate({rotation})" fill="#e3e7dc" opacity=".65"/><title>{esc(l["edge"]+" · "+l["target"]+" "+l["name"]+" · "+l["kind"])}</title></g>')
for e in P['corridors']:
 a=point(e['p']);b=point(e['q']);x=(a[0]+b[0])/2;y=(a[1]+b[1])/2
 parts += [f'<rect x="{x-23}" y="{y-12}" width="46" height="24" rx="6" fill="#0c171e" opacity=".96"/>',text(x,y+5,e['code'],14,'#9eb4c2',500,'text-anchor="middle"')]
for r in P['destinations']:
 x,y=point(r['position']);radius=r['radius']*SCALE;color='#d4b27b' if r['restricted'] else '#edf4f7'
 parts += [f'<g class="destination" data-id="{r["code"]}"><title>{esc(r["code"]+" · "+r["name"])}</title>',f'<circle cx="{x}" cy="{y}" r="{radius}" fill="transparent" stroke="transparent"/>',f'<rect x="{x-25}" y="{y-14}" width="50" height="29" rx="7" fill="#0c171e" opacity=".94"/>',text(x,y+8,r['code'],22,color,700,'text-anchor="middle"'),text(x,y+radius+23,r['name'],18,color,500,'text-anchor="middle"')]
 if r['restricted']:parts.append(text(x,y+radius+46,'폐쇄 · 입구 종단 / 통과 금지',13,'#b49a78',400,'text-anchor="middle"'))
 parts.append('</g>')
right=1900
parts += [card(right,235,420,260),text(right+24,274,'노선의 용도',23,'#edf4f7',700)]
for i,(code,meta) in enumerate(P['route_codes'].items()):
 y=319+i*61
 parts += [f'<line x1="{right+25}" y1="{y-7}" x2="{right+82}" y2="{y-7}" stroke="{meta["color"]}" stroke-width="4"/>',text(right+99,y,code+'  '+meta['name'],20,meta['color'],600)]
parts.append(text(right+24,474,'노선 색은 목적지·섹터 색을 뜻하지 않음',14,'#93acba'))
y=520
for key,sector in P['sectors'].items():
 members=[r for r in P['destinations'] if r['sector']==key];height=73+len(members)*31
 parts += [card(right,y,420,height),text(right+23,y+34,'SECTOR '+key+'  /  '+sector,19,'#c7dce7',700)]
 for i,r in enumerate(members):parts.append(text(right+23,y+69+i*31,r['code']+'   '+r['name'],17,'#a6becb'))
 y+=height+14
parts += [text(right+10,y+17,'VA 계단 A · VB 계단 B · VL 화물 승강기',15,'#c5d6df'),text(right+10,y+43,'공용 이동 목적지 / 섹터와 별도 관리',14,'#8da7b6')]
parts += [f'<line x1="80" y1="1420" x2="2320" y2="1420" stroke="#2e424d"/>',text(80,1465,'선·글자 겹침 0',25,'#cfebe0',700),text(420,1465,f'서로 다른 선 가장자리 간격 ≥ {validation["minimumDifferentRouteEdgeGapM"]*100:.1f}cm',21,'#a8c0cd'),text(1120,1465,'바닥 글자 영역 76곳',21,'#a8c0cd'),text(80,1510,f'실제 씬 대조: 안내선 {probe["pathSamples"]:,}표본 + 글자 영역 {probe["labelSamples"]:,}표본 / 막힘·바닥 누락 0',19,'#a3b8c4'),text(80,1553,'설계 검토용 도면. 전체도에서는 선을 굵게 표시했으며, 실제 선 폭·간격은 JSON과 상세도 기준.  작성자 송예찬 · 2026-11-07',16,'#728f9f'),'</svg>']
svg='\n'.join(parts)
(OUT/'B5_전체안내선.svg').write_text(svg,encoding='utf-8')
(OUT/'overview_render.html').write_text('<!doctype html><meta charset="utf-8"><style>body{margin:0;background:#0c171e}svg{display:block}</style>'+svg,encoding='utf-8')

options=''.join(f'<option value="{r["code"]}">{r["code"]} · {esc(r["name"])}</option>' for r in P['destinations'])
interactive='''<!doctype html><html lang="ko"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>B5 안내선 검토 V0.01</title><style>body{margin:0;background:#0c171e;color:#dbe6ec;font:15px "Malgun Gothic",sans-serif}header{padding:16px 24px;display:flex;gap:20px;align-items:center;flex-wrap:wrap;border-bottom:1px solid #29404e}button,select{background:#1a303e;color:#e5eef3;border:1px solid #476171;padding:8px 12px;border-radius:6px}label{cursor:pointer}main{display:grid;grid-template-columns:1fr 320px;height:calc(100vh - 80px)}#view{overflow:hidden;touch-action:none}#planMap{width:100%;height:100%;user-select:none}aside{padding:22px;background:#13232e;overflow:auto}h1{font-size:20px;margin:0}h2{font-size:22px}p{line-height:1.8}.muted{color:#8eabba}.item{padding:10px 0;border-bottom:1px solid #28404e}.pill{color:#b8d4e4} @media(max-width:900px){main{display:block;height:auto}#view{height:75vh}aside{min-height:220px}}</style></head><body><header><h1>B5 안내선 검토 V0.01</h1><label><input type="checkbox" checked data-toggle="R1"> R1 직원</label><label><input type="checkbox" checked data-toggle="S1"> S1 시료</label><label><input type="checkbox" checked data-toggle="M1"> M1 정비</label><select id="dest">'''+options+'''</select><button id="focus">구역 확대</button><button id="reset">전체 보기</button></header><main><div id="view">'''+svg+'''</div><aside><h2 id="name">전체 안내 체계</h2><p class="muted">휠로 확대하고 드래그로 이동할 수 있습니다. 공간을 누르면 목적지 이름과 연결 복도를 확인할 수 있습니다.</p><div id="detail"></div><p class="muted">이 문서는 제작 검토용입니다. Unity 씬 반영·최종 도장 상태 검수는 다음 단계입니다.</p></aside></main><script>const plan='''+json.dumps(P,ensure_ascii=False)+''';const map=document.getElementById('planMap');let box=[0,0,2400,1600];function setbox(){map.setAttribute('viewBox',box.join(' '))}function select(id,zoom=false){const r=plan.destinations.find(x=>x.code===id);document.getElementById('dest').value=id;document.getElementById('name').textContent=id+' · '+r.name;const edges=plan.corridors.filter(e=>e.a===id||e.b===id);document.getElementById('detail').innerHTML='<p class="pill">'+(r.sector==='CORE'?'공용 이동 목적지':'SECTOR '+r.sector+' · '+plan.sectors[r.sector])+'</p>'+edges.map(e=>{const next=e.a===id?e.b:e.a;const target=plan.destinations.find(x=>x.code===next);return '<div class="item">'+e.code+' → '+next+' '+target.name+'<br><span class="muted">'+Object.keys(e.lanes).join(' / ')+' · 복도 '+e.length.toFixed(1)+'m</span></div>'}).join('')+(r.restricted?'<p>폐쇄 구역의 입구에서 안내선이 끝납니다. 내부를 통과하는 경로로 사용하지 않습니다.</p>':'');if(zoom){const x=940+r.position[0]*6.2,y=810-r.position[1]*6.2;box=[x-220,y-150,440,300];setbox()}}document.querySelectorAll('[data-id]').forEach(e=>e.addEventListener('click',()=>select(e.dataset.id)));document.querySelectorAll('[data-toggle]').forEach(e=>e.addEventListener('change',()=>document.querySelector('.route-'+e.dataset.toggle).style.display=e.checked?'':'none'));document.getElementById('focus').onclick=()=>select(document.getElementById('dest').value,true);document.getElementById('reset').onclick=()=>{box=[0,0,2400,1600];setbox()};document.getElementById('dest').onchange=e=>select(e.target.value);map.addEventListener('wheel',e=>{e.preventDefault();const pt=map.createSVGPoint();pt.x=e.clientX;pt.y=e.clientY;const q=pt.matrixTransform(map.getScreenCTM().inverse());const f=e.deltaY>0?1.12:.89;if(box[2]*f<70||box[2]*f>6000)return;box=[q.x+(box[0]-q.x)*f,q.y+(box[1]-q.y)*f,box[2]*f,box[3]*f];setbox()},{passive:false});let drag=null;map.addEventListener('pointerdown',e=>{drag={x:e.clientX,y:e.clientY,b:[...box],id:e.target.closest('.destination')?.dataset.id};map.setPointerCapture(e.pointerId)});map.addEventListener('pointermove',e=>{if(!drag)return;const scale=map.getScreenCTM().a;box=[drag.b[0]-(e.clientX-drag.x)/scale,drag.b[1]-(e.clientY-drag.y)/scale,drag.b[2],drag.b[3]];setbox()});map.addEventListener('pointerup',e=>{if(drag&&drag.id&&Math.hypot(e.clientX-drag.x,e.clientY-drag.y)<5)select(drag.id);drag=null});select('C01');</script></body></html>'''
(OUT/'B5_안내선_검토.html').write_text(interactive,encoding='utf-8')

# Actual-width junction close-up with the sampled walkable floor as background.
rid='C04';room=D[rid];survey=json.loads((Path(__file__).parent/'survey.json').read_text(encoding='utf-8'));grid=next(g for g in survey['rooms'] if g['id']==rid)
scale=62;center=room['position'];xy=lambda p:[700+(p[0]-center[0])*scale,630-(p[1]-center[1])*scale]
detail=['<svg xmlns="http://www.w3.org/2000/svg" width="1400" height="1200" viewBox="0 0 1400 1200"><style>text{font-family:Malgun Gothic,Arial,sans-serif}</style><rect width="1400" height="1200" fill="#0c171e"/>',text(60,65,'C04 유틸리티동 · 세 노선 분리 상세',34,'#edf5f8',700),text(60,106,'실제 선 폭 표시 / 흰 이중선 R1 · 청록 S1 · 황토 M1',19,'#a9bfcd')]
for j,row in enumerate(grid['rows']):
 for i,c in enumerate(row):
  if c=='x':continue
  q=[grid['x0']+i*grid['step'],grid['z0']+j*grid['step']];x,y=xy(q);color='#1a2b35' if c=='.' else '#514039'
  detail.append(f'<rect x="{x-grid["step"]*scale/2}" y="{y-grid["step"]*scale/2}" width="{grid["step"]*scale}" height="{grid["step"]*scale}" fill="{color}"/>')
for path in P['paths']:
 if path.get('room')!=rid:continue
 code=path['code'];meta=P['route_codes'][code];points=path['points'];coords=' '.join(f'{x},{y}' for x,y in map(xy,points));dash='stroke-dasharray="15.5 10"' if code=='M1' else ''
 detail.append(f'<polyline points="{coords}" fill="none" stroke="{meta["color"]}" stroke-width="{meta["width"]*scale}" stroke-linejoin="round" {dash}/>')
 if code=='R1':detail.append(f'<polyline points="{coords}" fill="none" stroke="#1a2b35" stroke-width="{.19*scale}" stroke-linejoin="round"/>')
for e in P['corridors']:
 if rid not in [e['a'],e['b']]:continue
 pos=e['p'] if e['a']==rid else e['q'];x,y=xy(pos);target=e['b'] if e['a']==rid else e['a'];vx=pos[0]-center[0];vz=pos[1]-center[1];length=math.hypot(vx,vz);x+=vx/length*78;y-=vz/length*78
 detail += [text(x,y,e['code']+' → '+target,20,'#edf5f8',700,'text-anchor="middle"'),text(x,y+27,D[target]['name'],17,'#9db6c5',400,'text-anchor="middle"')]
detail += [text(60,1100,'서로 다른 노선은 실제 폭과 여백을 포함해 겹침 검사.',20,'#cfe7dc'),text(60,1140,'격자: 씬에서 확인한 통행 가능 바닥. 경로의 꺾임은 후속 표면 제작 시 여백 안에서 둥글게 마감.',17,'#90a9b8'),'</svg>']
(OUT/'C04_분기상세.svg').write_text('\n'.join(detail),encoding='utf-8')
(OUT/'detail_render.html').write_text('<!doctype html><meta charset="utf-8"><style>body{margin:0;background:#0c171e}svg{display:block}</style>'+''.join(detail),encoding='utf-8')
print('SVG overview, junction detail and offline interactive HTML written.')
