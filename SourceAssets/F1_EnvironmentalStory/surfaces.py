"""Location-aware marks on existing opaque surfaces; no floating decal planes."""
from pathlib import Path
import json,math
H=Path(__file__).resolve().parent;site=json.loads((H.parent/'F1_AbandonedCamouflage/site.json').read_text(encoding='utf8'))
s=(H.parent/'F1_DetailPass/AEWeathering.hlsl').read_text(encoding='utf8')
extra=r'''
float AEBlob(float2 p,float2 center,float2 radius){float d=length((p-center)/radius);return 1-smoothstep(.52,1.04,d+(AEField(p*6.3)-.5)*.35);}
float AEBoxMask(float2 p,float2 c,float2 r,float blur){float2 d=abs(p-c)-r;return 1-smoothstep(-blur,blur,max(d.x,d.y));}
void AEFactoryFloor(float3 ws,inout SurfaceData s){
 float2 p=ws.xz;float grain=AENoise(p*103);float cloud=AEField(p*.39);float aa=max(length(ddx(p)),length(ddy(p)));float fade=1-smoothstep(.01,.06,aa);
 float2 cell=abs(frac((p+float2(1.2,2.7))/4.8+.5)-.5)*4.8;
 float joints=AEThin(min(cell.x,cell.y),.0045);float wornJoint=AEThin(min(cell.x,cell.y),.018)*(1-joints)*smoothstep(.4,.7,AEField(p*4));
 float cracks=AECrack((p+float2(AENoise(p*.5),AENoise(p*.5+20))*.8)*.48)*smoothstep(.53,.72,AEField(p*.8+16));
 float oil=0,dust=0,scuff=0,imprint=0,edge=0;
 if(p.x>-26 && p.x<2 && p.y>-14 && p.y<14){
  oil=max(AEBlob(p,float2(-17.7,.65),float2(1.05,.72)),AEBlob(p,float2(-15.3,.55),float2(.63,.42))*.7);
  oil=max(oil,AEBlob(p,float2(-11.3,1.22),float2(.72,.46))*.8);oil=max(oil,AEBlob(p,float2(-8.8,-9),float2(1.1,.62))*.55);
  imprint=AEBoxMask(p,float2(-18.5,-10),float2(1.25,.88),.05);float outer=AEBoxMask(p,float2(-18.5,-10),float2(1.43,1.06),.15);edge=max(0,outer-imprint)*lerp(.25,.8,AEField(p*13));
  float drag=abs(p.x+18.5+sin(p.y*.27)*.10);scuff=(1-smoothstep(.035,.10,abs(drag-.95)))*(1-smoothstep(-6.5,-5.8,p.y))*smoothstep(-10.1,-9.3,p.y)*AEField(p*float2(45,1.6));
  dust=max(AEBlob(p,float2(-3.8,-6.4),float2(2.9,2.5)),AEBlob(p,float2(-19.55,-1.12),float2(1.5,1.7))*.65)*.43;
  float wall=min(min(p.x+26,2-p.x),min(p.y+14,14-p.y));dust=max(dust,(1-smoothstep(.12,1.1,wall))*(.25+cloud*.28));
 }else if(p.x>14 && p.x<34 && p.y>-18 && p.y<2){
  float track=abs(p.x-(25.2+sin((p.y+12)*.16)*1.65));scuff=(1-smoothstep(.06,.20,abs(track-.72)))*smoothstep(-17.4,-15.9,p.y)*(1-smoothstep(-3,-1,p.y))*lerp(.2,.7,AEField(p*float2(26,3)));
  oil=AEBlob(p,float2(30,-15),float2(.8,.7))*.48;
  imprint=AEBoxMask(p,float2(31,-9.4),float2(.86,1.1),.025);edge=max(0,AEBoxMask(p,float2(31,-9.4),float2(1.0,1.24),.1)-imprint)*.50;
  float wall=min(min(p.x-14,34-p.x),min(p.y+18,2-p.y));dust=(1-smoothstep(.08,.9,wall))*(.21+cloud*.30);dust=max(dust,AEBlob(p,float2(29.6,-12.6),float2(1.9,1.2))*.25);
 }else if(p.x>-37&&p.x<-23&&p.y>-33&&p.y<-19){dust=max(AEBlob(p,float2(-34.48,-24.46),float2(2.1,1.8)),AEBlob(p,float2(-28.32,-27.68),float2(1.7,1.9)))*.4;
 }else if(p.x>-19&&p.x<-5&&p.y>18&&p.y<32){dust=max(AEBlob(p,float2(-16.48,26.54),float2(1.7,1.8)),AEBlob(p,float2(-10.32,23.32),float2(1.6,1.4)))*.35;}
 float abrasion=smoothstep(.55,.8,AEField(p*float2(14,.8)))*fade;
 half3 base=_BaseColor.rgb*lerp(.85,1.10,cloud)*(1+(grain-.5)*.06*fade);
 base*=1-joints*.45-wornJoint*.14-cracks*.24-scuff*.36-edge*.36;
 base=lerp(base,_BaseColor.rgb*1.14,imprint*(.35+AEField(p*19)*.35));base=lerp(base,half3(.31,.29,.235),dust);
 base=lerp(base,half3(.065,.061,.049)*lerp(.9,1.25,grain),oil*lerp(.50,.88,AEField(p*9)));
 s.albedo=base;s.metallic=0;s.smoothness=lerp(.14,.25,oil*.65)*(1-dust*.5);s.occlusion*=1-joints*.1;
 s.normalTS=normalize(s.normalTS+half3((grain-.5)*.065*fade,(AENoise(p*103+7)-.5)*.065*fade,0));
}
float2 AEWallExposure(float3 ws){
 float horiz=ws.x+ws.z*1.137;float dampHeight=.15+AEField(ws.xz*.9)*.65;
 float baseDamp=1-smoothstep(.06,dampHeight,ws.y);float grit=AEField(float2(horiz*8,ws.y*2));
 float dirt=baseDamp*lerp(.22,.43,grit);float corrosion=baseDamp*.68;float sill=0;
'''
for q in site['walls']:
 if not q['room'].startswith('C'):continue
 a,b=q['a'],q['b'];length=math.dist(a,b)
 if not q['window'] or length<=2.8:continue
 h={'C01':9,'C02':7.3}.get(q['room'],q['h'])
 if h>6:sy=2.8 if h>8 else 2.4;ww=3.1;spacing=4
 else:sy=1.25;ww=2.3;spacing=3.5
 count=max(1,round(length/spacing));cell=length/count;ww=min(ww,cell-.85);dx,dz=(b[0]-a[0])/length,(b[1]-a[1])/length
 extra+=f' {{float2 d=ws.xz-float2({a[0]:.6f},{a[1]:.6f});float x=dot(d,float2({dx:.6f},{dz:.6f}));if(abs(dot(d,float2({-dz:.6f},{dx:.6f})))<.19 && x>0 && x<{length:.6f}){{float below={sy:.6f}-ws.y;float within=1-smoothstep({ww/2-.07:.6f},{ww/2+.03:.6f},abs(frac(x/{cell:.6f})-.5)*{cell:.6f});float trails=smoothstep(.40,.73,AEField(float2(x*14.8,below*.55)+{len(extra)%67}));sill=max(sill,within*smoothstep(-.015,.025,below)*(1-smoothstep(.20+trails*.55,.55+trails*1.25,below))*(.10+trails*.65));}}}}\n'
extra+=' dirt=max(dirt,sill*.35);corrosion=max(corrosion,sill*.9);return float2(dirt,corrosion);}\n'
s=s.replace('void AEApplyWeather',extra+'\nvoid AEApplyWeather',1).replace('    float3 scale=', '    if(_AE_Mode>6.5){AEFactoryFloor(ws,surface);return;}\n    float3 scale=',1)
s=s.replace('        float rust=saturate(chipped*.85+seamRust*.7);','        float2 exposure=_AE_Mode<1.5?AEWallExposure(ws):float2(0,0);\n        if(_AE_Mode<1.5)chipped*=saturate(.22+exposure.y*1.2+seamRust*.4);\n        float rust=saturate(chipped*.85+seamRust*.7);')
s=s.replace('        surface.albedo=color;','        if(_AE_Mode<1.5){color*=1-exposure.x;color=lerp(color,half3(.20,.135,.075),exposure.y*.12);}\n        surface.albedo=color;')
s=s.replace('V0.02.','V0.03.');(H/'AEWeathering.hlsl').write_text(s,encoding='utf8');print('SURFACES_READY',len(s))
