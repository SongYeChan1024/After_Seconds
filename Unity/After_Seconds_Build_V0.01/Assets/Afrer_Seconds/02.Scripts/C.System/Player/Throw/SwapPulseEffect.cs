using Cinemachine;
using UnityEngine;
using UnityEngine.Rendering;
using UnityEngine.Rendering.RenderGraphModule;
using UnityEngine.Rendering.RenderGraphModule.Util;
using UnityEngine.Rendering.Universal;

// 교환 큐의 같은 박자에서 화면 가장자리 물결, 짧은 카메라 떨림, 소리를 시작한다.
[RequireComponent(typeof(AudioSource))]
public sealed class SwapPulseEffect : CinemachineExtension
{
    [SerializeField] private PlayerSwap swap;
    [SerializeField] private AudioClip beat;
    [SerializeField] private Camera outputCamera;
    [SerializeField] private Shader rippleShader;
    [SerializeField, Min(.05f)] private float duration = .58f;
    [Tooltip("교환 박자의 상하 흔들림 강도(도). 0이면 물결과 소리만 재생한다.")]
    [SerializeField, Range(0f, 1f)] private float shakePitch = .48f;
    private const float ShakeDuration = .20f;
    private static readonly int Ripple = Shader.PropertyToID("_SwapRipple");
    private UniversalAdditionalCameraData cameraData;
    private RipplePass pass;
    private Material material;
    private AudioSource speaker;
    private double started;
    private float amplitude;

    protected override void Awake()
    {
        base.Awake();
        speaker = GetComponent<AudioSource>();
        if (outputCamera && outputCamera.TryGetComponent(out cameraData) && rippleShader)
        {
            material = CoreUtils.CreateEngineMaterial(rippleShader);
            pass = new RipplePass(material);
        }
    }

    protected override void OnEnable()
    {
        base.OnEnable();
        RenderPipelineManager.beginCameraRendering += BeforeCamera;
        if (swap)
        {
            swap.Pulse += PlayBeat;
            swap.FeedbackCleared += Clear;
        }
    }

    private void OnDisable()
    {
        RenderPipelineManager.beginCameraRendering -= BeforeCamera;
        if (swap)
        {
            swap.Pulse -= PlayBeat;
            swap.FeedbackCleared -= Clear;
        }
        Clear();
    }

    protected override void OnDestroy()
    {
        CoreUtils.Destroy(material);
        base.OnDestroy();
    }

    private void PlayBeat(float strength)
    {
        if (amplitude > 0f && Time.timeAsDouble - started < .09 && strength <= amplitude) return;
        started = Time.timeAsDouble;
        amplitude = strength;
        if (!beat) return;
        speaker.clip = beat;
        speaker.volume = .8f * strength;
        speaker.Play();
    }

    private void Clear()
    {
        amplitude = 0f;
        if (speaker && speaker.isPlaying) speaker.Stop();
    }

    protected override void PostPipelineStageCallback(CinemachineVirtualCameraBase vcam,
        CinemachineCore.Stage stage, ref CameraState state, float deltaTime)
    {
        if (stage != CinemachineCore.Stage.Finalize || amplitude <= 0f || Time.timeScale <= 0f) return;
        float phase = (float)(Time.timeAsDouble - started) / ShakeDuration;
        if (phase >= 1f) return;

        // 매 프레임 새로 계산한 카메라 자세에만 더해 시선 입력과 투척 방향을 보존한다.
        float falloff = 1f - phase;
        float pitch = Mathf.Sin(phase * 2f * Mathf.PI) * falloff * falloff * shakePitch * amplitude;
        state.OrientationCorrection *= Quaternion.Euler(pitch, 0f, 0f);
    }

    private void BeforeCamera(ScriptableRenderContext context, Camera camera)
    {
        if (amplitude <= 0f || camera != outputCamera || pass == null) return;
        if (Time.timeScale <= 0f) { Clear(); return; }
        float age = (float)(Time.timeAsDouble - started);
        if (age >= Mathf.Max(duration, ShakeDuration)) { amplitude = 0f; return; }
        float phase = age / duration;
        if (phase >= 1f) return;
        material.SetVector(Ripple, new Vector4(phase, amplitude, 0f, 0f));
        cameraData.scriptableRenderer.EnqueuePass(pass);
    }

    private sealed class RipplePass : ScriptableRenderPass
    {
        private readonly Material material;

        public RipplePass(Material material)
        {
            this.material = material;
            renderPassEvent = RenderPassEvent.BeforeRenderingPostProcessing;
            requiresIntermediateTexture = true;
        }

        public override void RecordRenderGraph(RenderGraph graph, ContextContainer frame)
        {
            var resources = frame.Get<UniversalResourceData>();
            if (resources.isActiveTargetBackBuffer) return;
            var source = resources.activeColorTexture;
            var descriptor = graph.GetTextureDesc(source);
            descriptor.name = "Swap edge ripple";
            descriptor.clearBuffer = false;
            var result = graph.CreateTexture(descriptor);
            graph.AddBlitPass(new RenderGraphUtils.BlitMaterialParameters(source, result, material, 0),
                passName: "Swap edge ripple");
            resources.cameraColor = result;
        }
    }
}
