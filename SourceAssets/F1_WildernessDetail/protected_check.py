from pathlib import Path
import json,hashlib,os
R=Path(__file__).resolve().parents[2];O=R/'Docs/Review/2026-11-13_1F_WildernessDetail';U=R/'Unity/After_Seconds_Build_V0.01'
baseline=json.loads((O.parent/'2026-11-13_1F_EnvironmentalStory/protected_before.json').read_text(encoding='utf8'))
paths=[p for p in baseline if (Path(p).suffix in ['.cs','.prefab','.controller','.overrideController','.inputactions','.unity'] or '/ProjectSettings/' in p or '/Packages/' in p or '/Assets/Settings/' in p) and not p.endswith('/Level_1F_Factory.unity')]
changed=[p for p in paths if not (R/p).is_file() or hashlib.sha256((R/p).read_bytes()).hexdigest()!=baseline[p]]
B=Path(os.environ['LOCALAPPDATA'])/'Temp/AfterSeconds_WildernessDetail_20261113/before'
sky=[]
for rel in ['FS_SunsetSky.shader','FS_SunsetSky.shader.meta','Materials/FS_SunsetSky.mat','Materials/FS_SunsetSky.mat.meta']:
 p=U/'Assets/Afrer_Seconds/05.Model/Environment/1F'/rel;sky.append({'asset':p.name,'unchanged':p.read_bytes()==(B/p.name).read_bytes()})
p=U/'Assets/Afrer_Seconds/06.Data/Rendering/1F/FL_FirstLightBloom.asset';sky.append({'asset':p.name,'unchanged':p.read_bytes()==(B/p.name).read_bytes()})
before=json.loads((O/'before_lighting.json').read_text());after=json.loads((O/'after_lighting.json').read_text());lights=before==after
result={'files':len(paths),'changed':changed,'acceptedSkyAndBloom':sky,'existingLightsFogAmbientUnchanged':lights}
(O/'protected_check.json').write_text(json.dumps(result,indent=2),encoding='utf8')
assert not changed and lights and all(q['unchanged'] for q in sky)
print(json.dumps(result,indent=2))
