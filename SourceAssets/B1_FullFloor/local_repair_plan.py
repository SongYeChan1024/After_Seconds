"""Local, reusable coplanar cleanup; excludes room-specific intersections."""
from pathlib import Path
import sys,os,json,copy
H=Path(__file__).resolve().parent;R=H.parents[1];sys.path.insert(0,str(R/'Unity/After_Seconds_Build_V0.01/Temp/ZFightingReview/deps'));sys.path.insert(0,str(R/'SourceAssets/ZFightingReview'))
os.environ['ZF_OUTPUT']='../B1_FullFloor/local_scan';os.environ['ZF_PLANS']='../B1_FullFloor/local_plans'
import analyze,repair_plan
d=json.loads((R/'Unity/After_Seconds_Build_V0.01/Temp/ZFightingReview/Level_B1_Circular.json').read_text());rows=[];seen=set()
for r in d['rows']:
 if r['mesh'] in seen or r['skinned'] or '/B1/BL_' in r['asset'] or not r['asset'].endswith('.fbx'):continue
 seen.add(r['mesh']);q=copy.deepcopy(r);q['level']=0;q['matrix']=[1,0,0,0,0,1,0,0,0,0,1,0,0,0,0,1];rows.append(q)
# Audit separately: different source meshes are not colocated in reality.
combined=dict(scene=d['scene'],rows=rows,internal=[],overlaps=[],duplicateMeshes=[],errors=[],cameras=d['cameras'])
for i,r in enumerate(rows):
 one=dict(d,rows=[r]);tmp=H/'local_scan'/'one.json';tmp.write_text(json.dumps(one));analyze.audit(tmp);found=json.loads((analyze.OUT/'one.json').read_text())
 for q in found['internal']:q['renderer']=i;combined['internal'].append(q)
 for q in found['overlaps']:q['a']=i;q['b']=i;combined['overlaps'].append(q)
 combined['duplicateMeshes'].extend(found['duplicateMeshes'])
path=H/'local_scan'/'B1_SharedMeshes.json';path.write_text(json.dumps(combined));repair_plan.plan(path)
print('GENERIC LOCAL PLAN COMPLETE',flush=True)
