// Original stone and dry vegetation surface, Song Yechan, 2026-11-13.
#ifndef WD_NATURAL_SURFACE_INCLUDED
#define WD_NATURAL_SURFACE_INCLUDED
float WDHash(float2 p){float3 q=frac(float3(p.xyx)*.1031);q+=dot(q,q.yzx+33.33);return frac((q.x+q.y)*q.z);}
float WDNoise(float2 p){float2 i=floor(p),f=frac(p);f=f*f*(3-2*f);return lerp(lerp(WDHash(i),WDHash(i+float2(1,0)),f.x),lerp(WDHash(i+float2(0,1)),WDHash(i+1),f.x),f.y);}
float WDField(float2 p){return WDNoise(p)*.57+WDNoise(p*2.19+17)*.28+WDNoise(p*6.3+51)*.15;}
void AEApplyWeather(float3 ws,half3 normalWS,inout SurfaceData surface){
 float3 local=TransformWorldToObject(ws);float3 n=abs(normalize(normalWS));float2 p=n.y>.65?ws.xz:(n.x>n.z?ws.zy:ws.xy);
 float grain=WDNoise(p*87.3),large=WDField(p*.81),fineFade=1-smoothstep(.008,.07,max(length(ddx(p)),length(ddy(p))));
 if(_AE_Mode<10.5){
  float stratum=WDField(float2(p.x*.9,(ws.y+WDField(ws.xz*.65)*.23)*15));
  float seam=smoothstep(.66,.81,stratum)*(1-smoothstep(.42,.68,WDField(p*3.3)));
  float mineral=smoothstep(.67,.82,WDField(p*28.9))*fineFade;
  float dust=saturate(normalWS.y)*smoothstep(.31,.7,WDField(ws.xz*1.8));
  surface.albedo=_BaseColor.rgb*lerp(.65,1.22,large)*(1-seam*.17)*(1+(grain-.5)*.19*fineFade);
  surface.albedo=lerp(surface.albedo,_BaseColor.rgb*1.4,mineral*.25+dust*.15);
  surface.smoothness=lerp(.08,.19,large);surface.occlusion*=lerp(.8,1,large);
  float2 bump=float2(WDNoise(p*51.1)-.5,WDNoise(p.yx*49.7+13)-.5)*.42*fineFade;
  surface.normalTS=normalize(float3(surface.normalTS.xy+bump,max(.4,surface.normalTS.z)));
 }else if(_AE_Mode<11.5){
  float h=saturate(local.y/1.1);float mottling=WDNoise(ws.xz*2.7);
  surface.albedo=_BaseColor.rgb*lerp(.72,1.3,h)*lerp(.82,1.16,mottling);
  surface.emission+=_BaseColor.rgb*.055;
  surface.smoothness=.06;surface.occlusion*=lerp(.78,1,h);
 }else{
  float grainB=WDNoise(p*float2(58,1.7));surface.albedo=_BaseColor.rgb*lerp(.65,1.18,grainB)*lerp(.85,1.1,large);surface.smoothness=.07;
 }
 surface.metallic=0;
}
#endif
