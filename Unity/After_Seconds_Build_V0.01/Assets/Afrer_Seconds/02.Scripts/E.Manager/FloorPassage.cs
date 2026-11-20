using UnityEngine;

#region 의사코드
// 출구의 로컬 좌표로 발 위치를 바꿔 계단참의 폭·깊이·높이 안인지 검사한다.
// 도착 표식에 출발 시의 수평 오프셋을 더한다. 목적 씬의 바닥 경사와 캡슐 여유가 모두 맞아야 이동을 허용한다.
// 먼저 목적 층에서 걸을 수 있는 바닥을 찾는다. 그 위에 플레이어 크기의 캡슐을 놓아 벽이나 천장과 겹치면 거절한다.
#endregion

public enum FloorCore { StairA, StairB, FreightLift }

// 층 시작점의 자식으로 둔다. 목적 씬을 지정하면 출발 계단참, 비워 두면 도착 표식이다.
public sealed class FloorPassage : MonoBehaviour
{
    [SerializeField] private FloorCore core;
    [Tooltip("빌드 목록에 등록된 목적 층의 씬 경로. 도착 표식은 비워 둔다.")]
    [SerializeField] private string destinationPath;
    [SerializeField] private Vector2 landingSize = new Vector2(1.25f, .8f);
    public FloorCore Core => core;
    public string DestinationPath => destinationPath;
    public bool IsExit => !string.IsNullOrEmpty(destinationPath);

    public bool ContainsFeet(Vector3 feet, float heightTolerance)
    {
        Vector3 local = transform.InverseTransformPoint(feet);
        return IsExit && isActiveAndEnabled && Mathf.Abs(local.y) <= heightTolerance &&
               Mathf.Abs(local.x) <= landingSize.x * .5f && Mathf.Abs(local.z) <= landingSize.y * .5f;
    }

    // 출발·도착 층은 잠시 같은 물리 월드에 겹친다. 도착 층의 표면만 검사한다.
    public bool TryPlaceFeet(Vector3 horizontalOffset, CharacterController body, out Vector3 feet)
    {
        feet = transform.position + Vector3.ProjectOnPlane(horizontalOffset, Vector3.up);
        float probe = body.stepOffset + body.skinWidth;
        var floor = gameObject.scene;
        var hits = Physics.RaycastAll(feet + Vector3.up * probe, Vector3.down, 2f * probe,
            Physics.AllLayers, QueryTriggerInteraction.Ignore);
        float distance = float.PositiveInfinity;
        foreach (var hit in hits)
        {
            if (hit.collider.gameObject.scene != floor || hit.distance >= distance ||
                Vector3.Angle(hit.normal, Vector3.up) > body.slopeLimit) continue;
            feet = hit.point + Vector3.up * body.skinWidth;
            distance = hit.distance;
        }
        if (float.IsPositiveInfinity(distance)) return false;

        var extents = body.bounds.extents;
        float radius = Mathf.Max(extents.x, extents.z);
        Vector3 bottom = feet + Vector3.up * radius;
        Vector3 top = feet + Vector3.up * (2f * extents.y - radius);
        foreach (var contact in Physics.OverlapCapsule(bottom, top, radius - Physics.defaultContactOffset,
                     Physics.AllLayers, QueryTriggerInteraction.Ignore))
            if (contact.gameObject.scene == floor) return false;
        return true;
    }

    private void OnDrawGizmosSelected()
    {
        Gizmos.matrix = transform.localToWorldMatrix;
        Gizmos.color = IsExit ? Color.yellow : Color.cyan;
        Gizmos.DrawWireCube(Vector3.zero, new Vector3(landingSize.x, .1f, landingSize.y));
    }
}
