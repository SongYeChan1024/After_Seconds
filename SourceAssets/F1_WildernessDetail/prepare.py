from pathlib import Path
R=Path(__file__).resolve().parents[2];H=Path(__file__).resolve().parent
old=R/'SourceAssets/F1_FirstLight'
s=(old/'Inspect.cs').read_text(encoding='utf8').replace('F1FirstLight','F1Wild').replace('1F_FirstLight/','1F_WildernessDetail/')
start=s.index(' if(phase=="before")');end=s.index('\n Shot(',start)
s=s[:start]+s[end:]
s=s.replace('Shot(phase,"Sky",new Vector3(-90,1.65f,-30),new Vector3(-400,85,-40),80);','Shot(phase,"Ground",new Vector3(-93,1.6f,-35),new Vector3(-97,.45f,-37),64);Shot(phase,"MidRoute",new Vector3(-285,-.438f,-39.32f),new Vector3(-900,25,-54),74);Shot(phase,"Vista",new Vector3(-590,4.36f,-50.97f),new Vector3(-1900,45,-90),74);')
(H/'Inspect.cs').write_text(s,encoding='utf8')
s=(old/'PlayCheck.cs').read_text(encoding='utf8').replace('F1FirstLight','F1Wild').replace('1F_FirstLight/','1F_WildernessDetail/')
s=s.replace('Shot("Factory",new Vector3(-21,2.1f,-10),new Vector3(-12,.7f,2),70)','Shot("Vista",new Vector3(-590,4.36f,-50.97f),new Vector3(-1900,45,-90),74)')
s=s.replace('c.farClipPlane=8500','c.farClipPlane=Camera.main.farClipPlane')
(H/'PlayCheck.cs').write_text(s,encoding='utf8')
for name in ['Finish.cs']:
    s=(old/name).read_text(encoding='utf8').replace('F1FirstLight','F1Wild').replace('1F_FirstLight/','1F_WildernessDetail/')
    (H/name).write_text(s,encoding='utf8')
E=R/'Unity/After_Seconds_Build_V0.01/Assets/Afrer_Seconds/05.Model/Environment/1F'
s=(E/'AEWeatheredLit.shader').read_text(encoding='utf8').replace('Shader "AfterSeconds/WeatheredLit"','Shader "AfterSeconds/1F/NaturalSurface"')
# Read-derived shader name; retain standard URP passes and a separate surface callback.
s=s.replace(s.splitlines()[2],s.splitlines()[2])
import re
s=re.sub(r'Shader "[^"]+"','Shader "AfterSeconds/1F/NaturalSurface"',s,count=1)
s=s.replace('AEWeatheredForward.hlsl','WDNaturalForward.hlsl').replace('AEWeatheredGBuffer.hlsl','WDNaturalGBuffer.hlsl')
(H/'WDNaturalLit.shader').write_text(s,encoding='utf8')
for src,dst in [('AEWeatheredForward.hlsl','WDNaturalForward.hlsl'),('AEWeatheredGBuffer.hlsl','WDNaturalGBuffer.hlsl')]:
    s=(E/src).read_text(encoding='utf8').replace('AEWeathering.hlsl','WDNaturalSurface.hlsl')
    (H/dst).write_text(s,encoding='utf8')
print('Scoped wilderness tools prepared')
