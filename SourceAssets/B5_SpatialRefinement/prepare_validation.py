from pathlib import Path
import json
H=Path(__file__).resolve().parent;R=H.parents[1];old=R/'SourceAssets/B5_RemainingDomes'
for name in ['Grid.cs','Walk.cs','Play.cs','PostPlay.cs','run_play.py','Occlusion.cs']:
 s=(old/name).read_text(encoding='utf-8').replace('B5_RemainingDomes','B5_SpatialRefinement').replace('Remaining','Spatial')
 # Occlusion previous API has its own root; retain existing volume layout for re-bake.
 (H/name).write_text(s,encoding='utf-8')
s=(old/'Capture.cs').read_text(encoding='utf-8').replace('RemainingCapture','SpatialCapture').replace('2026-11-08_B5_RemainingDomes','2026-11-08_B5_SpatialRefinement').replace('Repo+"/SourceAssets/B5_RemainingDomes/plan.json"','Repo+"/SourceAssets/B5_SpatialRefinement/plan.json"')
s=s.replace('plan["construction"].Values<string>()','((JObject)plan["rooms"]).Properties().Select(p=>p.Name).Where(n=>n!="C01")')
s=s.replace('Remaining_Domes_Art','B5_Spatial_Refinement').replace('new[]{"W01","LivingAlcove"},','')
(H/'Capture.cs').write_text(s,encoding='utf-8')
print('Verification helpers prepared')
