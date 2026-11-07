# Executed by guides.py after routing helpers are defined.
from copy import deepcopy
base={r['id']:r for r in routes};c=base['C01_FromVA'];v=base['VA_FromC01'];ci=[i for i,p in enumerate(c['points']) if math.hypot(p[0]+22,p[1]-18)<7.3];vi=[i for i,p in enumerate(v['points']) if math.hypot(p[0]+22,p[1]-18)<7.3]
start=(np.array(c['points'][ci[0]])+np.array(v['points'][vi[-1]]))*.5;end=(np.array(c['points'][ci[-1]])+np.array(v['points'][vi[0]]))*.5
saved=grids['C02'];wide=deepcopy(saved);f=saved['flags'];n=saved['size'];wide['flags']=''.join('1' if all(0<=x+dx<n and 0<=z+dz<n and f[(z+dz)*n+x+dx]=='1' for dx,dz in [(0,0),(1,0),(-1,0),(0,1),(0,-1)]) else '0' for z in range(n) for x in range(n));grids['C02']=wide
mid=np.array(dense(path('C02',start,end,'PAIR')));grids['C02']=saved
fwd=np.zeros_like(mid);fwd[0]=mid[1]-mid[0];fwd[-1]=mid[-1]-mid[-2];fwd[1:-1]=mid[2:]-mid[:-2];fwd/=np.linalg.norm(fwd,axis=1)[:,None];side=np.c_[fwd[:,1],-fwd[:,0]]
for route,ids,offset,reverse in [(c,ci,.17,False),(v,vi,-.17,True)]:
 points=(mid+side*offset).tolist()
 if reverse:points=points[::-1]
 route['points']=dense(route['points'][:ids[0]]+points+route['points'][ids[-1]+1:]);reserve(route)
for route in [base['C02_FromC01'],base['C02_FromVA']]:
 ids=[i for i,p in enumerate(route['points']) if math.hypot(p[0]+22,p[1]-18)<7.3];a,b=ids[0],ids[-1];assert b==len(route['points'])-1;ps=path('C02',route['points'][b],route['points'][a],route['code'],True)[::-1];route['points']=dense(route['points'][:a]+ps);reserve(route)
