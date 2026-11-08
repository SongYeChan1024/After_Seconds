from pathlib import Path
import json,math
R=Path(__file__).resolve().parents[2];H=Path(__file__).resolve().parent
O=R/'Docs/검수/2026-11-08_B5_CeilingLighting'
before=json.loads((O/'before.json').read_text(encoding='utf-8'))
src=json.loads((R/'SourceAssets/B5_CorridorOnlyGuidance/plan.json').read_text(encoding='utf-8'))
rooms=[];tunnels=[]
for code,r in src['rooms'].items():
 if r['kind']!='cavern':continue
 radius=r['r'];count=8 if radius>=9 else 4
 rooms.append(dict(code=code,center=r['position'],radius=radius,count=count,angle=10 if code=='C01' else 22.5,ring=radius*.55,intensity=9.75 if code=='C01' else radius*radius*.13,range=radius*1.65))
active=[r for r in before['renderers'] if r['active'] and r['enabled']]
for t in src['tunnels']:
 p=[t['p'][0],-82,-t['p'][1]];q=[t['q'][0],-82,-t['q'][1]]
 L=math.dist(p,q);f=[(b-a)/L for a,b in zip(p,q)]
 def along(row):return sum((v-a)*vdir for v,a,vdir in zip(row['position'],p,f))
 def domain(row):
  s=along(row);dx=row['position'][0]-p[0]-f[0]*s;dz=row['position'][2]-p[2]-f[2]*s
  return -.01<s<L+.01 and math.hypot(dx,dz)<.05
 ribs=sorted([r for r in active if r['mesh'].endswith('CFD_TunnelRib.fbx') and domain(r)],key=along)
 lamps=sorted([r for r in active if r['mesh'].endswith('CFD_SealedLight.fbx') and domain(r)],key=along)
 entry=dict(id=t['id'],p=p,q=q,length=L,forward=f,ribs=[dict(id=r['id'],s=along(r)) for r in ribs],moves=[],additions=[])
 if ribs:
  assert len(lamps)==len(ribs)
  # Door-frame ends also bound a bay: retain symmetric end lighting.
  edges=[.80]+[along(r) for r in ribs]+[L-.80]
  slots=[(a+b)/2 for a,b in zip(edges,edges[1:])]
  for i,s in enumerate(slots):
   item=dict(s=s,position=[p[0]+f[0]*s,-78.81,p[2]+f[2]*s])
   if i<len(lamps):entry['moves'].append(dict(**item,id=lamps[i]['id'],path=lamps[i]['path']))
   else:entry['additions'].append(dict(**item,cloneId=lamps[-1]['id']))
 else:
  lights=[l for l in before['lights'] if l['active'] and l['enabled'] and l['path'].split('/')[-1].startswith(t['id']+'_')]
  assert lights,t['id']
  for l in lights:
   entry['additions'].append(dict(position=[l['position'][0],-78.81,l['position'][2]],existingLight=l['id'],s=along(l)))
 tunnels.append(entry)
plan=dict(author='송예찬',rooms=rooms,tunnels=tunnels)
(H/'plan.json').write_text(json.dumps(plan,ensure_ascii=False,indent=2),encoding='utf-8')
print('Domes',len(rooms),'ceiling fixtures',sum(r['count'] for r in rooms),'corridor moves',sum(len(t['moves']) for t in tunnels),'added fixtures',sum(len(t['additions']) for t in tunnels))
# Record the design decision before applying scene edits.
doc=R/'Docs/AfterSeconds_메인기획서.md'
s=doc.read_text(encoding='utf-8')
s=s.replace('메인 기획서 V0.47','메인 기획서 V0.48',1)
note='2026-11-08 조명 보강 요청: 일반 돔12곳의 곡면 천장에 실제 등기구와 연결된 광원을 대칭 배치해 공간을 더 밝게 한다. 기존 작업등·사용자 광원 설정은 보존한다. 터널의 등기구는 리브 사이 중앙과 양 끝 문틀–리브 사이에 배치하고, 광원만 있던 구간에는 등기구 외형을 보완한다. 이동 안내선은 복도 전용 유지. 조명 배치/보강 범위이며 전체 색감의 최종 확정은 외형 검수 후다. 작성자 송예찬.'
s=s.replace('\n\n','\n\n'+note+'\n\n',1)
s+='\n- V0.48 (2026-11-08): 사용자 요청에 따른 돔 천장등 보강과 터널 리브 사이 조명 배치 기준. 기존 작업등과 복도 전용 안내선 보존. 송예찬.\n'
doc.write_text(s,encoding='utf-8')
