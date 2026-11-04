# After Seconds Unity 프로젝트 안내 V0.30

## 2026-11-04 건축 마감 전층 적용 완료

기둥·수평 레일·표지판 하우징·닫힌 단면 벽 패널을 원본6층 씬에 적용·저장했다. 벽/부스/칸막이237곳(패널3,747장)·표지30·레일16·기둥16·문틀12곳이다. 원래 배치와 충돌체·스크립트 구성·문구를 저장 후 재검증했다. 게임 기능은 추가하지 않았다.

공용 FBX·외형 프리팹은 `05.Model/Environment/Common/AD_{pillar,reveal,sign,panel}_Manufactured.*`, 층별 배치 패널은 `Environment/{층}/AD_WallPanels_*.asset`, 제작 원본은 `SourceAssets/ArchitectureDetail/ArchitectureDetail_Clean.blend`다. 최종 패널208tri·내부 공면 겹침0쌍이며 PC RP MSAA4와6개 카메라 SMAA High를 반영했다. 28시점 최종 렌더와 보호 범위는 [건축 마감 최종 검수](../Docs/검수/2026-11-04_Architecture_Detail/검수결과.md)에 있다. 실제 이동·FPS 검증은 아직이다. VARCO750점은 앞선 시안 제작 비용이며 이번 재개 때 추가 생성은 없다.

이전 검증 사본과 `_after`/`probe` 이미지는 최종 결과가 아니다. 현재 원본 씬에 이전 제작·Apply를 그대로 재실행하지 않는다. Unity 버전과 사용자 B5·소품/WF 보수·Packages AI Assistant 상태를 유지한다.

## 2026-11-04 전층 벽·문틀 보수

6층의 활성 건축 시각 메시614개를 검사해 같은 방향의 공면 겹침72쌍을 찾았다. B5 문틀·복도·계단·냉각조, B4 천장 접합, B3 포획 구역의 시각 메시81개를 해당 층 `05.Model/Environment/{층}/WF_*_SeamFixed.asset`로 교체했다. 위치를 옮기지 않고 중복 면만 잘라 맞췄으며 UV·UV2·원래 tangent를 보간했다. 저장 후 같은 검사 기준의 잔여 겹침은0쌍이다.

B2·B1·1F 씬은 파일까지 동일하다. 기존 모델·프리팹·meta·소품 마감과 Packages·ProjectSettings의 보호 파일1237개는 변경하지 않았다. B3·B4·B5 씬도 시각 메시 참조만 바뀌었으며 사용자 저장 B5 내용과 전층 Transform·Collider·Behaviour를 보존했다. 전후 사진·수치·검사의 한계는 [검수 결과](../Docs/검수/2026-11-04_Wall_Frame_Repair/검수결과.md)를 따른다. 실제 키보드 플레이 테스트는 아직이다.

## 2026-11-04 후속 소품 마감

가구·소품·설비35개 메시 파트에 작은 베벨을 추가하고 기존 베벨6개를 유지했다. 41개 모두60도 기준 스무스·가중 노멀을 적용했으며 같은 모델 폴더의 `_BevelSmooth.asset`를 기존 프리팹에 연결했다. 6층 배치110곳에서 새 참조를 확인했고 원본 FBX·기존 meta·Collider·Transform은 유지했다. 벽·바닥·천장에는 베벨을 추가하지 않았다.

공용 작업대의 큰 삼각형 색 얼룩은 기존 UV로 판재29곳을 재베이크한 `Props/Common/Textures/Props_LaboratoryWorkbench_BaseColor_Corrected.png`로 보정했다. 원본 색·노멀 텍스처를 보존한다. 당시 벽·문틀은 진단까지만 진행했으며 이후 보수는 위 전층 벽·문틀 항목을 따른다. 소품 전후 사진과 저장 후 검증은 [소품 마감·벽 문틀 진단](../Docs/검수/2026-11-04_Prop_Finish/검수결과.md)에 있다.

## 2026-11-04 마감 상태와 다음 작업

작성자 송예찬

최신 인수인계는 [2026-11-04 이어하기](../Docs/이어하기_2026-11-04.md)를 먼저 읽는다. 1F 출구의 셔터·외장 코너 2종을 재제작 FBX로 교체했다. 원본 모델과 기존 프리팹 GUID, 모델의 native bounds를 보존했고 실제 씬 렌더로 교체 외형을 확인했다. 원본 FBX를 덮어쓰지 않고 `05.Model/Environment/1F/Env_LoadingShutterWall_Rebuilt.fbx`, `Env_ExteriorCorner_Rebuilt.fbx`를 사용한다. Blender 원본은 `SourceAssets/1F_Facades_Rebuilt`다.

B2의 끊어진 직관·엘보·밸브 배치를 공급·회수 주 배관과 장비 연결을 포함한 10개 경로의 연결 관망으로 정리했다. 시각 프리팹1개·절차 메시12개이며 기존 배관 루트6개는 Renderer만 껐다. 장비 실제 표면에 끝단을 맞춰 보정한 최종 렌더를 확인했다. 새 Collider·런타임 Behaviour0개, 보호 구역7곳 침범0건이며 6층 기존 Collider·Transform 보존 검사를 통과했다. 자세한 경로·검수 범위는 최신 이어하기를 따른다. 기존 퍼즐의 빈 공간과 통로는 유지한다.

이전 환경·소품 48종 사용 기록과 6층 전체의 배치 완성은 구분한다. 오늘 B2 직관·엘보의 기존 Renderer를 관망 외형으로 대체했으므로 현재 48종 모두가 활성화됐다는 재검증은 하지 않았다. 다음 작업 세션은 수정 B2·1F 재확인 → 6층 배치·메시 검수 → 부족한 프랍 수급·배치 → 플레이어·경비 기능 → 플레이 테스트 → 난이도 곡선 검토 순서다. 작업대 3개·직선 덕트 9개·B5 잔여 접촉면은 우선 검토 후보이며 전부 파손으로 확정한 것은 아니다. 오늘 새 유료 에셋 생성은 하지 않았다. 실제 플레이 테스트와 예약·교환·경비 핵심 기능 구현은 남아 있다.

아래 11월 3일 기록은 B5 생활형 포드·내부 조명과 앞선 반입 작업의 상세 이력으로 보존한다.

## 돔 내부 중앙 조명

가운데 등을 돔 안쪽 꼭대기에서 세 가닥 지지선으로 매단 얇은 링 조명으로 교체했다. 외경1.404m이며 실제 조명 하단은 약5.11m다. 생활 공간을 아래로 비추도록 연결했고 기존 돔 밖 Cell_Lamp는 외형·광원만 비활성화했다. 바깥 천장 조명4개와 생활 배치·포드 크기는 유지했다. 상세와 사진은 [돔 내부 조명 검수](../Docs/검수/2026-11-03_Dome_Interior_Light/돔_내부_조명_검수.md)를 따른다.

## 생활·실험형 격리실 최신 상태

사용자가 조정한 포드 위치 `(0,0,10.32)`와 스케일 `(3,2,3)`을 그대로 저장했다. 외경8.43m·내경7.872m·높이6.442m다. Room01은 폭12m·깊이14m(z2~16), 천장 아래7.2m로 확장했고 돔 꼭대기와 약0.758m 여유가 있다. 기존 전면 통로는 그대로다. 경비는 사용자가 옮긴 `(0,0,5.064)`에서 돔 밖에 있다.

돔 안에는 침구를 얹은 침상, 식탁·고정 스툴·식판·컵·식사, 개인 수납, 세면대·변기·차폐판·폐기함, 검사 모니터를 배치했다. 돔 밖에는 관찰 콘솔·시료 준비대·의료 트롤리를 둔다. 가구는 사람 크기를 유지했다. 내부 바닥 물리 높이0.28m에 맞춰 플레이어 시작Y를0.885m로 조정했고 X/Z와 Controller 설정은 유지했다.

배식구는 두 문짝의 앞뒤 네 면에 같은 금속 인셋·손잡이·힌지 마감이 있고, 실제 개구와 깊이0.42m의 전달함·독립 회전축·문 충돌까지 연결했다. 저장 상태는 닫힘이다. 닫힘18/18차단·열림18/18관통·옆 유리12/12차단, 시작 겹침0·8방향 이동검사를 통과했다. 입력 개폐·잠금·배식·탈출 동작은 미구현이다.

상세와 사진은 [생활형 포드 검수](../Docs/검수/2026-11-03_Subject_Habitat/생활형_포드_검수.md)를 따른다. 원래 포드 FBX/프리팹과 이번 작업 전 사용자 씬 사본은 보존했다. 아래 작은 포드의 치수·장식 배식구 설명은 이전 작업 기록이며 현재 상태는 이 항목이 우선한다.

## 이전 6층 에셋 배치와 작은 포드 기록

2026-11-03 · 작성자 송예찬

최신 상태와 이어서 할 일은 [2026-11-04 이어하기](../Docs/이어하기_2026-11-04.md)를 먼저 읽는다. 아래는 11월 3일 배치 이력이다. 사용자 요청으로 기존 에셋을 B5~1F의 6개 층에 추가 배치했다. B4~1F에는 재제작한 건축 모듈의 시각 외형을 적용했다. 건축 프리팹 6종은 `05.Model/Environment/B5`에 한 벌만 두고 상층 5개 씬에서도 공유 참조하며, 이번 작업에서 Common으로 이동하거나 복제하지 않는다. 기존 벽 Transform과 사용자가 뒤집은 천장 방향을 유지한다.

기존 VARCO V0.01 미반입 에셋 14종을 모두 반입하고 6개 층에 총 29개 시각 인스턴스로 적용했다(지붕 패널 12개 포함). V0.01 22종과 V0.02 26종의 환경·소품 48종을 현행 프리팹 또는 재제작 모듈로 사용한다. 가벼운 상자 15개의 임시 외형도 물류 용기로 연결했다. 상층 5개 씬은 기존 건축 80개 표면에 318개 모듈을 반복 적용했다. B4의 떠 있던 서류장은 바닥으로 내렸다. 저장 씬 재열기·참조·충돌 보존·렌더 검수를 완료했다. 상세 배치표·안팎 렌더·검수 자료는 [전체 에셋 배치 결과](../Docs/검수/2026-11-03_Full_Asset_Placement/배치_검수결과.md)에 있다. 아래 이전 기록의 반입 수치는 당시 작업 범위에 해당한다.

시작 공간은 사용자 추가 요청으로 **실제 유리 관찰 포드 모델과 정적 충돌을 제작·반입했다.** B5 `Room01_Isolation` 로컬 `(0,0,10.45)`에 배치했으며 외경 2.81m, 높이 3.221m, 안쪽 지름 2.624m다. 흰색 받침·얇은 검은 프레임·Alpha 0.12 유리·청백색 LED·닫힌 배식구 외형을 갖춘다. 이전 참고 이미지는 `Docs/Reference/GlassObservationPod_Concept.png`에 보존한다.

Unity 경로는 `Assets/Afrer_Seconds/` 기준이다. 외형·충돌 모델과 외형 프리팹은 `05.Model/Environment/B5/ObservationPod_Visual.fbx`, `ObservationPod_Collision.fbx`, `ObservationPod_Visual.prefab`에 있고, 정적 충돌을 조립한 프리팹은 `04.Prefabs/Environment/ObservationPod.prefab`이다. Blender 원본은 저장소의 `SourceAssets/ObservationPod/ObservationPod.blend`, 제작 기록은 `06.Data/AssetSources/ObservationPod_source_manifest.json`이다.

기존 감방 벽 3개·지붕·철창·벤치 Collider는 삭제하지 않고 비활성화했고, 포드에 정적 MeshCollider 24개를 조립했다. 기존 시작 위치·CharacterController 설정·게임 코드는 유지했다. Editor 검사에서 시작 위치 겹침 0건, 16방향 벽 Raycast와 8방향 CharacterController.Move의 차단을 확인했다. 배식구 개폐·기어 나가기·포드 탈출과 사격·교환 기능은 아직 없다. 기획서 V0.11의 9.2에서 현재 포드 제작 상태와 기존 철창 원안을 구분했다. 포드의 상호작용·탈출 경로는 검토 대상으로 남겼다.

확인할 씬은 `01.Scenes/Stage/`의 B5·B4·B3·B2·B1·1F다. 각 씬에 플레이어·카메라가 있어 **한 번에 하나씩** 열어 확인한다. Player 씬이나 다른 층을 함께 로드하지 않는다. 고정 렌더·Editor 충돌 검사는 실제 키보드 플레이나 퍼즐 완주 검증과 구분한다.

B5 임상 톤 정리 때 남은 건축 표면 접합 후보 26쌍은 `Docs/검수/2026-11-03_B5_Clinical_Tone/surface_overlap_audit.json`을 따라 확인한다. 아래는 이번 추가 배치·포드 제작 전부터의 작업 기록이며 현재 상태는 이 최상단 항목을 우선한다.


## 2026-11-03 모델 폴더 단순화 완료

사용자 요청에 따라 `05.Model`은 Player·Enemy·Props·Environment 네 분류로 정리했다. Props와 Environment는 B5/B4/B3/B2/B1/1F/Common으로 나누고, 각 분류/층 폴더에 모델·프리팹·메시를 바로 보관한다. 하위 폴더는 Materials와 Textures만 사용한다. 여러 층에서 쓰는 에셋은 Common 한 곳을 참조하며 복제하지 않는다. 기존 VARCO·Batch02·Models·Prefabs·Meshes·Repaired 중간 폴더는 제거했다.

상자·시료 용기·물류 용기는 `Props/Common`, 플레이어 모델은 `Player`, 경비 모델은 `Enemy`에 있다. 기존 03.Art/Candidates의 3D 모델 3종도 해당 분류로 이동했다. 제작 출처·반입 기록은 `06.Data/AssetSources`에 모았고 동작 FBX·Animator 자료는 기존 `07.Animator`에 유지했다. 414개 파일을 AssetDatabase로 이동해 대상 443개 GUID, 6개 층 의존 참조, 53개 FBX 내부 ID와 40개 프리팹 참조를 확인했다. 이동 전후 경로표와 검수는 `Docs/검수/2026-11-03_ModelFolderCleanup/정리결과.md`를 따른다. 과거 검수 스크립트의 반입 경로를 그대로 재실행하면 옛 폴더가 생길 수 있으므로 새 경로표를 적용한다.


## 2026-11-03 B5 일반 벽 텍스처 시범 적용

B5 격리실 일반 벽 7개에 신규 공용 머티리얼 1개와 PBR 텍스처 3개를 적용했다. 상단 도장 콘크리트·하단 회녹색 보호 도장을 미터 기준 UV로 매핑했다. 위치·형상·대상 벽의 Collider는 유지했고, 다른 층은 아직 확장하지 않았다. 반입 위치는 `05.Model/Environment/Common/Materials`와 `Common/Textures`, 벽 UV 메시는 `Environment/B5`이며 전후 비교와 재현 스크립트는 `Docs/검수/2026-11-03_WallTexture_Pilot/검수결과.md`에 있다. 벽을 이동·크기 변경하면 해당 UV 재계산이 필요하다.


## 2026-11-03 건축 모듈 재제작·재적용 완료

남아 있던 원본 형상 문제를 해결하려고 벽·관찰창·바닥·천장 6종을 Blender에서 재제작하고 고해상도 모델→감량·토폴로지 정리→최종 FBX 재검사→Unity 반입을 완료했다. B5 기존 54개 인스턴스에 적용했으며 관통 볼트 구멍·비뚤어진 외곽·관찰창의 불투명막을 제거했다. 관찰창 뒤에는 얕은 관찰실 외형 2개를 추가했다. 바닥 18개는 시각 오브젝트만 +2mm 보정해 경계 틈을 막았다. 기존 Collider와 게임 코드는 유지했다.

반입 폴더는 `05.Model/Environment/B5`, Blender 원본은 저장소의 `SourceAssets/Architecture_Rebuilt`다. 검수 자료는 `Docs/검수/2026-11-03_Architecture_Rebuild/검수결과.md`에 있다. 아래 이전 기록의 '원본 형상 재제작 필요' 항목은 이번 결과로 해결했다. 유료 VARCO 재생성은 사용하지 않았다.


## 2026-11-03 추가 20종 반입·적용 및 기존 메시 복구

- Batch02 20종을 500k 원본에서 감량·국소 리토폴로지 후 Unity 반입 완료. 6층에 60개 시각 인스턴스 적용. 기존 Collider·게임 로직 보존, 저장 씬 재열기·참조·겹침 검사 통과.
- 기존 V0.01 환경·프랍 8종은 고해상도 원본에서 복구. 원본 FBX·.meta를 보존하고 기존 프리팹에 Repaired/Models의 .asset 메시 연결. 최종 FBX 열린 경계·엄격한 면 관통 모두 0건. 천장만 31,218 triangles로 상향.
- 관찰창 원본의 불투명막, 벽 원본의 관통 볼트 구멍·불규칙한 외곽/모듈 경계 틈은 별도 재제작 대상으로 남음. 모든 외형 문제까지 해결한 상태는 아님.
- 검수: `Docs/검수/2026-11-03_Existing_VARCO_Repair/검수결과.md`, `Docs/검수/2026-11-03_VARCO_V002_Batch02/반입_적용결과.md`. 아래 이전 리토폴로지·반입 대기 기록은 이 결과로 갱신됨.


2026-11-03 · 작성자 송예찬 · 실제 저장된 폴더 구조 기준

## 프로젝트 열기

- Unity Hub에서 열 폴더: `After_Seconds_Build_V0.01` — `Assets`, `Packages`, `ProjectSettings`가 있는 폴더.
- Unity: **6000.4.0f1**
- URP: **17.4.0**
- Input System: **1.19.0**
- Cinemachine: **2.10.7**, Pipeline: **0.9.1-exp.1**
- 실제 작업 루트: `Assets/Afrer_Seconds/`. 현재 폴더명을 그대로 사용한다.

집에서는 최신 `main`을 먼저 받은 뒤 연다. CLI 설치·로그인·조회 명령은 [집 CLI 안내](../README.md#집에서-unity-cli로-이어하기)를 따른다. VARCO 브릿지는 선택 설치로 분리했으므로 학원 PC의 Downloads 경로 없이 패키지를 복원할 수 있다. 기존 FBX와 현재 SampleScene에는 브릿지가 필요하지 않다.

### Hub에서 빈 프로젝트처럼 보일 때

Hub에 등록할 실제 경로는 저장소 안의 **`Unity/After_Seconds_Build_V0.01`**이다. 옛 `Unity_Project_After_Seconds/After_Seconds_Build_V0.01` 경로에는 소스 Assets 없이 캐시·기본 설정만 남아 있었고, 이 경로를 열면서 에셋이 사라진 것처럼 보였다. 2026-11-02 정식 경로를 다시 등록해 B5 씬·Console 오류 0·경고 0을 확인했다. 옛 Hub 항목은 목록에서 제외했으며 폴더의 파일을 프로젝트 복구 원본으로 사용하지 않는다.

## B5 격리층 씬

`Assets/Afrer_Seconds/01.Scenes/Stage/Level_B5_Isolation.unity`를 열면 B5층 외형을 확인할 수 있다. `Room01_Isolation`, `Connector_Airlock`, `Room02_CoolingPool`, `Exit_StairVestibule`로 나누며 이동·걷기 검증 씬은 현재 `Player.unity`로 관리한다. B4 추가 제작은 아래 2026-11-03 기록을 따른다.

VARCO의 기존 모델 8종을 반입해 외형 58개를 배치했다. 환경은 `05.Model/Environment/B5`, 소품은 `05.Model/Props/B5`에 보관하며 각 `source_manifest.json`에 출처·실측·프리팹 경로를 기록한다. 원본은 로컬 `tmp`에 보존하고 프로젝트에는 8천~1만6천 삼각형 파생 FBX와 최대 2K 텍스처를 넣었다.

새 씬은 기존 플레이어·카메라 연결을 복제하고 시작 위치·방향만 B5에 맞춘다. 기존 코드·프리팹·모델·Animator·이동 설정은 수정하지 않았다. 통로·계단·부모 오프셋은 제작 가안이다. [배치와 검수 결과](../Docs/B5_레벨_구성.md)를 참고한다.

사격·교환·경비 AI·문 작동·체크포인트·층 전환은 아직 없다. 감방 탈출·냉각조 횡단은 해당 기능을 구현한 뒤 진행한다. Build Settings는 기존 SampleScene만 유지하며, B5는 Editor에서 씬을 열어 실행한다.

## B4 관찰층 추가 초안 · 2026-11-03

추가 스테이지 제작 요청으로 `Assets/Afrer_Seconds/01.Scenes/Stage/Level_B4_Observation.unity`를 구성했다. 3번 관찰 복도와 4번 관제 데크의 도면 치수·가림벽·2.5m 단상·정적 경비·상자·B3행 계단 연결부를 포함한다. 기존 `Player.unity`의 플레이어와 카메라 연결을 복제했으므로 **B4 씬 하나를 열어** 확인한다. Player 씬과 함께 로드하면 플레이어·카메라가 중복될 수 있다.

새 환경 재질·표지·계단 충돌 메시지는 `05.Model/Environment/B4/`에 보관한다. 기존 B5·Player·코드·프리팹·모델·Animator·ProjectSettings는 보존했다. 사격·교환·제압·경비 AI·자동문·체크포인트·층 전환은 추가하지 않았다. 상세 좌표·검수·미완료 범위는 [B4 레벨 구성](../Docs/B4_레벨_구성.md)을 따른다. 아래 과거 폴더 구조의 SampleScene·B5 위치는 사용자 변경 전 기록이며, 현재 Player·Stage 분류를 우선한다.

## B3 시료층 추가 초안 · 2026-11-03

`Assets/Afrer_Seconds/01.Scenes/Stage/Level_B3_SampleStorage.unity`에 5번 시료 저장고·6번 오염 제거 에어록을 구성했다. 1.5m 발판·가림벽·2.5m 선반·무거운 궤짝과, 2.4m 폭·1.2m 깊이 피트·닫힌 셔터·정적 경비·B2행 화물 리프트 외형을 포함한다. **B3 씬 하나만 열어** 확인한다.

공간·충돌·조명 초안이며 발판·셔터·교환·경비·엘리베이터 작동은 아직 없다. 닫힌 셔터 뒤의 구역은 Scene View로 확인할 수 있다. 새 환경 재질은 `05.Model/Environment/B3`, 2D 표지는 `03.Art/Environment/B3/Signs`에 분류했다. 기존 파일과 Build Settings는 보존했다. 치수·검수·제약은 [B3 레벨 구성](../Docs/B3_레벨_구성.md)을 따른다.

B3에는 후속 요청으로 노출·Bloom·궤짝 조명·측면 증기를 추가하고 표지 아틀라스·광원/그림자 정리·오클루전 베이크를 적용했다. 새 Volume은 `06.Data/Rendering/B3`, 공유 표지 UV 메시는 `05.Model/Environment/B3/Meshes`, 아틀라스·증기 이미지는 `03.Art/Environment/B3`에 있다. Collider·게임 로직은 유지했다. [조명·최적화 결과와 LOD 방안](../Docs/B3_조명과_최적화.md)을 참고한다.

## 남은 B2·B1·1F 초안 · 2026-11-03

`01.Scenes/Stage/`에 `Level_B2_Machinery.unity`, `Level_B1_Experiment.unity`, `Level_1F_Checkpoint.unity`를 추가했다. 각각 방 7·8, 방 9, 방 10의 기존 설계에 따른 공간·충돌·정적 경비·조명 초안이다. 이로써 B5~1F의 층별 씬이 모두 있으나 교환·AI·문·층 전환은 아직 연결하지 않았다. 각 씬에는 독립 검수용 플레이어·카메라가 있어 하나씩 열어 확인한다.

새 환경 재질·표지 UV 메시·계단 충돌 메시는 `05.Model/Environment`, 2D 표지 아틀라스는 `03.Art/Environment/UpperFloors`, Volume은 `06.Data/Rendering/UpperFloors`에 분류했다. 층별 오클루전을 베이크하고 방과 통로의 벽 두께를 반영해 접합부 중첩을 검사했다. 상세 좌표·이미지·검수·미완료 범위는 [상층부 레벨 구성](../Docs/상층부_레벨_구성.md)을 따른다.

## VARCO V0.02 설비 6종 적용 · 2026-11-03

리토폴로지한 설비 6종을 `Assets/Afrer_Seconds/05.Model/Props/`에 반입하고 각 층에 총 10개 외형을 배치했다. 현재 모델·프리팹은 각 층 폴더에 바로 있고, Textures·Materials만 하위 분리한다. source_manifest 등의 제작 기록은 06.Data/AssetSources에 있다. 해당 방의 `VARCO_V002_Visuals`에서 배치를 찾을 수 있다.

| 층 | 반입 에셋 | 배치 |
| --- | --- | --- |
| B5 | IsolationMonitoringConsole | 격리실 서쪽 벽·냉각조 동쪽 벽에 2개 |
| B4 | ObservationMonitorBank | 관찰 복도·관제 데크 벽에 2개 |
| B3 | DecontaminationColumn | 에어록 양옆에 2개 |
| B2 | ControlDeskIsland | 관제 섬 위에 2개, 사다리 중앙 공간 유지 |
| B1 | ExperimentServicePanel | 남쪽 데크 서쪽 벽에 1개, 부스 내부에는 추가하지 않음 |
| 1F | SecurityInspectionCounter | 검문소 동쪽 벽 쪽에 1개 |

배치 높이·크기는 💡 외형 제작 가안이다. 6개 씬을 저장 후 다시 열어 메시·재질·프리팹 참조와 누락 스크립트 없음, 기존 Collider 기록 동일, 신규 외형 Collider 없음, 기존 충돌체와 신규 외형 bounds 겹침 없음을 확인했다. B3 가운데 기존 노즐 2개는 새 기둥과 중복돼 Renderer만 끄고 오브젝트를 보존했다. 기존 기획 치수·게임 코드·Player 씬·Animator·ProjectSettings·오클루전 데이터를 변경하지 않았다. 신규 외형은 정적 차폐물로 베이크하지 않으며 기존 조명·오클루전 베이크도 다시 만들지 않았다.

glTF의 금속·거칠기·AO 채널을 URP용 Metallic/Smoothness와 Occlusion으로 변환했고, 노멀 강도는 💡 0.35다. 신규 외형에는 그림자 투사를 끄고 기존 조명으로 확인했다. 저장된 6개 씬의 검수 렌더·참조 검증·파일 보존 기록은 [VARCO 검수 폴더](../Docs/검수/2026-11-03_VARCO_V002/)에 있다. 실제 퍼즐 완주·사격·교환·장치 동작 검증을 뜻하지 않는다. B5의 기존 벽·천장 생성 메시 깨짐은 별도 문제로 남아 있다.

## 현재 폴더 구조

아래는 `After_Seconds_Build_V0.01` 안의 게임 작업 폴더다. `.meta`는 생략했다. V0.3은 별도 보정 후보이며 Unity Humanoid 반입과 임시 미리보기 검수를 완료했다.

```text
Assets/Afrer_Seconds/
  01.Scenes/
    Player.unity                     # 기존 이동·걷기 검증 씬
    Stage/
      Level_B5_Isolation.unity        # B5층 전용
      Level_B4_Observation.unity      # B4층 초안, 독립 검수용 플레이어 포함
      Level_B3_SampleStorage.unity    # B3층 초안, 독립 검수용 플레이어 포함
      Level_B2_Machinery.unity        # 방 7·8, 독립 검수용 플레이어 포함
      Level_B1_Experiment.unity       # 방 9, 독립 검수용 플레이어 포함
      Level_1F_Checkpoint.unity       # 방 10, 독립 검수용 플레이어 포함
  02.Scripts/
    A.Define/DefineAD.asmdef
    B.Simulator/SimulatorAD.asmdef
    C.System/
      SystemAD.asmdef
      Player/
        InputSystem_Actions.inputactions
        PlayerInputSystem.cs          # 보관용, 현재 입력 흐름에 사용하지 않음
        PlayerMotor.cs
        PlayerMotorSettings.cs
        PlayerLook.cs
        PlayerLookSettings.cs
        PlayerAnimationSystem.cs
    D.Ui/UI_AD.asmdef
    E.Manager/ManagerAD.asmdef
    F.Presenter/
      PresenterAD.asmdef
      Player/PlayerPresenter.cs
  03.Art/
    Environment/                    # 2D 표지·아틀라스 등
  04.Prefabs/
    Environment/
      ObservationPod.prefab          # 외형·정적 충돌 조립, 탈출 기능은 미구현
  05.Model/
    Player/                         # 기준 모델·모델 단계 프리팹
      Materials/
      Textures/
    Enemy/
      Materials/
      Textures/
    Props/
      Common/                       # 상자·시료 용기·공용 설비
      B5/                           # 각 폴더에 모델·프리팹을 바로 보관
      B4/
      B3/
      B2/
      B1/
      1F/
    Environment/
      Common/                       # 여러 층에서 쓰는 배관·덕트·공용 재질
      B5/
      B4/
      B3/
      B2/
      B1/
      1F/
    # Props·Environment의 층/Common 폴더에도 Materials·Textures만 하위 분리
  06.Data/
    AssetSources/                   # 제작 출처·반입·검수 JSON/안내
    PlayerMotorSettings.asset
    PlayerLookSettings.asset
  07.Animator/
    Player/
      Clips/
        Player_Idle.fbx
        Player_Walk.fbx
        Player_Run.fbx
        Player_Jump.fbx
        Player_Land.fbx
        Player_Pickup.fbx
        Rigged_V0.3/                  # 별도 보정 리그에서 재생성한 동작
          Player_Idle.fbx
          Player_Walk.fbx
          Player_Run.fbx
          Player_Jump.fbx
          Player_Land.fbx
          Player_Pickup.fbx
        Invector_Basic/               # 전방 Walk·Run·Sprint 독립 .anim 비교 후보
      Controllers/
        Player_Animator.controller   # 기존 상태 구성 유지, V0.3 Motion 6개 연결
```

## 폴더별 사용 기준

| 폴더 | 보관할 내용 | 현재 상태 |
| --- | --- | --- |
| `01.Scenes` | 맵과 레벨, 층별 별도 씬 | SampleScene 보존, B5 격리층 별도 구성 |
| `02.Scripts` | 책임에 따라 분리한 게임 코드와 AD | 6개 AD와 입력·이동·시야·Presenter 코드 |
| `03.Art` | **2D 이미지 전용. UI·컷씬 등 종류별 하위 폴더로 분류** | 2D 표지·아틀라스·증기 이미지. 과거 VARCO 모델은 05.Model로 정리 완료 |
| `04.Prefabs` | **충돌·설정을 조립하고 해당 기능을 검증한 게임 에셋** | Environment/ObservationPod.prefab의 외형·정적 충돌 조립 완료. 배식구·탈출 기능은 미구현 |
| `05.Model` | **기준 리깅 모델·부속 재질과 조립 중인 외형 에셋** | Player·Enemy는 직접 분류, Props·Environment는 층별/Common으로 분류. 하위는 Materials·Textures만 사용하고 제작 기록은 06.Data/AssetSources에 보관함 |
| `06.Data` | ScriptableObject 설정 에셋 | 이동·시야 설정 |
| `07.Animator` | **동작 FBX·클립 및 AnimatorController·AnimatorOverrideController·AvatarMask** | Player/Clips에 기존 동작 6종을 유지하며 Rigged_V0.3에 신규 6종을 분리함. Controller는 Player/Controllers에서 관리함 |

앞으로 `03.Art`에는 2D 이미지만 추가한다. UI 이미지는 `03.Art/UI/`, 컷씬 이미지는 `03.Art/Cutscenes/`처럼 이미지 종류별 하위 폴더로 분류한다. 필요한 종류의 폴더는 해당 이미지를 반입할 때 만든다.

앞으로 가져오는 기준 리깅 모델과 부속 재질·외형 에셋은 `05.Model`의 용도에 맞는 분류에 정리한다. 플레이어에 사용할 모델은 `05.Model/Player`에, 환경·경비·소품은 해당 분류에 둔다. 모델을 묶은 `.prefab` 형식의 파일도 이 단계에서는 `05.Model`에서 관리한다. 동작이 필요한 에셋은 스크립트와 설정을 연결해 검증한 뒤 `04.Prefabs`에서 관리한다. ObservationPod는 검증한 정적 충돌을 외형과 조립해 이곳에 둔 경우이며, 프리팹 경로가 배식구·탈출 기능 완성을 뜻하지 않는다.

동작 FBX·애니메이션 클립과 Animator 구성 리소스는 `07.Animator`에서 관리한다. 플레이어용은 `07.Animator/Player/`, 경비용은 `07.Animator/Enemy/`처럼 대상별로 나누고, 그 아래 `Clips/`에 동작 FBX·클립을, `Controllers/`에 AnimatorController(`.controller`)·AnimatorOverrideController(`.overrideController`)를 둔다. AvatarMask(`.mask`)를 사용할 때는 해당 대상의 `Masks/` 폴더를 만든다. 현재 플레이어 동작 FBX 6종은 `07.Animator/Player/Clips/`에 정리했다.

현재 `03.Art/Candidates/VARCO/`에 남아 있는 모델·텍스처·재질·검수 기록은 과거 반입 결과이며, 위의 신규 파일 분류 기준과 구분한다. 기존 `05.Model`의 모델 프리팹과 리깅 모델이 이 위치의 재질·텍스처 등을 참조하므로 이번에는 과거 파일을 일괄 이동하지 않는다. 사용자가 이름을 바꾼 기존 `PlayerDummy_Rigged_V0.2.fbx`와 반입 기록은 `05.Model/Player/Rigged`에 유지한다. `AS05_PlayerDummy_Rigged.fbx`는 당시 반입명이며 현재 파일명과 구분한다. 추후 기존 파일을 정리할 때는 Unity 안에서 파일과 `.meta`를 함께 이동해 참조를 유지한다. 2026-11-02에는 사용자가 B5층 제작을 요청해 별도 씬에 배치했다. 게임 로직은 사용자가 의사코드부터 직접 구현한다.

## 코드 계층의 역할과 설정

| 폴더와 AD | 담당할 역할 | 현재 저장된 설정 |
| --- | --- | --- |
| `A.Define` · `DefineAD` | 식별자·값·상태·데이터 계약 | 내부 참조 없음, No Engine References 활성화 |
| `B.Simulator` · `SimulatorAD` | 시간·예약·교환 등 순수 규칙 | DefineAD 참조, No Engine References 활성화 |
| `C.System` · `SystemAD` | Unity 입력·물리·Transform·설정 데이터 연결 | Unity.InputSystem 참조 |
| `D.Ui` · `UI_AD` | 화면 표시와 UI 입력 | AD 이름만 설정 |
| `E.Manager` · `ManagerAD` | 세션 생성·종료·재시작과 기능 조립 | AD 이름만 설정 |
| `F.Presenter` · `PresenterAD` | 시스템·규칙·화면 표시 연결 | SystemAD·Unity.InputSystem 참조 |

다른 계층의 타입이 필요할 때 허용 참조표에 맞춰 AD 참조를 추가한다. 자세한 설계 제안은 [계층 분석·학습 순서](../Docs/Unity_계층_설계와_학습_순서.md)를 참고한다.

## 반입한 모델

| 모델 | 현재 위치 | 상태 |
| --- | --- | --- |
| 회색 플레이어 더미 | [05.Model/Player/Player_Dummy_V0.1.prefab](After_Seconds_Build_V0.01/Assets/Afrer_Seconds/05.Model/Player/Player_Dummy_V0.1.prefab) | V0.3 외형·Animator를 기준 프리팹에도 적용, WASD와 Idle·Walk 연결 |
| 주황 경비 더미 | [05.Model/Enemy/Enemy_Guard_V0.1.prefab](After_Seconds_Build_V0.01/Assets/Afrer_Seconds/05.Model/Enemy/Enemy_Guard_V0.1.prefab) | 정적 T포즈, 높이 💡 1.8m |
| 시료 궤짝 | [05.Model/Props/Common/Props_Crate_V0.1.prefab](After_Seconds_Build_V0.01/Assets/Afrer_Seconds/05.Model/Props/Common/Props_Crate_V0.1.prefab) | 높이 💡 1m |

위 높이와 충돌체 치수는 테스트용 가안이다. 경비 더미는 정적 T포즈이며 플레이어는 V0.3 외형·Animator와 WASD에 따른 Idle·Walk를 연결했다. 이동·시야 회전은 현재 SampleScene에서 확인했으며, 사격·경비 행동·교환 규칙은 아직이다. 세 후보 모두 8,000 triangles이며 색상·노멀 텍스처를 URP 재질에 연결했다. 자세한 상태와 출처는 [VARCO 에셋 반입 안내](After_Seconds_Build_V0.01/Assets/Afrer_Seconds/06.Data/AssetSources/Candidates_VARCO_README.md)를 참고한다.

2026-10-29의 기존 반입 모델은 현재 `05.Model/Player/PlayerDummy_Rigged_V0.2.fbx`, 기존 동작 FBX 6종은 `07.Animator/Player/Clips/`에 있다. 걷기는 사용자가 선택한 **좌발 전방걷기**다. 당시 Humanoid Avatar와 단위 변환을 확인했지만, 이후 하체 관절 오배치와 스킨 변형 문제가 확인되어 완성 리그로 판정하지 않는다.

손가락 본 30개를 보존한 별도 편집 리그에서 하체 관절을 바로잡고 동작 6종을 다시 적용한 V0.3 후보를 반입했다. 신규 기준 모델은 `05.Model/Player/PlayerDummy_Rigged_V0.3.fbx`, 신규 동작은 `07.Animator/Player/Clips/Rigged_V0.3/Player_*.fbx`로 분리했다. 웹 편집 저장본의 스킨 인덱스 불일치는 로컬에서 재매핑했으며, 웹 원본을 그대로 다시 받는 방식으로 대체하지 않는다. 새 7개 모두 유효한 Humanoid Avatar·매핑 52개(몸 22·손가락 30)·본과 bindpose 53개를 확인했다. 동작 6종을 임시 PreviewScene에서 9개 시점씩 총 54개 샘플로 확인했으며, 반입 검수 당시에는 기존 보호 파일 116개의 SHA-256과 사용자 씬·연결 상태를 유지했다. 이후 추가 승인으로 진행한 씬 연결은 아래 항목과 구분한다. 미세 찝힘·접지·루프·손 쥐기 품질은 추가 검수 대상이다. 파일별 출처·검증 상태·독립 발가락과 손가락의 제한은 [플레이어 리깅·애니메이션 안내](After_Seconds_Build_V0.01/Assets/Afrer_Seconds/06.Data/AssetSources/Player_Rigged_README.md)를 따른다.

## Invector 이동 애니메이션 보관

실습 프로젝트에서 사용 중인 전방 Walk·Run·Sprint를 독립 Humanoid `.anim`으로 추출해 `07.Animator/Player/Clips/Invector_Basic/`에 비교 후보로 보관했다. 원본 곡선·반복·루트 설정과 출처를 유지하며, 기존 `Rigged_V0.3` 동작·Animator·플레이어·씬에는 연결하지 않았다. 파일별 길이·출처·검수 범위는 [보관 안내](After_Seconds_Build_V0.01/Assets/Afrer_Seconds/07.Animator/Player/Clips/Invector_Basic/README.md)를 따른다.

## 현재 플레이어 연결

`PlayerInput`의 `Invoke Unity Events`로 Move → `PlayerPresenter.OnMove`, Look → `PlayerPresenter.OnLook`를 연결했다. Presenter는 매 프레임 `PlayerLook.Rotate`를 먼저 호출하고 `PlayerMotor.Move`에 입력과 경과 시간을 전달한다. 사용자 코드의 `PlayerPresenter → PlayerAnimationSystem.isMove → Animator.IsMoving`이 이동 입력 여부를 전달해 WASD와 Idle·Walk를 전환한다. 실제 위치 변화가 아닌 입력 유무를 기준으로 한다. 이동은 CharacterController, 상하 시야 회전은 CameraRoot가 담당하며 Cinemachine Virtual Camera가 CameraRoot를 따른다.

사용자가 `05.Model/Player/Player_Dummy_V0.1.prefab`에도 V0.3 외형·Animator와 현재 구성을 적용했다. SampleScene과 기준 플레이어 프리팹을 함께 관리하며, 학습 중인 입력·이동·애니메이션 구성을 조립·검증한 뒤 `04.Prefabs`의 완성 게임 에셋으로 관리한다.

SampleScene의 `Player_Dummy_V0.1/VisualRoot` 아래 `PlayerDummy_Rigged_V0.3`은 유효한 V0.3 Avatar와 기존 [Player_Animator](After_Seconds_Build_V0.01/Assets/Afrer_Seconds/07.Animator/Player/Controllers/Player_Animator.controller)를 사용하며 Apply Root Motion은 껐다. 현재 모델 로컬 Y는 `0.4`, CharacterController의 Center Y는 `0.3`, Height는 `1.8`이다. 기존 V0.2 모델 파일과 이전 동작은 비교용으로 보존한다.

최초 V0.3 연결에서는 Controller 상태 6개의 Motion만 교체하고 기존 전이·파라미터·속도를 유지했다. 당시 보호 대상 134개 중 변경은 승인한 SampleScene·Controller 2개뿐이었다. [최초 씬 연결 검수 기록](../Docs/검수/2026-10-29_Player_FullRig/scene-connection.json)은 이후의 사용자 코드·프리팹 적용·걷기 보정 전 기록으로 구분한다.

최신 Walk는 `Rigged_V0.3/Player_Walk.fbx`의 원본 프레임 `124–160`을 사용해 길이가 약 `1.2초`이며 Loop Time·Loop Pose를 켰다. Walk State는 `1.5배`여서 한 주기는 약 `0.8초`, Motor의 이동 속도는 `1.5m/s`다. 구간을 자른 뒤 Height Offset은 `0.164 → 0.227`로 다시 보정했다. 원본 FBX와 키는 그대로이며 importer의 사용 구간만 바꿨다. 이전 약 7.5초 전체 시퀀스와 과거 검수 기록은 보존한다.

실제 약 `3.30초` 동안 약 `4.13회` 반복했고 CharacterController 접지는 `51/51` 샘플이었다. 이동 속도 약 `1.5m/s`, 모델 로컬 yaw `0°`를 확인했다. 지면 대비 발바닥 높이 잔차는 약 `−0.016~+0.045m`로 남아 있어 완전한 접지·발 미끄러짐 제거 판정은 아니다. 기존 Run → Walk의 상충 조건, Land 조건, Pickup 복귀 전이는 이번 걷기 보정에서 수정하지 않았다.

`06.Data/PlayerLookSettings.asset`의 현재 감도는 좌우·상하 각각 💡 0.1, 상하 제한은 💡 -80°~80°다. C# 파일은 프로젝트 루트 `.editorconfig`의 UTF-8 BOM 설정을 기준으로 편집한다.

## 버전 관리와 다음 작업

Assets와 `.meta`, Packages, ProjectSettings를 함께 버전 관리한다. Library·Temp·Logs·Obj·UserSettings는 각 PC에서 재생성하므로 제외한다.

사용자가 직접 분석 → 의사코드 → 구현을 진행한다. **현재 WASD와 Idle·Walk 연동, 걷기 한 주기의 반복·높이·속도 보정까지 확인했다.** 다음은 점프·스프린트·상호작용과 관련 애니메이션을 의사코드로 분석한 뒤 사용자가 코드를 작성하고 검토하는 단계다. 기존 전이 조건과 발 접촉·미세 변형도 이어서 검수한다. 손가락 본 보존은 쥐기 애니메이션이나 손 상호작용 구현 완료를 뜻하지 않는다. 예약·교환 의사코드와 규칙 구현은 이후 남은 작업이며, A/B안은 프로토타입으로 비교한 뒤 결정한다.

- [최신 이어하기](../Docs/이어하기_2026-11-04.md)
- [초기 집 작업 준비 기록](../Docs/이어하기_2026-10-26.md)
- [계층 분석·학습 순서](../Docs/Unity_계층_설계와_학습_순서.md)
