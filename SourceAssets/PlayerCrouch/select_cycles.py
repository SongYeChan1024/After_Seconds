from pathlib import Path
import json, math
p=Path(__file__).parent
scans=json.loads((p/'motion_scan.json').read_text(encoding='utf-8-sig'))
results={}
for scan in scans:
    if scan['name']=='Stand':
        print('Stand heights',[(r['frame'],round(r['head'][1],3)) for r in scan['rows'][::10]])
        continue
    r=scan['rows']; candidates=[]
    for i in range(20,len(r)-35):
        for j in range(i+30,min(i+65,len(r)-8)):
            a,b=r[i],r[j]
            if min(a['head'][1],b['head'][1])<.58: continue
            feet=sum(sum((a[k][v]-b[k][v])**2 for v in range(3)) for k in ['lf','rf'])
            muscle=sum((x-y)**2 for x,y in zip(a['muscles'],b['muscles']))/len(a['muscles'])
            velocity=0
            for k in ['lf','rf']:
                for v in range(3):
                    va=r[i+1][k][v]-r[i-1][k][v]
                    vb=r[j+1][k][v]-r[j-1][k][v]
                    velocity+=(va-vb)**2
            amplitude=max(x['lf'][2] for x in r[i:j+1])-min(x['lf'][2] for x in r[i:j+1])
            amplitude+=max(x['lf'][0] for x in r[i:j+1])-min(x['lf'][0] for x in r[i:j+1])
            if amplitude<.06: continue
            score=muscle+feet*3+velocity*6+(a['hips'][1]-b['hips'][1])**2*4
            candidates.append(dict(firstFrame=int(a['frame']),lastFrame=int(b['frame']),score=round(score,6),muscle=round(muscle,5),feet=round(math.sqrt(feet),4),head=[round(a['head'][1],3),round(b['head'][1],3)],amplitude=round(amplitude,3)))
    candidates.sort(key=lambda x:x['score'])
    results[scan['name']]=candidates[0]
    print(scan['name'],json.dumps(candidates[:4]))
(p/'cycles.json').write_text(json.dumps(results,indent=2),encoding='utf-8')
