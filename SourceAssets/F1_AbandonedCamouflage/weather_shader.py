"""Preserve URP17.4 lighting/shadow passes and SRP CBUFFER; add continuous macro wear to Forward/GBuffer."""
from pathlib import Path
import sys,shutil,json
H=Path(__file__).resolve().parent;R=H.parents[1];U=R/'Unity/After_Seconds_Build_V0.01';E=U/'Assets/Afrer_Seconds/05.Model/Environment/1F';P=next((U/'Library/PackageCache').glob('com.unity.render-pipelines.universal@*'))
header='// Derived from Unity URP 17.4.0 Lit, copyright Unity Technologies ApS.\n// Unity Companion License. Local adaptations by Song Yechan, 2026-11-12.\n'
s=(P/'Shaders/Lit.shader').read_text(encoding='utf8').replace('Shader "Universal Render Pipeline/Lit"','Shader "AfterSeconds/1F/ContinuousWeatheredLit"')
s=s.replace('// Specular vs Metallic workflow','_AE_Mode("Weather: Plaster 1, Steel 2, Concrete 3", Float) = 1\n        _AE_MacroScale("World wear frequency", Float) = 0.28\n        // Specular vs Metallic workflow')
for a,b in [('LitInput.hlsl','AEWeatheredInput.hlsl'),('LitForwardPass.hlsl','AEWeatheredForward.hlsl'),('LitGBufferPass.hlsl','AEWeatheredGBuffer.hlsl')]:s=s.replace('Packages/com.unity.render-pipelines.universal/Shaders/'+a,b)
s=s.replace('#pragma target 2.0','#pragma target 3.5');(E/'AEWeatheredLit.shader').write_text(header+s,encoding='utf8')
s=(P/'Shaders/LitInput.hlsl').read_text(encoding='utf8').replace('half _Surface;','half _Surface;\nfloat _AE_Mode;\nfloat _AE_MacroScale;');(E/'AEWeatheredInput.hlsl').write_text(header+s,encoding='utf8')
for original,out in [('LitForwardPass.hlsl','AEWeatheredForward.hlsl'),('LitGBufferPass.hlsl','AEWeatheredGBuffer.hlsl')]:
 s=(P/'Shaders'/original).read_text(encoding='utf8');s=s.replace('    InitializeStandardLitSurfaceData(input.uv, surfaceData);','    InitializeStandardLitSurfaceData(input.uv, surfaceData);\n    AEApplyWeather(input.positionWS, input.normalWS, surfaceData);')
 # Ensure positionWS exists for the world-space material, including no-light variants.
 s=s.replace('#define UNIVERSAL_FORWARD_LIT_PASS_INCLUDED','#define UNIVERSAL_FORWARD_LIT_PASS_INCLUDED\n#define REQUIRES_WORLD_SPACE_POS_INTERPOLATOR') if original=='LitForwardPass.hlsl' else s.replace('#define UNIVERSAL_LIT_GBUFFER_PASS_INCLUDED','#define UNIVERSAL_LIT_GBUFFER_PASS_INCLUDED\n#define REQUIRES_WORLD_SPACE_POS_INTERPOLATOR')
 at=s.index('struct Attributes');s=s[:at]+'#include "AEWeathering.hlsl"\n\n'+s[at:];(E/out).write_text(header+s,encoding='utf8')
shutil.copyfile(H/'AEWeathering.hlsl',E/'AEWeathering.hlsl');shutil.copyfile(P/'LICENSE.md',H/'Unity-URP-LICENSE.md')
sys.path.insert(0,str(U/'Temp/ZFightingReview/deps'))
import numpy as np
from PIL import Image
rng=np.random.default_rng(120611);N=1024;y,x=np.mgrid[:N,:N];row=y//43;col=(x+(row%2)*62)//124;shade=rng.uniform(.85,1.15,(25,10));v=shade[np.minimum(row,24),np.minimum(col,9)];mortar=((y%43)<4)|(((x+(row%2)*62)%124)<5);fine=rng.uniform(-5,5,(N,N))
rgb=np.stack((112*v+fine,77*v+fine,55*v+fine),2);rgb[mortar]=[82,80,69];Image.fromarray(np.uint8(np.clip(rgb,0,255))).save(E/'Textures/AE_BrickDetail_Albedo.png')
height=np.where(mortar,.0,.045)+rng.random((N,N))*.006
def normal(name,h):
 dx=(np.roll(h,-1,1)-np.roll(h,1,1))*6;dy=(np.roll(h,-1,0)-np.roll(h,1,0))*6;n=np.stack((-dx,dy,np.ones_like(h)),2);n/=np.linalg.norm(n,axis=2,keepdims=True);Image.fromarray(np.uint8(np.clip((n*.5+.5)*255,0,255))).save(E/('Textures/'+name))
normal('AE_BrickDetail_Normal.png',height);N=512;noise=rng.uniform(.45,.55,(N,N));Image.fromarray(np.uint8(np.repeat((noise*255)[:,:,None],3,axis=2))).save(E/'Textures/AE_Grain_Albedo.png');normal('AE_Grain_Normal.png',noise*.06)
(H/'weather_source.json').write_text(json.dumps({'author':'송예찬','basePackage':P.name,'baseVersion':'17.4.0','license':'Unity-URP-LICENSE.md','change':'Original world-space procedural weather in forward and deferred shading; no geometry changes; shared UnityPerMaterial layout preserved'},ensure_ascii=False,indent=2),encoding='utf8')
print('Continuous world wear shader and four detail maps generated')
