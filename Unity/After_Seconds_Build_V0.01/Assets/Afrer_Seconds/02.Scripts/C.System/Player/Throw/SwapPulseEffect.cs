using Cinemachine;
using UnityEngine;
using UnityEngine.Rendering;
using UnityEngine.Rendering.RenderGraphModule;
using UnityEngine.Rendering.RenderGraphModule.Util;
using UnityEngine.Rendering.Universal;

#region 의사코드
// 교환 큐의 박자에 음원을 재생하고 시작 시각과 세기를 저장한다.
// 주음과 잔향의 곡선으로 시야각·카메라 떨림과 흰 안개를 갱신한다. 이번 프레임의 렌즈에만 보정을 적용한다.
// 박동 종료나 예약 정리 시 화면 효과와 재생 상태를 정리한다.
#endregion

// 교환 큐의 같은 박자에서 화면 전체 박동, 짧은 카메라 떨림, 소리를 시작한다.
[RequireComponent(typeof(AudioSource))]
public sealed class SwapPulseEffect : CinemachineExtension
{
    [SerializeField] private PlayerSwap swap;
    [SerializeField] private AudioClip beat;
    [SerializeField] private Camera outputCamera;
    [SerializeField] private Shader rippleShader;
    [SerializeField, Min(.05f)] private float duration = .58f;
    [Tooltip("교환 박자의 상하 흔들림 강도(도). 0이면 화면 박동과 소리만 재생한다.")]
    [SerializeField, Range(0f, 1f)] private float shakePitch = .48f;
    [Tooltip("박동 정점에서 현재 시야각을 줄이는 비율입니다. 조준 시야각도 같은 비율로 반응합니다.")]
    [SerializeField, Range(0f, .1f)] private float fovKick = .06f;
    private static readonly int BeatEnvelope = Shader.PropertyToID("_SwapBeat");
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
        speaker.volume = .25f + .75f * strength;
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
        float phase = (float)(Time.timeAsDouble - started) / duration;
        if (phase >= 1f) return;
        float beatAmount = SampleBeat(phase);
        // Cinemachine이 이번 프레임에 만든 렌즈에만 적용한다. 조준 배율과 입력 자세에는 누적하지 않는다.
        state.Lens.FieldOfView *= 1f - fovKick * beatAmount;
        float wobble = Mathf.Sin(phase * Mathf.PI * 4f) * beatAmount * shakePitch;
        state.OrientationCorrection *= Quaternion.Euler(wobble, 0f, 0f);
    }

    private void BeforeCamera(ScriptableRenderContext context, Camera camera)
    {
        if (amplitude <= 0f || camera != outputCamera || pass == null) return;
        if (Time.timeScale <= 0f) { Clear(); return; }
        float age = (float)(Time.timeAsDouble - started);
        if (age >= duration) { amplitude = 0f; return; }
        float phase = age / duration;
        // 흰 안개는 첫 박자에서 서서히 차오르고 두 번째 울림 사이에도 매끄럽게 걷힌다.
        float mist = amplitude * HeartbeatLobe(phase, 0f, .20f, 1f);
        material.SetFloat(BeatEnvelope, .62f * mist + .38f * SampleBeat(phase));
        cameraData.scriptableRenderer.EnqueuePass(pass);
    }

    private float SampleBeat(float phase)
    {
        // 음원의 두 어택(약 0.05초와 0.23초)을 렌즈, 화면 색과 진동이 함께 따른다.
        float first = HeartbeatLobe(phase, 0f, .085f, .37f);
        float echo = HeartbeatLobe(phase, .285f, .40f, .91f);
        return (first + .63f * echo) * amplitude;
    }

    private static float HeartbeatLobe(float phase, float onset, float peak, float end)
    {
        float rise = Mathf.SmoothStep(0f, 1f, Mathf.InverseLerp(onset, peak, phase));
        float decay = Mathf.SmoothStep(1f, 0f, Mathf.InverseLerp(peak, end, phase));
        return rise * decay;
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
            descriptor.name = "Swap heartbeat";
            descriptor.clearBuffer = false;
            var result = graph.CreateTexture(descriptor);
            graph.AddBlitPass(new RenderGraphUtils.BlitMaterialParameters(source, result, material, 0),
                passName: "Swap heartbeat");
            resources.cameraColor = result;
        }
    }
}
