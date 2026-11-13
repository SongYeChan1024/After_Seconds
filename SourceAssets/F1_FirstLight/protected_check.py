from pathlib import Path
import hashlib,json,os
R=Path(__file__).resolve().parents[2]
O=R/'Docs/Review/2026-11-13_1F_FirstLight'
baseline=json.loads((O.parent/'2026-11-13_1F_EnvironmentalStory/protected_before.json').read_text(encoding='utf8'))
paths=[p for p in baseline if (Path(p).suffix in ['.cs','.prefab','.controller','.overrideController','.inputactions','.unity'] or '/ProjectSettings/' in p or '/Packages/' in p or '/Assets/Settings/' in p) and not p.endswith('/Level_1F_Factory.unity')]
changed=[p for p in paths if not (R/p).is_file() or hashlib.sha256((R/p).read_bytes()).hexdigest()!=baseline[p]]
U=R/'Unity/After_Seconds_Build_V0.01'
B=Path(os.environ['LOCALAPPDATA'])/'Temp/AfterSeconds_FirstLight_20261113/before'
meta=[]
for rel in ['FS_SunsetSky.shader.meta','Materials/FS_SunsetSky.mat.meta']:
    p=U/'Assets/Afrer_Seconds/05.Model/Environment/1F'/rel
    meta.append({'path':str(p.relative_to(U)),'unchanged':p.read_bytes()==(B/p.name).read_bytes()})
before=json.loads((O/'before_lighting.json').read_text())
after=json.loads((O/'after_lighting.json').read_text())
assert before==after,'Existing lights/RenderSettings unexpectedly changed'
result={'files':len(paths),'changed':changed,'skyMeta':meta,'existingLightsAndRenderSettingsUnchanged':True}
(O/'protected_check.json').write_text(json.dumps(result,indent=2),encoding='utf8')
assert not changed and all(x['unchanged'] for x in meta)
print(json.dumps(result,indent=2))
