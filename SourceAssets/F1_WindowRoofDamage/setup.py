from pathlib import Path
import os,shutil,json,hashlib
R=Path(__file__).resolve().parents[2];H=Path(__file__).resolve().parent
out=R/'Docs/Review/2026-11-13_1F_WindowRoofDamage';out.mkdir(parents=True,exist_ok=True)
tmp=Path(os.environ['LOCALAPPDATA'])/'Temp/AfterSeconds_WindowRoofDamage_20261113';(tmp/'before').mkdir(parents=True,exist_ok=True);(tmp/'candidate').mkdir(exist_ok=True)
E=R/'Unity/After_Seconds_Build_V0.01/Assets/Afrer_Seconds/05.Model/Environment/1F'
names=['AE_'+k+'_Walls.fbx' for k in ['C01','C02','C03','C04','VA','VB','VL']+['T%02d'%i for i in range(1,8)]]+['AE_'+k+'_Roof.fbx' for k in ['C01','C02','C03','C04']+['T%02d'%i for i in range(1,8)]]
manifest=[]
for n in names:
 for suffix in ['', '.meta']:
  p=E/(n+suffix);dest=tmp/'before'/p.name
  if not dest.exists():shutil.copy2(p,dest)
  manifest.append(dict(path=str(p.relative_to(R)),sha256=hashlib.sha256(dest.read_bytes()).hexdigest()))
scene=R/'Unity/After_Seconds_Build_V0.01/Assets/Afrer_Seconds/01.Scenes/Stage/Level_1F_Factory.unity'
if not (tmp/'before'/scene.name).exists():shutil.copy2(scene,tmp/'before'/scene.name)
(out/'backup.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')
old=(R/'SourceAssets/F1_SurfaceDetail/Review.cs').read_text(encoding='utf-8').replace('F1SurfaceReview','F1WindowRoofReview').replace('2026-11-13_1F_SurfaceDetail','2026-11-13_1F_WindowRoofDamage')
old=old.replace('static object Close(string phase){','static object Close(string phase){')
start=old.index(' static object Close(string phase)');end=old.index(' public static object Extra()',start)
old=old[:start]+''' static object Close(string phase){Directory.CreateDirectory(Out+phase);
 Shot(phase,"Metal_Close",new Vector3(-1.3f,8.6f,-5),new Vector3(-2,10.5f,-5),72);
 Shot(phase,"Metal_Top",new Vector3(4,15,-17),new Vector3(-3,9.8f,-5),70);
 Shot(phase,"Concrete_Close",new Vector3(-34.3f,2.5f,-23.9f),new Vector3(-34.5f,3.9f,-24.2f),84);
 Shot(phase,"Concrete_Top",new Vector3(-35,7,-22),new Vector3(-33,3.9f,-24),70);
 Shot(phase,"Window_Front",new Vector3(-15,2.4f,-22),new Vector3(-12,4.5f,-14),72);
 Shot(phase,"Window_C03",new Vector3(-38,2,-37),new Vector3(-30,2,-33),70);
 return new{phase,closeViews=6};}
''' +old[end:]
(H/'Review.cs').write_text(old,encoding='utf-8')
print('Backup and review ready',len(names))
