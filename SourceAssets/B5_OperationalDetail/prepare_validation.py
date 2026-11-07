from pathlib import Path
H=Path(__file__).resolve().parent;R=H.parents[1];old=R/'SourceAssets/B5_SpatialRefinement'
for fn in ['Audit.cs','Verify.cs','Play.cs','PostPlay.cs','run_play.py','walk_plan.py','guides.py','paired_guides.py']:
 if (H/fn).exists():continue
 s=(old/fn).read_text(encoding='utf-8').replace('B5_SpatialRefinement','B5_OperationalDetail')
 if fn in ['Audit.cs']:s=s.replace('B5_Spatial_Refinement','B5_Operational_Detail')
 s=s.replace('SpatialAudit','OperationalAudit').replace('SpatialVerify','OperationalVerify').replace('SpatialPlay','OperationalPlay').replace('SpatialPostPlay','OperationalPostPlay').replace('Spatial_Play','Operational_Play')
 (H/fn).write_text(s,encoding='utf-8')
if not (H/'guidance.json').exists():(H/'guidance.json').write_text((old/'guidance.json').read_text(encoding='utf-8'),encoding='utf-8')
s=(old/'Capture.cs').read_text(encoding='utf-8').replace('SpatialCapture','OperationalCapture').replace('B5_SpatialRefinement','B5_OperationalDetail')
s=s.replace('.Where(n=>n!="C01")','.Where(n=>new[]{"E01","E02","E03","S01","C04","VL"}.Contains(n))')
if not (H/'Capture.cs').exists():(H/'Capture.cs').write_text(s,encoding='utf-8')
print('Validation scripts ready; no game scripts added')
