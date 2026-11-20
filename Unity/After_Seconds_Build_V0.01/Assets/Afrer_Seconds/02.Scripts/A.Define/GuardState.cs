#region 의사코드
// 경비가 플레이어를 식별하면 추격 상태를 사용한다.
// 마지막 목격 지점에서 수색하고, 수색을 마치면 복귀를 거쳐 순찰로 돌아간다.
#endregion

public enum GuardState { Patrol, Chase, Search, Return }
