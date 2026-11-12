from pathlib import Path
import os,sys,json
H=Path(__file__).resolve().parent;R=H.parents[1]
sys.path[:0]=[str(R/'Unity/After_Seconds_Build_V0.01/Temp/ZFightingReview/deps'),str(R/'SourceAssets/ZFightingReview')]
os.environ['ZF_OUTPUT']='../F1_FullFloor/geometry_scan';os.environ['ZF_PLANS']='../F1_FullFloor/geometry_verified'
import analyze,repair_plan
source=R/'Unity/After_Seconds_Build_V0.01/Temp/ZFightingReview/Level_1F_Factory.json'
analyze.audit(source);repair_plan.plan(analyze.OUT/source.name)
j=json.loads((repair_plan.PLAN/source.name).read_text());d=json.loads((analyze.OUT/source.name).read_text())
result={'scope':'All 1F active mesh renderers; opaque planar faces >=0.005m2, exact 0.05mm plane tolerance; mutually exclusive LODs separated','patches':len(j['patches']),'scanKeys':list(d),'duplicateMeshes':len(d['duplicateMeshes']),'internalCandidates':len(d['internal']),'coplanarCandidates':len(d['overlaps']),'exact':{k:v for k,v in j.items() if k not in ['patches','rows']}}
(R/'Docs/Review/2026-11-12_1F_FullFloor/geometry.json').write_text(json.dumps(result,indent=2),encoding='utf8')
print(json.dumps(result,default=str),flush=True)
assert not j['patches'],'Exact geometry overlaps remain'
