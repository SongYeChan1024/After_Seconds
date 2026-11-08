from pathlib import Path
import json,math
H=Path(__file__).resolve().parent
f=H/'Review.cs';s=f.read_text(encoding='utf-8')
s=s.replace('results.Add(Travel(cc,player,code+"_17m_up",pts));','pts.Add(c+new Vector3(0,17,-2.38f));pts.Add(c+new Vector3(0,17,-4.0f));results.Add(Travel(cc,player,code+"_17m_up",pts));')
s=s.replace('center+Vector3.up*((string)r["kind"]=="core"?4.7f:Mathf.Min(4.8f,(float)r["r"]*.60f)),center+new Vector3(0,.4f,1.3f),105','center-dir*((float)r["r"]*.57f)+Vector3.up*((string)r["kind"]=="core"?4.7f:3.3f),center+dir*((float)r["r"]*.12f)+Vector3.up*.9f,94')
f.write_text(s,encoding='utf-8')
f=H/'Occlusion.cs';s=f.read_text(encoding='utf-8').replace('a.Contains("BO_ApproachTunnel")','a.Contains("BO_T02_ApproachShell")');f.write_text(s,encoding='utf-8')
s=(H.parent/'B4_Observation/Play.cs').read_text(encoding='utf-8').replace('B4Play','BFFPlay').replace('2026-11-08_B4_Observation','2026-11-08_B4_FullFloor').replace('testCamera.useOcclusionCulling=false','testCamera.useOcclusionCulling=true')
p=json.loads((H/'layout.json').read_text(encoding='utf-8'))
methods=[]
for code in ['C02','C04','W01','W02','W03','E01','E02','E03','N01','S01','VA','VL']:
 r=next(r for r in p['rooms'] if r['id']==code);d=r['doors'][0];length=math.hypot(d['x'],d['z']);radius=r['r']-.9
 x=r['x']+d['x']/length*radius;z=-r['v']+d['z']/length*radius;yaw=math.degrees(math.atan2(-d['x'],-d['z']))
 methods.append(f' public static object {code}()=>Start("{code}",new Vector3({x:.5f}f,-65.32f,{z:.5f}f),{yaw:.5f}f,.55f);')
s=s.replace(' static object Start(', '\n'.join(methods)+'\n static object Start(')
(H/'Play.cs').write_text(s,encoding='utf-8')
