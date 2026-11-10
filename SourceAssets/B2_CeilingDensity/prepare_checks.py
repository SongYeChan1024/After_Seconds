from pathlib import Path
import re
H=Path(__file__).resolve().parent;R=H.parents[1]
s=(R/'SourceAssets/B2_SurfaceRefinement/Play.cs').read_text(encoding='utf8').replace('BRPlay','CDPlay').replace('B2_SurfaceRefinement','B2_CeilingDensity').replace('stages=6','stages=8').replace('stage<6','stage<8')
start=s.index('static void Next()');end=s.index('var r=plan["rooms"]',start)
s=s[:start]+'''static void Next(){string room;Vector3[] local;crouch=false;
if(stage<6){room=new[]{"C02","C01","W02","S01","E03","N01"}[stage];label=room+" resized equipment aisle";
var routes=new[]{
 new[]{new Vector3(0,0,-7),new Vector3(0,0,3.9f)},
 new[]{new Vector3(0,0,-6),new Vector3(0,0,3.6f)},
 new[]{new Vector3(.5f,0,-4.6f),new Vector3(.5f,0,3.1f)},
 new[]{new Vector3(0,0,-4.5f),new Vector3(0,0,2.5f)},
 new[]{new Vector3(-5.4f,0,0),new Vector3(1.5f,0,0),new Vector3(1.5f,0,3.3f)},
 new[]{new Vector3(0,0,-4),new Vector3(0,0,4.2f)}};local=routes[stage];
}else{label=new[]{"C02_Stair_0","E01_Stair_1"}[stage-6];var route=plan["routes"].Single(r=>(string)r["name"]==label);room=(string)route["room"];local=route["points"].Select(p=>new Vector3((float)p[0],(float)p[1],(float)p[2])).ToArray();crouch=(float)route["height"]<1.5f;}
'''+s[end:]
(H/'Play.cs').write_text(s,encoding='utf8')
one=s.replace('CDPlay','CDGenerator').replace('stages=8','stages=1').replace('stage<8','stage<1').replace('play.json','play_generator.json')
start=one.index('static void Next()');end=one.index('var r=plan["rooms"]',start)
one=one[:start]+'''static void Next(){string room="W02";label="W02 west generator and fuel service aisle";crouch=false;Vector3[] local=new[]{new Vector3(-5.35f,0,-3.9f),new Vector3(-5.35f,0,3.8f)};'''+one[end:]
(H/'PlayGenerator.cs').write_text(one,encoding='utf8')
s=(H/'Verify.cs').read_text(encoding='utf8')
s=s.replace('Directory.GetFiles("Assets/Afrer_Seconds/05.Model/Props/B2","BR_*.fbx")','Directory.GetFiles("Assets/Afrer_Seconds/05.Model/Environment/B2","CD_*.fbx")')
(H/'Verify.cs').write_text(s,encoding='utf8')
print('8 Play routes, CD mesh validation ready')
