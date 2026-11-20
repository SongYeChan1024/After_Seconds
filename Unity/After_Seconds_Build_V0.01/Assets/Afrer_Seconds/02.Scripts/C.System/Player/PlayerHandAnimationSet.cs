using UnityEngine;

#region 의사코드
// 걷기·달리기 및 위로 던지기의 원본 클립과 양손 위치 곡선을 짝지어 보관한다.
// 요청된 동작의 정규화 시간에서 X·Y·Z 곡선을 각각 읽어 손 위치 벡터를 만든다.
#endregion

// VARCO 휴머노이드 클립을 현재 리그에 재생해 추출한 1인칭용 손 경로.
// 원본 클립 참조와 표본 곡선을 함께 보관한다. 전신 본/이동/방출 시점은 변경하지 않는다.
[CreateAssetMenu(fileName = "PlayerHandAnimations", menuName = "After Seconds/Player Hand Animations")]
public class PlayerHandAnimationSet : ScriptableObject
{
    public AnimationClip walkSource, runSource, overhandSource;
    public HandVectorCurve walkRight = new HandVectorCurve(), walkLeft = new HandVectorCurve();
    public HandVectorCurve runRight = new HandVectorCurve(), runLeft = new HandVectorCurve();
    public HandVectorCurve prepareRight = new HandVectorCurve(), prepareLeft = new HandVectorCurve();
    public HandVectorCurve releaseRight = new HandVectorCurve(), releaseLeft = new HandVectorCurve();
    [Min(0.05f)] public float prepareDuration = 0.18f;
    [Min(0.05f)] public float releaseDuration = 0.42f;
    public float sourceReleaseTime = 2.133333f;
    public float sourceReleaseEnd = 2.55f;
    public bool HasLocomotion => walkSource != null && runSource != null;
    public bool HasOverhand => overhandSource != null;
}

[System.Serializable]
public class HandVectorCurve
{
    public AnimationCurve x = AnimationCurve.Linear(0f, 0f, 1f, 0f);
    public AnimationCurve y = AnimationCurve.Linear(0f, 0f, 1f, 0f);
    public AnimationCurve z = AnimationCurve.Linear(0f, 0f, 1f, 0f);
    public Vector3 Evaluate(float normalizedTime) => new Vector3(x.Evaluate(normalizedTime), y.Evaluate(normalizedTime), z.Evaluate(normalizedTime));
}
