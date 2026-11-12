# B1 데스크·기물 보수 원본 V0.01

작성자 송예찬 · 2026-11-12

현재 B1의 최신 기물 보수다. [검수](../../Docs/Review/2026-11-12_B1_DeskProps/Review.md) · [전후 화면](../../Docs/Review/2026-11-12_B1_DeskProps/review.html).

**사용자 후속 편집 뒤 제작기·Apply를 일괄 재실행하지 않는다.** 현재 씬부터 확인해 지적 범위만 보수한다. B1_InteriorRedesign의 layout은 실내 구조 제작 당시 기록이며 녹음기10개의 최신 위치는 이 폴더 plan과 Decision 현재 배치를 따른다.

- Inspect.cs / before.json / protected_files.json: 작업 전 씬53관련 배치·전체Transform/Collider/Light와 기존13041파일 기준. Inspect 재실행으로 덮어쓰지 않는다.
- source_geometry.json.gz: 당시 저장 씬에서 읽은 원본 메시·UV·노멀·재질. 원본의 하부 가구 형상을 유지하기 위한 압축 원본. mesh_export와 before.unity는 PC 임시 사본으로 Git 제외.
- plan.py / plan.json: 51시각 교체와 녹음기10자리 변경. 24연구 데스크12구성, 각6석 방 안에서 중복 없음.
- models.py / models.json: Blender 네이티브30FBX·3LOD. 기존 하부 가구 보존, 키/마우스·기물·배선 재제작. DP_ONLY로 지정 모델만 만들 수 있지만 후속 작업에서 자동 적용하지 않는다.
- textures.py / atlas.json: 2048공유 업무 화면·인쇄 기록 아틀라스1장. 기존 PD_KeyLegend 재사용.
- Apply.cs: Unity 네이티브 적용·Undo·저장·보존 감사. 공유 원본FBX나 게임 C#을 수정하지 않는다. 이전 렌더러는 비표시 보존하고 새 B1 모델을 연결한다.
- Quality.cs / GeometryExport.cs / geometry.py: 메시·LOD·오른손 배치·전체B1 깊이 충돌 검사. 이전 가림 데이터용 메시 캐시는 같은 파일을 중복해서 덮어쓰지 않는다.
- Capture.cs / Walk.cs / Play.cs / Look.cs / run_play.py: 전후 확대·LOD·통행·실제 입력/시점 검수. 실제 입력 장치를 비활성화하지 않고 임시 설정을 복구한다.
- Finish.cs / report.py: 반사/가림 갱신·편집 상태 복귀·로컬 기록. Assets 안에 게임 스크립트를 추가하지 않는다.

다음은 사용자 전체 B1 외형 검수와 지정 범위 보수다. 다른 층·게임 C#·Player·Animator 보존, 커밋·push 미실시.
