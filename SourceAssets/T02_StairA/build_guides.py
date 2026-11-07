"""Destination-coloured lanes on the current C01/T01/C02/T02/T05 layout. 송예찬."""
from pathlib import Path
import json,math
import numpy as np
H=Path(__file__).resolve().parent;R=H.parents[1];S=json.loads((H/'survey_guides.json').read_text(encoding='utf-8'))
origin=np.array([-22.,18.]);base=np.array([[p[0],p[2]] for p in S['centerline']]);hub=int(np.argmin(np.linalg.norm(base-origin,axis=1)));base=base[:hub+1]
def resample(points,step=.08):
 out=[np.array(points[0])]
 for a,b in zip(points,points[1:]):
  if np.linalg.norm(b-a)<1e-6:continue
  n=max(1,math.ceil(np.linalg.norm(b-a)/step));out.extend(a+(b-a)*i/n for i in range(1,n+1))
 return np.array(out)
def length(p):return np.r_[0,np.cumsum(np.linalg.norm(np.diff(p,axis=0),axis=1))]
def trim(p,start=0,end=0):
 d=length(p);lo=start;hi=d[-1]-end
 def at(t):
  k=min(len(d)-2,max(0,np.searchsorted(d,t)-1));return p[k]+(p[k+1]-p[k])*(t-d[k])/(d[k+1]-d[k])
 return np.array([at(lo)]+[v for v,t in zip(p,d) if lo<t<hi]+[at(hi)])
def offset(p,d,taper=False):
 tangent=np.vstack((p[1]-p[0],p[2:]-p[:-2],p[-1]-p[-2]));tangent/=np.linalg.norm(tangent,axis=1)[:,None];right=np.c_[tangent[:,1],-tangent[:,0]]
 factor=np.clip(length(p)/1.3,0,1) if taper else np.ones(len(p));return p+right*(d*factor[:,None])
def quad(a,c,b):return np.array([(1-t)**2*a+2*(1-t)*t*c+t*t*b for t in np.linspace(0,1,51)])
def join(*parts):
 return resample(np.vstack([p if i==0 else p[1:] for i,p in enumerate(parts)]))
door=np.array([-17.23132775,-1.074689]);axis=np.array([-.242535625,.9701425]);approach=door-axis*1.5
base=join(quad(base[0],door-axis*3.0,approach),resample([approach,origin]));west=join(resample([origin,np.array([-40.4,26.364])]),np.array([(1-t)**3*np.array([-40.4,26.364])+3*(1-t)**2*t*np.array([-41.765,26.985])+3*(1-t)*t*t*np.array([-41.9,25.45])+t**3*np.array([-43.3,25.45]) for t in np.linspace(0,1,61)]),resample([np.array([-43.3,25.45]),np.array([-44.96,25.45])]));east=resample([origin,np.array([12.8044,19.8318])])
# Round the existing bend for nested, non-crossing C01/VA lanes.
pre=trim(base,end=2);post=trim(west,start=2);main=join(pre,quad(pre[-1],origin,post[0]),post)
routes=[]
def route(id,code,pts,reverse=False):
 if reverse:pts=pts[::-1]
 routes.append(dict(id=id,code=code,width=.10,points=np.round(pts,6).tolist()))
route('C01_FromVA','C01',offset(main,-.32,True),True)
route('VA_FromC01','VA',offset(trim(main,start=1.4),0))
blue=offset(trim(base,start=1.4,end=2),.32);joinpoint=origin+np.array([.32,1.50]);ops=origin+np.array([.32,2.20])
route('C02_FromC01','C02',join(blue,quad(blue[-1],origin+np.array([.32,-.1]),joinpoint),resample([joinpoint,ops])))
violet=offset(trim(base,start=1.4,end=3),.48);eastlane=offset(trim(east,start=2),.16)
route('C04_FromC01','C04',join(violet,quad(violet[-1],origin+np.array([1.12,-.13]),eastlane[0]),eastlane))
fromwest=offset(trim(west,start=2),.32)[::-1]
route('C02_FromVA','C02',join(fromwest,quad(fromwest[-1],origin+np.array([-1.0,1.65]),joinpoint)))
fromeast=offset(trim(east,start=2),-.16)[::-1]
route('C02_FromC04','C02',join(fromeast,quad(fromeast[-1],origin+np.array([1.0,1.5]),joinpoint)))
destinations={'C01':dict(name='실험동',color='#39C8E3',sector='C',pattern='circle'),'C02':dict(name='보안관제동',color='#4F8CFF',sector='C',pattern='square'),'C04':dict(name='유틸리티동',color='#C27FFF',sector='C',pattern='diamond'),'VA':dict(name='계단 A',color='#70D692',sector='CORE',pattern='double')}
routes=[r for r in routes if r['code']!='C04' and r['id']!='C02_FromC04']
destinations={k:destinations[k] for k in ['C01','C02','VA']}
plan=dict(title='T02 계단A 연결 목적지 안내선 V0.01',author='송예찬',origin=[0,-82,0],scope='C01/T01/C02/T02/VA stair foot only; other destinations deferred',destinations=destinations,routes=routes,legend=dict(position=(-19.7,15.8),forward=(0,1),width=1.30,length=1.45))
plan['labLegend']=dict(position=(-13.8,-3.0),forward=(0,1),width=1.0,length=1.115)
plan['coreLegend']=dict(position=(-43.2,24.0),forward=(0,1),width=1.0,length=1.115)
(H/'plan.json').write_text(json.dumps(plan,ensure_ascii=False,indent=2),encoding='utf-8')
# Segment-pair distances: sampled every 8cm, then exact segment intersection / distance in verify_plan.py.
mins=[]
for i,a in enumerate(routes):
 for b in routes[i+1:]:
  if a['code']==b['code']:continue
  aa=np.array(a['points']);bb=np.array(b['points']);distance=np.sqrt(((aa[:,None,:]-bb[None,:,:])**2).sum(axis=2));ix=np.unravel_index(np.argmin(distance),distance.shape)
  mins.append(dict(a=a['id'],b=b['id'],edgeClearance=float(distance[ix])-.1,aPoint=aa[ix[0]].tolist(),bPoint=bb[ix[1]].tolist()))
(H/'spacing_draft.json').write_text(json.dumps(mins,indent=2),encoding='utf-8')
print(json.dumps({'routes':len(routes),'minApproxEdgeClearance':min(m['edgeClearance'] for m in mins),'worst':min(mins,key=lambda m:m['edgeClearance'])},ensure_ascii=True))
