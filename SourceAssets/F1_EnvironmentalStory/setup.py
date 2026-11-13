from pathlib import Path
import json, shutil
H=Path(__file__).resolve().parent;R=H.parents[1];old=H.parent/'F1_DetailPass';O=R/'Docs/Review/2026-11-13_1F_EnvironmentalStory';O.mkdir(parents=True,exist_ok=True)
for name in ['mesh.py','backup.py','Walk.cs','Finish.cs','Check.cs','PlayCheck.cs']:
 s=(old/name).read_text(encoding='utf8').replace('F1_DetailPass','F1_EnvironmentalStory').replace('AfterSeconds_DetailPass','AfterSeconds_EnvironmentalStory').replace('F1Detail','F1Story')
 (H/name).write_text(s,encoding='utf8')
s=(old/'Inspect.cs').read_text(encoding='utf8').replace('F1_DetailPass','F1_EnvironmentalStory').replace('F1Detail','F1Story')
a=s.index(' Shot(phase,"Wall"');b=s.index(' return new{phase',a)
shots=[('Factory',(-21,2.1,-10),(-12,.7,2),70),('PressFloor',(-20,1.65,-1),(-15.2,.25,1.9),67),('Footprint',(-22,1.65,-10),(-18,.08,-9.8),65),('Loading',(25,1.7,-17),(23,.1,-7),72),('Wall',(-8,1.2,-15.5),(-7.5,1.2,-14.14),63),('Facade',(-15,2.4,-22),(-12,3.3,-14),72),('Ivy',(-28,1.7,-36),(-29,1.4,-33),65),('RoofDebris',(-5,1.65,-10),(-3.5,.4,-6.4),68),('OfficeDebris',(-29,1.65,-29),(-34,.2,-26),67)]
def v(q):return 'new Vector3('+','.join(str(float(x))+'f' for x in q)+')'
cmd=' Shot(phase,"Warmup",'+v(shots[0][1])+','+v(shots[0][2])+',70);\n'
cmd+='\n'.join(' Shot(phase,"'+n+'",'+v(p)+','+v(t)+','+str(f)+');' for n,p,t,f in shots)+'\n'
s=s[:a]+cmd+s[b:];(H/'Inspect.cs').write_text(s,encoding='utf8')
site=json.loads((H.parent/'F1_AbandonedCamouflage/site.json').read_text(encoding='utf8'))
print('rooms',[(q['id'],q['x'],q['z'],q.get('w'),q.get('d'),q['h']) for q in site['rooms']]);print('walls',len(site['walls']),site['walls'][:2])
