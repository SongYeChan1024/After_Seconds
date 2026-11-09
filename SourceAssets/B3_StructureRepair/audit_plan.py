from pathlib import Path
import json, math, itertools,sys
from shapely.geometry import Point, LineString
from shapely.ops import unary_union
from PIL import Image,ImageDraw,ImageFont

H=Path(__file__).resolve().parent; R=H.parents[1]
O=R/'Docs/Review/2026-11-09_B3_StructureRepair';O.mkdir(parents=True,exist_ok=True)
after='--after' in sys.argv
p=json.loads((H/'layout_after.json' if after else H/'layout_before.json').read_text(encoding='utf-8'))
ts=p['tunnels']; rooms=p['rooms']; issues=[]
for y in [0,1.7,2.7,3.3]:
    voids=unary_union([Point(r['x'],r['v']).buffer(r['r'] if r['kind']=='core' else math.sqrt(r['r']**2-y*y),quad_segs=128) for r in rooms])
    # tunnel section: vertical shoulder 1.3m + semicircle radius 2.1m
    rr=2.1 if y<=1.3 else math.sqrt(max(0,2.1**2-(y-1.3)**2))
    shapes={t['id']:LineString(t.get('path',[t['p'],t['q']])).buffer(math.sqrt(max(0,2.28**2-max(0,y-1.3)**2)),cap_style=2) for t in ts}
    for a,b in itertools.combinations(ts,2):
        inter=shapes[a['id']].intersection(shapes[b['id']]).difference(voids)
        if inter.area>.025:
            issues.append(dict(a=a['id'],b=b['id'],height=y,area=round(inter.area,3),bounds=list(inter.bounds),shared=list(set([a['a'],a['b']])&set([b['a'],b['b']]))))
    for t in ts:
        for r in rooms:
            if r['id'] in [t['a'],t['b']]:continue
            intersect=shapes[t['id']].intersection(Point(r['x'],r['v']).buffer(math.sqrt(r['r']**2-y*y)))
            if intersect.area>.025:issues.append(dict(tunnel=t['id'],room=r['id'],height=y,area=round(intersect.area,3)))
print(json.dumps(issues,indent=2))
(H/('plan_audit_after.json' if after else 'plan_audit.json')).write_text(json.dumps(issues,indent=2))
im=Image.new('RGB',(1800,1150),'white');draw=ImageDraw.Draw(im);font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',18)
def pt(x,y):return (900+x*6,575+y*6)
for t in ts:
    a,b=t['p'],t['q'];draw.line([pt(*v) for v in t.get('path',[a,b])],fill='#8da3b2',width=25)
    draw.text(pt((a[0]+b[0])/2,(a[1]+b[1])/2),t['id'].split('-')[1],fill='#14324b',font=font)
for r in rooms:
    draw.ellipse([pt(r['x']-r['r'],r['v']-r['r']),pt(r['x']+r['r'],r['v']+r['r'])],fill='#e0e7ea',outline='#253746',width=2)
    draw.text(pt(r['x']-2,r['v']-1),r['id'],font=font,fill='black')
for i in issues:
    if 'bounds' not in i or i['height']!=0:continue
    a,b,c,d=i['bounds'];draw.rectangle([pt(a-1,b-1),pt(c+1,d+1)],outline='#c42828',width=3)
draw.text((30,25),'B3 - corridor structure '+('after repair' if after else 'before repair'),fill='black',font=font);im.save(O/('plan_after.png' if after else 'plan_before.png'))
