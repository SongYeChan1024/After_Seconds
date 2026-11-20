Shader "After Seconds/Screen FX/Swap Edge Ripple"
{
    Properties
    {
        [HideInInspector] _SwapBeat ("Heartbeat envelope", Float) = 0
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
                float _SwapBeat;
            CBUFFER_END

            half4 Frag(Varyings input) : SV_Target
            {
                UNITY_SETUP_STEREO_EYE_INDEX_POST_VERTEX(input);
                float2 uv = input.texcoord;
                float2 screen = 2.0 * input.positionCS.xy / _ScaledScreenParams.xy - 1.0;
                float edge = smoothstep(0.06, 1.35, dot(screen, screen));
                float haze = saturate(_SwapBeat);
                // Keep the middle in focus. Sample all color channels together through the mist.
                float radius = lerp(0.0, 6.0, edge) * haze * (_ScaledScreenParams.y / 1080.0);
                float2 offset = _BlitTexture_TexelSize.xy * radius;
                half4 scene = SAMPLE_TEXTURE2D_X(_BlitTexture, sampler_LinearClamp, uv);
                half3 blurred = scene.rgb * .25h;
                blurred += .1875h * SAMPLE_TEXTURE2D_X(_BlitTexture, sampler_LinearClamp, uv + offset).rgb;
                blurred += .1875h * SAMPLE_TEXTURE2D_X(_BlitTexture, sampler_LinearClamp, uv - offset).rgb;
                blurred += .1875h * SAMPLE_TEXTURE2D_X(_BlitTexture, sampler_LinearClamp, uv + float2(offset.x, -offset.y)).rgb;
                blurred += .1875h * SAMPLE_TEXTURE2D_X(_BlitTexture, sampler_LinearClamp, uv + float2(-offset.x, offset.y)).rgb;
                half coverage = haze * lerp(.018h, .41h, edge);
                return half4(lerp(blurred, half3(.84h, .86h, .88h), coverage), scene.a);
            }
            ENDHLSL
        }
    }
}
