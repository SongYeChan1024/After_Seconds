// Original static art sky, Song Yechan, 2026-11-13. FirstLight revision.
Shader "AfterSeconds/1F/WildernessSunset"
{
 Properties
 {
  [HDR] _Zenith("Upper violet sky",Color)=(0.045,0.05,0.135,1)
  [HDR] _Horizon("Warm horizon",Color)=(0.9,0.30,0.11,1)
  [HDR] _Opposite("Opposite rose horizon",Color)=(0.34,0.18,0.24,1)
  [HDR] _SunColor("Sun radiance",Color)=(7.5,5.2,2.8,1)
  _SunDirection("Direction toward sun",Vector)=(-0.995,0.087,-0.035,0)
  _SunRadius("Sun angular radius",Range(0.002,0.06))=0.026
  _CoronaStrength("Near sun glow",Range(0,3))=1.2
  _HaloStrength("Wide atmospheric glow",Range(0,2))=0.6
  _HaloWidth("Atmospheric glow width",Range(0.04,0.35))=0.16
  _CloudAmount("Cloud coverage",Range(0,1))=0.48
  _Exposure("Exposure",Range(0.2,2))=1
 }
 SubShader
 {
  Tags {"Queue"="Background" "RenderType"="Background" "PreviewType"="Skybox"}
  Cull Off ZWrite Off
  Pass
  {
   HLSLPROGRAM
   #pragma vertex vert
   #pragma fragment frag
   #include "UnityCG.cginc"
   struct Attributes {float4 vertex:POSITION;UNITY_VERTEX_INPUT_INSTANCE_ID};
   struct Varyings {float4 vertex:SV_POSITION;float3 direction:TEXCOORD0;UNITY_VERTEX_OUTPUT_STEREO};
   float4 _Zenith,_Horizon,_Opposite,_SunColor,_SunDirection;
   float _SunRadius,_CoronaStrength,_HaloStrength,_HaloWidth,_CloudAmount,_Exposure;
   Varyings vert(Attributes v){Varyings o;UNITY_SETUP_INSTANCE_ID(v);UNITY_INITIALIZE_VERTEX_OUTPUT_STEREO(o);o.vertex=UnityObjectToClipPos(v.vertex);o.direction=v.vertex.xyz;return o;}
   float hash3(float3 p){p=frac(p*.1031);p+=dot(p,p.yzx+33.33);return frac((p.x+p.y)*p.z);}
   float noise3(float3 p){float3 i=floor(p),f=frac(p);f=f*f*(3-2*f);return lerp(lerp(lerp(hash3(i),hash3(i+float3(1,0,0)),f.x),lerp(hash3(i+float3(0,1,0)),hash3(i+float3(1,1,0)),f.x),f.y),lerp(lerp(hash3(i+float3(0,0,1)),hash3(i+float3(1,0,1)),f.x),lerp(hash3(i+float3(0,1,1)),hash3(i+1),f.x),f.y),f.z);}
   float cloudField(float3 p){return noise3(p)*.54+noise3(p*2.07+19)*.27+noise3(p*4.19+53)*.13+noise3(p*8.3+83)*.06;}
   half4 frag(Varyings i):SV_Target
   {
    float3 d=normalize(i.direction),sun=normalize(_SunDirection.xyz);
    float elevation=saturate(d.y);float direction=saturate(dot(normalize(d.xz+float2(.00001,0)),normalize(sun.xz))*.5+.5);
    float warmth=pow(direction,3.5);float3 horizon=lerp(_Opposite.rgb,_Horizon.rgb,warmth);
    float upper=pow(saturate((elevation+.015)/.88),.56);float3 sky=lerp(horizon,_Zenith.rgb,upper);
    float haze=exp(-abs(d.y)*19);sky+=float3(.16,.10,.055)*haze*(.4+warmth*.6);
    float angularDistance=length(d-sun);
    // Layered scattering, continuous across the panorama and independent of screen position.
    float broadGlow=exp(-pow(angularDistance/max(_HaloWidth,.001),1.4));
    sky+=float3(1,.43,.16)*broadGlow*_HaloStrength;
    float3 p=d*float3(5.4,23,5.4)+float3(13.2,7.1,9.5);
    float field=cloudField(p);float threshold=lerp(.76,.45,_CloudAmount);
    float cloud=smoothstep(threshold,threshold+.19,field)*smoothstep(.025,.12,elevation)*(1-smoothstep(.52,.82,elevation));
    float edge=(1-smoothstep(threshold+.04,threshold+.17,field));
    float3 cloudShade=lerp(float3(.10,.095,.16),float3(.29,.13,.15),warmth);
    float3 copper=lerp(float3(.23,.14,.22),float3(.72,.29,.14),warmth);
    sky=lerp(sky,lerp(cloudShade,copper,edge*.7),cloud*.82);
    float aa=max(fwidth(angularDistance),.00003);
    float disk=1-smoothstep(_SunRadius-aa,_SunRadius+aa,angularDistance);
    float outside=max(angularDistance-_SunRadius,0);
    float corona=exp(-outside/max(_SunRadius*.65,.001));
    float nearGlow=exp(-outside/max(_SunRadius*2.8,.001));
    float visibility=(1-cloud*.75)*smoothstep(-.015,.005,d.y);
    sky+=(float3(1,.68,.34)*corona+float3(.32,.14,.045)*nearGlow)*_CoronaStrength*visibility;
    sky+=_SunColor.rgb*disk*visibility;
    sky=lerp(float3(.11,.065,.08),sky,smoothstep(-.12,.005,d.y));
    return half4(max(0,sky)*_Exposure,1);
   }
   ENDHLSL
  }
 }
 Fallback Off
}
