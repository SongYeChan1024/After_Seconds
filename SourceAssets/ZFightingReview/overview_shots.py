"""Add review cameras in the walkable floor areas of the archived scenes."""
from pathlib import Path
import json
H=Path(__file__).parent;shots=json.loads((H/'shots.json').read_text())
poses={
 'Level_1F_Checkpoint':([-5.2,1.6,-10.2],[0,1,-5]),
 'Level_B1_Experiment':([0,1.6,-1],[1,1,5]),
 'Level_B2_Machinery':([-3.7,1.6,-26.5],[1,1,-20]),
 'Level_B2_MezzaninePreview':([17,-32.4,-7],[20,-31.5,1]),
 'Level_B3_SampleStorage':([-3.8,1.6,-4],[2,1,3]),
 'Level_B3_Stealth':([-20,1.6,-12],[-14,1,-7]),
 'Level_B4_Observation':([-2,1.6,-8],[1,1,-1]),
 'Level_B4_Stealth':([-20,1.6,-12],[-14,1,-7]),
 'Level_B5_Isolation':([0,1.882,10.5],[0,1.2,3]),
 'Level_B5_Stealth':([-11.8,1.882,1.8],[-11.8,1.2,-5.5])}
for name,(pos,target) in poses.items():
    d=json.loads((H/'results'/f'{name}.json').read_text());key=name+'_overview'
    if not any(s['name']==key for s in shots):shots.append(dict(scene=d['scene'],name=key,position=pos,target=target))
(H/'shots.json').write_text(json.dumps(shots,indent=2))
print(len(shots))
