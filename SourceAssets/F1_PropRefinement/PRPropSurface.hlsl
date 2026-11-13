// Original local-space prop microstructure. Song Yechan, 2026-11-13.
#ifndef PR_PROP_SURFACE_INCLUDED
#define PR_PROP_SURFACE_INCLUDED
float PRHash(float2 p){float3 q=frac(float3(p.xyx)*.1031);q+=dot(q,q.yzx+33.33);return frac((q.x+q.y)*q.z);}
float PRNoise(float2 p){float2 i=floor(p),f=frac(p);f=f*f*(3-2*f);return lerp(lerp(PRHash(i),PRHash(i+float2(1,0)),f.x),lerp(PRHash(i+float2(0,1)),PRHash(i+1),f.x),f.y);}
void AEApplyWeather(float3 ws,half3 normalWS,inout SurfaceData s){
 float3 q=TransformWorldToObject(ws),n=abs(TransformWorldToObjectDir(normalWS));float2 p=n.x>n.y&&n.x>n.z?q.zy:(n.y>n.z?q.xz:q.xy);
 float aa=max(length(ddx(p)),length(ddy(p)));float detail=1-smoothstep(.002,.018,aa);
 float fine=PRNoise(p*173.1+_AE_Seed),patch=PRNoise(p*7.3+_AE_Seed),macro=PRNoise(p*1.7+13);
 s.albedo*=lerp(.91,1.06,macro);s.occlusion*=lerp(.93,1,patch);
 if(_AE_Mode<20.5){ // enamel: isolated chips, with dust concentrated low down
  float chip=smoothstep(.77,.9,PRNoise(p*91))*smoothstep(.45,.75,patch)*_AE_WearAmount;
  float rust=smoothstep(.68,.84,PRNoise(p*59+13))*smoothstep(.5,.76,patch)*_AE_WearAmount;
  s.albedo=lerp(s.albedo,float3(.19,.205,.19),chip*.75);s.albedo=lerp(s.albedo,float3(.19,.091,.037),rust*.55);
  float dirt=(1-smoothstep(.12,.46,q.y))*smoothstep(.3,.75,patch)*.25;s.albedo=lerp(s.albedo,float3(.15,.115,.07),dirt);
  s.smoothness*=lerp(.66,1.1,fine);s.normalTS=normalize(float3((fine-.5)*.055*detail,(PRNoise(p*187)-.5)*.055*detail,1));
 }else if(_AE_Mode<21.5){ // directional tool marks, not large rust islands
  float brushed=PRNoise(p*float2(18,680));s.albedo*=1+(brushed-.5)*.10*detail;s.smoothness*=lerp(.76,1.14,brushed);
 }else if(_AE_Mode<22.5){ // long wood fibres and cut end grain
  float board=floor(q.y/.24333),cy=(board+.5)*.24333,kz=(PRHash(float2(board,_AE_Seed))-.5)*.8;
  float knotDist=length(float2((q.z-kz)*.75,(q.y-cy)*3.4));
  float knot=1-smoothstep(.035,.17,knotDist);
  float grain=sin(q.y*450+PRNoise(q.zy*float2(1.5,22))*10+PRNoise(q.zy*8)*3+knot*6);
  float checks=pow(saturate(grain),20)*smoothstep(.36,.78,PRNoise(q.zy*float2(2,27)));
  float end=sin(length(float2(q.x*4,q.y*2))*100+PRNoise(p*14)*4);
  float f=lerp(grain,end,smoothstep(.65,.94,n.z));s.albedo*=1+(f*.12-checks*.22-knot*.11)*detail;
  s.smoothness=.12;s.metallic=0;s.normalTS=normalize(float3((fine-.5)*.14*detail,f*.10*detail,1));
 }else if(_AE_Mode<23.5){ // rubber: fine pores, hairline checking, dirty contact band
  float crack=pow(saturate(sin(p.x*230+PRNoise(p*39)*8)),24)*smoothstep(.60,.86,patch);
  s.albedo*=1+(fine-.5)*.16*detail-crack*.2*detail;
  float contact=(1-smoothstep(.045,.15,q.y))*smoothstep(.25,.75,patch);s.albedo=lerp(s.albedo,float3(.115,.095,.068),contact*.46);
  s.smoothness=.14;s.metallic=0;s.normalTS=normalize(float3((fine-.5)*.12*detail,(PRNoise(p*211)-.5)*.1*detail,1));
 }else if(_AE_Mode<24.5){ // fabric warp/weft, faded rounded edges, matte response
  float weave=(sin(p.x*2100)*sin(p.y*2000))*.5;float fade=1-smoothstep(.0005,.005,aa);
  s.albedo*=1+(fine-.5)*.12*detail+weave*.10*fade;s.smoothness=.055;s.metallic=0;
  s.normalTS=normalize(float3(sin(p.x*2100)*.12*fade,sin(p.y*2000)*.12*fade,1));
 }else {s.albedo*=1+(fine-.5)*.1*detail;s.smoothness=min(s.smoothness,.2);}
}
#endif
