from pathlib import Path
import os,json,hashlib
H=Path(__file__).resolve().parent;R=H.parents[1];U=R/'Unity/After_Seconds_Build_V0.01';O=R/'Docs/Review/2026-11-13_1F_PropRefinement'
# Fix capture fallback for the reused, single-mesh tool trolley. Baseline data remains intact.
p=H/'Inspect.cs';s=p.read_text(encoding='utf8')
s=s.replace('public static object After()=>Run("after");','public static object After()=>Run("after");public static object ResumeBefore()=>Run("resume");')
s=s.replace('Directory.CreateDirectory(Out+phase);','bool resume=phase=="resume";if(resume)phase="before";Directory.CreateDirectory(Out+phase);')
s=s.replace('if(phase=="before"){','if(phase=="before"&&!resume){')
s=s.replace('File.WriteAllText(Out+phase+"_transforms.json"','if(!resume)File.WriteAllText(Out+phase+"_transforms.json"').replace('File.WriteAllText(Out+phase+"_inventory.json"','if(!resume)File.WriteAllText(Out+phase+"_inventory.json"')
s=s.replace('var b=rr[0].bounds;','if(rr.Length==0)rr=t.GetComponentsInChildren<Renderer>().Where(r=>!r.name.StartsWith("FD_")).ToArray();var b=rr[0].bounds;')
p.write_text(s,encoding='utf8')
if not (O/'protected_before.json').exists():
 files={}
 for base in ['Assets','ProjectSettings','Packages']:
  for p in (U/base).rglob('*'):
   if p.is_file():files[p.relative_to(R).as_posix()]=hashlib.sha256(p.read_bytes()).hexdigest()
 (O/'protected_before.json').write_text(json.dumps(files,indent=2),encoding='utf8');print('PROTECTED',len(files))
for old,new in [('WDNaturalLit.shader','PRPropLit.shader'),('WDNaturalForward.hlsl','PRPropForward.hlsl'),('WDNaturalGBuffer.hlsl','PRPropGBuffer.hlsl')]:
 s=(H.parent/'F1_WildernessDetail'/old).read_text(encoding='utf8').replace('AfterSeconds/1F/NaturalSurface','AfterSeconds/1F/PropSurface').replace('WDNatural','PRProp')
 s=s.replace('#include "AEWeatheredInput.hlsl"','#include "../../Environment/1F/AEWeatheredInput.hlsl"')
 (H/new).write_text(s,encoding='utf8')
for old,new,cls in [('Walk.cs','Walk.cs','F1DetailWalk'),('PlayCheck.cs','PlayCheck.cs','F1WildPlayCheck'),('Finish.cs','Finish.cs','F1WildFinish')]:
 src=H.parent/('F1_DetailPass' if old=='Walk.cs' else 'F1_WildernessDetail')/old
 s=src.read_text(encoding='utf8').replace(cls,'PR'+cls.replace('F1Detail','').replace('F1Wild','')).replace('2026-11-13_1F_DetailPass','2026-11-13_1F_PropRefinement').replace('2026-11-13_1F_WildernessDetail','2026-11-13_1F_PropRefinement')
 if old=='PlayCheck.cs':
  s=s.replace('Shot("Wilderness",new Vector3(-82,1.65f,-29.1f),new Vector3(-550,25,-46),74)','Prop("CableReel")').replace('Shot("Exit",new Vector3(-51,1.65f,-28),new Vector3(-230,10,-34),76)','Prop("Forklift")').replace('Shot("Vista",new Vector3(-590,4.36f,-50.97f),new Vector3(-1900,45,-90),74)','Prop("Press")')
  s=s.replace('using System;','using System;using System.Linq;')
  s=s.replace(' static void Shot(', ' static void Prop(string kind){var t=UnityEngine.Object.FindObjectsByType<Transform>(FindObjectsSortMode.None).First(x=>x.name.StartsWith("F1_")&&x.name.Contains("_"+kind+"_"));var r=t.GetComponentsInChildren<Renderer>().First(x=>x.name=="PR_"+kind+"_LOD0");float d=Mathf.Max(r.bounds.size.x,r.bounds.size.y,r.bounds.size.z);Shot(kind,r.bounds.center+t.TransformDirection(new Vector3(-.72f,.37f,1.05f))*Mathf.Clamp(d*1.18f,.85f,5.5f),r.bounds.center,53);}\n static void Shot(')
 (H/new).write_text(s,encoding='utf8')
print('Prepared source and verification helpers')
