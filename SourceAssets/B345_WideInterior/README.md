# 확장 복도·원호 아치 제작 원본 V0.02

현재 기준은 평면V0.04와 터널·돔 단면이다. 큰 차폐벽12개를 제거하고 벽면 설비12개를 배치했다. 주요실 돔10곳과 기존 평천장/조명 제거를 포함한다. 아래 V0.03 확장 설명 뒤의 제작 순서는 현재 후속 내용을 우선한다.

1. `wide_plan.py`는 확장 전 스냅샷에서 설계 원안을 재생성한다. 최종 예상 동선을 덮어쓰므로 단독 재실행하지 않는다.
2. `build_wide.py`, `prepare_tools.py` → `build_arches.py`가 WC/WA 모델을 만든다. 돔과 터널 함수는 dome_geometry.txt/tunnel_geometry.txt다.
3. 최초 확장은 ApplyWide.Apply가1회 수행했고, 현재 후속 아트 교체는 Structure/RebuildArches다. 현재 씬에 최초 Apply를 다시 하지 않는다.
4. `ReplanRoutes.Run`으로 B5/B4/B3 도면 동선을 현재 정적 충돌/바닥 기준으로 재계산한다. 게임 C#이 아니다.
5. render_plans.ps1/render_routes.ps1/render_sections.ps1은 현재 JSON을 읽어 SVG/PNG만 갱신한다.
6. WideValidate/WideWalk/WideAudit, 반사 갱신·사진·반입 검수를 수행한다. 최종 수치는 최신 검수 문서에 있다.

새 조명은 복도16개/층 + 돔12/24/14개다. 기존 B4 조명 이름은 숫자 접미사 없는 Ceiling_A/AN/AS/B/D도 있으므로 함께 정리한다. 원본 Asset과 GUID를 보존하고, 현재 제작 모델만 업데이트한다.

반사 굽기는 `renderDynamicObjects=true`로 일반 배치 메시까지 포함한다. 인물 렌더러는 굽는 동안만 숨긴다. 이 설정을 빼면 B3 반사 이미지가 비게 되므로 유지한다. 최종 전체25개를 재생성했고, 단일 층 재검사 파일은 실제 층 이름으로 저장한다.

아래 날짜별 문단은 이전 작업 이력이다.

작성자 송예찬 · 2026-11-06

사용자 요청은 B5/B4/B3 복도 확장, 더 둥글고 돌출된 아치, 기존 조명 겹침 정리와 개수 감축이다. 기준 이미지는 `Docs/Reference/Reference_004.jpg`다. 게임 C#·AI·문 동작·UI는 작성하지 않는다.

현재 제작 좌표는 `wide_plan.py`가 `layout_before.json`/`routes_before.json`에서 만든다. 일반 복도3→4.2m, 북측4→4.8m로 확장한다. 방 크기를 줄이지 않고 일반 출입구1.5m와 계단 치수를 유지한다. 수직 코어는 동쪽3.6m·남쪽0.8m 이동한다. B2/B1/1F는 동일 수직 코어 좌표의 도면만 갱신하며 새 Unity 레벨을 제작하지 않았다.

- `build_wide.py`: LC B5/B4, SD B3, WS 벽과 B4 ServiceDetails 편집 원본을 읽어 파생 WC 모델을 만든다. 소스/기존 Unity 모델과 GUID를 유지한다. 기존 복도 LightBody/LightLens를 파생 모델에서 제외한다. 배치 조각 이름은 기존 씬과 연결하기 위해 LC/WS 이름을 유지한다.
- `build_arches.py`: 새 평면의 곡면 마감과 원호 아치를 Blender 메시로 만든다. 아치 단면0.24m·복도 방향 깊이0.44m·주 베벨22mm. 발 돌출 약0.58m, 몸통 약0.44m. 확산판은 천장에 밀착하고 약8m 간격으로 배치한다.
- `ApplyWide.cs`: 외부 Editor 도구. 새 Mesh 참조를 연결하고 건축 충돌을 맞추며 문·프랍·인물·플레이어·반사를 옮긴다. 한 번만 적용하며 `Wide_Corridor_V0.01` 표식으로 중복 적용을 막는다. Arched_Interior만 재제작 가능하다. 씬 적용 전 사본은 Projects/Management/AfterSeconds_Wide_20261106에 있다.
- `WideValidate/WideWalk/WideAudit/WideReview`: 경로·문·프랍·계단·마감·사진 검수. 실제 사용자 키보드 플레이와 별개다. 최신 수치는 [검수결과](../../Docs/검수/2026-11-06_B345_WideInterior/검수결과.md)를 따른다.
- `render_plans.ps1`/`render_routes.ps1`: 현재 JSON을 읽어 SVG/PNG와 예상 경로 복사본을 만든다. 도면의 기존 V0.02 생성기는 덮어쓰기 방지를 위해 중지 안내를 넣었다. `prepare_drawings.py`는 렌더러 생성 도구다.

Blender FBX 원본은 WC/WA .blend이며 모서리 베벨은 편집 가능한 상태로 저장한다. Unity 모델은 `05.Model/Environment/{B5,B4,B3}`에 바로 놓고, 텍스처·재질은 기존 공용 WS/AR 계열을 재사용한다. 생활 흔적 상자 SW와 신규 프랍101개는 유지한다. 원래 SC/SD/LC 모델과 이전 제작 도구를 현재 확장 씬에 덮어 적용하지 않는다.
