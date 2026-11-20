using System;
using UnityEngine;

#region 의사코드
// 층별 실측 보행 경로, 근무 위치와 계단 입구를 보관한다. 시간은 각 구간의 보행 거리와 경비 설정에서 얻는다.
#endregion
[CreateAssetMenu(menuName = "After Seconds/Dome Patrol Plan")]
public sealed class DomePatrolPlan : ScriptableObject
{
    public GuardPresenter guardPrefab;
    public GameObject dutyChair;
    public StairApproach[] stairs;
    public DomePost[] domes;
}

[Serializable]
public sealed class StairApproach
{
    public string core;
    public Vector3[] entryFeet;
    public Vector3[] threshold;
    public Vector3[] landings;
    public bool fromBelow;
}

[Serializable]
public sealed class DomePost
{
    public string id;
    public DomeWatchMode watch;
    public string[] passages;
    public Vector3[] circuit;
    public float[] legLengths;
    public int[] entranceIndices;
    public bool[] inspectionStops;
    [NonSerialized] private Vector3[] entrances;
    // 굽은 복도마다 안내 지점 수가 다르므로 출입구 번호를 따로 기록한다.
    public Vector3[] Entrances
    {
        get
        {
            if (entrances != null) return entrances;
            int count = passages.Length;
            if (count == 0) return Array.Empty<Vector3>();
            int stopsPerPassage = circuit.Length / count;
            entrances = new Vector3[count];
            for (int i = 0; i < count; i++)
            {
                int index = entranceIndices != null && entranceIndices.Length == count ? entranceIndices[i] : i * stopsPerPassage;
                entrances[i] = circuit[index];
            }
            return entrances;
        }
    }
    public float WaitAt(int index, float patrolWait) =>
        inspectionStops == null || inspectionStops.Length != circuit.Length || inspectionStops[index] ? patrolWait : 0f;

    public Vector3[] indoor;
    public Vector3[] meeting;
    public Vector3 chairFeet;
    public float watchYaw;
    public bool addChair;
    public int stairIndex;
    public float arrivalDistance;
}
