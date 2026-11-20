using UnityEngine;

// 의사코드
// 총성·충돌·발소리는 발생한 순간의 월드 위치만 전달한다.
// 현재 층 경비가 들을 수 있는지는 층 담당자가 거리와 차폐를 검사해 결정한다.
public enum GuardNoise { Footstep, Impact, Gunshot }

public static class StealthNoise
{
    public static event System.Action<Vector3, float, GuardNoise> Emitted;
    public static void Emit(Vector3 position, float radius, GuardNoise kind)
    {
        if (Time.timeScale > 0f) Emitted?.Invoke(position, radius, kind);
    }
}
