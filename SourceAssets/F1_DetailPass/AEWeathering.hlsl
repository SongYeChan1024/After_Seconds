// Original After Seconds surface detail, Song Yechan, 2026-11-13, V0.02.
// Metre-scale material coordinates stay attached to moving models. No brick layer.
#ifndef AE_WEATHERING_INCLUDED
#define AE_WEATHERING_INCLUDED
float AEHash(float2 p){float3 q=frac(float3(p.xyx)*.1031);q+=dot(q,q.yzx+33.33);return frac((q.x+q.y)*q.z);}
float AENoise(float2 p){float2 i=floor(p),f=frac(p);f=f*f*(3-2*f);return lerp(lerp(AEHash(i),AEHash(i+float2(1,0)),f.x),lerp(AEHash(i+float2(0,1)),AEHash(i+1),f.x),f.y);}
float AEField(float2 p){return AENoise(p)*.57+AENoise(p*3.19+float2(17.3,9.7))*.28+AENoise(p*10.7+float2(71.2,34.6))*.15;}
float AEThin(float d,float radius){float aa=max(fwidth(d)*.7,.00015);return 1-smoothstep(radius-aa,radius+aa,d);}
float AECrack(float2 p){float2 cell=floor(p),f=frac(p);float first=10,second=10;[unroll]for(int y=-1;y<=1;y++)[unroll]for(int x=-1;x<=1;x++){float2 g=float2(x,y),id=cell+g;float2 jitter=float2(AEHash(id),AEHash(id+float2(73.1,22.4)));float d=length(g+jitter-f);if(d<first){second=first;first=d;}else second=min(second,d);}return AEThin(second-first,.0012);}
void AEApplyWeather(float3 ws,half3 normalWS,inout SurfaceData surface){
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
