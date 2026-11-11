from pathlib import Path
import os,sys,json
H=Path(__file__).resolve().parent;R=H.parents[1]
sys.path[:0]=[str(R/'Unity/After_Seconds_Build_V0.01/Temp/ZFightingReview/deps'),str(R/'SourceAssets/ZFightingReview')]
os.environ['ZF_OUTPUT']='../B1_StaffDataRevision/geometry_scan';os.environ['ZF_PLANS']='../B1_StaffDataRevision/geometry_verified'
import analyze,repair_plan
p=R/'Unity/After_Seconds_Build_V0.01/Temp/ZFightingReview'/('Level_B1_Circular_C05.json' if len(sys.argv)>1 and sys.argv[1]=='C05' else 'Level_B1_Circular.json')
analyze.audit(p);repair_plan.plan(analyze.OUT/p.name)
j=json.loads((repair_plan.PLAN/p.name).read_text());assert not j['patches'], 'New coplanar geometry overlaps'
