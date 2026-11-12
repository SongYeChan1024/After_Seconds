// Original After Seconds environmental wear. Author: Song Yechan, 2026-11-12.
// Macro wear follows continuous world coordinates, independent of the repeating brick/grain UVs.
#ifndef AE_WEATHERING_INCLUDED
#define AE_WEATHERING_INCLUDED
float AEHash(float2 p) {
    float3 q=frac(float3(p.xyx)*.1031);q+=dot(q,q.yzx+33.33);return frac((q.x+q.y)*q.z);
}
float AENoise(float2 p) {
    float2 i=floor(p),f=frac(p);f=f*f*(3-2*f);
    return lerp(lerp(AEHash(i),AEHash(i+float2(1,0)),f.x),lerp(AEHash(i+float2(0,1)),AEHash(i+1),f.x),f.y);
}
float AEField(float2 p) {
    return AENoise(p)*.57+AENoise(p*3.19+float2(17.3,9.7))*.28+AENoise(p*10.7+float2(71.2,34.6))*.15;
}
float AECrack(float2 p) {
    float2 cell=floor(p),f=frac(p);float first=10,second=10;
    [unroll] for(int y=-1;y<=1;y++) [unroll] for(int x=-1;x<=1;x++) {
        float2 g=float2(x,y),id=cell+g;
        float2 jitter=float2(AEHash(id),AEHash(id+float2(73.1,22.4)));
        float d=length(g+jitter-f);
        if(d<first){second=first;first=d;}else second=min(second,d);
    }
    float width=max(fwidth(second-first),.003);
    return 1-smoothstep(.006-width,.012+width,second-first);
}
void AEApplyWeather(float3 ws,half3 normalWS,inout SurfaceData surface) {
    float3 n=abs(normalWS);
    float2 plane=n.y>.65?ws.xz:(n.x>n.z?ws.zy:ws.xy);
    // Different parallel walls do not receive a duplicated stamp, even when their UVs match.
    plane+=dot(ws,n)*float2(.137,.173);
    float field=AEField(plane*_AE_MacroScale);
    float wide=AENoise(plane*.075+float2(5.1,38.2));
    float grain=AENoise(plane*29.7);
    if(_AE_Mode<1.5) {
        float edgeField=field+(AENoise(plane*19.3)-.5)*.075+(AENoise(plane*67.1)-.5)*.025;
        float edgeWidth=max(fwidth(edgeField)*.6,.003);
        float broken=smoothstep(.503-edgeWidth,.503+edgeWidth,edgeField);
        float damp=(1-smoothstep(.05,1.75,ws.y))*(.25+.75*AENoise(plane*float2(.63,.10)+31));
        float streak=smoothstep(.48,.76,AENoise(plane*float2(2.2,.065)+17))*.25;
        half3 plaster=half3(.255,.235,.185)*lerp(.62,1.06,wide)*( .88+grain*.24 );
        half3 brick=surface.albedo*(.85+wide*.25);
        surface.albedo=lerp(plaster,brick,broken)*(1-damp*.35-streak);
        surface.normalTS=normalize(lerp(half3(0,0,1),surface.normalTS,broken));
        surface.metallic=0;surface.smoothness=.12-damp*.04;
    } else if(_AE_Mode<2.5) {
        float rust=smoothstep(.36,.68,field);
        half3 paint=half3(.11,.135,.115)*(.80+wide*.35);
        half3 oxidation=lerp(half3(.065,.029,.012),half3(.22,.095,.035),grain*.45+field*.55);
        surface.albedo=lerp(paint,oxidation,rust)*_BaseColor.rgb;
        surface.metallic=lerp(.62,.13,rust);surface.smoothness=lerp(.25,.10,rust);
    } else {
        float2 warped=plane+float2(AENoise(plane*.43),AENoise(plane*.43+41))*.65+float2(AENoise(plane*5.3),AENoise(plane*5.3+71))*.07;
        float cracks=AECrack(warped*.47+float2(4.8,11.1))*smoothstep(.38,.62,AENoise(plane*.87+8));
        float stain=smoothstep(.63,.75,AEField(plane*.33+18));
        surface.albedo=half3(.16,.165,.14)*lerp(.66,1.20,field)*(.90+grain*.20)*(1-cracks*.35-stain*.26);
        surface.metallic=0;surface.smoothness=.13;
    }
}
#endif
