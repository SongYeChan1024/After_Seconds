// Original After Seconds surface detail, Song Yechan, 2026-11-13, V0.03.
// Metre-scale material coordinates stay attached to moving models. No brick layer.
#ifndef AE_WEATHERING_INCLUDED
#define AE_WEATHERING_INCLUDED
float AEHash(float2 p){float3 q=frac(float3(p.xyx)*.1031);q+=dot(q,q.yzx+33.33);return frac((q.x+q.y)*q.z);}
float AENoise(float2 p){float2 i=floor(p),f=frac(p);f=f*f*(3-2*f);return lerp(lerp(AEHash(i),AEHash(i+float2(1,0)),f.x),lerp(AEHash(i+float2(0,1)),AEHash(i+1),f.x),f.y);}
float AEField(float2 p){return AENoise(p)*.57+AENoise(p*3.19+float2(17.3,9.7))*.28+AENoise(p*10.7+float2(71.2,34.6))*.15;}
float AEThin(float d,float radius){float aa=max(fwidth(d)*.7,.00015);return 1-smoothstep(radius-aa,radius+aa,d);}
float AECrack(float2 p){float2 cell=floor(p),f=frac(p);float first=10,second=10;[unroll]for(int y=-1;y<=1;y++)[unroll]for(int x=-1;x<=1;x++){float2 g=float2(x,y),id=cell+g;float2 jitter=float2(AEHash(id),AEHash(id+float2(73.1,22.4)));float d=length(g+jitter-f);if(d<first){second=first;first=d;}else second=min(second,d);}return AEThin(second-first,.0012);}

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
 {float2 d=ws.xz-float2(2.000000,-14.000000);float x=dot(d,float2(0.000000,1.000000));if(abs(dot(d,float2(-1.000000,0.000000)))<.19 && x>0 && x<8.712052){float below=2.800000-ws.y;float within=1-smoothstep(1.480000,1.580000,abs(frac(x/4.356026)-.5)*4.356026);float trails=smoothstep(.40,.73,AEField(float2(x*14.8,below*.55)+49));sill=max(sill,within*smoothstep(-.015,.025,below)*(1-smoothstep(.20+trails*.55,.55+trails*1.25,below))*(.10+trails*.65));}}
 {float2 d=ws.xz-float2(2.000000,-0.934274);float x=dot(d,float2(0.000000,1.000000));if(abs(dot(d,float2(-1.000000,0.000000)))<.19 && x>0 && x<14.934274){float below=2.800000-ws.y;float within=1-smoothstep(1.371784,1.471784,abs(frac(x/3.733569)-.5)*3.733569);float trails=smoothstep(.40,.73,AEField(float2(x*14.8,below*.55)+33));sill=max(sill,within*smoothstep(-.015,.025,below)*(1-smoothstep(.20+trails*.55,.55+trails*1.25,below))*(.10+trails*.65));}}
 {float2 d=ws.xz-float2(2.000000,14.000000);float x=dot(d,float2(-1.000000,0.000000));if(abs(dot(d,float2(-0.000000,-1.000000)))<.19 && x>0 && x<11.875000){float below=2.800000-ws.y;float within=1-smoothstep(1.480000,1.580000,abs(frac(x/3.958333)-.5)*3.958333);float trails=smoothstep(.40,.73,AEField(float2(x*14.8,below*.55)+17));sill=max(sill,within*smoothstep(-.015,.025,below)*(1-smoothstep(.20+trails*.55,.55+trails*1.25,below))*(.10+trails*.65));}}
 {float2 d=ws.xz-float2(-14.125000,14.000000);float x=dot(d,float2(-1.000000,0.000000));if(abs(dot(d,float2(-0.000000,-1.000000)))<.19 && x>0 && x<11.875000){float below=2.800000-ws.y;float within=1-smoothstep(1.480000,1.580000,abs(frac(x/3.958333)-.5)*3.958333);float trails=smoothstep(.40,.73,AEField(float2(x*14.8,below*.55)+3));sill=max(sill,within*smoothstep(-.015,.025,below)*(1-smoothstep(.20+trails*.55,.55+trails*1.25,below))*(.10+trails*.65));}}
 {float2 d=ws.xz-float2(-26.000000,14.000000);float x=dot(d,float2(0.000000,-1.000000));if(abs(dot(d,float2(1.000000,0.000000)))<.19 && x>0 && x<27.875000){float below=2.800000-ws.y;float within=1-smoothstep(1.480000,1.580000,abs(frac(x/3.982143)-.5)*3.982143);float trails=smoothstep(.40,.73,AEField(float2(x*14.8,below*.55)+57));sill=max(sill,within*smoothstep(-.015,.025,below)*(1-smoothstep(.20+trails*.55,.55+trails*1.25,below))*(.10+trails*.65));}}
 {float2 d=ws.xz-float2(-14.980499,-14.000000);float x=dot(d,float2(1.000000,0.000000));if(abs(dot(d,float2(-0.000000,1.000000)))<.19 && x>0 && x<16.980499){float below=2.800000-ws.y;float within=1-smoothstep(1.480000,1.580000,abs(frac(x/4.245125)-.5)*4.245125);float trails=smoothstep(.40,.73,AEField(float2(x*14.8,below*.55)+43));sill=max(sill,within*smoothstep(-.015,.025,below)*(1-smoothstep(.20+trails*.55,.55+trails*1.25,below))*(.10+trails*.65));}}
 {float2 d=ws.xz-float2(34.000000,-18.000000);float x=dot(d,float2(0.000000,1.000000));if(abs(dot(d,float2(-1.000000,0.000000)))<.19 && x>0 && x<20.000000){float below=2.400000-ws.y;float within=1-smoothstep(1.480000,1.580000,abs(frac(x/4.000000)-.5)*4.000000);float trails=smoothstep(.40,.73,AEField(float2(x*14.8,below*.55)+30));sill=max(sill,within*smoothstep(-.015,.025,below)*(1-smoothstep(.20+trails*.55,.55+trails*1.25,below))*(.10+trails*.65));}}
 {float2 d=ws.xz-float2(34.000000,2.000000);float x=dot(d,float2(-1.000000,0.000000));if(abs(dot(d,float2(-0.000000,-1.000000)))<.19 && x>0 && x<7.875000){float below=2.400000-ws.y;float within=1-smoothstep(1.473750,1.573750,abs(frac(x/3.937500)-.5)*3.937500);float trails=smoothstep(.40,.73,AEField(float2(x*14.8,below*.55)+16));sill=max(sill,within*smoothstep(-.015,.025,below)*(1-smoothstep(.20+trails*.55,.55+trails*1.25,below))*(.10+trails*.65));}}
 {float2 d=ws.xz-float2(21.875000,2.000000);float x=dot(d,float2(-1.000000,0.000000));if(abs(dot(d,float2(-0.000000,-1.000000)))<.19 && x>0 && x<7.875000){float below=2.400000-ws.y;float within=1-smoothstep(1.473750,1.573750,abs(frac(x/3.937500)-.5)*3.937500);float trails=smoothstep(.40,.73,AEField(float2(x*14.8,below*.55)+1));sill=max(sill,within*smoothstep(-.015,.025,below)*(1-smoothstep(.20+trails*.55,.55+trails*1.25,below))*(.10+trails*.65));}}
 {float2 d=ws.xz-float2(14.000000,2.000000);float x=dot(d,float2(0.000000,-1.000000));if(abs(dot(d,float2(1.000000,0.000000)))<.19 && x>0 && x<5.600941){float below=2.400000-ws.y;float within=1-smoothstep(1.480000,1.580000,abs(frac(x/5.600941)-.5)*5.600941);float trails=smoothstep(.40,.73,AEField(float2(x*14.8,below*.55)+52));sill=max(sill,within*smoothstep(-.015,.025,below)*(1-smoothstep(.20+trails*.55,.55+trails*1.25,below))*(.10+trails*.65));}}
 {float2 d=ws.xz-float2(14.000000,-7.954615);float x=dot(d,float2(0.000000,-1.000000));if(abs(dot(d,float2(1.000000,0.000000)))<.19 && x>0 && x<10.045385){float below=2.400000-ws.y;float within=1-smoothstep(1.179231,1.279231,abs(frac(x/3.348462)-.5)*3.348462);float trails=smoothstep(.40,.73,AEField(float2(x*14.8,below*.55)+35));sill=max(sill,within*smoothstep(-.015,.025,below)*(1-smoothstep(.20+trails*.55,.55+trails*1.25,below))*(.10+trails*.65));}}
 {float2 d=ws.xz-float2(14.000000,-18.000000);float x=dot(d,float2(1.000000,0.000000));if(abs(dot(d,float2(-0.000000,1.000000)))<.19 && x>0 && x<10.853606){float below=2.400000-ws.y;float within=1-smoothstep(1.313934,1.413934,abs(frac(x/3.617869)-.5)*3.617869);float trails=smoothstep(.40,.73,AEField(float2(x*14.8,below*.55)+20));sill=max(sill,within*smoothstep(-.015,.025,below)*(1-smoothstep(.20+trails*.55,.55+trails*1.25,below))*(.10+trails*.65));}}
 {float2 d=ws.xz-float2(29.300240,-18.000000);float x=dot(d,float2(1.000000,0.000000));if(abs(dot(d,float2(-0.000000,1.000000)))<.19 && x>0 && x<4.699760){float below=2.400000-ws.y;float within=1-smoothstep(1.480000,1.580000,abs(frac(x/4.699760)-.5)*4.699760);float trails=smoothstep(.40,.73,AEField(float2(x*14.8,below*.55)+6));sill=max(sill,within*smoothstep(-.015,.025,below)*(1-smoothstep(.20+trails*.55,.55+trails*1.25,below))*(.10+trails*.65));}}
 {float2 d=ws.xz-float2(-23.000000,-33.000000);float x=dot(d,float2(0.000000,1.000000));if(abs(dot(d,float2(-1.000000,0.000000)))<.19 && x>0 && x<14.000000){float below=1.250000-ws.y;float within=1-smoothstep(1.080000,1.180000,abs(frac(x/3.500000)-.5)*3.500000);float trails=smoothstep(.40,.73,AEField(float2(x*14.8,below*.55)+57));sill=max(sill,within*smoothstep(-.015,.025,below)*(1-smoothstep(.20+trails*.55,.55+trails*1.25,below))*(.10+trails*.65));}}
 {float2 d=ws.xz-float2(-23.000000,-19.000000);float x=dot(d,float2(-1.000000,0.000000));if(abs(dot(d,float2(-0.000000,-1.000000)))<.19 && x>0 && x<4.875000){float below=1.250000-ws.y;float within=1-smoothstep(1.080000,1.180000,abs(frac(x/4.875000)-.5)*4.875000);float trails=smoothstep(.40,.73,AEField(float2(x*14.8,below*.55)+44));sill=max(sill,within*smoothstep(-.015,.025,below)*(1-smoothstep(.20+trails*.55,.55+trails*1.25,below))*(.10+trails*.65));}}
 {float2 d=ws.xz-float2(-32.125000,-19.000000);float x=dot(d,float2(-1.000000,0.000000));if(abs(dot(d,float2(-0.000000,-1.000000)))<.19 && x>0 && x<4.875000){float below=1.250000-ws.y;float within=1-smoothstep(1.080000,1.180000,abs(frac(x/4.875000)-.5)*4.875000);float trails=smoothstep(.40,.73,AEField(float2(x*14.8,below*.55)+32));sill=max(sill,within*smoothstep(-.015,.025,below)*(1-smoothstep(.20+trails*.55,.55+trails*1.25,below))*(.10+trails*.65));}}
 {float2 d=ws.xz-float2(-37.000000,-19.000000);float x=dot(d,float2(0.000000,-1.000000));if(abs(dot(d,float2(1.000000,0.000000)))<.19 && x>0 && x<5.532051){float below=1.250000-ws.y;float within=1-smoothstep(0.888013,0.988013,abs(frac(x/2.766026)-.5)*2.766026);float trails=smoothstep(.40,.73,AEField(float2(x*14.8,below*.55)+20));sill=max(sill,within*smoothstep(-.015,.025,below)*(1-smoothstep(.20+trails*.55,.55+trails*1.25,below))*(.10+trails*.65));}}
 {float2 d=ws.xz-float2(-37.000000,-33.000000);float x=dot(d,float2(1.000000,0.000000));if(abs(dot(d,float2(-0.000000,1.000000)))<.19 && x>0 && x<14.000000){float below=1.250000-ws.y;float within=1-smoothstep(1.080000,1.180000,abs(frac(x/3.500000)-.5)*3.500000);float trails=smoothstep(.40,.73,AEField(float2(x*14.8,below*.55)+6));sill=max(sill,within*smoothstep(-.015,.025,below)*(1-smoothstep(.20+trails*.55,.55+trails*1.25,below))*(.10+trails*.65));}}
 {float2 d=ws.xz-float2(-5.000000,18.000000);float x=dot(d,float2(0.000000,1.000000));if(abs(dot(d,float2(-1.000000,0.000000)))<.19 && x>0 && x<14.000000){float below=1.250000-ws.y;float within=1-smoothstep(1.080000,1.180000,abs(frac(x/3.500000)-.5)*3.500000);float trails=smoothstep(.40,.73,AEField(float2(x*14.8,below*.55)+59));sill=max(sill,within*smoothstep(-.015,.025,below)*(1-smoothstep(.20+trails*.55,.55+trails*1.25,below))*(.10+trails*.65));}}
 {float2 d=ws.xz-float2(-5.000000,32.000000);float x=dot(d,float2(-1.000000,0.000000));if(abs(dot(d,float2(-0.000000,-1.000000)))<.19 && x>0 && x<14.000000){float below=1.250000-ws.y;float within=1-smoothstep(1.080000,1.180000,abs(frac(x/3.500000)-.5)*3.500000);float trails=smoothstep(.40,.73,AEField(float2(x*14.8,below*.55)+44));sill=max(sill,within*smoothstep(-.015,.025,below)*(1-smoothstep(.20+trails*.55,.55+trails*1.25,below))*(.10+trails*.65));}}
 {float2 d=ws.xz-float2(-19.000000,23.521932);float x=dot(d,float2(0.000000,-1.000000));if(abs(dot(d,float2(1.000000,0.000000)))<.19 && x>0 && x<5.521932){float below=1.250000-ws.y;float within=1-smoothstep(0.885483,0.985483,abs(frac(x/2.760966)-.5)*2.760966);float trails=smoothstep(.40,.73,AEField(float2(x*14.8,below*.55)+31));sill=max(sill,within*smoothstep(-.015,.025,below)*(1-smoothstep(.20+trails*.55,.55+trails*1.25,below))*(.10+trails*.65));}}
 {float2 d=ws.xz-float2(-19.000000,18.000000);float x=dot(d,float2(1.000000,0.000000));if(abs(dot(d,float2(-0.000000,1.000000)))<.19 && x>0 && x<4.875000){float below=1.250000-ws.y;float within=1-smoothstep(1.080000,1.180000,abs(frac(x/4.875000)-.5)*4.875000);float trails=smoothstep(.40,.73,AEField(float2(x*14.8,below*.55)+16));sill=max(sill,within*smoothstep(-.015,.025,below)*(1-smoothstep(.20+trails*.55,.55+trails*1.25,below))*(.10+trails*.65));}}
 {float2 d=ws.xz-float2(-9.875000,18.000000);float x=dot(d,float2(1.000000,0.000000));if(abs(dot(d,float2(-0.000000,1.000000)))<.19 && x>0 && x<4.875000){float below=1.250000-ws.y;float within=1-smoothstep(1.080000,1.180000,abs(frac(x/4.875000)-.5)*4.875000);float trails=smoothstep(.40,.73,AEField(float2(x*14.8,below*.55)+1));sill=max(sill,within*smoothstep(-.015,.025,below)*(1-smoothstep(.20+trails*.55,.55+trails*1.25,below))*(.10+trails*.65));}}
 dirt=max(dirt,sill*.35);corrosion=max(corrosion,sill*.9);return float2(dirt,corrosion);}

void AEApplyWeather(float3 ws,half3 normalWS,inout SurfaceData surface){
    if(_AE_Mode>6.5){AEFactoryFloor(ws,surface);return;}
    float3 scale=float3(length(GetObjectToWorldMatrix()._m00_m10_m20),length(GetObjectToWorldMatrix()._m01_m11_m21),length(GetObjectToWorldMatrix()._m02_m12_m22));
    float3 pos=TransformWorldToObject(ws)*scale;
    float3 n=abs(normalize(TransformWorldToObjectDir(normalWS)));
    float2 p=n.y>.65?pos.xz:(n.x>n.z?pos.zy:pos.xy);
    p+=dot(pos,n)*float2(.137,.173);
    float2 seed=float2(_AE_Seed*1.731,_AE_Seed*3.219);
    float wide=AEField(p*.21+seed);
    float fine=AENoise(p*87.7+seed);
    // Fade subpixel pits rather than turning fine wear into sparkling noise.
    float detailFade=1-smoothstep(.009,.05,max(length(ddx(p)),length(ddy(p))));
    float pits=smoothstep(.81,.91,AENoise(p*145.3+seed))*detailFade;
    float scr=AENoise(p*float2(115,.38)+seed+41);
    float scratches=smoothstep(.86,.94,scr)*smoothstep(.56,.7,AENoise(p*float2(2.3,21)+8))*detailFade;
    half3 basePaint=_BaseColor.rgb*lerp(.93,1.05,wide)*(1+(fine-.5)*.035*detailFade);
    if(_AE_Mode<2.5){
        float chipsField=AEField(p*(7.2*_AE_MacroScale)+seed);
        chipsField+=(AENoise(p*95+seed)-.5)*.06;
        float threshold=.79-_AE_WearAmount*.22;
        float chipped=smoothstep(threshold-.015,threshold+.015,chipsField);
        float cluster=smoothstep(.30,.65,AEField(p*.79+seed+31));
        chipped*=cluster;
        float seam=0,bolt=0,seamRust=0,rib=0,slot=0,lapHighlight=0;
        if(_AE_Mode<1.5 && n.y<.65){
            // Long sheet-metal cladding, with no staggered masonry bond.
            float vertical=abs(frac(p.x/1.20+.5)-.5)*1.20;
            float horizontal=abs(frac(p.y/3.30+.5)-.5)*3.30;
            seam=max(AEThin(vertical,.0045),AEThin(horizontal,.003));
            float boltX=abs(vertical-.027),boltY=abs(frac(p.y/.48+.5)-.5)*.48;
            float boltDist=length(float2(boltX,boltY));bolt=AEThin(boltDist,.0055);
            float rim=AEThin(boltDist,.011)*(1-bolt);
            slot=AEThin(boltX,.0012)*AEThin(boltY,.0042)*bolt*detailFade;
            lapHighlight=AEThin(abs(vertical-.0075),.0015)*detailFade;
            float panelID=AEHash(floor(p/float2(1.2,3.3))+seed);
            basePaint*=lerp(.975,1.025,panelID);
            float jointRough=smoothstep(.47,.75,AEField(p*float2(27,8)+seed));
            seamRust=max(AEThin(vertical,.015)*jointRough,rim*.75);
            float run=(1-smoothstep(.004,.095,boltY))*AEThin(boltX,.006)*smoothstep(.44,.78,AENoise(floor(p/.48)+seed));
            seamRust=max(seamRust,run*.36);
            // Fold crests are narrower than the flat pans between them.
            float wave=sin(p.x*6.283185/.15);
            rib=wave*pow(abs(wave),3)*.075;
            rib*=1-smoothstep(.015,.10,max(length(ddx(p)),length(ddy(p))));
        }
        float2 exposure=_AE_Mode<1.5?AEWallExposure(ws):float2(0,0);
        if(_AE_Mode<1.5)chipped*=saturate(.22+exposure.y*1.2+seamRust*.4);
        float rust=saturate(chipped*.85+seamRust*.7);
        float exposed=saturate(chipped*1.28-rust*.30+scratches*.12);
        float2 px=ddx(p),py=ddy(p);float determinant=px.x*py.y-px.y*py.x;
        float invDet=abs(determinant)>1e-10?1/determinant:0;
        float cx=ddx(chipped),cy=ddy(chipped);
        float2 chipSlope=clamp(float2(cx*py.y-cy*px.y,cy*px.x-cx*py.x)*invDet*.00065,-.16,.16)*detailFade;
        float chipRim=smoothstep(threshold-.035,threshold-.012,chipsField)*(1-chipped)*cluster;
        half3 steel=half3(.18,.185,.17)*lerp(.82,1.12,fine);
        half3 oxidation=lerp(half3(.045,.021,.009),half3(.15,.068,.027),AENoise(p*49+seed))*(1-pits*.25);
        half3 color=lerp(basePaint,steel,exposed*.50);
        color=lerp(color,oxidation,rust);
        float dirt=smoothstep(.62,.79,AEField(p*float2(1.7,.19)+seed+17))*.12;
        color*=1-dirt-seam*.22-pits*.16-chipRim*.09;
        color=lerp(color,half3(.21,.22,.205),bolt*.66);
        color*=1-slot*.65;
        color+=basePaint*lapHighlight*.12;
        if(_AE_Mode<1.5){color*=1-exposure.x;color=lerp(color,half3(.20,.135,.075),exposure.y*.12);}
        surface.albedo=color;
        surface.metallic=lerp(_Metallic,.035,rust);surface.metallic=lerp(surface.metallic,.63,bolt*.8+scratches*.12);
        surface.smoothness=lerp(_Smoothness,.12,rust)*(1-pits*.4);
        surface.occlusion*=1-seam*.08-pits*.025;
        surface.normalTS=normalize(surface.normalTS+half3(rib+(fine-.5)*.045*detailFade+chipSlope.x,(AENoise(p*87.7+1.7)-.5)*.035*detailFade+chipSlope.y,0));
    }else if(_AE_Mode<3.5){
        float2 warped=p+float2(AENoise(p*.47),AENoise(p*.47+41))*.55;
        float cracks=AECrack(warped*.73+seed)*smoothstep(.56,.76,AEField(p*1.3+seed));
        float grit=smoothstep(.78,.9,AENoise(p*113+seed))*detailFade;
        float grime=smoothstep(.62,.78,AEField(p*.48+seed+18));
        surface.albedo=basePaint*(1-cracks*.28-grime*.09-grit*.12);
        surface.metallic=0;surface.smoothness=.15-grit*.05;
        surface.normalTS=normalize(surface.normalTS+half3((fine-.5)*.07*detailFade,(AENoise(p*87.7+4)-.5)*.07*detailFade,0));
    }else if(_AE_Mode<4.5){
        float bending=AENoise(p*float2(.8,.35)+seed)*.09;
        float growth=sin((p.x+bending)*180+sin(p.y*.9)*2);
        float fibre=AENoise(p*float2(170,1.5)+seed);
        float worn=smoothstep(.70,.85,AEField(p*6+seed));
        surface.albedo=basePaint*(.94+growth*.04*detailFade+(fibre-.5)*.13)*lerp(1,1.18,worn);
        surface.metallic=0;surface.smoothness=.12;
        surface.normalTS=normalize(surface.normalTS+half3(growth*.025*detailFade,0,0));
    }else{
        float scuff=smoothstep(.72,.84,AEField(p*float2(9,27)+seed))*detailFade;
        surface.albedo=basePaint*(1+scuff*.18-pits*.08);
        surface.metallic=0;surface.smoothness=_AE_Mode>5.5?.08:.23;
        if(_AE_Mode>5.5){float weave=sin(p.x*1900)*sin(p.y*1900);surface.albedo*=1+weave*.035*detailFade;}
        surface.normalTS=normalize(surface.normalTS+half3((fine-.5)*.025*detailFade,(AENoise(p*87.7+1)-.5)*.025*detailFade,0));
    }
}
#endif
