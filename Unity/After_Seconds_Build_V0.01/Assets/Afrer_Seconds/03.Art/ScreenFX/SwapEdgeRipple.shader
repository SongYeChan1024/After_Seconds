Shader "After Seconds/Screen FX/Swap Edge Ripple"
{
    Properties
    {
        [HideInInspector] _SwapRipple ("Beat phase and strength", Vector) = (0,0,0,0)
    }
    SubShader
    {
        Tags { "RenderPipeline"="UniversalPipeline" }
        Pass
        {
            Cull Off ZWrite Off ZTest Always
            HLSLPROGRAM
            #pragma vertex Vert
            #pragma fragment Frag
            #include "Packages/com.unity.render-pipelines.universal/ShaderLibrary/Core.hlsl"
            #include "Packages/com.unity.render-pipelines.core/Runtime/Utilities/Blit.hlsl"

            CBUFFER_START(UnityPerMaterial)
                float4 _SwapRipple; // normalized age, beat strength
            CBUFFER_END

            half4 SceneAt(float2 uv)
            {
                return SAMPLE_TEXTURE2D_X(_BlitTexture, sampler_LinearClamp, uv);
            }

            half4 Frag(Varyings input) : SV_Target
            {
                UNITY_SETUP_STEREO_EYE_INDEX_POST_VERTEX(input);
                float2 uv = input.texcoord;
                half4 source = SceneAt(uv);
                float2 fromCenter = input.positionCS.xy / _ScaledScreenParams.xy * 2.0 - 1.0;
                float2 toEdge = 1.0 - abs(fromCenter);
                // Smooth the corners of the rectangular vignette on all aspect ratios.
                float corner = saturate(1.0 - abs(toEdge.x - toEdge.y) / .48);
                float borderDepth = min(toEdge.x, toEdge.y) - .12 * corner * corner;
                float depth = max(0.0, lerp(borderDepth, 1.0 - length(fromCenter), .55));
                if (depth >= .48) return source;

                float age = _SwapRipple.x;
                float envelope = smoothstep(0.0, .075, age) * (1.0 - smoothstep(.35, 1.0, age)) * _SwapRipple.y;
                float travel = 1.0 - (1.0 - age) * (1.0 - age);
                float front = lerp(-.035, .36, travel);
                float band = (depth - front) / lerp(.074, .106, travel);
                float crest = exp2(-2.5 * band * band);
                float edgeMist = exp2(-depth * 9.5) * (1.0 - age);
                float strength = envelope * (1.0 - smoothstep(.36, .48, depth));
                float haze = strength * (.82 * crest + .58 * edgeMist);

                float2 pixel = abs(_BlitScaleBias.xy) / _ScaledScreenParams.xy;
                float2 outward = normalize(float2((uv.x - .5) * _ScaledScreenParams.x / _ScaledScreenParams.y, uv.y - .5));
                float pixelsPer1080 = _ScaledScreenParams.y / 1080.0;
                float2 bend = outward * pixel * pixelsPer1080 * (11.0 * band * crest * strength);
                float2 offset = pixel * pixelsPer1080 * (6.8 * haze);
                float2 refracted = uv + bend;
                half3 soft = SceneAt(refracted).rgb * .28;
                soft += .18 * (SceneAt(refracted + offset).rgb + SceneAt(refracted - offset).rgb);
                offset.x = -offset.x;
                soft += .18 * (SceneAt(refracted + offset).rgb + SceneAt(refracted - offset).rgb);

                half3 color = lerp(source.rgb, soft, saturate(haze * 1.5));
                // Translucent, cool-neutral mist leaves the underlying scene readable.
                color = lerp(color, half3(.47, .51, .53), saturate(.23 * haze));
                return half4(color, source.a);
            }
            ENDHLSL
        }
    }
}
