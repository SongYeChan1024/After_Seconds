"""Fitted service cable/terminal details for the two existing C01 observation consoles."""
from pathlib import Path
import math,json
H=Path(__file__).resolve().parent;R=H.parents[1]
library=R/'SourceAssets/B5_Sector01/build_details.py'
env={'__file__':str(library),'__name__':'connection_helpers'}
exec(compile(library.read_text('utf-8').split('# Structural ribs')[0],str(library),'exec'),env)
env['H']=H;env['reset']();mesh=env['mesh'];tube=env['tube'];cyl=env['cyl']
def obox(name,c,radial,width,height,depth,mat='Steel',bevel=.004):
    x,y,z=c;rx,rz=radial;tx,tz=-rz,rx
    v=[(x+tx*u*width/2+rx*w*depth/2,y+h*height/2,z+tz*u*width/2+rz*w*depth/2) for u,h,w in [(-1,-1,-1),(1,-1,-1),(1,-1,1),(-1,-1,1),(-1,1,-1),(1,1,-1),(1,1,1),(-1,1,1)]]
    return mesh(name,v,[(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)],mat,bevel)
for label,deg,console in [('A',135,(-5.4,5.1)),('B',315,(5.4,-4.9))]:
    a=math.radians(deg);rx,rz=math.cos(a),math.sin(a);tx,tz=-rz,rx
    def p(r,y,t=0):return (rx*r+tx*t,y,rz*r+tz*t)
    obox('Terminal_'+label,p(9.77,1.25),(rx,rz),.34,.46,.16,'Coat',.008)
    obox('Terminal_Face_'+label,p(9.684,1.25),(rx,rz),.29,.40,.016,'Dark',.003)
    for h in [1.08,1.42]:
        for t in [-.12,.12]:cyl('Terminal_Fastener_'+label,p(9.673,h,t),p(9.66,h,t),.012,'Steel',6)
    for j in [-1,0,1]:
        t=j*.065
        start=(console[0]+rx*.57+tx*t,.42,console[1]+rz*.57+tz*t)
        points=[start,(start[0]+rx*.05,.22,start[2]+rz*.05),(start[0]+rx*.20,.075,start[2]+rz*.20),p(8.8,.075,t),p(9.62,.075,t),p(9.67,.16,t),p(9.67,.98,t),p(9.67,1.10,t)]
        tube('Console_'+label+'_ServiceCable',points,.013 if j else .019,'Dark',8)
        cyl('Socket_'+label,p(9.675,1.10,t),p(9.645,1.10,t),.027,'Steel',12)
    obox('Wall_Cable_Guard_'+label,p(9.70,.57),(rx,rz),.28,.77,.075,'Steel',.005)
    for h in [.22,.84]:obox('Guard_Strap_'+label,p(9.65,h),(rx,rz),.30,.035,.025,'Dark',.003)
env['export']('AF_C01_ConsoleConnections',collide=False)
(H/'connections_geometry.json').write_text(json.dumps(env['manifest'],indent=2),encoding='utf-8')
